import telebot

BOT_TOKEN = "8055886559:AAEsauJZQCOHNQV8tz5LdoTIAbS4e_rFTUU"
bot = telebot.TeleBot(BOT_TOKEN)

bot.infinity_polling()
