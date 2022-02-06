from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length
from flask_babel import lazy_gettext as _l
from flask_babel import _

from app.models import User


class EditProfileForm(FlaskForm):
    """Login form for a User"""

    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = StringField(_l('About me'), validators=[Length(min=0, max=128)])
    submit = SubmitField(_l('Save'))

    def __init__(self, original_username, *args, **kwargs):
        """Adds {original_username} field to compare original username and entered one in profile edit form"""

        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        """Checks whether edited username already exists. Raises error in case of existence"""

        if username.data != self.original_username and User.query.filter_by(username=username.data).first():
            raise ValidationError(_('Please use a different username.'))


class SubmitForm(FlaskForm):
    """Form for user follow or unfollow"""

    submit = SubmitField(_l('Submit'))


class PostForm(FlaskForm):
    """Form for post creating"""

    text = StringField(_l('Post text'), validators=[Length(min=0, max=256)])
    submit = SubmitField(_l('Save'))


class SearchForm(FlaskForm):
    """Form for searching posts"""

    text = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super().__init__(*args, **kwargs)


class MessageForm(FlaskForm):
    """Form for sending private messages"""

    message = TextAreaField(_l('Message'), validators=[DataRequired(), Length(min=0, max=256)])
    submit = SubmitField(_l('Send'))
