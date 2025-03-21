from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from sqlalchemy import Boolean
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

from .models.user import User




# Валидаторы вообще убрать можно - уязвимость. Надо прочитать про них. В идеале вообще удалить все валидаторы. Чтобы инъекции были и т.д.
class RegistrationForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=2, max=20)], render_kw={
        'class':'form-control',
        'placeholder': 'Логин'
    })
    flag = StringField('Номер телефона', validators=[DataRequired(), Length(min=2, max=60)], render_kw={})
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердтие пароль', validators=[DataRequired(), EqualTo('password')])
    avatar = FileField('Загрузите своё фото', validators=[DataRequired()]) # тут мы ставив валидаторы, чтобы нам случайно чего опасного не закинули - в целом уяза для CTF-ки
    submit = SubmitField('Зарегистрироваться')


    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user:
            raise ValidationError("Данное имя уже занято. Пожалуйста выберите другое...")


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=2, max=20)], render_kw =
    {
        'class':'form-control',
        'placeholder': 'Логин'
    })
    password = PasswordField('<PASSWORD>', validators=[DataRequired()], render_kw=
    {
        'class':'form-control',
        'placeholder': 'Логин'
    })
    remember = BooleanField('Запомнить меня', render_kw=
    {
        'class':'form-control',
    })
    submit = SubmitField('Войти', render_kw=
    {
        'class':'form-control',
    })


class CarCreateForm(FlaskForm):
    picture = FileField('Загрузите своё фото', validators=[DataRequired()]) # тут мы ставив валидаторы, чтобы нам случайно чего опасного не закинули - в целом уяза для CTF-ки


class ReviewForm(FlaskForm):
    rating = StringField('Оценка', validators=[DataRequired(), Length(min=2, max =10)],render_kw=
    {
        'class':'form-control',
         'placeholder': 'Оставьте вашу оценку'
    })
    comment = StringField('Комментарий', validators=[DataRequired(), Length(min=2, max =10)], render_kw=
    {
        'class':'form-control',
        'placeholder': 'Комментарий к оценке'
    })
