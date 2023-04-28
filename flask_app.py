import datetime
import json
import random
from flask import Flask, render_template, redirect, request
from data.zodiacs import ZodiacCompatibility
from data.names import NameCompatibility
from extra_files.finder import get_png
from data import db_session
from data.users import User
from data.forms import RegisterForm, LoginForm, RecoveryForm, FinalRecoveryForm, ZodiacsForm, NamesForm, StolenContentForm
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
#             image = data[current_user.email]
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
    """ Страница авторизации пользователя """
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль, подбери другое заклинание или "
                                                     "признай наконец, что забыл его...", form=form, photo=get_image())
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    """ Страница регистрации пользователя """
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают, проверь раскладку (язык)", photo=get_image())
        pswd = form.password.data
        if len(pswd) > 20 or len(pswd) < 8 or pswd.isdigit() or pswd.islower():
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Пароль не надёжный, подумай ещё", photo=get_image())
        pswd = None  # политика конфиденциальности, нигде не сохраняем не хэшированный пароль пользователя
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.login.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой маг уже есть. Если этот маг - ты, нажми на кнопку 'Войти' ниже!")
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


@app.route('/recovery', methods=['GET', 'POST'])
def recovery():
    """ Страница первого этапа восстановления пароля """
    form = RecoveryForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data, User.name == form.name.data,
                                          User.surname == form.surname.data).first()
        if user:
            to_email = form.email.data
            message = 'https://pinguin.pythonanywhere.com/frecovery\n' \
                      'Привет, вот ссылка, чтобы восстановить пароль!'
            msg['Subject'] = 'Восстановление пароля'
            from_email = 'witcheshut@mail.ru'
            password = 'ejtkcTCZXiBBT7dHkLQM'

            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP('smtp.mail.ru: 25')  # эту часть лучше не трогать
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
            server.quit()
            return redirect('/')
    return render_template('recovery.html', title='Восстановление пароля', form=form)


@app.route('/frecovery', methods=['GET', 'POST'])
def frecovery():
    """ Страница заключительного этапа восстановления пароля """
    form = FinalRecoveryForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают, ты снова его забыл?")
        pswd = form.password.data
        if len(pswd) > 20 or len(pswd) < 8 or pswd.isdigit() or pswd.islower():
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Пароль не надёжный, подумай ещё")
        pswd = None  # политика конфиденциальности, нигде не сохраняем не хэшированный пароль пользователя
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:
            user.set_password(form.password.data)
            db_sess.commit()
        return redirect('/login')
    return render_template('recovery1.html', title='Восстановление пароля', form=form)


@app.route('/stolen_content')
def stolen():
    """ Страница с нашими источниками """
    form = StolenContentForm()
    if form.validate_on_submit():
        return redirect('/')
    return render_template('stolen.html', title='Наши источники', form=form)


@app.route('/power_places')
def show_places():
    """ Страница отображения мест силы и их фото со спутника"""
    coords = [["94.315662%2C68.340233", '6', 'plato_putorana.jpg', 'Плато Путорана (Красноярский край)'],
              ["59.298585%2C62.257436", '15', 'manpupuner.jpg', 'Столбы выветривания (Республика Коми)'],
              ["57.006969%2C57.440527", '16', 'cave.jpg', 'Кунгурская ледяная пещера (Пермский край)']]
    images = []
    for coord in coords:
        img = get_png(*coord[:-1])
        images.append([img, coord[-1]])
    return render_template("power_places.html", title='Магазины', images=images, photo=get_image())


