from flask import jsonify, Response

from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth


@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token() -> Response:
    """Generates and returns token for the current user as a Response object"""

    token = basic_auth.current_user().get_token()
    db.session.commit()

    return jsonify({'token': token})


@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token() -> (str, int):
    """Makes token invalid for the current user"""

    token_auth.current_user().revoke_token()
    db.session.commit()

    return '', 204
