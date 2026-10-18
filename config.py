import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:12345678@127.0.0.1:3306/agriserve?charset=utf8mb4",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}

    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER", os.path.join(INSTANCE_DIR, "uploads")
    )
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))
    ALLOWED_UPLOAD_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "docx"}

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    WTF_CSRF_TIME_LIMIT = None

    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@agriserve.local")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "ChangeMe_Str0ng!_2026")

        # Email Settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_email@gmail.com'  # <--- PUT YOUR GMAIL HERE
    MAIL_PASSWORD = 'abcdefghijklmnop'      # <--- PUT YOUR 16-LETTER APP PASSWORD HERE (no spaces)
    MAIL_DEFAULT_SENDER = 'your_email@gmail.com'