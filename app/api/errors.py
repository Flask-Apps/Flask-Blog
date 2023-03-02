from flask import request, jsonify, render_template
from .. import main


@main.app_errorhandler(404)
def page_not_found(e):
    """responds with JSON to webservice clients and HTML to others"""
    if (
        # checks the Accept request header to see the format the client
        # wants the response in
        request.accept_mimetypes.accept_json
        and not request.accept_mimetypes.accept_html
    ):
        response = jsonify({"error": "not found"})
        response.status_code = 404
        return response
    return render_template("404.html"), 404


def forbidden(message):
    """
    view functions in the API blueprint can invoke this to
    generate error responses when necessary
    """
    response = jsonify({"error": "forbidden", "message": message})
    response.status_code = 403
    return response


"""
Remaining status codes are genereated explicitly by the webservice
so we can implement with the help of a helper function inside the
blueprint
"""
