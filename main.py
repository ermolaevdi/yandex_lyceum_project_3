import os

import telebot

from dotenv import load_dotenv
from telebot.apihelper import ApiTelegramException

from game.capitals import play_capitals
from game.population import play_population
from game.flags import play_flags


# Токен для телеграмм-бота
load_dotenv()
TOKEN_BOT = '6431099780:AAGypGzzncLqsyPEfgRyhNfqffXqbstGIO8'


# Обрабатываем возможную ошибку при подключении
try:
    bot = telebot.TeleBot(TOKEN_BOT)
except ApiTelegramException as e:
    print(f"Ошибка подключения: {e}")

users: dict = {}


# Набор команд для бота
def set_commands() -> None:
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "Запустить бота"),
        telebot.types.BotCommand("/capitals", "Столица"),
        telebot.types.BotCommand("/population", "Население"),
        telebot.types.BotCommand("/flags", "Флаги"),
        telebot.types.BotCommand("/back", "Выйти из игры"),
        telebot.types.BotCommand("/help", "Функции бота")
    ])


# Нажатие на кнопку "start"
@bot.message_handler(commands=["start"])
def start(message) -> None:
    users[message.chat.id] = {'hits': 0, 'index' : []}
    bot.send_message(message.chat.id, "Добро пожаловать, дорогой друг!\n"
        "\n"
        "/capitals         : Находи столицы\n"
        "/population   : Сопоставляй население\n"
        "/flags               : Отгадывай флаги")


# Нажатие на кнопку "start"
@bot.message_handler(commands=["help"])
def bot_help(message) -> None:
    bot.send_message(message.chat.id, "Тренируйте географию вместе с Mouse_Bot!\n"
        "\n"
        "/capitals         : Находи столицы\n"
        "/population   : Сопоставляй население\n"
        "/flags               : Отгадывай флаги\n"
        "\n"
        "Используйте /back, чтобы выйти из текущей игры.\n"
        "\n"
        "Помните, у Вас есть только 5 секунд, чтобы дать ответ на вопрос!"
        "\n"
        "Дерзайте!")


# Нажатие на кнопку "capitals"
@bot.message_handler(commands=["capitals"])
def capitals(message) -> None:
    play_capitals(message, bot, users[message.chat.id])


# Нажатие на кнопку "population"
@bot.message_handler(commands=["population"])
def population(message) -> None:
    play_population(message, bot, users[message.chat.id])


# Нажатие на кнопку "flags"
@bot.message_handler(commands=["flags"])
def flags(message) -> None:
    play_flags(message, bot, users[message.chat.id])


# Нажатие на кнопку "back"
@bot.message_handler(commands=["back"])
def back(message) -> None:
    
    bot.send_message(message.chat.id, "Игровой режим отключен\n"
        "Выберите один из игровых режимов\n"
        "\n"
        "/capitals         : Находи столицы\n"
        "/population   : Сопоставляй население\n"
        "/flags               : Отгадывай флаги\n"
        "\n")


# ------------- ГЛАВНЫЙ ЦИКЛ ------------- #
if __name__ == '__main__':
    print("Запуск БОТа...")
    set_commands()
    try:
        bot.infinity_polling()
    except ApiTelegramException as e:
        print(f"Ошибка подключения: {e}")
