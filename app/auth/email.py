from flask import render_template
from flask_babel import _
from flask import current_app as app

from app.email import send_email
from app.models import User


def send_password_reset_email(user: User) -> None:
    """Sends email for password reset to the user"""

    token = user.generate_token_for_password_reset()
    send_email(_('[Flask Blog] Password Reset'),
               sender=app.config['MAIL_USERNAME'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token)
               )
