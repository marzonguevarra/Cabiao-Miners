from wtforms import Form, BooleanField, StringField, PasswordField, SubmitField, ValidationError, validators
from flask_wtf.file import FileRequired,FileAllowed,FileField
from flask_wtf import FlaskForm
from main.models.customers import tblCustomers

class CustomerRegisterForm(FlaskForm):
    name = StringField('Name: ')
    username = StringField('Username: ',[validators.DataRequired()])
    email = StringField('Email: ',[validators.Email(), validators.DataRequired()] )
    password = PasswordField('Password: ',[validators.DataRequired(), validators.EqualTo('confirm')])
    confirm = PasswordField('Confirm Password: ',[validators.DataRequired()])
    address = StringField('Delivery Address: ',[validators.DataRequired()])
    number = StringField('Contact Number: ',[validators.DataRequired()])
    profile = FileField('Profile: ', validators=[FileAllowed(['jpg','png','jpeg'])])

    def validate_username(self, username):
        if tblCustomers.query.filter_by(username=username.data).first():
            raise ValidationError("This username is already in use")
    
    def validate_email(self, email):
        if tblCustomers.query.filter_by(email=email.data).first():
            raise ValidationError("This email is already in use")
    
    def validate_number(self, number):
        if tblCustomers.query.filter_by(number=number.data).first():
            raise ValidationError("This Contact Number is already in use")

class CustomerLoginForm(FlaskForm):
    email = StringField('Email: ',[validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ',[validators.DataRequired()])