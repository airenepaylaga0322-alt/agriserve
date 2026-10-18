from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..decorators import role_required
from ..models.user import Role
from ..models.farmer import FarmerProfile, Farm
from ..extensions import db
from ..forms import ProfileForm, FarmForm
from ..models.farmer import FarmerProfile, Farm, Crop, AgriculturalLoss
from ..forms import ProfileForm, FarmForm, CropForm, LossForm
from datetime import datetime

bp = Blueprint("farmer", __name__)

@bp.route("/dashboard")
@login_required
@role_required(Role.FARMER)
def dashboard():
    if not current_user.profile:
        # Create an empty profile if they don't have one yet
        profile = FarmerProfile(user_id=current_user.id, farmer_code=f"FARM-{current_user.id:04d}")
        db.session.add(profile)
        db.session.commit()
        
    return render_template("farmer/dashboard.html", profile=current_user.profile)

@bp.route("/profile", methods=["GET", "POST"])
@login_required
@role_required(Role.FARMER)
def profile():
    form = ProfileForm(obj=current_user.profile)
    if form.validate_on_submit():
        form.populate_obj(current_user.profile)
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("farmer.dashboard"))
    return render_template("farmer/profile.html", form=form)

@bp.route("/farms/add", methods=["GET", "POST"])
@login_required
@role_required(Role.FARMER)
def add_farm():
    form = FarmForm()
    if form.validate_on_submit():
        farm = Farm(
            farmer_profile_id=current_user.profile.id,
            farm_code=f"FRM-{current_user.profile.id:02d}-{len(current_user.profile.farms)+1:02d}",
            location=form.location.data,
            barangay=form.barangay.data,
            municipality=form.municipality.data,
            province=form.province.data,
            area=form.area.data,
            land_tenure=form.land_tenure.data
        )
        db.session.add(farm)
        db.session.commit()
        flash("Farm added successfully!", "success")
        return redirect(url_for("farmer.dashboard"))
    return render_template("farmer/farm_form.html", form=form)

@bp.route("/farms/<int:farm_id>")
@login_required
@role_required(Role.FARMER)
def view_farm(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    if farm.farmer_profile_id != current_user.profile.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("farmer.dashboard"))
    return render_template("farmer/view_farm.html", farm=farm)

@bp.route("/farms/<int:farm_id>/crops/add", methods=["GET", "POST"])
@login_required
@role_required(Role.FARMER)
def add_crop(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    if farm.farmer_profile_id != current_user.profile.id:
        return redirect(url_for("farmer.dashboard"))
        
    form = CropForm()
    if form.validate_on_submit():
        crop = Crop(
            farm_id=farm.id,
            crop_type=form.crop_type.data,
            planting_date=form.planting_date.data,
            estimated_production=form.estimated_production.data
        )
        db.session.add(crop)
        db.session.commit()
        flash("Crop added successfully!", "success")
        return redirect(url_for("farmer.view_farm", farm_id=farm.id))
    return render_template("farmer/crop_form.html", form=form, farm=farm)

@bp.route("/farms/<int:farm_id>/losses/add", methods=["GET", "POST"])
@login_required
@role_required(Role.FARMER)
def add_loss(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    if farm.farmer_profile_id != current_user.profile.id:
        return redirect(url_for("farmer.dashboard"))
        
    form = LossForm()
    # Populate the crop dropdown with only this farm's crops
    form.crop_id.choices = [(c.id, c.crop_type) for c in farm.crops]
    
    if not form.crop_id.choices:
        flash("You must add a crop to this farm before recording a loss.", "warning")
        return redirect(url_for("farmer.view_farm", farm_id=farm.id))

    if form.validate_on_submit():
        loss = AgriculturalLoss(
            farm_id=farm.id,
            crop_id=form.crop_id.data,
            loss_type=form.loss_type.data,
            loss_percentage=form.loss_percentage.data,
            estimated_value=form.estimated_value.data,
            loss_date=form.loss_date.data,
            description=form.description.data
        )
        db.session.add(loss)
        db.session.commit()
        flash("Loss recorded successfully!", "success")
        return redirect(url_for("farmer.view_farm", farm_id=farm.id))
    return render_template("farmer/loss_form.html", form=form, farm=farm)