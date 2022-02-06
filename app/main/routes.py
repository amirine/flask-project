from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from flask_babel import _
from langdetect import detect, LangDetectException
from datetime import datetime
from flask import g
from flask_babel import get_locale
from flask import current_app as app

from app import db
from app.main import bp
from app.main.forms import EditProfileForm, SubmitForm, PostForm, SearchForm
from app.models import User, Post
from app.translate import translate


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """Home Page: displays posts from users you follow with pagination"""

    form = PostForm()
    if form.validate_on_submit():

        try:
            language = detect(form.text.data)
        except LangDetectException:
            language = ''

        post = Post(body=form.text.data, user_id=current_user.id, language=language)
        db.session.add(post)
        db.session.commit()

    page = request.args.get('page', 1, type=int)
    posts = current_user.get_posts_from_followed_users().paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None

    return render_template('main/index.html', title='Home', posts=posts.items, form=form, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    """Explore Page: displays posts from all users paginated and ordered by timestamp"""

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None

    return render_template('main/index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/translate', methods=['POST'])
@login_required
def translate_post():
    """View for post text translation. Returns {'text': <translated text>} dictionary"""

    return jsonify({
        'text': translate(request.form['text_to_translate'], request.form['source_language'],
                          request.form['destination_language'])
    })


@bp.route('/user_profile/<username>')
@login_required
def user_profile(username):
    """User Profile Page: displays common info of the user"""

    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user_profile', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user_profile', username=user.username, page=posts.prev_num) if posts.has_prev else None
    form = SubmitForm()

    return render_template('main/user_profile.html', user=user, posts=posts.items, form=form, prev_url=prev_url,
                           next_url=next_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit Profile Page: allows to make changes to username and about_me field"""

    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.user_profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('main/edit_profile.html', form=form)


@bp.route('/follow/<username>', methods=['GET', 'POST'])
@login_required
def follow(username):
    """View to follow the user. Called by submit button on user profile page"""

    form = SubmitForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()

        if not user:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))

        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('main.user_profile', username=username))

        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('main.user_profile', username=username))

    return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    """View to unfollow the user. Called by submit button on user profile page"""

    form = SubmitForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()

        if not user:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))

        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user_profile', username=username))

        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user_profile', username=username))

    return redirect(url_for('main.index'))


@bp.route('/search')
@login_required
def search():
    """View handling search form input. Returns posts satisfying the search"""

    if not g.search_form.validate():
        return redirect(url_for('main.explore'))

    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.text.data, page, app.config['POSTS_PER_PAGE'])

    next_url = None
    prev_url = None

    if total > page * app.config['POSTS_PER_PAGE']:
        next_url = url_for('main.search', text=g.search_form.q.data, page=page + 1)

    if page > 1:
        prev_url = url_for('main.search', text=g.search_form.text.data, page=page - 1)

    return render_template('main/search.html', title=_('Search'), posts=posts.all(),
                           next_url=next_url, prev_url=prev_url)


@bp.before_request
def before_request():
    """Sets {last_seen} date and local dates for the user before the page request"""

    # Sets last_seen date
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()

    # Sets locale for dates on pages
    g.locale = str(get_locale())
