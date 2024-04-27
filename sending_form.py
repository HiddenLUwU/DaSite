from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired


class SendingForm(FlaskForm):
    image = FileField('Приложите картинку', validators=[DataRequired()])
    message = StringField('Напишите сообщение', validators=[DataRequired()])
    submit = SubmitField('Отправить')
