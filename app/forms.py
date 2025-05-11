from wtforms import StringField, PasswordField
from wtforms.validators import Email, EqualTo, Length, DataRequired
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, DateField, SubmitField

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")