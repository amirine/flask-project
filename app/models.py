from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from hashlib import md5

from app import db
from app import login

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

        if not self.already_follows_check(user_to_follow) and user_to_follow.id != self.id:
            self.followed.append(user_to_follow)

    def unfollow(self, user_to_unfollow) -> None:
        """Makes current user unfollow {user_to_follow}"""

        if self.already_follows_check(user_to_unfollow) and user_to_unfollow.id != self.id:
            self.followed.remove(user_to_unfollow)

    def already_follows_check(self, user_to_follow) -> int:
        """Checks whether current user already follows {user_to_follow}"""

        return self.followed.filter(followers.c.followed_id == user_to_follow.id).count()

    def get_posts_from_followed_users(self):
        """Gets posts from followed users + current user's own posts"""

        followed_posts = Post.query.join(followers, (followers.c.followed_id == Post.user_id)) \
            .filter(followers.c.follower_id == self.id)
        current_user_posts = self.posts

        return followed_posts.union(current_user_posts).order_by(Post.timestamp.desc())

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
