import time
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..extensions import db
from ..decorators import role_required
from ..models.user import Role
from ..models.assistance import AssistanceProgram, AssistanceApplication, ApplicationStatus
from ..models.farmer import Farm
from ..forms import ApplyForm

bp = Blueprint("applications", __name__)

@bp.route("/")
@login_required
@role_required(Role.FARMER)
def my_applications():
    apps = AssistanceApplication.query.filter_by(farmer_user_id=current_user.id).order_by(AssistanceApplication.submitted_at.desc()).all()
    return render_template("applications/my_applications.html", applications=apps)

@bp.route("/available")
@login_required
@role_required(Role.FARMER)
def available_programs():
    programs = AssistanceProgram.query.filter_by(status="active").all()
    return render_template("applications/available.html", programs=programs)

@bp.route("/apply/<int:program_id>", methods=["GET", "POST"])
@login_required
@role_required(Role.FARMER)
def apply(program_id):
    program = AssistanceProgram.query.get_or_404(program_id)
    if not current_user.profile or not current_user.profile.farms:
        flash("You must register at least one farm before applying.", "warning")
        return redirect(url_for("applications.available_programs"))
        
    form = ApplyForm()
    form.farm_id.choices = [(f.id, f"{f.farm_code} ({f.area} ha)") for f in current_user.profile.farms]

    if form.validate_on_submit():
        # This generates a unique reference code so it doesn't crash
        unique_ref = f"APP-{program.code}-{current_user.id:04d}-{int(time.time())}"

        app = AssistanceApplication(
            reference_code=unique_ref,
            farmer_user_id=current_user.id,
            program_id=program.id,
            farm_id=form.farm_id.data,
            notes=form.notes.data,
            status=ApplicationStatus.SUBMITTED
        )
        db.session.add(app)
        db.session.commit()
        flash("Application submitted successfully!", "success")
        return redirect(url_for("applications.my_applications"))

    return render_template("applications/apply.html", form=form, program=program)

@bp.route("/<int:app_id>/assessment")
@login_required
@role_required(Role.FARMER)
def assessment_result(app_id):
    app_record = AssistanceApplication.query.get_or_404(app_id)
    if app_record.farmer_user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("applications.my_applications"))
    return render_template("applications/assessment_result.html", app=app_record)