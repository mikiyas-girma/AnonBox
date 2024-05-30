from main_bot import bot
from telebot.types import (ForceReply, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from models.engine.storage import SessionLocal
from models.user import User
from sqlalchemy import func
from models.question import Question
from models.answer import Answer

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
        followers = session.query(func.array_length(User.followers, 1)).\
            filter_by(telegram_id=message.chat.id).count()
        following = session.query(func.array_length(User.following, 1)).\
            filter_by(telegram_id=message.chat.id).count()
        date_joined = user.date_joined
        num_questions = session.query(Question).filter_by(
            user_id=message.chat.id).count()
        num_answered = session.query(Answer).filter_by(
            user_id=message.chat.id).count()
    session.close()
    keyboard = create_profile_keyboard(user.telegram_id)

    bot.send_message(message.chat.id,
                     text=f'<b>{name } | {reputation} reps | 1\
 followers | {followers} following {following}</b>\n\nAsked {num_questions} Questions,\
 <em>Answered {num_answered} Questions, Joined {date_joined} </em>\
                        \n\n<b>Bio:</b> {user.bio}',
                     parse_mode='HTML',
                     reply_markup=keyboard)


def create_profile_keyboard(profile_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        '📝 Edit Profile',
        callback_data=f'EditProfile_{profile_id}'))
    keyboard.row(InlineKeyboardButton('🤔 My Questions',
                                      callback_data='Questions'),
                 InlineKeyboardButton('🙋‍♂️ My Answers',
                                      callback_data='Answers'))
    keyboard.row(InlineKeyboardButton('👥 Followers',
                                      callback_data='Followers'),
                 InlineKeyboardButton('👣 Followings',
                                      callback_data='Following'))
    keyboard.add(InlineKeyboardButton('⚙️ Settings', callback_data='Settings'))
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith('EditProfile_'))
def edit_profile(call):
    profile_id = call.data.split('_')[1]
    keyboard = create_edit_profile_keyboard(profile_id)
    bot.send_message(call.message.chat.id,
                     'Edit Profile',
                     reply_markup=keyboard)


def create_edit_profile_keyboard(profile_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    keyboard.row(InlineKeyboardButton('Edit Name',
                                      callback_data=f'EditName_{profile_id}'))
    keyboard.row(InlineKeyboardButton('Edit Bio',
                                      callback_data=f'EditBio_{profile_id}'))
    keyboard.row(InlineKeyboardButton('Edit Gender',
                                      callback_data=f'EditGender_{profile_id}'))
    keyboard.row(InlineKeyboardButton('🔙 Back',
                                      callback_data='👤 Profile'))
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith('EditName_'))
def edit_name(call):
    bot.send_message(call.message.chat.id, 'Please enter your new name:',
                     reply_markup=ForceReply(selective=True))
    bot.register_next_step_handler(call.message, process_name_step)


def process_name_step(message):
    name = message.text
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(
            telegram_id=message.chat.id).first()
        user.name = name
        session.commit()
        session.close()
        bot.send_message(message.chat.id, 'Name updated successfully!')
    except Exception as e:
        bot.send_message(
            message.chat.id, 'An error occurred. Please try again later.')
        session.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('EditBio_'))
def edit_bio(call):
    bot.send_message(call.message.chat.id, 'Enter Bio, (max 200 characters)',
                     reply_markup=ForceReply(selective=True))
    bot.register_next_step_handler(call.message, process_bio_step)


def process_bio_step(message):
    bio = message.text
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(
            telegram_id=message.chat.id).first()
        user.bio = bio
        session.commit()
        session.close()
        bot.send_message(message.chat.id, 'Bio updated successfully!')
    except Exception as e:
        bot.send_message(
            message.chat.id, 'An error occurred. Please try again later.')
        session.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('EditGender_'))
def edit_gender(call):
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 3
    keyboard.add(InlineKeyboardButton('None', callback_data='Gender_None'),
                 InlineKeyboardButton('Male', callback_data='Gender_Male'),
                 InlineKeyboardButton('Female', callback_data='Gender_female'))
    bot.edit_message_text('Select your gender',
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('Gender_'))
def handle_gender(call):
    session = SessionLocal()
    try:
        gender = call.data.split('_')[1].lower()
        if gender in ['male', 'female', 'none']:
            user = session.query(User).filter_by(
                telegram_id=call.message.chat.id).first()
            user.gender = gender
            session.commit()
            session.close()
            bot.send_message(call.message.chat.id, 'Gender updated successfully!')
        else:
            bot.send_message(
                call.message.chat.id, 'Invalid')
    except Exception as e:
        bot.send_message(
            call.message.chat.id, 'An error occurred. Please try again later.')
        session.close()
