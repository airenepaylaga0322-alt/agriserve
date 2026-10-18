from datetime import datetime
from ..extensions import db

class VerificationStatus:
    NOT_VERIFIED = "not_verified"
    PENDING = "pending"
    VERIFIED = "verified"
    REQUIRES_CORRECTION = "requires_correction"
    UNABLE_TO_VERIFY = "unable_to_verify"
    
    LABELS = {
        NOT_VERIFIED: "Not Yet Verified",
        PENDING: "Pending Verification",
        VERIFIED: "Verified",
        REQUIRES_CORRECTION: "Requires Correction",
        UNABLE_TO_VERIFY: "Unable to Verify",
    }

class FarmerProfile(db.Model):
    __tablename__ = "farmer_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    farmer_code = db.Column(db.String(32), unique=True, index=True)
    contact_number = db.Column(db.String(32))
    barangay = db.Column(db.String(120), index=True)
    municipality = db.Column(db.String(120), index=True)
    province = db.Column(db.String(120), index=True)
    household_size = db.Column(db.Integer, default=1)
    dependents = db.Column(db.Integer, default=0)
    primary_income_source = db.Column(db.String(120))
    estimated_monthly_income = db.Column(db.Numeric(12, 2))
    verification_status = db.Column(db.String(30), nullable=False, default=VerificationStatus.NOT_VERIFIED, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("profile", uselist=False, cascade="all, delete-orphan"))
    farms = db.relationship("Farm", back_populates="owner_profile", cascade="all, delete-orphan")

class LandTenure:
    OWNED = "owned"
    TENANT = "tenant"
    LEASED = "leased"
    SHARED = "shared"
    OTHER = "other"

class Farm(db.Model):
    __tablename__ = "farms"

    id = db.Column(db.Integer, primary_key=True)
    farmer_profile_id = db.Column(db.Integer, db.ForeignKey("farmer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_code = db.Column(db.String(32), unique=True, index=True)
    location = db.Column(db.String(255))
    barangay = db.Column(db.String(120), index=True)
    municipality = db.Column(db.String(120), index=True)
    province = db.Column(db.String(120), index=True)
    area = db.Column(db.Numeric(10, 2))
    area_unit = db.Column(db.String(16), default="hectare")
    land_tenure = db.Column(db.String(20), default=LandTenure.OWNED)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    owner_profile = db.relationship("FarmerProfile", back_populates="farms")

class Crop(db.Model):
    __tablename__ = "crops"

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_type = db.Column(db.String(80), nullable=False, index=True)
    planting_date = db.Column(db.Date)
    estimated_production = db.Column(db.Numeric(12, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    farm = db.relationship("Farm", backref=db.backref("crops", cascade="all, delete-orphan"))


class AgriculturalLoss(db.Model):
    __tablename__ = "agricultural_losses"

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = db.Column(db.Integer, db.ForeignKey("crops.id", ondelete="SET NULL"))
    loss_type = db.Column(db.String(80))  # e.g. Typhoon, Pest, Drought
    description = db.Column(db.Text)
    loss_percentage = db.Column(db.Numeric(5, 2))
    estimated_value = db.Column(db.Numeric(12, 2))
    loss_date = db.Column(db.Date)
    is_verified = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    farm = db.relationship("Farm", backref=db.backref("losses", cascade="all, delete-orphan"))
    crop = db.relationship("Crop")