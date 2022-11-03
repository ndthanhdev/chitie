import os
from dotenv import load_dotenv

load_dotenv()


class Local(object):
    DEBUG = False if os.getenv("APP_ENV") == "production" else True
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")

    JWT_ACCESS_TOKEN_EXPIRES = 30 * 60
    JWT_SECRET_KEY = os.getenv('SECRET_KEY')

    LOCALE = os.getenv("LOCALE", "vi_VN")

    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    TELEGRAM_SECRET = os.getenv("TELEGRAM_SECRET")
    TELEGRAM_AUTH_CALLBACK = os.getenv("TELEGRAM_AUTH_CALLBACK")
    TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET")

    WEB_BASE_URL = os.getenv("WEB_BASE_URL")
