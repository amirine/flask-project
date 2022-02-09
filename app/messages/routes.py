from datetime import datetime
from flask import flash, redirect, url_for, render_template, request
from flask_login import current_user, login_required
from flask_babel import _
from flask import current_app as app

from app import db
from app.messages import bp
from app.messages.forms import MessageForm
from app.models import User, Message


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    """Send Message View: sends private messages to the user"""

    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.add(msg)
        db.session.commit()
        flash(_('Your message has been sent.'))
        return redirect(url_for('main.user_profile', username=recipient))

    return render_template('messages/send_message.html', title=_('Send Message'), form=form, recipient=recipient)


@bp.route('/messages')
@login_required
def messages():
    """Messages View: displays messages of and for the current user"""

    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(Message.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    next_url = None
    prev_url = None

    if messages.has_next:
        next_url = url_for('messages.messages', page=messages.next_num)

    if messages.has_prev:
        prev_url = url_for('messages.messages', page=messages.prev_num)

    return render_template('messages/messages.html', title=_('Messages'), messages=messages.items, next_url=next_url,
                           prev_url=prev_url)
