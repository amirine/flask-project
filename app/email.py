from flask_mail import Message
from threading import Thread
from flask import current_app as app

from app import mail


def send_async_email(app, msg):
    """Function for async emails sending invoked via the Thread class"""

    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body, attachments=None, sync=False):
    """Sends email to recipients"""

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email, args=(app._get_current_object(), msg)).start()
