from main_bot import bot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from models.engine.storage import SessionLocal
from models.user import User
from sqlalchemy import func
from models.question import Question
from models.answer import Answer
import datetime

name = 'Anonymous'
first_name = 'Anonymous'
last_name = 'Anonymous'

bot = bot.bot


@bot.message_handler(func=lambda message: message.text == '👤 Profile')
def profile(message):
    print('Profile')
    session = SessionLocal()
    user = session.query(User).filter_by(
        telegram_id=message.chat.id).first()
    if not user:
        user = User(
            telegram_id=message.chat.id,
            first_name=first_name,
            last_name=last_name
        )
        session.add(user)
        session.commit()
    else:
        print('User exists')
        name = user.name
        reputation = user.reputation
        # followers = session.query(func.array_length(User.followers, 1)).\
        #     filter_by(telegram_id=message.chat.id).count()
        # following = session.query(func.array_length(User.following, 1)).\
        #     filter_by(telegram_id=message.chat.id).count()
        date_joined = user.date_joined
        num_questions = session.query(Question).filter_by(
            user_id=message.chat.id).count()
        num_answered = session.query(Answer).filter_by(
            user_id=message.chat.id).count()
    session.close()
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Edit Profile', callback_data='Edit'))
    keyboard.row(InlineKeyboardButton('View Questions', callback_data='Questions'),
                 InlineKeyboardButton('View Answers', callback_data='Answers'))
    keyboard.row(InlineKeyboardButton('View Followers', callback_data='Followers'),
                 InlineKeyboardButton('View Following', callback_data='Following'))
    keyboard.add(InlineKeyboardButton('Settings', callback_data='Settings'))

    bot.send_message(message.chat.id,
                     text=f'<b>{name } | {reputation} reps | 1\
 followers | 1 following </b>\n\nAsked {num_questions} Questions,\
 <em>Answered {num_answered} Questions, Joined {date_joined} </em>\
                        \n\n<b>Bio:</b> {user.bio}',
                     parse_mode='HTML',
                     reply_markup=keyboard)
