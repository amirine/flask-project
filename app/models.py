import jwt
from flask_login import UserMixin
from flask import current_app as app
from flask_sqlalchemy import BaseQuery
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from datetime import datetime
from time import time

from app import db, login

# Table for followers
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


class User(UserMixin, db.Model):
    """Model for User"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(128), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def set_password(self, password: str) -> None:
        """Generates password hash for input password"""

        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Checks password correctness by its hash"""

        return check_password_hash(self.password_hash, password)

    def get_avatar(self, size=80) -> str:
        """Returns avatar url by email address of the user"""

        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user_to_follow) -> None:
        """Makes current user follow {user_to_follow}"""

        if not self.is_following(user_to_follow):
            self.followed.append(user_to_follow)

    def unfollow(self, user_to_unfollow) -> None:
        """Makes current user unfollow {user_to_follow}"""

        if self.is_following(user_to_unfollow):
            self.followed.remove(user_to_unfollow)

    def is_following(self, user_to_follow) -> int:
        """Checks whether current user already follows {user_to_follow}"""

        return self.followed.filter(followers.c.followed_id == user_to_follow.id).count()

    def get_posts_from_followed_users(self) -> BaseQuery:
        """Gets posts from followed users + current user's own posts"""

        followed_posts = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        current_user_posts = self.posts

        return followed_posts.union(current_user_posts).order_by(Post.timestamp.desc())

    def generate_token_for_password_reset(self, expires_in=600) -> str:
        """Generates token for password reset"""

        return jwt.encode({'reset_password': self.id, 'expire': time() + expires_in},
                          app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_token_for_password_reset(token):
        """Decodes token for password reset and returns user from the token"""

        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
            return User.query.get(id)
        except:
            return None

    def __repr__(self):
        return f"{self.username}"


class Post(db.Model):
    """Model for user Posts"""

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return f"Post {self.id} from user {self.user_id}"


@login.user_loader
def load_user(user_id):
    """Gets user by id for session"""

    return User.query.get(int(user_id))
