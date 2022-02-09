from flask import render_template, request

from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response


@bp.errorhandler(404)
def not_found_error(error):
    """Custom page for 404 error"""

    if wants_json_response():
        return api_error_response(404)

    return render_template('errors/404.html'), 404


@bp.errorhandler(500)
def internal_error(error):
    """Custom page for 500 error"""

    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)

    return render_template('errors/500.html'), 500


def wants_json_response():
    """Compares JSON and HTML formats, returns the most preferable one"""

    return request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']
