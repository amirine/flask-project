from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length

from app.models import User


class LoginForm(FlaskForm):
    """Login form for a User"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Registration form for a User"""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    @staticmethod
    def validate_username(self, username):
        """Checks whether username already exists"""

        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Please use a different username.')

    @staticmethod
    def validate_email(self, email):
        """Checks whether email already exists"""

        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    """Login form for a User"""

    username = StringField('Username', validators=[DataRequired()])
    about_me = StringField('About me', validators=[Length(min=0, max=128)])
    submit = SubmitField('Save')

    def __init__(self, original_username, *args, **kwargs):
        """Adds {original_username} field to compare original username and entered one in profile edit form"""

        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        """Checks whether edited username already exists. Raises error in case of existence"""

        if username != self.original_username and User.query.filter_by(username=username.data).first():
            raise ValidationError('Please use a different username.')