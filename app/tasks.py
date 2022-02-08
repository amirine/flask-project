import json
import sys
from flask import render_template
from flask_babel import _
from rq import get_current_job

from app import create_app
from app import db
from app.email import send_email
from app.models import Task, User, Post

app = create_app()
app.app_context().push()


def export_posts(user_id: int) -> None:
    """Exports all the user's posts and sends to the appropriate email"""

    try:
        user = User.query.get(user_id)
        _set_task_progress(0)
        posts_to_export = []
        progress_counter = 0
        total_posts = user.posts.count()

        for post in user.posts.order_by(Post.timestamp.asc()):
            posts_to_export.append({'body': post.body, 'timestamp': post.timestamp.isoformat() + 'Z'})
            progress_counter += 1
            _set_task_progress(100 * progress_counter // total_posts)

        send_email(
            _('[Blog] Your blog posts'),
            sender=app.config['MAIL_USERNAME'], recipients=[user.email],
            text_body=render_template('email/export_posts.txt', user=user),
            html_body=render_template('email/export_posts.html', user=user),
            attachments=[('posts.json', 'application/json', json.dumps({'posts': posts_to_export}, indent=4))],
            sync=True
        )

    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())

    finally:
        _set_task_progress(100)


def _set_task_progress(progress: float) -> None:
    """Sets the progress percentage for th task"""

    job = get_current_job()

    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification('task_progress', {'task_id': job.get_id(), 'progress': progress})

        if progress >= 100:
            task.complete = True
        db.session.commit()
