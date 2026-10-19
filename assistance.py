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
    required_documents = db.Column(db.Text)
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


class RubricAssessment(db.Model):
    __tablename__ = "rubric_assessments"
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("assistance_applications.id"), unique=True, nullable=False)
    
    score_a = db.Column(db.Numeric(5, 2))
    score_b = db.Column(db.Numeric(5, 2))
    score_c = db.Column(db.Numeric(5, 2))
    score_d = db.Column(db.Numeric(5, 2))
    total_score = db.Column(db.Numeric(5, 2))
    recommendation = db.Column(db.String(50))

    application = db.relationship("AssistanceApplication", backref=db.backref("rubric_assessment", uselist=False))


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(255), nullable=False)
    target_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    actor = db.relationship("User")