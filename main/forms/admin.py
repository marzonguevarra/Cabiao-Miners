from wtforms import Form, BooleanField, StringField, PasswordField, SubmitField, ValidationError, validators
from main.models.admin import tblAdmins

class AdminRegistrationForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=25)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35),validators.Email()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

    def validate_username(self, username):
        if tblAdmins.query.filter_by(username=username.data).first():
            raise ValidationError("This username is already in use")
    
    def validate_email(self, email):
        if tblAdmins.query.filter_by(email=email.data).first():
            raise ValidationError("This email is already in use")

class AdminLoginForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=35),validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])
