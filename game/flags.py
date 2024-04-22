import telebot

from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

import random
import threading
import time
import re

from data import countries


# Количество стран
NUM_COUNTRIES = len(countries)
# Ограничение времени
TIME_LIMIT = 5


# Сопоставляй население
def play_flags(message, bot: telebot, user: dict) -> None:
    user['hits'] = 0
    user['index'].clear()
    user['index'] = list(range(0, NUM_COUNTRIES))
    random.shuffle(user['index'])
    bot.send_message(message.chat.id, "Из какой страны этот флаг?")
    next_question(message, bot, user)


# Проверка ответа
def check_answer(message, bot: telebot, user: dict, country: str) -> None:
    if 'timer' not in user:
        next_question(message, bot, user)
        return
    
    elif re.match(r'^/', message.text):
        user['timer'].cancel()
        user.pop('timer')
        user['hits'] = 0
        user['index'].clear()
        bot.send_message(message.chat.id, "Выход из игрового режима", reply_markup = ReplyKeyboardRemove())
        time.sleep(1)
        bot.send_message(message.chat.id, "Выберите новый игровой режим")
        return
    
    elif message.text == country:
        user['timer'].cancel()
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(message.chat.id, '<b><i>ПРАВИЛЬНО</i></b>', parse_mode="html", disable_web_page_preview= True)
        user['hits'] += 1

        if user['hits'] == NUM_COUNTRIES:
            bot.send_message(message.chat.id, ("&lt---------- " + '<b><i>ИДЕАЛЬНЫЙ РАУНД</i></b>' + " ----------&gt"), parse_mode= "html", disable_web_page_preview= True)
        else:
            next_question(message, bot, user)

    else:
        user['timer'].cancel()
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(message.chat.id, f"<b><i>НЕПРАВИЛЬНО</i></b>, правильный ответ: <b><i>{country}</i></b>",
                         parse_mode="html", disable_web_page_preview=True, reply_markup=ReplyKeyboardRemove())
        time.sleep(1)
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(message.chat.id, ("&lt------- " + '<b><i>РЕШЕННЫЕ</i></b>' + f"{user['hits']}" + " -------&gt"),
                         parse_mode= "html", disable_web_page_preview= True)
        time.sleep(1)
        time.sleep(1)
        bot.send_message(message.chat.id, "Используйте /flags, чтобы сыграть снова")


# Обработка следующего вопроса (задания)
def next_question(message, bot: telebot, user: dict) -> None:
    country = user['index'][user['hits']]
    aux_index = [i for i in user['index'] if i != country]
    candidates = random.choices(aux_index, k=2) + [country]
    random.shuffle(candidates)

    buttons_text = [countries[candidate]['country'] for candidate in candidates]

    markup = ReplyKeyboardMarkup(
        one_time_keyboard= False,
        input_field_placeholder= "Выберите один",
        resize_keyboard= False,
        row_width=1
    )

    markup.add(*buttons_text)
    user['timer'] = threading.Timer(TIME_LIMIT, handle_timeout, args=[message, bot, user])
    user['timer'].start()
    answer = bot.send_message(message.chat.id, f"{countries[country]['flag'].encode().decode('unicode_escape')}",
                              reply_markup=markup)
    bot.register_next_step_handler(answer, check_answer, bot, user, countries[country]['country'])


# Проигрыш игры по времени
def handle_timeout(message, bot: telebot, user: dict):
    user['timer'].cancel()
    user.pop('timer')
    bot.send_message(message.chat.id, "Время вышло", reply_markup = ReplyKeyboardRemove())

    user['hits'] = 0
    user['index'].clear()
    bot.send_message(message.chat.id, "Используйте /flags, чтобы сыграть снова")
