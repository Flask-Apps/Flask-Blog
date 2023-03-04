from flask import jsonify  # , request, render_template

from app.exceptions import ValidationError

# from .. import main

from . import api


# @main.app_errorhandler(404)
# def page_not_found(e):
#     """responds with JSON to webservice clients and HTML to others"""
#     if (
#         # checks the Accept request header to see the format the client
#         # wants the response in
#         request.accept_mimetypes.accept_json
#         and not request.accept_mimetypes.accept_html
#     ):
#         response = jsonify({"error": "not found"})
#         response.status_code = 404
#         return response
#     return render_template("404.html"), 404


"""
view functions in the API blueprint can invoke this to
generate error responses when necessary
"""


def forbidden(message):
    response = jsonify({"error": "forbidden", "message": message})
    response.status_code = 403
    return response


def unauthorized(message):
    response = jsonify({"error": "unauthorized", "message": message})
    response.status_code = 401
    return response


def bad_request(message):
    response = jsonify({"error": "bad request", "message": message})
    response.status_code = 400
    return response


"""
Remaining status codes are genereated explicitly by the webservice
so we can implement with the help of a helper function inside the
blueprint
"""


@api.errorhandler(ValidationError)
def validation_error(e):
    """
    - global exception handler to avoid having to add exception-catching
        code in view functions
    - decorated func will be invoked any time an exception of the given
        class is raised
    - only invoke when the exception is raised while a route from
        the blueprint is being handled
    """
    return bad_request(e.args[0])
