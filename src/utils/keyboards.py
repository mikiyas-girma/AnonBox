from main_bot import bot
import telebot

from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

# markup = ReplyKeyboardMarkup(resize_keyboard=True)
# markup.add(KeyboardButton('Btn 1'))


# @bot.message_handler(commands=['keyboard'])
# def show_keyboard(message):
#     bot.send_message(message.chat.id,
#                      'you will see a keyboard',
#                      reply_markup=markup)

keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "a", "s", "d", "f", "g", "h", "j", "k", "l", "z", "x", "c", "v", "b", "n", "m"]
symbols = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "\'", "\"", "/", "\\", ",", ".", ";", ":"]


def keyboard(key_type="Normal"):
    markup = ReplyKeyboardMarkup(row_width=10)
    if key_type == "Normal":
        row = [KeyboardButton(x) for x in keys[:10]]
        markup.add(*row)
        row = [KeyboardButton(x) for x in keys[10:20]]
        markup.add(*row)
        row = [KeyboardButton(x) for x in keys[20:29]]
        markup.add(*row)
        row = [KeyboardButton(x) for x in keys[29:]]
        markup.add(*row)
        markup.add(KeyboardButton("Caps Lock"), KeyboardButton("Symbols"), KeyboardButton("🔙Delete"), KeyboardButton("✅Done"), KeyboardButton("Send"))
    elif key_type == "Symbols":
        row = [KeyboardButton(x) for x in symbols[:10]]
        markup.add(*row)
        row = [KeyboardButton(x) for x in symbols[10:20]]
        markup.add(*row)
        row = [KeyboardButton(x) for x in symbols[20:]]
        markup.add(*row)
        markup.add(KeyboardButton("Caps Lock"), KeyboardButton("Normal"), KeyboardButton("🔙Delete"), KeyboardButton("✅Done"), KeyboardButton("Send"))
    else:
        row = [KeyboardButton(x.upper()) for x in keys[:10]]
        markup.add(*row)
        row = [KeyboardButton(x.upper()) for x in keys[10:20]]
        markup.add(*row)
        row = [KeyboardButton(x.upper()) for x in keys[20:29]]
        markup.add(*row)
        row = [KeyboardButton(x.upper()) for x in keys[29:]]
        markup.add(*row)
        markup.add(KeyboardButton("Normal"), KeyboardButton("Symbols"), KeyboardButton("🔙Delete"), KeyboardButton("✅Done"), KeyboardButton("Send"))
    return markup


@bot.message_handler(commands=["key"])
def start_message(message):
    bot.send_message(message.chat.id, "You can use the keyboard", reply_markup=keyboard())


user_input = ""


@bot.message_handler(func=lambda message: True)
def all_messages(message):
    global user_input
    if message.text == "Send":
        if user_input:
            bot.send_message(message.chat.id, user_input)
            bot.reply_to(message, 'ok')
            user_input = ""
    elif message.text == "✅Done":
        markup = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         "Done with Keyboard",
                         reply_markup=markup)
    elif message.text == "Symbols":
        bot.send_message(message.from_user.id, "Special characters",
                         reply_markup=keyboard("Symbols"))
    elif message.text == "Normal":
        bot.send_message(message.from_user.id, "Normal Keyboard",
                         reply_markup=keyboard("Normal"))
    elif message.text == "Caps Lock":
        bot.send_message(message.from_user.id, "Caps Lock",
                         reply_markup=keyboard("Caps"))
    elif message.text == "🔙Delete":
        bot.delete_message(message.from_user.id, message.message_id)
    else:
        user_input += message.text
