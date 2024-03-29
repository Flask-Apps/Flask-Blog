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
    IBLOG_POSTS_PER_PAGE = int(os.environ.get("IBLOG_POSTS_PER_PAGE", 10))
    IBLOG_FOLLOWERS_PER_PAGE = int(os.environ.get("IBLOG_FOLLOWERS_PER_PAGE", 10))
    IBLOG_COMMENTS_PER_PAGE = int(os.environ.get("IBLOG_COMMENTS_PER_PAGE", 10))

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

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to administrators
        import logging
        from logging.handlers import SMTPHandler

        credentials = None
        secure = None

        if getattr(cls, "MAIL_USERNAME", None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, "MAIL_USE_TLS", None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.IBLOG_MAIL_SENDER,
            toaddrs=[cls.IBLOG_ADMIN],
            subject=cls.IBLOG_MAIL_SUBJECT_PREFIX + "Application Error",
            credentials=credentials,
            secure=secure,
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler

        # heroku considers o/p written by the application to stdout or stderr
        # logs so a logging handler is added to generate this o/p
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class DockerConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler

        # docker automatically captures logs to stderr
        # and exposes through docker logs command
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "testing-with-selenium": TestingWithSeleniumConfig,
    "production": ProductionConfig,
    "heroku": HerokuConfig,
    "docker": DockerConfig,
    "default": DevelopmentConfig,
}
