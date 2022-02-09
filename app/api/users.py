from flask import jsonify, request, url_for, Response
from flask_babel import _

from app import db
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request, error_response
from app.models import User


@bp.route('/users/<int:user_id>', methods=['GET'])
@token_auth.login_required
def get_user(user_id) -> Response:
    """Returns user info by user id"""

    return jsonify(User.query.get_or_404(user_id).to_dict())


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users() -> Response:
    """Returns all the users paginated"""

    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')

    return jsonify(data)


@bp.route('/users/<int:user_id>/followers', methods=['GET'])
@token_auth.login_required
def get_followers(user_id):
    """Returns followers for the user by user id"""

    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.followers, page, per_page, 'api.get_followers', user_id=user_id)

    return jsonify(data)


@bp.route('/users/<int:user_id>/followed', methods=['GET'])
@token_auth.login_required
def get_followed(user_id) -> Response:
    """Returns users user {id} is following"""

    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.followed, page, per_page, 'api.get_followed', user_id=user_id)

    return jsonify(data)


@bp.route('/users', methods=['POST'])
def create_user() -> Response:
    """Creates the user account"""

    data = request.get_json() or {}

    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request(_('Must include username, email and password fields'))

    if User.query.filter_by(username=data['username']).first():
        return bad_request(_('Please use a different username'))

    if User.query.filter_by(email=data['email']).first():
        return bad_request(_('Please use a different email address'))

    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()

    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', user_id=user.id)

    return response


@bp.route('/users/<int:user_id>', methods=['PUT'])
@token_auth.login_required
def update_user(user_id) -> Response:
    """Updates user's info: users can update their own profile data only"""

    if token_auth.current_user().id != user_id:
        return error_response(403, message=_("Authorized user has no permissions for changes"))

    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request(_('Please use a different username'))

    if 'email' in data and data['email'] != user.email and User.query.filter_by(email=data['email']).first():
        return bad_request(_('Please use a different email address'))

    user.from_dict(data, new_user=False)
    db.session.commit()

    return jsonify(user.to_dict())
