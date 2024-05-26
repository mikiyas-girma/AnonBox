import telebot
from main_bot import bot
from flask import Flask, request
from handlers import (message_handlers, inline_handlers,
                      callback_handlers, browse_questions)
from utils import keyboards
from models.engine.storage import init_db

# reference to import all handlers
message_handlers
inline_handlers
callback_handlers
keyboards
browse_questions


app = Flask(__name__)


# Set webhook for the bot
@app.route('/webhook', methods=['POST'])
def webhook_handler():
    update = telebot.types.Update.de_json(
        request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return '', 200


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
