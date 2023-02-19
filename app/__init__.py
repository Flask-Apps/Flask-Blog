from flask import Flask

from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown

from config import config


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
# sets the endpoint for the login page
# login route is inside a blueprint so blueprint name view function
login_manager.login_view = "auth.login"
# wrapper for markdown to html converter implemented in js (client-side)
pagedown = PageDown()


def create_app(config_name):
    """Factory function for creating app instances

    Args:
        config_name (str): name of the config class to use

    Returns:
        An application instance created with the factory function
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    # attach routes and custom error pages here
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint

    # register the blueprint to an app
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    return app
