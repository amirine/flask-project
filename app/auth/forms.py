from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask_babel import lazy_gettext as _l
from flask_babel import _

from app.models import User


class LoginForm(FlaskForm):
    """Login form for a User"""

    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    """Registration form for a User"""

    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        """Checks whether username already exists"""

        print(type(username))
        if User.query.filter_by(username=username.data).first():
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        """Checks whether email already exists"""

        if User.query.filter_by(email=email.data).first():
            raise ValidationError(_('Please use a different email address.'))


class PasswordResetRequestForm(FlaskForm):
    """Form for password reset request"""

    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class PasswordResetForm(FlaskForm):
    """Form for password reset"""

    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Save'))
