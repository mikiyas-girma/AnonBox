import telebot
import os
from dotenv import load_dotenv

load_dotenv()


def create_bot():
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    bot = telebot.TeleBot(BOT_TOKEN)
    bot.remove_webhook()
    bot.set_webhook(WEBHOOK_URL)
    return bot


bot = create_bot()
