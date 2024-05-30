from sqlalchemy import select
from main_bot import bot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from telebot.util import quick_markup
from models.engine.storage import SessionLocal
from models.user import User
from models.states import State
from models.question import Question
# from models.admin_message import AdminMessage
from telebot.types import Message, Chat
import os
from handlers.answer_to import answer_callback
from handlers.browse_anwers import browse_callback
from models.answer import Answer

ADMIN_CHANNEL_ID = os.getenv('ADMIN_CHANNEL_ID')
PUBLIC_CHANNEL_ID = os.getenv('PUBLIC_CHANNEL_ID')

name = 'Anonymous'
first_name = 'Anonymous'
last_name = 'Anonymous'

bot = bot.bot


@bot.message_handler(func=lambda message: message.text == 'Cancel')
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    global name, first_name, last_name
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=message.chat.id).first()
    if not user:
        print("dateYY", message.date)
        new_user = User(telegram_id=message.chat.id,
                        username=message.from_user.username,
                        first_name=first_name,
                        last_name=last_name,
                        name=name,
                        date_joined=message.date)
        session.add(new_user)
        session.commit()
        session.close()
    else:
        session.close()
    if message.text.startswith('/start answer_'):
        answer_callback(message)
        return
    elif message.text.startswith('/start browse_'):
        browse_callback(message)
        return
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


def handle_question(message):
    user_question = message.text

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
        bot.register_next_step_handler(
            message, lambda message: handle_category(
             message, user_question
            ))


def handle_category(message, question):
    global name
    print('in handle category', question)

    if message.text == 'Cancel':
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id,
                              text="Select an option")
        return

    user_question = question
    question_category = message.text

    bot.send_message(message.chat.id, "preview your question and press submit \
once you are done")

    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(InlineKeyboardButton('Edit Question',
                                      callback_data='Edit Question'),
                 InlineKeyboardButton(
                     'Cancel',
                     callback_data=f"Cancelled_{message.message_id}_{question_category}_{user_question}"),
                 InlineKeyboardButton('Submit',
                                      callback_data=f"Submitted_{user_question}_{question_category}"))
    print("the question was", message.message_id,
          user_question, question_category)

    bot.send_message(message.chat.id, f"#{question_category}\n\n{user_question}\n\nBy: \
{name}\n ``` Status: previewing```",
                     parse_mode="Markdown", reply_markup=keyboard)


# submit question callback handler
@bot.callback_query_handler(func=lambda call: call.data.startswith('Submitted_'))
def handle_submit_question(call):
    print("in handle submit",
          call.data)
    global name
    query = call.data.split('_')
    question = query[1]
    category = query[2]

    session = SessionLocal()
    try:
        new_question = Question(
            user_id=call.from_user.id,
            question_id=call.message.message_id,
            question=question,
            category=category,
            status="pending",
            name=name,
            username=call.from_user.username
        )

        admin_keyboard = create_admin_keyboard(new_question.question_id)
        admin_msg = bot.send_message(ADMIN_CHANNEL_ID,
                                     f"#{category}\n\n{question}\
        \n\nBy: {name}\n ``` Status: {new_question.status}```",
                                     reply_markup=admin_keyboard,
                                     parse_mode="Markdown")
        new_question.admin_message_id = admin_msg.message_id
        # new_admin_message = AdminMessage(
        #     user_message_id=new_question.message_id,
        #     admin_message_id=admin_message.message_id
        # )
        # session.add(new_admin_message)
        session.add(new_question)
        session.commit()
        bot.send_message(call.message.chat.id, "Submitted")
        send_welcome(call.message)

    except Exception as e:
        session.rollback()
        print(e)
    finally:
        keyboard = InlineKeyboardMarkup()
        keyboard.row_width = 2
        keyboard.add(
            InlineKeyboardButton(
                'Cancel',
                callback_data=f"Cancelled_{call.message.message_id}_{category}_{question}_{admin_msg.message_id}"))
        bot.answer_callback_query(
            call.id,
            "Your question has been submitted for approval! it will be \
reviewed by our team and published shortly",
            show_alert=True)

        #
        session = SessionLocal()

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f"#{category}\n\n{question}\
        \n\nBy: {name}\n ``` Status: {'pending'}```",
                              parse_mode="Markdown", reply_markup=keyboard)

        session.close()


# edit question callback handler
@bot.callback_query_handler(func=lambda call: call.data == 'Edit Question')
def handle_edit_question(call):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Enter your question again")
    bot.register_next_step_handler(call.message, handle_question)


