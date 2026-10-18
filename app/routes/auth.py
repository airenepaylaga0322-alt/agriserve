from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import db
from ..models.user import User, Role
from ..forms import RegisterForm, LoginForm

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("public.home"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if existing:
            flash("That email is already registered.", "danger")
            return render_template("auth/register.html", form=form)

        user = User(
            email=form.email.data.lower().strip(),
            full_name=form.full_name.data.strip(),
            role=Role.FARMER,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Account created. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(_dashboard_url_for(current_user))

    form = LoginForm()
    
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form)
            
        if not user.is_active_account:
            flash("Account is disabled.", "danger")
            return render_template("auth/login.html", form=form)

        login_user(user, remember=False)
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        return redirect(_dashboard_url_for(user))

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("public.home"))


def _dashboard_url_for(user):
    if user.is_admin:
        return url_for("admin.dashboard")
    if user.is_officer:
        return url_for("admin.dashboard")
    return url_for("farmer.dashboard")