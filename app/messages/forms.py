from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class MessageForm(FlaskForm):
    """Form for sending private messages"""

    message = TextAreaField(_l('Message'), validators=[DataRequired(), Length(min=0, max=256)])
    submit = SubmitField(_l('Send'))
