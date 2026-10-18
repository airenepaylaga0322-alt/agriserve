import io
import csv
from flask import send_file
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func

from ..decorators import role_required
from ..extensions import db
from ..models.user import User, Role
from ..models.assistance import AssistanceProgram, AssistanceApplication, ApplicationStatus
from ..forms import ProgramForm

bp = Blueprint("admin", __name__)


@bp.route("/dashboard")
@login_required
@role_required(Role.ADMIN, Role.OFFICER)
def dashboard():
    total_farmers = db.session.query(func.count(User.id)).filter(User.role == Role.FARMER).scalar() or 0
    total_officers = db.session.query(func.count(User.id)).filter(User.role == Role.OFFICER).scalar() or 0
    total_admins = db.session.query(func.count(User.id)).filter(User.role == Role.ADMIN).scalar() or 0
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()

    return render_template(
        "admin/dashboard.html",
        total_farmers=total_farmers,
        total_officers=total_officers,
        total_admins=total_admins,
        recent_users=recent_users,
    )


@bp.route("/programs", methods=["GET", "POST"])
@login_required
@role_required(Role.ADMIN)
def programs():
    form = ProgramForm()
    if form.validate_on_submit():
        prog = AssistanceProgram(
            code=form.code.data,
            name=form.name.data,
            category=form.category.data,
            description=form.description.data,
            available_allocation=form.available_allocation.data,
            max_benefit_per_farmer=form.max_benefit_per_farmer.data,
        )
        db.session.add(prog)
        db.session.commit()
        flash("Program created successfully!", "success")
        return redirect(url_for("admin.programs"))
        
    all_programs = AssistanceProgram.query.order_by(AssistanceProgram.created_at.desc()).all()
    return render_template("admin/programs.html", form=form, programs=all_programs)


@bp.route("/applications")
@login_required
@role_required(Role.ADMIN, Role.OFFICER)
def review_applications():
    apps = AssistanceApplication.query.order_by(AssistanceApplication.submitted_at.desc()).all()
    return render_template("admin/review_applications.html", applications=apps)


@bp.route("/applications/<int:app_id>/decide", methods=["POST"])
@login_required
@role_required(Role.ADMIN, Role.OFFICER)
def decide_application(app_id):
    app_record = AssistanceApplication.query.get_or_404(app_id)
    
    decision = request.form.get("decision") 
    reason = request.form.get("reason", "").strip()
    
    if decision not in ["approved", "rejected"]:
        flash("Invalid decision.", "danger")
        return redirect(url_for("admin.review_applications"))
        
    if not reason:
        flash("You must provide a reason for the decision.", "warning")
        return redirect(url_for("admin.review_applications"))

    app_record.status = ApplicationStatus.APPROVED if decision == "approved" else ApplicationStatus.REJECTED
    app_record.decided_by_id = current_user.id
    app_record.decided_at = datetime.utcnow()
    app_record.decision_reason = reason
    
    db.session.commit()
    
    flash(f"Application {app_record.reference_code} has been {decision}.", "success")
    return redirect(url_for("admin.review_applications"))

@bp.route("/export/excel")
@login_required
@role_required(Role.ADMIN)
def export_excel():
    """Generates an Excel file of all farmers and their applications."""
    
    # 1. Create the workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Farmer Applications"

    # 2. Define Headers
    headers = [
        "Farmer Name", "Email", "Barangay", "Municipality", 
        "Program Applied", "Farm Code", "Status", "Date Submitted", "Admin Decision Reason"
    ]
    
    # Style the header row
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="174D35", end_color="174D35", fill_type="solid")
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill

    # 3. Fetch all applications (joining with user and program data)
    apps = AssistanceApplication.query.order_by(AssistanceApplication.submitted_at.desc()).all()

    # 4. Populate the rows
    for row_num, app in enumerate(apps, 2):
        farmer = app.farmer_user
        profile = farmer.profile
        
        ws.cell(row=row_num, column=1, value=farmer.full_name)
        ws.cell(row=row_num, column=2, value=farmer.email)
        ws.cell(row=row_num, column=3, value=profile.barangay if profile else "N/A")
        ws.cell(row=row_num, column=4, value=profile.municipality if profile else "N/A")
        ws.cell(row=row_num, column=5, value=app.program.name)
        ws.cell(row=row_num, column=6, value=app.farm.farm_code if app.farm else "N/A")
        ws.cell(row=row_num, column=7, value=app.status.upper())
        ws.cell(row=row_num, column=8, value=app.submitted_at.strftime('%Y-%m-%d') if app.submitted_at else "")
        ws.cell(row=row_num, column=9, value=app.decision_reason or "")

    # 5. Auto-adjust column widths
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # 6. Save to a memory buffer (so we don't write temp files to the disk)
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="AgriServe_Farmer_Data.xlsx"
    )