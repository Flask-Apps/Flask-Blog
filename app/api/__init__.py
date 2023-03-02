from flask import Blueprint


api = Blueprint("api", __name__)

# importing all the components of the blueprint is necessary so that
# routes and other handlers are registered
# these modules need to import the api blueprint referenced here
# so they're put at the bottom to prevent circular dependencies
from . import authentication, posts, users, comments, errors  # noqa
