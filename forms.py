from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, DecimalField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange


class SignUpForm(FlaskForm):

    username = StringField("Username (required)")
    password = PasswordField("Password (required)")
    firstname = StringField("First Name (required)")
    lastname = StringField("Last Name")

class LoginForm(FlaskForm):

    username = StringField("Username (required)")
    password = PasswordField("Password (required)")


class ProductUploadForm(FlaskForm):
    image = FileField('Product Image', validators=[DataRequired(''),])
    name = StringField('Product Name', validators=[DataRequired(''), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(''), Length(max=500)])
    price = DecimalField('Price (USD)', validators=[DataRequired(''), NumberRange(min=0)], places=2)    