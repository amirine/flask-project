from flask import jsonify, Response
from werkzeug.http import HTTP_STATUS_CODES
from flask_babel import _


def error_response(status_code, message=None) -> Response:
    """Returns Response object for the error"""

    payload = {'error': HTTP_STATUS_CODES.get(status_code, _('Unknown error'))}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code

    return response


def bad_request(message: str) -> Response:
    """Returns 400 error response"""

    return error_response(400, message)
