import os
from dotenv import load_dotenv
from ratelimitedbot import RateLimitedBot

load_dotenv()


def create_bot():
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    bot = RateLimitedBot(BOT_TOKEN)
    bot.bot.remove_webhook()
    bot.bot.set_webhook(WEBHOOK_URL)
    return bot


bot = create_bot()
