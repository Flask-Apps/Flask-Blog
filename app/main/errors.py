from . import main
from flask import render_template


# for errors that originate in the routes including the ones not defined
# in the blueprint
@main.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500
