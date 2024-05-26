from sqlalchemy import select
from main_bot import bot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from models.engine.storage import SessionLocal
from models.user import User
from models.states import State
from models.question import Question
from models.admin_message import AdminMessage
from telebot.types import Message, Chat
import os

ADMIN_CHANNEL_ID = os.getenv('ADMIN_CHANNEL_ID')
PUBLIC_CHANNEL_ID = os.getenv('PUBLIC_CHANNEL_ID')


@bot.message_handler(func=lambda message: message.text == 'Cancel')
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    session = SessionLocal()
    states = session.query(State).filter_by(user_id=message.chat.id).first()
    if not states:
        new_state = State(user_id=message.chat.id,
                          question_type='Popular',
                          category='All',
                          timeframe='Today')
        session.add(new_state)
        session.commit()
        session.close()
    else:
        session.close()
    keyboard = ReplyKeyboardMarkup()
    keyboard.resize_keyboard = True
    keyboard.row_width = 2
    keyboard.add(KeyboardButton('Ask a question'),
                 KeyboardButton('Search questions'),
                 KeyboardButton('Browse Questions'),
                 KeyboardButton('Trending Answers'),
                 KeyboardButton('Profile'),
                 KeyboardButton('Leaderboard'),
                 KeyboardButton('More'))

    bot.send_message(message.chat.id, "Select an option",
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Ask a question')
def handle_ask_question(message):
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True)
    keyboard.resize_keyboard = True
    keyboard.row_width = 1
    keyboard.add(KeyboardButton('Cancel'))

    bot.send_message(
        message.chat.id,
        "Send me your question  ``` Note that you can send your questions \
through voice messages, images, videos, and documents```",
        parse_mode="Markdown", reply_markup=keyboard)

    bot.register_next_step_handler(message, handle_question)


question = None
category = None


def handle_question(message):

    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True)
    # keyboard.resize_keyboard = True
    keyboard.row_width = 2
    keyboard.add(KeyboardButton('Technology'),
                 KeyboardButton('Relationship'),
                 KeyboardButton('Health'),
                 KeyboardButton('Business'),
                 KeyboardButton('Education'),
                 KeyboardButton('Politics'),
                 KeyboardButton('Science'),
                 KeyboardButton('Cancel'),
                 KeyboardButton('Other'))

    if message.text == 'Cancel' or message.text == '/start' or \
       message.text == '/hello':
        return send_welcome(message)
    else:
        bot.send_message(message.chat.id, "Choose a category for your question\
``` if you don't see a category that fits your question, \
choose 'Other' option```",
                         parse_mode="Markdown", reply_markup=keyboard)
        global question
        question = message.text

        bot.register_next_step_handler(message, handle_category, question)
        bot.register_next_step_handler(message, send_welcome)


def handle_category(message, question):
    if message.text == 'Cancel':
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id,
                              text="Select an option")
        return
    global category
    category = message.text

    bot.send_message(message.chat.id, "preview your question and press submit \
once you are done")

    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(InlineKeyboardButton('Edit Question',
                                      callback_data='Edit Question'),
                 InlineKeyboardButton('Cancel', callback_data='Cancelled'),
                 InlineKeyboardButton('Submit', callback_data='Submitted'))

    bot.send_message(message.chat.id, f"#{category}\n\n{question}\n\nBy: \
{message.from_user.username}\n ``` Status: previewing```",
                     parse_mode="Markdown", reply_markup=keyboard)


# edit question callback handler
@bot.callback_query_handler(func=lambda call: call.data == 'Edit Question')
def handle_edit_question(call):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Enter your question again")
    bot.register_next_step_handler(call.message, handle_question)


