import os
from flask import Flask, render_template, request
from .extensions import db, login_manager
from .models.user import User
from config import Config
from flask_mail import Mail


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    mail = Mail()
    mail.init_app(app)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from .routes.public import bp as public_bp
    from .routes.auth import bp as auth_bp
    from .routes.farmer import bp as farmer_bp
    from .routes.admin import bp as admin_bp
    from .routes.applications import bp as apps_bp  # <--- ADDED THIS

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(farmer_bp, url_prefix="/farmer")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(apps_bp, url_prefix="/applications")  # <--- ADDED THIS

    register_error_handlers(app)
    register_cli(app)

    return app


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        app.logger.exception("Server error on %s", request.path)
        return render_template("errors/500.html"), 500


def register_cli(app):
    from .cli import register_commands
    register_commands(app)