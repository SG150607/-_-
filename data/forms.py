from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, SelectField, FileField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    """форма регистрации"""
    login = StringField('Введи почту', validators=[DataRequired()])
    password = PasswordField('Введи пароль', validators=[DataRequired()])
    confirm = PasswordField('Повтори пароль', validators=[DataRequired()])
    surname = StringField('Твоя фамилия', validators=[DataRequired()])
    name = StringField('Твоё имя', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    """форма авторизации"""
    email = EmailField('Введи почту', validators=[DataRequired()])
    password = PasswordField('Введи пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RecoveryForm(FlaskForm):
    """форма восстановления пароля"""
    name = StringField('Твоё имя', validators=[DataRequired()])
    surname = StringField('Твоя фамилия', validators=[DataRequired()])
    email = StringField('Введи почту', validators=[DataRequired()])
    submit = SubmitField('Восстановить доступ')


class FinalRecoveryForm(FlaskForm):
    """форма восстановления пароля"""
    email = StringField('Введи почту', validators=[DataRequired()])
    password = PasswordField('Введи новый пароль', validators=[DataRequired()])
    confirm = PasswordField('Повтори пароль', validators=[DataRequired()])
    submit = SubmitField('Изменить пароль')


class ZodiacsForm(FlaskForm):
    """форма выбора знаков зодиака"""
    his_sign = SelectField('Его знак зодиака', validators=[DataRequired()])
    her_sign = SelectField('Её знак зодиака', validators=[DataRequired()])
    submit = SubmitField('Узнать совместимость (%)')


class NamesForm(FlaskForm):
    """форма выбора имён"""
    his_name = StringField('Его имя', validators=[DataRequired()])
    her_name = StringField('Её имя', validators=[DataRequired()])
    submit = SubmitField('Узнать совместимость (%)')


class StolenContentForm(FlaskForm):
    """форма наших источников"""
    submit = SubmitField('Вернутся на главную страницу')


class ImageForm(FlaskForm):
    file = FileField('Фото', validators=[DataRequired()])
    submit = SubmitField('Загрузить фото')