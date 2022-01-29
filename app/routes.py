from flask import render_template, flash, redirect, url_for, request
from flask_login import logout_user, current_user, login_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, SubmitForm, PostForm
from app.models import User, Post


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """Home Page: displays posts from users you follow"""

    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.text.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()

    page = request.args.get('page', 1, type=int)
    posts = current_user.get_posts_from_followed_users().paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title='Home', posts=posts.items, form=form, next_url=next_url,
                           prev_url=prev_url)


@app.route('/explore')
@login_required
def explore():
    """Explore Page: displays posts from all users paginated and ordered by timestamp"""

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Page: displays login form for unauthorized users and redirects to Home Page for authorized ones"""

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('index'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc:
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """View for user registration"""

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    """View for user logout"""

    logout_user()
    return redirect(url_for('index'))


@app.route('/user_profile/<username>')
@login_required
def user_profile(username):
    """User Profile Page: displays common info of the user"""

    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user_profile', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user_profile', username=user.username, page=posts.prev_num) if posts.has_prev else None
    form = SubmitForm()

    return render_template('user_profile.html', user=user, posts=posts.items, form=form, prev_url=prev_url,
                           next_url=next_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit Profile Page: allows to make changes to username and about_me field"""

    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user_profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', form=form)


@app.route('/follow/<username>', methods=['GET', 'POST'])
@login_required
def follow(username):
    """View to follow the user. Called by submit button on user profile page"""

    form = SubmitForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user_profile', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user_profile', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    """View to unfollow the user. Called by submit button on user profile page"""

    form = SubmitForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user_profile', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user_profile', username=username))
    else:
        return redirect(url_for('index'))


@app.before_request
def before_request():
    """Sets {last_seen} date for the user before the page request"""

    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.shell_context_processor
def make_shell_context():
    """Allows to use database models in shell with no import"""

    return {'db': db, 'User': User, 'Post': Post}
