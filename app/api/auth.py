from typing import Optional
from flask import Response
from flask_httpauth import HTTPBasicAuth
from flask_httpauth import HTTPTokenAuth

from app.models import User
from app.api.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username: str, password: str) -> Optional[User]:
    """Checks username and password correctness"""

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user


@basic_auth.error_handler
def basic_auth_error(status: int) -> Response:
    """Returns error response for basic auth"""

    return error_response(status)


@token_auth.verify_token
def verify_token(token: str) -> Optional[User]:
    """Verifies token: validates token and token expiration and gets the user by token"""

    return User.check_token(token) if token else None


@token_auth.error_handler
def token_auth_error(status: int) -> Response:
    """Returns error response for token auth"""

    return error_response(status)
