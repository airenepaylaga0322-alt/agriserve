from datetime import datetime
from ..extensions import db

class ApplicationStatus:
    SUBMITTED = "submitted"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELIVERED = "delivered"
    
    LABELS = {
        SUBMITTED: "Submitted",
        PENDING_REVIEW: "Pending Review",
        APPROVED: "Approved",
        REJECTED: "Rejected",
        DELIVERED: "Assistance Delivered"
    }
    BADGE = {
        SUBMITTED: "info",
        PENDING_REVIEW: "warning",
        APPROVED: "primary",
        REJECTED: "danger",
        DELIVERED: "success"
    }

class AssistanceProgram(db.Model):
    __tablename__ = "assistance_programs"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(30), nullable=False)
    available_allocation = db.Column(db.Numeric(14, 2))
    max_benefit_per_farmer = db.Column(db.Numeric(14, 2))
    status = db.Column(db.String(20), default="active", index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    applications = db.relationship("AssistanceApplication", back_populates="program")

class AssistanceApplication(db.Model):
    __tablename__ = "assistance_applications"

    id = db.Column(db.Integer, primary_key=True)
    reference_code = db.Column(db.String(32), unique=True, index=True)
    farmer_user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    program_id = db.Column(db.Integer, db.ForeignKey("assistance_programs.id", ondelete="RESTRICT"), nullable=False, index=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="SET NULL"))
    status = db.Column(db.String(40), nullable=False, default=ApplicationStatus.SUBMITTED, index=True)
    notes = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Decision fields
    decided_at = db.Column(db.DateTime)
    decided_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    decision_reason = db.Column(db.Text)

    farmer_user = db.relationship("User", foreign_keys=[farmer_user_id])
    program = db.relationship("AssistanceProgram", back_populates="applications")
    farm = db.relationship("Farm")

    @property
    def status_label(self):
        return ApplicationStatus.LABELS.get(self.status, self.status)

    @property
    def status_badge(self):
        return ApplicationStatus.BADGE.get(self.status, "secondary")