import base64
import json
import os

import jwt
import redis
import rq
from flask_login import UserMixin
from flask import current_app as app, url_for
from flask_sqlalchemy import BaseQuery
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from datetime import datetime, timedelta
from time import time

from app import db, login
from app.mixins import SearchableMixin, PaginatedAPIMixin

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

# Table for followers
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))


class Task(db.Model):
    """Model for tasks"""

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self) -> rq.job.Job:
        """Gets Job instance by task id. Returns None in case the job has been already finished"""

        try:
            rq_job = rq.job.Job.fetch(self.id, connection=app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None

        return rq_job

    def get_progress(self):
        """Returns the progress percentage for the task"""

        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job else 100


class User(PaginatedAPIMixin, UserMixin, db.Model):
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
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='author', lazy='dynamic')
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient',
                                        lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    tasks = db.relationship('Task', backref='user', lazy='dynamic')
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

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

    def new_messages(self) -> int:
        """Returns the number of unread messages the user has"""

        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(Message.timestamp > last_read_time).count()

    def add_notification(self, name: str, data: int) -> Notification:
        """Returns notification for the unread message"""

        self.notifications.filter_by(name=name).delete()
        notification = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(notification)

        return notification

    def launch_task(self, name: str, description: str, *args, **kwargs) -> Task:
        """Adds a task to the RQ queue and the database"""

        rq_job = app.task_queue.enqueue('app.tasks.' + name, self.id, *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description, user=self)
        db.session.add(task)

        return task

    def get_tasks_in_progress(self):
        """Gets all the tasks not completed"""

        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name: str):
        """Gets specific task by its {name} not completed"""

        return Task.query.filter_by(name=name, user=self, complete=False).first()

    def to_dict(self, include_email=False) -> dict:
        """Transforms user data to dictionary"""

        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.isoformat() + 'Z',
            'about_me': self.about_me,
            'post_count': self.posts.count(),
            'follower_count': self.followers.count(),
            'followed_count': self.followed.count(),
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'followers': url_for('api.get_followers', id=self.id),
                'followed': url_for('api.get_followed', id=self.id),
                'avatar': self.get_avatar(128)
            }
        }

        if include_email:
            data['email'] = self.email

        return data

    def from_dict(self, data, new_user=False) -> None:
        """Gets data from dictionary"""

        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])

        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600) -> str:
        """Generates token for a user"""

        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token

        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)

        return self.token

    def revoke_token(self) -> None:
        """Makes token invalid"""

        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        """Returns the user the {token} belongs to"""

        user = User.query.filter_by(token=token).first()
        if not user or user.token_expiration < datetime.utcnow():
            return None

        return user

    def __repr__(self):
        return f"{self.username}"


class Post(SearchableMixin, db.Model):
    """Model for user Posts"""

    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return f"Post {self.id} from user {self.user_id}"


class Message(db.Model):
    """Model for private messages"""

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Message {self.id} from user {self.sender_id} to user {self.recipient_id}"


@login.user_loader
def load_user(user_id):
    """Gets user by id for session"""

    return User.query.get(int(user_id))
