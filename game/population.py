import telebot

from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

import random
import threading
import time

from data import countries


# Количество стран
NUM_COUNTRIES = len(countries)
# Ограничение времени
TIME_LIMIT = 5


# Отгадывай флаги
def play_population(message, bot: telebot, user: dict) -> None:
    user['hits'] = 0
    user['index'].clear()
    user['index'] = list(range(0, NUM_COUNTRIES))
    random.shuffle(user['index'])
    bot.send_message(message.chat.id, "У какой страны население больше?")
    next_question(message, bot, user)

# Проверка ответа
def check_answer(message, bot: telebot, user: dict, c1: dict, c2: dict) -> None:
    if 'timer' not in user:
        next_question(message, bot, user)
        return
    
    elif message.text == "/back":
        user['timer'].cancel()
        user.pop('timer')
        user['hits'] = 0
        user['index'].clear()
        bot.send_message(message.chat.id, "Выход из игрового режима", reply_markup = ReplyKeyboardRemove())
        time.sleep(1)
        bot.send_message(message.chat.id, "Выберите новый игровой режим")
        return
    
    higher = c1 if c1['population'] > c2['population'] else c2
    attemp = c2['country'] if message.text == "Higher" else c1['country']

    if higher['country'] == attemp:
        user['timer'].cancel()
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(message.chat.id, '<b><i>ПРАВИЛЬНО</i></b>', parse_mode="html", disable_web_page_preview= True)
        user['hits'] += 1
        next_question(message, bot, user)

    else:
        user['timer'].cancel()
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(message.chat.id, f"<b><i>НЕПРАВИЛЬНО</i></b>,"
                                          f"{c2['country']} {c2['flag'].encode().decode('unicode_escape')} имеет "
                                          f"{c2['population']: ,}",parse_mode="html", disable_web_page_preview=True,
                         reply_markup=ReplyKeyboardRemove())
        bot.send_chat_action(message.chat.id, "typing")
        time.sleep(1)
        bot.send_message(message.chat.id, ("&lt------- " + '<b><i>РЕШЕННЫЕ</i></b>' + f"{user['hits']}" + " -------&gt"),
                         parse_mode= "html", disable_web_page_preview= True)
        time.sleep(1)
        time.sleep(1)
        bot.send_message(message.chat.id, "Используйте /population, чтобы сыграть снова")


# Обработка следующего вопроса (задания)
def next_question(message, bot: telebot, user: dict) -> None:
    current_country = user['index'][user['hits']]
    next_country = user['index'][user['hits'] + 1]

    markup = ReplyKeyboardMarkup(
        one_time_keyboard = False,
        input_field_placeholder= "Выберите один",
        resize_keyboard= False,
        row_width= 1
    )

    markup.add("Higher", "Lower")

    bot.send_chat_action(message.chat.id, "typing")
    user['timer'] = threading.Timer(TIME_LIMIT, handle_timeout, args=[message, bot, user])
    user['timer'].start()
    bot.send_message(message.chat.id, f"{countries[current_country]['country']} "
                                      f"{countries[current_country]['flag'].encode().decode('unicode_escape')} "
                                      f"{countries[current_country]['population']: ,}")
    answer = bot.send_message(message.chat.id, f"{countries[next_country]['country']} "
                                               f"{countries[next_country]['flag'].encode().decode('unicode_escape')}",
                              reply_markup=markup)
    bot.register_next_step_handler(answer, check_answer, bot, user, countries[current_country], countries[next_country])


# Проигрыш игры по времени
def handle_timeout(message, bot: telebot, user: dict) -> None:
    user['timer'].cancel()
    user.pop('timer')
    bot.send_message(message.chat.id, "Время вышло", reply_markup = ReplyKeyboardRemove())

    user['hits'] = 0
    user['index'].clear()
    bot.send_message(message.chat.id, "Используйте /population, чтобы сыграть снова")
