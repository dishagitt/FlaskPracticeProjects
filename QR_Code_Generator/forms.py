from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class QRCodeForm(FlaskForm):
    data = StringField('Enter Data', validators=[DataRequired()])
    submit = SubmitField('Generate QR Code')