import datetime
import json
import logging
import os
import random
import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')


def start(update, context):
    """ Функция с описанием бота """
    reply_keyboard = [['/start', '/help'],
                      ['/horoscope', '/info']]
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 one_time_keyboard=False)
    update.message.reply_text("Привет! Я подмастерье. Вот список команд: \n"
                              "/help - Контакты \n"
                              "/horoscope - Гороскоп & Котики \n"
                              "/info - Гадатели и цены", reply_markup=markup)


def helps(update, context):
    update.message.reply_text('Почта: witcheshut@mail.ru \n'
                              'Телеграм: @changethispls')


def info(update, context):
    context.bot.send_photo(
        update.message.chat_id, photo=open('../static/img/specialists/all_witches.png', 'rb'),
        caption="Наши специалисты приведены выше. \nСвязаться с нами напрямую: witcheshut@mail.ru"
    )


def horoscope(update, context):
    with open('../static/json/horoscope.json', encoding='utf-8') as file:
        data = json.load(file)
    if update.message.text == '/horoscope':
        reply_keyboard = [['Овен', 'Телец', 'Близнецы'],
                          ['Рак', 'Лев', 'Дева'],
                          ['Весы', 'Скорпион', 'Стрелец'],
                          ['Козерог', 'Водолей', 'Рыбы']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text("Напиши свой знак зодиака:", reply_markup=markup)
    else:
        month = {'01': 'Января', '02': 'Февраля', '03': 'Марта', '04': 'Апреля', '05': 'Мая', '06': 'Июня',
                 '07': 'Июля', '08': 'Августа', '09': 'Сентября', '10': 'Октяря', '11': 'Ноября', '12': 'Декабря'}
        english = {"Овен": "aries", "Телец": "taurus", "Близнецы": "twins", "Рак": "cancer", "Лев": "lion",
                   "Дева": "virgin", "Весы": "scales", "Скорпион": "scorpio", "Стрелец": "sagittarius",
                   "Козерог": "capricorn", "Водолей": "aquarius", "Рыбы": "fish"}

        text = f'Гороскоп на сегодня для знака зодиака {update.message.text.capitalize()}: \n'
        today = datetime.date.today()
        date = str(today).split(' ')[0].split('-')
        date = f"{date[2]} {month[date[1]]} {date[0]}"

        if date not in data:
            all_znak = {}
            with open('../static/txt/horoscope.txt', encoding='utf-8') as file3:
                day_predictions_and_pictures = file3.read().replace('\n', '').split('***')
                day_predictions_and_pictures = [i.split('*') for i in day_predictions_and_pictures]
            for i in ["aries", "taurus", "twins", "cancer", "lion", "virgin", "scales", "scorpio", "sagittarius",
                      "capricorn", "aquarius", "fish"]:
                all_znak.update({i: random.choice(day_predictions_and_pictures)})
            data.update({date: all_znak})
            with open('../static/json/horoscope.json', 'w', encoding='utf-8') as file2:
                json.dump(data, file2)
            with open('../static/json/horoscope.json', encoding='utf-8') as file:
                data = json.load(file)

        if update.message.text.capitalize() in english and english[update.message.text.capitalize()] in data[date]:
            text += data[date][english[update.message.text.capitalize()]][0]

            response = requests.get('https://api.thecatapi.com/v1/images/search')
            data = response.json()
            reply_keyboard = [['/start', '/help'],
                              ['/horoscope', '/info']]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
            context.bot.send_photo(update.message.chat_id, photo=data[0]['url'], caption=text, reply_markup=markup)
        else:
            update.message.reply_text('Такого знака зодиака нет...')


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', helps))
    dp.add_handler(CommandHandler('info', info))
    text_handler = MessageHandler(Filters.text, horoscope)
    dp.add_handler(text_handler)
    dp.add_handler(CommandHandler('horoscope', horoscope))
    updater.start_polling()
    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
