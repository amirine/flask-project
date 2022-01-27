from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from app import login


class User(UserMixin, db.Model):
    """Model for User"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(128), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        """Generates password hash for input password"""

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks password correctness by its hash"""

        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"{self.username}"


class Post(db.Model):
    """Model for user Posts"""

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Post {self.id} from user {self.user_id}"


@login.user_loader
def load_user(user_id):
    """Gets user by id for session"""

    return User.query.get(int(user_id))