# submit question callback handler
@bot.callback_query_handler(func=lambda call: call.data == 'Submitted')
def handle_submit_question(call):
    global question, category

    session = SessionLocal()
    try:
        new_question = Question(
            user_id=call.from_user.id,
            question_id=call.message.message_id,
            chat_id=call.message.chat.id,
            question=question,
            category=category,
            status="pending",
            username=call.from_user.username
        )
        admin_keyboard = create_admin_keyboard(new_question.question_id)
        admin_message = bot.send_message(ADMIN_CHANNEL_ID, text=f"#{category}\n\n{question}\
        \n\nBy: {call.from_user.username}\n ``` Status: {new_question.status}```",
                                         reply_markup=admin_keyboard,
                                         parse_mode="Markdown")
        new_question.admin_message_id = admin_message.message_id
        # new_admin_message = AdminMessage(
        #     user_message_id=new_question.message_id,
        #     admin_message_id=admin_message.message_id
        # )
        # session.add(new_admin_message)
        session.add(new_question)
        session.commit()
        bot.send_message(call.message.chat.id, call.data)

    except Exception as e:
        session.rollback()
        print(e)
    finally:
        keyboard = InlineKeyboardMarkup()
        keyboard.row_width = 2
        keyboard.add(InlineKeyboardButton('Cancel', callback_data='Cancelled'))
        bot.answer_callback_query(
            call.id,
            "Your question has been submitted for approval! it will be \
reviewed by our team and published shortly",
            show_alert=True)

        # Fetch category, question, and username from the database
        session = SessionLocal()
        question_data = session.query(Question).filter_by(
            question_id=call.message.message_id).first()
        category = question_data.category
        question = question_data.question
        username = question_data.username
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f"#{category}\n\n{question}\
        \n\nBy: {username}\n ``` Status: {question_data.status}```",
                              parse_mode="Markdown", reply_markup=keyboard)

        session.close()


@bot.callback_query_handler(func=lambda call: call.data == 'Resubmitted')
def handle_resubmitted(call):
    session = SessionLocal()
    stmt = select(Question).where(
        Question.question_id == call.message.message_id)
    qst = session.scalars(stmt).one()
    qst.status = "pending"
    session.commit()
    message_id = call.message.message_id
    admin_keyboard = create_admin_keyboard(message_id)
    admin_message = bot.send_message(ADMIN_CHANNEL_ID, text=f"#{qst.category}\n\n{qst.question}\
    \n\nBy: {call.from_user.username}\n ``` Status: {qst.status}```",
                                     reply_markup=admin_keyboard,
                                     parse_mode="Markdown")
    qst.admin_message_id = admin_message.message_id
    # new_admin_message = AdminMessage(
    #     user_message_id=message_id,
    #     admin_message_id=admin_message.message_id
    # )
    # session.add(new_admin_message)
    session.commit()
    bot.answer_callback_query(
        call.id,
        "Your question has been resubmitted for approval! it will be \
reviewed by our team and published shortly",
        show_alert=True)
    bot.send_message(call.message.chat.id, call.data)
    question_data = session.query(Question).filter_by(
        question_id=call.message.message_id).first()
    category = question_data.category
    question = question_data.question
    username = question_data.username
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(InlineKeyboardButton('Cancel', callback_data='Cancelled'))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f"#{category}\n\n{question}\
    \n\nBy: {username}\n ``` Status: {'pending'}```",
                          parse_mode="Markdown", reply_markup=keyboard)
    session.close()


@bot.callback_query_handler(func=lambda call: call.data == 'Cancelled')
def handle_cancelled(call):
    global question, category
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(InlineKeyboardButton('Resubmit', callback_data='Resubmitted'))

    try:
        session = SessionLocal()
        questionary = session.query(Question).get(call.message.message_id)
        # questionary = session.query(Question).\
        #     filter_by(question_id=call.message.message_id).first()
        if questionary and questionary.status == "pending" and \
           questionary.user_id == call.from_user.id:

            questionary.status = "cancelled"
            category = questionary.category
            question = questionary.question
            session.commit()
            if questionary.admin_message_id:
                bot.delete_message(ADMIN_CHANNEL_ID,
                                   questionary.admin_message_id)
        else:
            new_question = Question(
                question_id=call.message.message_id,
                user_id=call.from_user.id,
                question=question,
                category=category,
                status="cancelled",
                username=call.from_user.username
            )
            category = new_question.category
            question = new_question.question
            session.add(new_question)

        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f"#{category}\n\n{question}\
        \n\nBy: {call.from_user.username}\n ``` Status: Cancelled```",
                              parse_mode="Markdown", reply_markup=keyboard)

        bot.send_message(call.message.chat.id, "Cancelled")
        session.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('approve'))