@app.route('/study/<cards_type>')
def study(cards_type):
    """
    Страница получения предсказаний

    Attributes
    ----------
    cards_type : str
        Тип справочника (tarot - таро, cards - игральные карты)
    """
    if cards_type == 'tarot':
        with open('static/json/all_cards.json', encoding='utf-8') as file:
            data = json.load(file)
            keys = list(data["Карты Таро"])
        cards = []
        for key in keys:
            cards.append((key, data["Карты Таро"][key]['описание'], data["Карты Таро"][key]['изображение']))
        return render_template("guide.html", title='Справочник по картам Таро', type=cards_type, cards=cards, photo=get_image())
    elif cards_type == 'cards':
        with open('static/json/all_cards.json', encoding='utf-8') as file:
            data = json.load(file)
            keys = list(data["Карты игральные"])
        cards = []
        for key in keys:
            cards.append((key, data["Карты игральные"][key]['описание'], data["Карты игральные"][key]['изображение']))
        return render_template("guide.html", title='Справочник по Игральным картам', type=cards_type, cards=cards, photo=get_image())


@app.route('/prediction/<pred_type>')
def prediction(pred_type):
    """
    Страница получения предсказаний

    Attributes
    ----------
    pred_type : str
        Тип гадания (choice - выбор гадания,
                     cards - гадание на игральных картах,
                     tarot - гадание на картах Таро,
                     special - наши специалисты и их цены на персональное гадание)
    """
    if pred_type == 'choice':
        pred_type = None
        return render_template("prediction.html", title="Расклад", type=pred_type, photo=get_image())
    elif pred_type == 'cards':
        with open('static/json/all_cards.json', encoding='utf-8') as file:
            data = json.load(file)
            cards = random.sample(list(data["Карты игральные"]), 3)
        new_cards = []
        for i in cards:
            new_cards.append((i, data["Карты игральные"][i]["описание"], data["Карты игральные"][i]["изображение"]))
        return render_template("prediction.html", title='Гадание на игральных картах',
                               type=pred_type, cards=new_cards, photo=get_image())
    elif pred_type == 'tarot':
        with open('static/json/all_cards.json', encoding='utf-8') as file:
            data = json.load(file)
            cards = random.sample(list(data["Карты Таро"]), 3)
        new_cards = []
        for i in cards:
            new_cards.append((i, data["Карты Таро"][i]["описание"], data["Карты Таро"][i]["изображение"]))
        return render_template("prediction.html", title='Гадание на Таро',
                               type=pred_type, cards=new_cards, photo=get_image())
    elif pred_type == 'special':
        return render_template("prediction.html", title="Специалисты", type=pred_type, photo=get_image())


@app.route('/compatibility/<type_of_divination>', methods=['GET', 'POST'])
def compatibility(type_of_divination='zodiacs'):
    """
    Страница получения информации о совместимости двух людей по заданному критерию

    Attributes
    ----------
    type_of_divination : str
        Критерий, по которому выводится совместимость (zodiacs - по знаку зодиака,
                                                       names - по именам)
    """
    if type_of_divination == 'zodiacs':
        form = ZodiacsForm()
        if form.submit.data:
            db_sess = db_session.create_session()
            percent = db_sess.query(ZodiacCompatibility).filter(ZodiacCompatibility.his_sign == form.his_sign.data,
                                                                ZodiacCompatibility.her_sign == form.her_sign.data).first()
            if percent:
                images = (f'img/zodiacs/{form.his_sign.data}.jpg', f'img/zodiacs/{form.her_sign.data}.jpg')
                percent = (f'{form.his_sign.data} + {form.her_sign.data}', f'{percent}%')
                return render_template('compatibility.html', title='Совместимость', type=type_of_divination,
                                       images=images, percent=percent, form=form)
            return render_template('compatibility.html', title='Совместимость', type=type_of_divination,
                                   message='Нет такого(-их) знака(-ов) зодиака, ведьмак!', form=form)
        return render_template('compatibility.html', title='Совместимость', type=type_of_divination, form=form, photo=get_image())
    elif type_of_divination == 'names':
        form = NamesForm()
        if form.submit.data:
            db_sess = db_session.create_session()
            percent = db_sess.query(NameCompatibility).filter(NameCompatibility.his_name == form.his_name.data,
                                                              NameCompatibility.her_name == form.her_name.data).first()
            if percent:
                percent = (f'{form.his_name.data} + {form.her_name.data}', f'{percent}%')
                return render_template('compatibility.html', title='Совместимость',
                                       type=type_of_divination, percent=percent, form=form)
            elif not form.his_name.data and not form.her_name.data:
                return render_template('compatibility.html', title='Совместимость', type=type_of_divination,
                                       message='Ты не ввёл имени, ведьмак!', form=form)
            percent = random.randint(38, 96)
            new_compatibility = NameCompatibility(
                his_name=form.his_name.data,
                her_name=form.her_name.data,
                percent=percent
            )
            db_sess.add(new_compatibility)
            db_sess.commit()
            percent = db_sess.query(NameCompatibility).filter(NameCompatibility.his_name == form.his_name.data,
                                                              NameCompatibility.her_name == form.her_name.data).first()
            percent = (f'{form.his_name.data} + {form.her_name.data}', f'{percent}%')
            return render_template('compatibility.html', title='Совместимость', type=type_of_divination,
                                   percent=percent, form=form)
        return render_template('compatibility.html', title='Совместимость', type=type_of_divination, form=form, photo=get_image())