@bot.callback_query_handler(func=lambda call: call.data.startswith('Cancelled_'))
def handle_cancelled(call):
    global name
    message_id = call.data.split('_')[1]
    category = call.data.split('_')[2]
    question = call.data.split('_')[3]
    admin_msg = call.data.split('_')[4]

    print('the fours', message_id, category, question, admin_msg)
    # keyboard = InlineKeyboardMarkup()
    # keyboard.row_width = 2
    # keyboard.add(
    #     InlineKeyboardButton('Resubmit',
    #                          callback_data=f"Resubmitted_{message_id}"))

    try:
        session = SessionLocal()
        questionary = session.query(Question).get(message_id)
        # questionary = session.query(Question).\
        #     filter_by(question_id=call.message.message_id).first()
        if questionary and questionary.status == "pending" and \
           questionary.user_id == call.from_user.id:

            questionary.status = "cancelled"
            session.commit()
            print("deleting from admin channel")
            bot.delete_message(ADMIN_CHANNEL_ID, admin_msg)
            print("deleted from admin")
        else:
            new_question = Question(
                question_id=message_id,
                user_id=call.from_user.id,
                question=question,
                category=category,
                status="cancelled",
                username=call.from_user.username,
                name=name
            )
            session.add(new_question)

        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        keyboard = InlineKeyboardMarkup()
        keyboard.row_width = 2
        keyboard.add(
            InlineKeyboardButton('Resubmit',
                                 callback_data=f"Resubmitted_{message_id}"))

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f"#{category}\n\n{question}\
        \n\nBy: {name}\n ``` Status: Cancelled```",
                              parse_mode="Markdown", reply_markup=keyboard)

        bot.send_message(call.message.chat.id, "Cancelled")
        session.close()


# when resubmitted
@bot.callback_query_handler(func=lambda call: call.data.startswith('Resubmitted_'))
def handle_resubmitted(call):
    global name
    question_id = call.data.split('_')[-1]
    print(question_id)
    session = SessionLocal()
    try:
        question = session.query(Question).get(question_id)
        if not question:
            bot.answer_callback_query(call.id, "Question not found")
        question.status = 'pending'
        session.commit()
        admin_keyboard = create_admin_keyboard(question_id)
        admin_msg = bot.send_message(ADMIN_CHANNEL_ID,
                                     f"#{question.category}\n\n{question.question}\
        \n\nBy: {name}\n ``` Status: {question.status}```",
                                     reply_markup=admin_keyboard,
                                     parse_mode="Markdown")
        question.admin_message_id = admin_msg.message_id
        session.commit()

        keyboard = InlineKeyboardMarkup()
        keyboard.row_width = 2
        keyboard.add(
            InlineKeyboardButton(
                'Cancel',
                callback_data=f"Cancelled_{question_id}_{question.category}_{question.question}_{admin_msg.message_id}"))
        bot.answer_callback_query(
            call.id,
            "Your question has been Resubmitted for approval! it will be \
reviewed by our team and published shortly",
            show_alert=True)
        print("passed to delete if cancalled id: ", question.admin_message_id)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f"#{question.category}\n\n{question.question}\
        \n\nBy: {name}\n ``` Status: {question.status}```",
                              parse_mode="Markdown", reply_markup=keyboard)

    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('approve'))
def handle_admin_action(call):
    global name
    session = SessionLocal()
    try:
        question_id = int(call.data.split('_')[-1])
        print("if call starts with approve: ", question_id)
        question = session.query(Question).get(question_id)
        if not question:
            bot.answer_callback_query(call.id, "Question not found")
        if call.data.startswith('approve'):

            question.status = 'approved'

            user_keyboard = create_answer_keyboard(question.question_id)
            name = question.name
            bot.send_message(PUBLIC_CHANNEL_ID,
                             f"#{question.category}\n\n{question.question}\
            \n\nBy: {name}", reply_markup=user_keyboard)

            bot.send_message(
                chat_id=question.user_id,
                text=f"#{question.category}\n\n{question.question}\
                \n\nBy: {name}\n ``` Status: {question.status}```\
                ",
                reply_to_message_id=question.question_id,
                reply_markup=user_keyboard,
                parse_mode="Markdown")

            bot.edit_message_text(
                chat_id=question.user_id,
                message_id=question.question_id,
                text=f"#{question.category}\n\n{question.question}\
                \n\nBy: {name}\n ``` Status: {question.status}```\
                ",
                parse_mode="Markdown")

            keyboard = InlineKeyboardMarkup()
            keyboard.row_width = 2
            keyboard.add(InlineKeyboardButton('Reject',
                                              callback_data='Reject'))

            bot.edit_message_text(chat_id=ADMIN_CHANNEL_ID,
                                  message_id=question.admin_message_id,
                                  text=f"#{question.category}\n\n{question.question}\
            \n\nBy: {name}\n ``` Status: {question.status}```",
                                  parse_mode="Markdown", reply_markup=keyboard)

            session.commit()

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
    global name
    session = SessionLocal()
    try:
        question_id = int(call.data.split('_')[-1])
        print("from call data: ", question_id)
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
            \n\nBy: {name}\n ``` Status: {question.status}```",
                              parse_mode="Markdown")
        bot.edit_message_text(chat_id=ADMIN_CHANNEL_ID,
                              message_id=question.admin_message_id,
                              text=f"#{question.category}\n\n{question.question}\
        \n\nBy: {name}\n ``` Status: {question.status}```",
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


def create_answer_keyboard(question_id):
    session = SessionLocal()
    answer_count = 4
    session.close()
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    answer_button = InlineKeyboardButton(
        "Answer",
        url=f"https://t.me/{bot.get_me().username}?start=answer_{question_id}"
        )
    browse_button = InlineKeyboardButton(
        f"Browse {answer_count}",
        url=f"https://t.me/{bot.get_me().username}?start=browse_{question_id}"
    )
    keyboard.add(answer_button, browse_button)
    return keyboard


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
