import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Message
import os

from text import *

text_number = 0
PART_ONE_TEXT = "part_one_text_"
PART_TWO_TEXT = "part_two_text_"
PART_ONE_AUDIO = "part_one_audio_"
PART_TWO_AUDIO = "part_two_audio_"
BOT_TOKEN = "8055886559:AAEsauJZQCOHNQV8tz5LdoTIAbS4e_rFTUU"
SAVE_PATH = "C:\\notSystem\\vcs\\WizardReader\\saved_notes"
is_part_one = True
is_text = True
current_passage = None
passage = None
notes = {}
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton(go)
    keyboard.add(button)

    bot.send_message(message.chat.id, greeting, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "Поехали")
def send_first_part(message):
    global text_number, current_passage
    text_number += 1

    text_to_read = globals().get(f"{PART_ONE_TEXT}{text_number}")
    current_passage = text_to_read
    bot.send_message(message.chat.id, author)
    bot.send_message(message.chat.id, text_to_read)
    note_keyboard(message.chat.id)


def note_keyboard(chat_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    button_note = KeyboardButton(note)
    button_next = KeyboardButton(next_part)
    button_end = KeyboardButton(end_reading)
    button_format = KeyboardButton(text_audio if not is_text else text_text)

    keyboard.add(button_note)
    keyboard.add(button_next, button_end)
    keyboard.add(button_format)

    bot.send_message(chat_id, "Выберите действие" ,reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == end_reading)
def end_bot(message):
    send_notes(message.chat.id)
    bot.send_message(message.chat.id, "Конец произведения")
    bot.send_message(message.chat.id, farewell, reply_markup=ReplyKeyboardRemove())
    bot.send_message(message.chat.id, f"<a href='{link}'>Google Form</a>", parse_mode="HTML")
    bot.stop_polling()


@bot.message_handler(func=lambda message: message.text == next_part)
def send_part(message):
    global text_number
    text_number += 1

    if is_part_one:
        if is_text:
            is_part_one_exist = globals().get(f"{PART_ONE_TEXT}{text_number}")
            if is_part_one_exist:
                send_text_part(message, PART_ONE_TEXT, text_number)
            else:  # text not exist, consequently part one is end, need take a choice to user: continue or end
                ask_continue(message)
        else:
            audio_path = f"audio/{PART_ONE_AUDIO}{text_number}.mp3"
            is_part_one_exist = os.path.exists(audio_path)
            if is_part_one_exist:
                send_audio_part(message, audio_path)
            else:  # audio not exist, consequently part one is end, need take a choice to user: continue or end
                ask_continue(message)
    else:
        if is_text:
            is_part_two_exist = globals().get(f"{PART_TWO_TEXT}{text_number}")
            if is_part_two_exist:
                send_text_part(message, PART_TWO_TEXT, text_number)
                if text_number == 1:
                    note_keyboard(message.chat.id)
            else:  # text not exist, consequently part one is end, need take a choice to user: continue or end
                farewell_message(message)
        else:
            audio_path = f"audio/{PART_TWO_AUDIO}{text_number}.mp3"
            is_part_two_exist = os.path.exists(audio_path)
            if is_part_two_exist:
                send_audio_part(message, audio_path)
                if text_number == 1:
                    note_keyboard(message.chat.id)
            else:  # audio not exist, consequently part one is end, need take a choice to user: continue or end
                farewell_message(message)


def farewell_message(message):
    global notes

    send_notes(message.chat.id)
    bot.send_message(message.chat.id, "Конец произведения")
    bot.send_message(message.chat.id, farewell, reply_markup=ReplyKeyboardRemove())
    bot.send_message(message.chat.id, f"<a href='{link}'>Google Form</a>", parse_mode="HTML")


def send_text_part(message, text_part, number):
    global current_passage

    text_to_read = globals().get(f"{text_part}{number}")
    current_passage = text_to_read
    bot.send_message(message.chat.id, text_to_read)


def send_audio_part(message, audio_path):
    global current_passage

    audio = open(audio_path, "rb")
    current_passage = audio
    bot.send_audio(message.chat.id, audio)


@bot.message_handler(func=lambda message: message.text in [text_audio, text_text])
def swap_format(message):
    global is_text
    is_text = not is_text
    note_keyboard(message.chat.id)


def ask_continue(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_yes = KeyboardButton(yes_continue)
    button_no = KeyboardButton(no_continue)
    keyboard.add(button_yes, button_no)
    bot.send_message(message.chat.id, "Первая часть закончилась. Хотите продолжить?", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text in [yes_continue, no_continue])
def handle_continue_response(message):
    if message.text == yes_continue:
        global is_part_one, text_number
        is_part_one = False
        text_number = 0
        bot.send_message(message.chat.id, "Продолжаем!", reply_markup=telebot.types.ReplyKeyboardRemove())
        send_part(message)
    else:
        farewell_message(message)


@bot.message_handler(func=lambda message: message.text == note)
def request_note(message: Message):
    bot.send_message(message.chat.id, "Пришлите текст или картинку для заметки")
    bot.register_next_step_handler(message, test)


def test(message):
    global current_passage, notes

    if message.text:
        notes[current_passage] = message.text
        bot.send_message(message.chat.id, "Вы прислали мне текстовую заметку")

    if message.photo:
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_path = os.path.join(SAVE_PATH, f"{photo.file_id}.jpg")
        with open(file_path, "wb") as new_file:
            new_file.write(downloaded_file)
        notes[current_passage] = file_path
        bot.send_message(message.chat.id, "Вы прислали мне фото-заметку")


def send_notes(chat_id):
    for key, value in notes.items():
        if os.path.isfile(value):
            with open(value, "rb") as photo:
                bot.send_photo(chat_id, photo, caption=f"Фото-заметка: {key}")
        else:
            bot.send_message(chat_id, f"Текстовая заметка: {key}: {value}")


bot.infinity_polling()
