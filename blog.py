from app import create_app, db
from app import cli
from app.models import User, Post, Notification

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    """Allows to use database models in shell with no import"""

    return {'db': db, 'User': User, 'Post': Post, 'Notification': Notification}