@app.route('/horoscope/<znak_type>')
@app.route('/horoscope/<znak_type>/<day>')
def horoscope(znak_type, day='today'):
    """
    Страница получения гороскопа на два дня (сегодня и завтра) для каждого знака зодиака, каждый день обновляется

    Attributes
    ----------
    znak_type : str
        Название знака зодиака для получения гороскопа (choice - выбор знака зодиака, прочие - названия знаков)
    day : str
        День, на который предоставляется гороскоп (today - сегодня, прочие - другие дни)
    """
    month = {'01': 'Января', '02': 'Февраля', '03': 'Марта', '04': 'Апреля', '05': 'Мая', '06': 'Июня', '07': 'Июля',
             '08': 'Августа', '09': 'Сентября', '10': 'Октяря', '11': 'Ноября', '12': 'Декабря'}
    # Запоминаем запрошенный знак зодиака
    znak = znak_type
    if znak_type == 'choice':
        znak_type = None
    # сегодняшняя дата
    today = datetime.date.today()
    # Запрошенный день
    need_day = day
    if day == 'today':
        day = None
        date = str(today).split(' ')[0].split('-')
    else:
        tomorrow = today + datetime.timedelta(days=1)
        date = str(tomorrow).split(' ')[0].split('-')
    # Нужная дата
    date = f"{date[2]} {month[date[1]]} {date[0]}"
    # Открываем наш гороскоп
    with open('static/json/horoscope.json', encoding='utf-8') as file:
        data = json.load(file)
    if date not in data:
        all_znak = {}
        with open('static/txt/horoscope.txt', encoding='utf-8') as file3:
            day_predictions_and_pictures = file3.read().replace('\n', '').split('***')
            day_predictions_and_pictures = [i.split('*') for i in day_predictions_and_pictures]
        for i in ["aries", "taurus", "twins", "cancer", "lion", "virgin", "scales", "scorpio", "sagittarius",
                  "capricorn", "aquarius", "fish"]:
            all_znak.update({i: random.choice(day_predictions_and_pictures)})
        data.update({date: all_znak})
        with open('static/json/horoscope.json', 'w', encoding='utf-8') as file2:
            json.dump(data, file2)
        with open('static/json/horoscope.json', encoding='utf-8') as file:
            data = json.load(file)
    if znak != 'choice':
        forecast = data[date][znak][0]
    else:
        forecast = None
    return render_template("horoscope.html", title='Гороскоп', type=znak_type, day=day, date=date, forecast=forecast, photo=get_image())


@app.errorhandler(404)
def not_found_error(error):
    return render_template("error.html", title='Ошибка 404')


@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", title='Ошибка 500')


def main():
    """ Функция запуска приложения (и подключения к базе данных) """
    name_db = 'webproject.db'
    db_session.global_init(f"db/{name_db}")
    app.run()


if __name__ == '__main__':
    main()
