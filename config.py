import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # needed for flask_wtf
    SECRET_KEY = os.environ.get("SECRET_KEY")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.googlemail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    IBLOG_MAIL_SUBJECT_PREFIX = "[IBlog]"
    IBLOG_MAIL_SENDER = "IBlog Admin <admin@iblog.com>"
    IBLOG_ADMIN = os.environ.get("IBLOG_ADMIN")
    IBLOG_POSTS_PER_PAGE = int(os.environ.get("IBLOG_POSTS_PER_PAGE"))
    IBLOG_FOLLOWERS_PER_PAGE = int(os.environ.get("IBLOG_FOLLOWERS_PER_PAGE"))
    IBLOG_COMMENTS_PER_PAGE = int(os.environ.get("IBLOG_COMMENTS_PER_PAGE"))

    # For measuring db performance
    # enable recording of the query statistics
    SQLALCHEMY_RECORD_QUERIES = True
    IBLOG_SLOW_DB_QUERY_TIME = float(os.environ.get("IBLOG_SLOW_DB_QUERY_TIME", 0.5))

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data-test.sqlite")


class TestingWithSeleniumConfig(TestingConfig):
    @staticmethod
    def init_app(app):
        if os.environ.get("FLASK_RUN_FROM_CLI"):
            os.environ.pop("FLASK_RUN_FROM_CLI")


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data.sqlite")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "testing-with-selenium": TestingWithSeleniumConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
