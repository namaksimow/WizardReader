import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Message
import os
from text import *

text_number = 0
PART_ONE_TEXT = "part_one_text_"
PART_TWO_TEXT = "part_two_text_"
PART_ONE_AUDIO = "part_one_audio_"
PART_TWO_AUDIO = "part_two_audio_"
BOT_TOKEN = "7722283150:AAEB7wFmXkuDMMVfmCLhFruqU7hrODIpemM"
SAVE_PATH = "D:\\PyCharmProjects\\WizardReader\\saved_notes"
is_part_one = True
is_text = True
current_passage = None
notes = {}
bot = telebot.TeleBot(BOT_TOKEN)
continue_message_id = None

@bot.message_handler(commands=['start'])
def start(message):
    global text_number, is_part_one
    text_number = 0
    is_part_one = True

    user_id = message.from_user.id
    if user_id in notes:
        del notes[user_id]

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton(go)
    keyboard.add(button)
    username = message.from_user.username or message.from_user.first_name
    greeting_message = get_greeting(username)
    with open('cat with book.jpg', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=greeting_message, reply_markup=keyboard, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "Поехали")
def send_first_part(message):
    global text_number, current_passage
    text_number += 1

    text_to_read = globals().get(f"{PART_ONE_TEXT}{text_number}")
    current_passage = text_to_read
    bot.send_message(message.chat.id, text_to_read, parse_mode="Markdown")
    note_keyboard(message.chat.id)


def note_keyboard(chat_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    button_note = KeyboardButton(note)
    button_next = KeyboardButton(next_part)
    button_end = KeyboardButton(end_reading)
    button_format = KeyboardButton(text_audio if not is_text else text_text)

    keyboard.add(button_note)
    keyboard.add(button_next, button_format, button_end)

    bot.send_message(chat_id, "Выберите действие", reply_markup=keyboard, parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == end_reading)
def end_bot(message):
    global text_number

    user_id = message.from_user.id
    bot.send_message(message.chat.id, "Конец чтения.")
    send_notes(message.chat.id, user_id)
    bot.send_message(message.chat.id, farewell, reply_markup=ReplyKeyboardRemove(), parse_mode="MarkdownV2")


@bot.message_handler(func=lambda message: message.text == next_part)
def send_part(message):
    bot.delete_message(message.chat.id, message.message_id)
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
            else:  # text not exist, consequently part one is end, need take a choice to user: continue or end
                farewell_message(message)
        else:
            audio_path = f"audio/{PART_TWO_AUDIO}{text_number}.mp3"
            is_part_two_exist = os.path.exists(audio_path)
            if is_part_two_exist:
                send_audio_part(message, audio_path)
            else:  # audio not exist, consequently part one is end, need take a choice to user: continue or end
                farewell_message(message)


def farewell_message(message):
    global notes, text_number

    user_id = message.from_user.id
    bot.send_message(message.chat.id, "Конец чтения.")
    send_notes(message.chat.id, user_id)
    bot.send_message(message.chat.id, farewell, reply_markup=ReplyKeyboardRemove(), parse_mode="MarkdownV2")


def send_text_part(message, text_part, number):
    global current_passage

    text_to_read = globals().get(f"{text_part}{number}")
    current_passage = text_to_read
    bot.send_message(message.chat.id, text_to_read, parse_mode="Markdown")


def send_audio_part(message, audio_path):
    global current_passage

    audio = open(audio_path, "rb")
    current_passage = audio
    bot.send_audio(message.chat.id, audio)


@bot.message_handler(func=lambda message: message.text in [text_audio, text_text])
def swap_format(message):
    global is_text

    is_text = not is_text
    if is_text:
        bot.send_message(message.chat.id, "Смена формата на *текст*.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Смена формата на *аудио*.", parse_mode="Markdown")
    note_keyboard(message.chat.id)


def ask_continue(message):
    global continue_message_id

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_yes = KeyboardButton(yes_continue)
    button_no = KeyboardButton(no_continue)
    keyboard.add(button_yes, button_no)
    sent_message = bot.send_message(message.chat.id, "Первая часть закончилась. Хотите продолжить?", reply_markup=keyboard)
    continue_message_id = sent_message.message_id


@bot.message_handler(func=lambda message: message.text in [yes_continue, no_continue])
def handle_continue_response(message):
    global continue_message_id

    if continue_message_id is not None:
        bot.delete_message(message.chat.id, continue_message_id)
        continue_message_id = None

    if message.text == yes_continue:
        global is_part_one, text_number
        is_part_one = False
        text_number = 0
        bot.send_message(message.chat.id, "Продолжаем чтение...", reply_markup=telebot.types.ReplyKeyboardRemove())
        send_part(message)
        note_keyboard(message.chat.id)
    else:
        farewell_message(message)


@bot.message_handler(func=lambda message: message.text == note)
def request_note(message: Message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, f"Пришлите *текст или картинку* для заметки.", parse_mode="Markdown")
    bot.register_next_step_handler(message, test, user_id)


def test(message, user_id):
    global current_passage, notes

    if user_id not in notes:
        notes[user_id] = {}

    if message.text:
        notes[user_id][current_passage] = message.text
        bot.send_message(message.chat.id, "Текстовая заметка сохранена.")
        return

    if message.photo:
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_path = os.path.join(f"saved_notes/{photo.file_id}.jpg")
        with open(file_path, "wb") as new_file:
            new_file.write(downloaded_file)
        notes[user_id][current_passage] = file_path
        bot.send_message(message.chat.id, "Фото-заметка сохранена.")
        return

    else:
        bot.send_message(message.chat.id, "Прислана заметка некорректного формата. Она не была сохранена.")
        return


def send_notes(chat_id, user_id):
    if user_id in notes:
        for key, value in notes[user_id].items():
            if os.path.isfile(value):
                with open(value, "rb") as photo:
                    bot.send_photo(chat_id, photo, caption=f"*Фрагмент текста:* \n{key}", parse_mode="Markdown")
            else:
                bot.send_message(chat_id, f"*Фрагмент текста:* \n{key} \n\n*Заметка:* {value}", parse_mode="Markdown")


bot.infinity_polling()
