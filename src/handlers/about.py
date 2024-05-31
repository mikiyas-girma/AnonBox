from main_bot import bot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from models.engine.storage import SessionLocal
from handlers.message_handlers import send_welcome

bot = bot.bot


@bot.message_handler(func=lambda message: message.text == '➡️ More')
def about_callback(message):
    print(message)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row_width = 2
    keyboard.add(KeyboardButton('🔙 Back'),
                 KeyboardButton('🌐 Language'),
                 KeyboardButton('⁉️ FAQ'),
                 KeyboardButton('📄 Rules'),
                 KeyboardButton('💬 Feedback'),
                 KeyboardButton('📥 Contact Us'),
                 KeyboardButton('ℹ️ About Us'))

    bot.send_message(message.chat.id, "Select an option",
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == '🔙 Back')
def back_to_profile(message):
    send_welcome(message)


@bot.message_handler(func=lambda message: message.text == '🌐 Language')
def language(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton('🇬🇧 English', callback_data='en'),
                 InlineKeyboardButton('🇪🇹 Amharic', callback_data='am'))
    bot.send_message(message.chat.id, "Select a language",
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == '⁉️ FAQ')
def faq(message):
    text = '<b>--- Frequently Asked Questions ---</b>\n\n \
1. How long do questions take to be approved?\n — Questions can take from less\
 than an hour to a day or two to be approved, since\
there is a large volume of questions being asked daily.\
 If we seem to be taking too long to give you a response, please reach out to\
 admins.\n2. Is my identity hidden from everyone if I choose to be anonymous? \
\n— Yes! There\'s no way for others to know your identity.\n\
3. Why has my question been denied? \n — Your question probably doesn\'t\
 follow the rules that we have set. You should receive reasoning behind your\
 denial but if you don\'t, feel free to contact admins.\n 4. Why did I receive\
 a warning?\n -You have gotten reported by a member of the channels and admins\
 have chosen to give you a warning. Please do not repeatedly break channel \
 rules or it might result in a ban.'

    bot.send_message(message.chat.id, text, parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == '📄 Rules')
def rules(message):
    print("Rules")
    text = '<b>--- Rules ---</b>\n\n \
1. No questions related to buying or selling. You can ask where some\
 business is located or where you can buy something but you can not ask people\
 to buy an item you\'re selling or advertise your business.\n 2. Your question\
 has to be an actual question, and not a public announcement, vent (unless you\
 have a question or want advice on ask another question again; \for example:\
  are there any people here who know how to...  Please rephrase these\
 questions in a way that states your actual question.\n 3. Please keep your\
question clear and use the proper category tag,if you are not sure, \
select other.'

    bot.send_message(message.chat.id, text, parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == '💬 Feedback')
def feedback(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row_width = 1
    keyboard.add(KeyboardButton('🔙 Back'))
    bot.send_message(message.chat.id, "Send us your feedback",
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, send_feedback)


def send_feedback(message):
    if message.text == '🔙 Back':
        return about_callback(message)
    bot.send_message(message.chat.id, "Thank you for your feedback!")


@bot.message_handler(func=lambda message: message.text == '📥 Contact Us')
def contact_us(message):
    text = 'If you have any questions or concerns, please contact us at\
 [@KEPVERSE](mailto:kepaverse@gmail.com)'
    bot.send_message(message.chat.id, text, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == 'ℹ️ About Us')
def about_us(message):
    text = 'Youbot developed by \n \
[@Loopcop](mailto:Loopcop@gmail.com)'
    bot.send_message(message.chat.id, text, parse_mode='Markdown')
