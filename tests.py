import unittest
from datetime import datetime, timedelta
from hashlib import md5
# from flask import current_app as app
from app import app, db
from app.models import User, Post


class UserModelTest(unittest.TestCase):

    def setUp(self) -> None:
        """Creates database for testing"""

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        print(app.config['SQLALCHEMY_DATABASE_URI'])
        print(app.config['MAIL_SERVER'])
        print(app.config['MAIL_USE_TLS'])
        db.create_all()

    def tearDown(self) -> None:
        """Clears test database after each test"""

        db.session.remove()
        db.drop_all()

    def test_password_hashing(self) -> None:
        """Testing password hashing"""

        user = User(username='ira')
        user.set_password('ira')
        self.assertFalse(user.check_password('dasha'))
        self.assertTrue(user.check_password('ira'))

    def test_avatar(self):
        """Testing avatar correctness"""

        user = User(username='ira', email='ira@gmail.com')
        digest = md5('ira@gmail.com'.encode('utf-8')).hexdigest()
        self.assertEqual(user.get_avatar(), f'https://www.gravatar.com/avatar/{digest}?d=identicon&s=80')

    def test_follow(self):
        """Testing follow functionality"""

        user1 = User(username='ira', email='ira@gmail.com')
        user2 = User(username='dasha', email='dasha@gmail.com')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        self.assertEqual(user1.followed.all(), [])
        self.assertEqual(user2.followed.all(), [])

        user1.follow(user2)
        db.session.commit()
        self.assertEqual(user1.followed.count(), 1)
        self.assertEqual(user1.followers.count(), 0)
        self.assertEqual(user2.followed.count(), 0)
        self.assertEqual(user2.followers.count(), 1)
        self.assertTrue(user1.already_follows_check(user2))
        self.assertFalse(user2.already_follows_check(user1))

    def test_followed_posts(self):
        """Testing followed posts"""

        # Creating users
        user1 = User(username='john', email='john@example.com')
        user2 = User(username='susan', email='susan@example.com')
        user3 = User(username='mary', email='mary@example.com')
        user4 = User(username='david', email='david@example.com')
        db.session.add_all([user1, user2, user3, user4])

        # Creating posts
        now = datetime.utcnow()
        post1 = Post(body="post from john", author=user1, timestamp=now + timedelta(seconds=1))
        post2 = Post(body="post from susan", author=user2, timestamp=now + timedelta(seconds=4))
        post3 = Post(body="post from mary", author=user3, timestamp=now + timedelta(seconds=3))
        post4 = Post(body="post from david", author=user4, timestamp=now + timedelta(seconds=2))
        db.session.add_all([post1, post2, post3, post4])
        db.session.commit()

        # Creating follow relationships
        user1.follow(user2)
        user1.follow(user4)
        user2.follow(user3)
        user3.follow(user4)
        db.session.commit()

        # Testing posts
        self.assertEqual(user1.followed_posts().all(), [post2, post4, post1])
        self.assertEqual(user2.followed_posts().all(), [post2, post3])
        self.assertEqual(user3.followed_posts().all(), [post3, post4])
        self.assertEqual(user4.followed_posts().all(), [post4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
