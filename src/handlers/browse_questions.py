from main_bot import bot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,  # noqa
                           InlineKeyboardButton, InlineKeyboardMarkup)  # noqa
from models.engine.storage import SessionLocal
from models.states import State

bot = bot.bot

CHECKED = '✅'
UNCHECKED = ' '


@bot.message_handler(func=lambda message: message.text == '🙋‍♂️Browse Questions')
def questions(message):
    session = SessionLocal()
    states = session.query(State).filter_by(user_id=message.chat.id).first()
    if not states:
        states = State(user_id=message.chat.id, question_type='Popular',
                       category='All', timeframe='Today')
        session.add(states)
        session.commit()
    session.close()
    last_clicked = states.question_type
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(
        InlineKeyboardButton(
            f'{CHECKED if last_clicked == "Popular" else UNCHECKED} Popular',
            callback_data='Popular'),
        InlineKeyboardButton(
            f'{CHECKED if last_clicked == "Unanswered" else UNCHECKED} \
Unanswered', callback_data='Unanswered'),
        InlineKeyboardButton('Category - Tech', callback_data='Category'),
        InlineKeyboardButton('Timeframe - Today', callback_data='Timeframe'))
    bot.send_message(message.chat.id, 'Browse Questions',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in [
    'Popular', 'Unanswered', 'Category', 'Timeframe'])
def callback_query(call):
    session = SessionLocal()
    states = session.query(State).filter_by(
        user_id=call.message.chat.id).first()
    if call.data == 'Popular':
        states.question_type = 'Popular'
    elif call.data == 'Unanswered':
        states.question_type = 'Unanswered'
    elif call.data == 'Category':
        states.category = 'Tech'
    elif call.data == 'Timeframe':
        states.timeframe = 'Today'
    session.commit()
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(
        InlineKeyboardButton(
            f'{CHECKED if states.question_type == "Popular" else UNCHECKED} \
  Popular', callback_data='Popular'),
        InlineKeyboardButton(
            f'{CHECKED if states.question_type == "Unanswered" else UNCHECKED}\
  Unanswered', callback_data='Unanswered'),
        InlineKeyboardButton('Category - Tech', callback_data='Category'),
        InlineKeyboardButton('Timeframe - Today', callback_data='Timeframe'))
    bot.edit_message_text('Browse Questions', call.message.chat.id,
                          call.message.message_id, reply_markup=keyboard)
