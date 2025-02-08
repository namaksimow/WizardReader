import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from text import *
from telebot import types

BOT_TOKEN = "8055886559:AAEsauJZQCOHNQV8tz5LdoTIAbS4e_rFTUU"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    keyboard_go = ReplyKeyboardMarkup(resize_keyboard=True)
    button_go = KeyboardButton(go)
    keyboard_go.add(button_go)

    bot.send_message(message.chat.id, greeting, reply_markup=keyboard_go)


bot.infinity_polling()
