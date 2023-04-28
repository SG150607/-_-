import datetime
import json
import random
from flask import Flask, render_template, redirect, request
from data.names import NameCompatibility
from data import db_session
from data.users import User
from data.forms import RegisterForm, LoginForm, RecoveryForm, FinalRecoveryForm, ZodiacsForm, NamesForm, \
    StolenContentForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
msg = MIMEMultipart()


def get_image():
    if current_user.is_authenticated and os.path.exists(f'static/img/photo_profile/{current_user.id}.png'):
        return f'img/photo_profile/{current_user.id}.png'
    else:
        return f'img/photo_profile/00.png'


@login_manager.user_loader
def load_user(id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    """ Главная страница: введение и термины """
    files_to_delete = ['manpupuner.jpg', 'plato_putorana.jpg', 'cave.jpg']
    for file in files_to_delete:
        if os.path.exists(f'static/img/{file}'):
            os.remove(f'static/img/{file}')
    with open("static/txt/about.txt", "r", encoding="utf-8") as about:
        data_about = about.read()
    with open("static/txt/terms.txt", "r", encoding="utf-8") as terms:
        data_terms = terms.readlines()
    data_terms = list(map(lambda x: x.rstrip(), data_terms))
    return render_template("main.html", title='Главная', about=data_about, terms=data_terms, photo=get_image())


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if request.method == 'GET':
        with open('static/json/profile_images.json', 'r', encoding='utf-8') as list_images:
            data = json.load(list_images)
        return render_template('profile.html', title='Профиль пользователя', photo=get_image())
    elif request.method == 'POST':
        f = request.files['file']
        with open(f'static/img/photo_profile/{current_user.id}.png', "wb") as file:
            file.write(f.read())
        with open('static/json/profile_images.json', 'r', encoding='utf-8') as list_images:
            data = json.load(list_images)
            data.update({current_user.email: f'img/photo_profile/{current_user.id}.png'})
            with open('static/json/profile_images.json', 'w', encoding='utf-8') as update_images:
                json.dump(data, update_images)
        with open('static/json/profile_images.json', 'r', encoding='utf-8') as list_images:
            data = json.load(list_images)
            #             image = data[current_user.email]
            if not f:
                os.remove(f'static/img/photo_profile/{current_user.id}.png')
                render_template('profile.html', title='Профиль пользователя', photo=get_image())
        return render_template('profile.html', title='Профиль пользователя', photo=get_image())


@app.route('/login', methods=['GET', 'POST'])
def login():
    # страница авторизации пользователя
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form, photo=get_image())
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    # регистрация пользователя
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают",
                                   photo=get_image())
        pswd = form.password.data
        if len(pswd) > 20 or len(pswd) < 8 or pswd.isdigit() or pswd.islower():
            return render_template('register.html', title='Регистрация', form=form, message="Пароль не надёжный",
                                   photo=get_image())
        pswd = None
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.login.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.login.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def main():
    name_db = 'database.db'
    db_session.global_init(f"db/{name_db}")
    app.run()


if __name__ == '__main__':
    main()
