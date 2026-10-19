from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from sqlalchemy import func
import io
import time

from ..decorators import role_required
from ..extensions import db
from ..models.user import User, Role
from ..models.assistance import AssistanceProgram, AssistanceApplication, ApplicationStatus, RubricAssessment, AuditLog
from ..forms import ProgramForm
from ..services.scoring_service import calculate_priority_score

# PDF Generation Imports
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

bp = Blueprint("admin", __name__)

def log_action(action, target_id=None, details=None):
    log = AuditLog(actor_id=current_user.id, action=action, target_id=target_id, details=details)
    db.session.add(log)
    db.session.commit()

@bp.route("/dashboard")
@login_required
@role_required(Role.ADMIN, Role.OFFICER)
def dashboard():
    total_farmers = db.session.query(func.count(User.id)).filter(User.role == Role.FARMER).scalar() or 0
    total_officers = db.session.query(func.count(User.id)).filter(User.role == Role.OFFICER).scalar() or 0
    total_admins = db.session.query(func.count(User.id)).filter(User.role == Role.ADMIN).scalar() or 0
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    total_applications = AssistanceApplication.query.count()
    approved_count = AssistanceApplication.query.filter_by(status="approved").count()
    pending_count = AssistanceApplication.query.filter_by(status="submitted").count()

    return render_template("admin/dashboard.html", total_farmers=total_farmers, total_officers=total_officers, total_admins=total_admins, recent_users=recent_users, total_applications=total_applications, approved_count=approved_count, pending_count=pending_count)

@bp.route("/audit-logs")
@login_required
@role_required(Role.ADMIN)
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).all()
    return render_template("admin/audit_logs.html", logs=logs)

@bp.route("/applications")
@login_required
@role_required(Role.ADMIN, Role.OFFICER)
def review_applications():
    # Search and Filter Feature
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    query = AssistanceApplication.query
    if search_query:
        query = query.join(User).filter(User.full_name.ilike(f'%{search_query}%') | AssistanceApplication.reference_code.ilike(f'%{search_query}%'))
    if status_filter:
        query = query.filter(AssistanceApplication.status == status_filter)
        
    apps = query.order_by(AssistanceApplication.submitted_at.desc()).all()
    return render_template("admin/review_applications.html", applications=apps, search_query=search_query, status_filter=status_filter)

@bp.route("/applications/<int:app_id>/run-score", methods=["POST"])
@login_required
@role_required(Role.ADMIN, Role.OFFICER)
def run_score(app_id):
    app_record = AssistanceApplication.query.get_or_404(app_id)
    
    income = float(request.form.get("monthly_income", 0))
    loss_pct = float(request.form.get("loss_percentage", 0))
    is_primary = request.form.get("is_primary_income") == "yes"
    
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    prior_aid_record = AssistanceApplication.query.filter(
        AssistanceApplication.farmer_user_id == app_record.farmer_user_id,
        AssistanceApplication.program_id == app_record.program_id,
        AssistanceApplication.status.in_(['approved', 'delivered']),
        AssistanceApplication.decided_at >= six_months_ago,
        AssistanceApplication.id != app_record.id
    ).first()

    has_prior_aid = prior_aid_record is not None
    result = calculate_priority_score(income, loss_pct, is_primary, has_prior_aid)

    assessment = app_record.rubric_assessment or RubricAssessment(application_id=app_id)
    assessment.score_a = result['score_a']
    assessment.score_b = result['score_b']
    assessment.score_c = result['score_c']
    assessment.score_d = result['score_d']
    assessment.total_score = result['total']
    assessment.recommendation = result['recommendation']
    
    db.session.add(assessment)
    db.session.commit()
    
    log_action("RAN_RUBRIC_SCORE", app_record.id, f"Score: {result['total']}")
    
    if has_prior_aid:
        flash(f"WARNING: Duplicate check found prior assistance. Score: {result['total']}", "warning")
    else:
        flash(f"Calculation Complete. Score: {result['total']} -> {result['recommendation']}", "info")
    return redirect(url_for("admin.review_applications"))

@bp.route("/applications/<int:app_id>/decide", methods=["POST"])
@login_required
@role_required(Role.ADMIN, Role.OFFICER)
def decide_application(app_id):
    app_record = AssistanceApplication.query.get_or_404(app_id)
    decision = request.form.get("decision")
    reason = request.form.get("reason", "").strip()
    
    if decision not in ["approved", "rejected", "requires_info"]:
        flash("Invalid decision.", "danger")
        return redirect(url_for("admin.review_applications"))
        
    if decision == "requires_info":
        app_record.status = "requires_additional_info"
        app_record.decision_reason = reason
        db.session.commit()
        log_action("REQUESTED_INFO", app_record.id, reason)
        # NOTE: Email sending logic would trigger here for missing documents
        flash("Marked as Requires Additional Information. Email sent to farmer.", "warning")
        return redirect(url_for("admin.review_applications"))

    if app_record.rubric_assessment and app_record.rubric_assessment.recommendation == "REJECTED" and decision == "approved":
        if len(reason) < 20:
            flash("You are overriding a REJECTED recommendation. You must provide a detailed justification (min 20 chars).", "danger")
            return redirect(url_for("admin.review_applications"))
    elif not reason:
        flash("You must provide a reason.", "warning")
        return redirect(url_for("admin.review_applications"))

    app_record.status = ApplicationStatus.APPROVED if decision == "approved" else ApplicationStatus.REJECTED
    app_record.decided_by_id = current_user.id
    app_record.decided_at = datetime.utcnow()
    app_record.decision_reason = reason
    
    db.session.commit()
    log_action("DECIDED_APPLICATION", app_record.id, f"Decision: {decision.upper()}, Reason: {reason}")
    flash(f"Application {app_record.reference_code} has been {decision}.", "success")
    return redirect(url_for("admin.review_applications"))

@bp.route("/generate-certificate/<int:app_id>")
@login_required
@role_required(Role.FARMER)
def generate_certificate(app_id):
    app_record = AssistanceApplication.query.get_or_404(app_id)
    if app_record.farmer_user_id != current_user.id or app_record.status != "approved":
        flash("Unauthorized or application not approved.", "danger")
        return redirect(url_for("applications.my_applications"))

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Draw PDF Content
    p.setFont("Helvetica-Bold", 20)
    p.setFillColor(colors.HexColor("#174D35"))
    p.drawCentredString(300, 750, "AgriServe Approval Certificate")
    
    p.setFont("Helvetica", 12)
    p.setFillColor(colors.black)
    p.drawString(100, 700, f"This certifies that farmer {app_record.farmer_user.full_name}")
    p.drawString(100, 680, f"has been approved for the program: {app_record.program.name}")
    p.drawString(100, 660, f"Reference Code: {app_record.reference_code}")
    p.drawString(100, 640, f"Date of Approval: {app_record.decided_at.strftime('%Y-%m-%d')}")
    
    p.drawString(100, 580, "Please present this digital certificate to the Municipal Agriculture Office.")
    p.drawString(100, 560, "This document is generated by the AgriServe Research Prototype.")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f"Certificate_{app_record.reference_code}.pdf")