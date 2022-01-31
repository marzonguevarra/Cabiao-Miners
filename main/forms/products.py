from wtforms import Form, IntegerField, StringField, BooleanField, TextAreaField, DecimalField, validators
from flask_wtf.file import FileAllowed, FileField, FileRequired

class ProductForm(Form):
    name = StringField('Name', [validators.DataRequired()])
    price = DecimalField('Price', [validators.DataRequired()])
    discount = IntegerField('Discount', default = 0)
    stock = IntegerField('Stock', [validators.DataRequired()])
    colors = StringField('Colors', [validators.DataRequired()])
    description = TextAreaField('Description', [validators.DataRequired()])
    image_1 = FileField('Image 1', validators=[FileAllowed(['jpg','png','jpeg'])])
    image_2 = FileField('Image 2', validators=[FileAllowed(['jpg','png','jpeg'])])
    image_3 = FileField('Image 3', validators=[FileAllowed(['jpg','png','jpeg'])])