def handle_admin_action(call):
    session = SessionLocal()
    try:
        question_id = int(call.data.split('_')[-1])
        print(question_id)
        question = session.query(Question).get(question_id)
        if not question:
            bot.answer_callback_query(call.id, "Question not found")
        if call.data.startswith('approve'):

            user_keyboard = InlineKeyboardMarkup()
            user_keyboard.row_width = 2
            user_keyboard.add(InlineKeyboardButton(
                            'Answer', callback_data='Answer'),
                         InlineKeyboardButton(
                            'Browse (5)', callback_data='Browse'))
            question.status = 'approved'
            session.commit()
            bot.send_message(PUBLIC_CHANNEL_ID,
                             f"#{question.category}\n\n{question.question}\
            \n\nBy: {question.username}", reply_markup=user_keyboard)

            bot.send_message(
                chat_id=question.user_id,
                text=f"#{question.category}\n\n{question.question}\
                \n\nBy: {question.username}\n ``` Status: {question.status}```\
                ",
                reply_to_message_id=question.question_id,
                reply_markup=user_keyboard,
                parse_mode="Markdown")

            bot.edit_message_text(
                chat_id=question.chat_id,
                message_id=question.question_id,
                text=f"#{question.category}\n\n{question.question}\
                \n\nBy: {question.username}\n ``` Status: {question.status}```\
                ",
                parse_mode="Markdown")

            keyboard = InlineKeyboardMarkup()
            keyboard.row_width = 2
            keyboard.add(InlineKeyboardButton('Reject',
                                              callback_data='Reject'))

            bot.edit_message_text(chat_id=ADMIN_CHANNEL_ID,
                                  message_id=question.admin_message_id,
                                  text=f"#{question.category}\n\n{question.question}\
            \n\nBy: {question.username}\n ``` Status: {question.status}```",
                                  parse_mode="Markdown", reply_markup=keyboard)

        elif call.data.startswith('reject'):
            question.status = 'rejected'
            bot.send_message(question.user_id,
                             "Your question has been rejected")
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('reject'))
def handle_reject(call):
    session = SessionLocal()
    try:
        question_id = int(call.data.split('_')[-1])
        question = session.query(Question).get(question_id)
        if not question:
            bot.answer_callback_query(call.id, "Question not found")
        question.status = 'rejected'
        session.commit()
        keyboard = InlineKeyboardMarkup()
        keyboard.row_width = 2
        keyboard.add(InlineKeyboardButton('Approve',
                                          callback_data='Approve'))
        bot.send_message(question.user_id,
                         "Your question has been rejected",
                         reply_to_message_id=question.question_id)
        bot.edit_message_text(chat_id=question.chat_id,
                              message_id=question.question_id,
                              text=f"#{question.category}\n\n{question.question}\
            \n\nBy: {question.username}\n ``` Status: {question.status}```",
                              parse_mode="Markdown")
        bot.edit_message_text(chat_id=ADMIN_CHANNEL_ID,
                              message_id=question.admin_message_id,
                              text=f"#{question.category}\n\n{question.question}\
        \n\nBy: {question.username}\n ``` Status: {question.status}```",
                              parse_mode="Markdown", reply_markup=keyboard)
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session.close()


def create_admin_keyboard(question_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    approve_button = InlineKeyboardButton(
        "Approve", callback_data=f"approve_{question_id}")
    reject_button = InlineKeyboardButton(
        "Reject", callback_data=f"reject_{question_id}")
    keyboard.add(approve_button, reject_button)
    return keyboard


@bot.message_handler(commands=['register'])
def register(message):
    session = SessionLocal()
    user = session.query(User).\
        filter_by(telegram_id=message.from_user.id).first()

    if user:
        bot.reply_to(message, "You are already registered")
    else:
        new_user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )

        session.add(new_user)
        session.commit()
        bot.reply_to(message, "You have been registered")

    session.close()


@bot.message_handler(commands=['list'])
def list_users(message):
    session = SessionLocal()
    users = session.query(User).all()

    if users:
        users_list = '\n'.join([f" {user.username} - {user.first_name} -"
                                f"{user.last_name}" for user in users])
        bot.reply_to(message, f"Registered users:\n{users_list}")
    else:
        bot.reply_to(message, "No users found")

    session.close()


@bot.message_handler(content_types=['photo'])
def handle_photo_upload(message):
    photo_file_id = message.photo[-1].file_id
    file_info = bot.get_file(photo_file_id)
    bot.send_message(message.chat.id, file_info.file_path)
    bot.send_photo(message.chat.id, photo_file_id,
                   caption="Thank you for uploading photo!")


uploaded_videos = {}


@bot.message_handler(content_types=['video'])
def handle_video_upload(message):
    video_file_id = message.video.file_id
    # bot.send_message(message.chat.id, f"{message.video}\
    #                  thank you for the video")
    bot.send_video(message.chat.id, video_file_id,
                   caption="here is what you sent")
    uploaded_videos[message.chat.id] = video_file_id


@bot.message_handler(commands=['showvideo'])
def show_uploaded_video(message):
    chat_id = message.chat.id
    if chat_id in uploaded_videos:
        video_file_id = uploaded_videos[chat_id]
        bot.send_video(chat_id, video_file_id)
    else:
        bot.send_message(chat_id, "No video was uploaded previously.")
