import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BaseConfig:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY")
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = False
    TESTING = False

    # PostgreSQL Database (REQUIRED)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL is required for PostgreSQL")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 60 * 60 * 24)
    )  # 24 hours

    # OpenAI / AI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AI_REQUEST_TIMEOUT = int(os.getenv("AI_REQUEST_TIMEOUT", 30))

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # Subscription / Payments
    PAYMENT_PROVIDER = os.getenv("PAYMENT_PROVIDER", "apple")
    SUBSCRIPTION_SECRET = os.getenv("SUBSCRIPTION_SECRET")

    # Notifications
    FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY")

    # Usage limits
    FREE_DAILY_LIMIT = int(os.getenv("FREE_DAILY_LIMIT", 5))


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    FLASK_ENV = "development"


class ProductionConfig(BaseConfig):
    DEBUG = False
    FLASK_ENV = "production"


def get_config():
    env = os.getenv("FLASK_ENV", "production").lower()
    if env == "development":
        return DevelopmentConfig
    return ProductionConfig
