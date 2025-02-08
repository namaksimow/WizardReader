import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os

from text import *


text_number = 1
PART_ONE_TEXT = "part_one_text_"

BOT_TOKEN = "8055886559:AAEsauJZQCOHNQV8tz5LdoTIAbS4e_rFTUU"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton(go)
    keyboard.add(button)

    bot.send_message(message.chat.id, greeting, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "Поехали")
def send_first_part(message):
    text_to_read = globals().get(f"{PART_ONE_TEXT}{text_number}")
    bot.send_message(message.chat.id, author)
    bot.send_message(message.chat.id, text_to_read)
    note_keyboard(message.chat.id)


def note_keyboard(chat_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    button_note = KeyboardButton("Прикрепить заметку")
    button_next = KeyboardButton("Дальше")
    button_end = KeyboardButton("Завершить чтение")

    keyboard.add(button_note)
    keyboard.add(button_next, button_end)

    bot.send_message(chat_id, "Выберите действие" ,reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "Завершить чтение")
def end_bot(message):
    bot.send_message(message.chat.id, "Спасибо за работу, пока!")
    bot.stop_polling()



bot.infinity_polling()
