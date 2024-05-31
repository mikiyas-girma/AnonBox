from main_bot import bot
from telebot.types import (ForceReply, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from models.engine.storage import SessionLocal
from models.user import User
from sqlalchemy import func
from models.question import Question
from models.answer import Answer
from handlers.message_handlers import send_welcome, create_answer_keyboard

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
                     text=f'<b>{name } | {reputation} reps | \
 {followers} followers | {following} following</b>\n\nAsked {num_questions} Questions,\
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
                                      callback_data=f'Questions_{profile_id}'),
                 InlineKeyboardButton('🙋‍♂️ My Answers',
                                      callback_data=f'Answers_{profile_id}'))
    keyboard.row(InlineKeyboardButton('👥 Followers',
                                      callback_data=f'Followers_{profile_id}'),
                 InlineKeyboardButton('👣 Followings',
                                      callback_data=f'Following_{profile_id}'))
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
                                      callback_data='Back_to_Profile'))
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
        profile(message)
        return send_welcome(message)
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
        profile(message)
        return send_welcome(message)
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
            bot.send_message(call.message.chat.id,
                             'Gender updated successfully!')
            profile(call.message)
            return send_welcome(call.message)
        else:
            bot.send_message(
                call.message.chat.id, 'Invalid')
    except Exception as e:
        bot.send_message(
            call.message.chat.id, 'An error occurred. Please try again later.')
        session.close()


@bot.callback_query_handler(func=lambda call: call.data == 'Back_to_Profile')
def back_to_profile(call):
    profile(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('Questions_'))
def my_questions(call):
    user_id = call.data.split('_')[1]
    print('My Questions id: ', user_id)
    session = SessionLocal()
    questions = session.query(Question).filter_by(user_id=user_id).all()
    if not questions:
        bot.send_message(call.message.chat.id, 'No questions found')
        return profile(call.message)
    for question in questions:
        keyboard = None
        if question.status == 'approved':
            keyboard = create_answer_keyboard(question.question_id)
        if question.status == 'pending':
            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton(
                    'Cancel',
                    callback_data=f'Cancelled_{question.question_id}_{question.category}_\
                        {question.question}_{question.admin_message_id}'))
        if question.status == 'cancelled':
            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton(
                    'Resubmit',
                    callback_data=f'Resubmitted_{question.question_id}'))
        bot.answer_callback_query(call.id,
                                  'Your questions',
                                  show_alert=True)
        bot.send_message(call.message.chat.id, f"#{question.category}\
\n\n{question.question}\n\nBy: {name}\n ``` Status: {question.status}```",
                         parse_mode="Markdown", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('Followers_'))
def my_followers(call):
    """
    handler for getting peoples who follows me
    """
    text = '<b>0 Followers </b> \n\n \
------------------------ \n \
You don\'t have any followers yet. \n \
------------------------'
    bot.answer_callback_query(call.id, 'Followers', show_alert=False)
    keyboard = back_keyboard()
    bot.send_message(call.message.chat.id, text,
                     reply_markup=keyboard, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data.startswith('Following_'))
def my_followings(call):
    """
    handler for getting peoples who follows me
    """
    text = '<b>0 Followings </b> \n\n \
------------------------ \n \
You don\'t follow any one yet. \n \
------------------------'
    bot.answer_callback_query(call.id, 'Followings', show_alert=False)
    keyboard = back_keyboard()
    bot.send_message(call.message.chat.id, text,
                     reply_markup=keyboard,
                     parse_mode='HTML')


def back_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('🔙 Back', callback_data='Back_to_Profile'))
    return keyboard
