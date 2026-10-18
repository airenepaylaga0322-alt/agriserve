from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db


class Role:
    FARMER = "farmer"
    OFFICER = "officer"
    ADMIN = "admin"
    ALL = (FARMER, OFFICER, ADMIN)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=Role.FARMER, index=True)
    is_active_account = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime)

    def set_password(self, raw: str) -> None:
        self.password_hash = generate_password_hash(raw, method="pbkdf2:sha256")

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

    @property
    def is_active(self) -> bool:
        return self.is_active_account

    @property
    def is_farmer(self) -> bool:
        return self.role == Role.FARMER

    @property
    def is_officer(self) -> bool:
        return self.role == Role.OFFICER

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"