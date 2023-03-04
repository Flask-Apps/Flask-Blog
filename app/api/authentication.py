from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import User
from .errors import unauthorized, forbidden
from . import api

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    """
    A callback function to verify user credentials
    """
    # we need to define the procedure to verify user credentials
    # like in flask-login
    if email_or_token == "":
        return False
    if password == "":
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    """ensure that the response is consistent with other errors
    returned by the API
    """
    return unauthorized("Invalid credentials")


@api.before_request
@auth.login_required
def before_request():
    """
    As all routes in the blueprint need to be protected in the same way
    login_required decorator can be included once in a before_request
    handler
    """
    # reject authenticated users who have not confirmed their accounts
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden("Unconfirmed account")


@api.route("/tokens/", methods=["POST"])
def get_token():
    # to prevent authenticating to this route using previously obtained token
    # instead of meail and password g.token_used is used
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized("Invalid Credentials")
    return jsonify({"token": g.current_user.generate_auth_token(), "expiration": 3600})
