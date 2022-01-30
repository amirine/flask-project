from flask import render_template
from flask_mail import Message
from threading import Thread
from flask_babel import _

from app import mail, app
from app.models import User


def send_async_email(app, msg):
    """Function for async emails sending invoked via the Thread class"""

    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    """Sends email to recipients"""

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user: User) -> None:
    """Sends email for password reset to the user"""

    token = user.generate_token_for_password_reset()
    send_email(_('[Flask Blog] Password Reset'),
               sender=app.config['MAIL_USERNAME'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token)
               )
