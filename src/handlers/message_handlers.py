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
from models.asked import Asked
from hashlib import sha256

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
                        name=name
                        )
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
    keyboard.add(KeyboardButton('📝 Ask a question'),
                 KeyboardButton('🔍 Search questions'),
                 KeyboardButton('🙋‍♂️Browse Questions'),
                 KeyboardButton('📈 Trending Answers'),
                 KeyboardButton('👤 Profile'),
                 KeyboardButton('🏆 Leaderboard'),
                 KeyboardButton('➡️ More'))

    bot.send_message(message.chat.id, "Select an option",
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == '📝 Ask a question')
def handle_ask_question(message):
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True)
    keyboard.resize_keyboard = True
    keyboard.row_width = 1
    keyboard.add(KeyboardButton('❌ Cancel'))

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
                 KeyboardButton('Entertainment'),
                 KeyboardButton('Food'),
                 KeyboardButton('Sport'),
                 KeyboardButton('Art'),
                 KeyboardButton('Religion'),
                 KeyboardButton('Philosophy'),
                 KeyboardButton('Music'),
                 KeyboardButton('Society'),
                 KeyboardButton('Personal'),
                 KeyboardButton('Family'),
                 KeyboardButton('Other'),
                 KeyboardButton('🔙 Back'),
                 KeyboardButton('❌ Cancel'))

    if message.text == '❌ Cancel' or message.text == '/start' or \
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

    if message.text == '❌ Cancel':
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id,
                              text="Select an option")
        return

    bot.send_message(message.chat.id, "preview your question and press submit \
once you are done")

    session = SessionLocal()
    print("to asked :", question, message.text)
    asked_query = Asked(user_question=question,
                        question_id=message.message_id,
                        question_category=message.text)
    session.add(asked_query)
    asked_query_id = asked_query.question_id
    session.commit()

    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(InlineKeyboardButton('Edit Question',
                                      callback_data='Edit Question'),
                 InlineKeyboardButton(
                     'Cancel',
                     callback_data=f"Cancelled_{asked_query_id}"),
                 InlineKeyboardButton(
                     'Submit',
                     callback_data=f"Submitted_{asked_query_id}"))

    bot_msg = bot.send_message(message.chat.id, f"#{asked_query.question_category}\n\n\
{asked_query.user_question}\n\nBy: {name}\n ``` Status: previewing```",
                               parse_mode="Markdown", reply_markup=keyboard)
    asked_query.preview_message_id = bot_msg.message_id
    session.commit()
    send_welcome(message)
    session.close()


# submit question callback handler
@bot.callback_query_handler(func=lambda call: call.data.startswith('Submitted_'))
def handle_submit_question(call):
    global name
    asked_query_id = call.data.split('_')[-1]
    session = SessionLocal()
    asked_query = session.query(Asked).filter_by(question_id=asked_query_id).first()
    session.close()

    if asked_query is not None:
        question_id = asked_query.question_id
        question = asked_query.user_question
        category = asked_query.question_category
    session = SessionLocal()
    try:
        new_question = Question(
            user_id=call.from_user.id,
            question_id=question_id,
            question=question[:10],
            category=category,
            status="pending",
            name=name,
            username=call.from_user.username
        )

        admin_keyboard = create_admin_keyboard(question_id)
        admin_msg = bot.send_message(ADMIN_CHANNEL_ID,
                                     f"#{category}\n\n{question}\
        \n\nBy: {name}\n ``` Status: {new_question.status}```",
                                     reply_markup=admin_keyboard,
                                     parse_mode="Markdown")
        new_question.admin_message_id = admin_msg.message_id
        session.add(new_question)
        session.commit()
        bot.send_message(call.message.chat.id, "Submitted",
                         reply_to_message_id=asked_query.preview_message_id)
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
                callback_data=f"Cancelled_{admin_msg.message_id}_{asked_query_id}"))
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
    asked_query_id = call.data.split('_')[-1]
    session = SessionLocal()
    asked_query = session.query(Asked).filter_by(question_id=asked_query_id).first()

    if asked_query is not None:
        print("call.data before splitting: ", call.data)
        question = asked_query.user_question
        category = asked_query.question_category

        try:
            session = SessionLocal()
            questionary = session.query(Question).\
                filter_by(question_id=asked_query_id).first()

            if questionary and questionary.status == "pending" and \
               questionary.user_id == call.from_user.id:

                questionary.status = "cancelled"
                print("deleting from admin channel id was :", questionary.admin_message_id)
                bot.delete_message(ADMIN_CHANNEL_ID, questionary.admin_message_id)
                questionary.admin_message_id = None
                session.commit()
                print("deleted from admin msg id: ", questionary.admin_message_id)
            else:
                new_question = Question(
                    user_id=call.from_user.id,
                    question_id=asked_query_id,
                    question=question[:10],
                    category=category,
                    status="cancelled",
                    name=name,
                    username=call.from_user.username
                    )
                session.add(new_question)
                session.commit()

        except Exception as e:
            print(e)
        finally:
            keyboard = InlineKeyboardMarkup()
            keyboard.row_width = 2
            keyboard.add(
                InlineKeyboardButton(
                    'Resubmit',
                    callback_data=f"Resubmitted_{asked_query_id}"))

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f"#{category}\n\n{question}\
        \n\nBy: {name}\n ``` Status: Cancelled```",
                          parse_mode="Markdown", reply_markup=keyboard)

    bot.send_message(call.message.chat.id, "Cancelled",
                     reply_to_message_id=asked_query.preview_message_id)
    session.close()


# when resubmitted
@bot.callback_query_handler(func=lambda call: call.data.startswith('Resubmitted_'))
def handle_resubmitted(call):
    global name
    asked_query_id = call.data.split('_')[-1]
    session = SessionLocal()
    asked_query = session.query(Asked).filter_by(question_id=asked_query_id).first()

    if asked_query is not None:
        question_id = asked_query.question_id
        question = asked_query.user_question
    try:
        session = SessionLocal()
        print("from resubmitted: from cancelled", question_id, asked_query_id)
        question = session.query(Question).get(question_id)
        if not question:
            bot.answer_callback_query(call.id, "Question not found")
        question.status = 'pending'
        admin_keyboard = create_admin_keyboard(question_id)
        admin_msg = bot.send_message(ADMIN_CHANNEL_ID,
                                     f"#{asked_query.question_category}\n\n{asked_query.user_question}\
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
                callback_data=f"Cancelled_{admin_msg.message_id}_{asked_query_id}"))
        bot.answer_callback_query(
            call.id,
            "Your question has been Resubmitted for approval! it will be \
reviewed by our team and published shortly",
            show_alert=True)
        bot.send_message(call.message.chat.id, "Resubmitted",
                         reply_to_message_id=asked_query.preview_message_id)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f"#{asked_query.question_category}\n\n{asked_query.user_question}\
        \n\nBy: {name}\n ``` Status: {question.status}```",
                              parse_mode="Markdown", reply_markup=keyboard)

    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def handle_admin_action(call):
    global name
    session = SessionLocal()
    try:
        if len(call.data.split('_')) == 3:
            question_id = int(call.data.split('_')[1])
        else:
            question_id = int(call.data.split('_')[-1])
        print("if call starts with approve: ", question_id)
        question = session.query(Question).get(question_id)
        asked_query = session.query(Asked).filter_by(question_id=question_id).first()
        if not question:
            bot.answer_callback_query(call.id, "Question not found")
        if call.data.startswith('approve'):

            question.status = 'approved'

            user_keyboard = create_answer_keyboard(question.question_id)
            name = question.name
            public_msg = bot.send_message(PUBLIC_CHANNEL_ID,
                                          f"#{asked_query.question_category}\n\n{asked_query.user_question}\
            \n\nBy: {name}", reply_markup=user_keyboard)

            question.public_message_id = public_msg.message_id
            session.commit()

            notify = bot.send_message(
                chat_id=question.user_id,
                text=f"#{asked_query.question_category}\n\n{asked_query.user_question}\
                \n\nBy: {name}\n ``` Status: {question.status}```\
                ",
                reply_to_message_id=asked_query.preview_message_id,
                reply_markup=user_keyboard,
                parse_mode="Markdown")

            bot.edit_message_text(
                chat_id=question.user_id,
                message_id=asked_query.preview_message_id,
                text=f"#{question.category}\n\n{question.question}\
                \n\nBy: {name}\n ``` Status: {question.status}```\
                ",
                parse_mode="Markdown")

            keyboard = InlineKeyboardMarkup()
            keyboard.row_width = 2
            keyboard.add(InlineKeyboardButton(
                'Reject',
                callback_data=f"reject_{question_id}_{public_msg.message_id}"))

            bot.edit_message_text(chat_id=ADMIN_CHANNEL_ID,
                                  message_id=question.admin_message_id,
                                  text=f"#{asked_query.question_category}\n\n{asked_query.user_question}\
            \n\nBy: {name}\n ``` Status: {question.status}```",
                                  parse_mode="Markdown", reply_markup=keyboard)

        session.commit()
        print("after commit: ", question.public_message_id)
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_'))
def handle_reject(call):
    global name
    print("before splitting reject data :", call.data)
    if len(call.data.split('_')) == 3:
        question_id = int(call.data.split('_')[1])
        public_msg_id = int(call.data.split('_')[2])
    else:
        question_id = int(call.data.split('_')[1])
        public_msg_id = None
    print("from call data with reject : ", question_id, public_msg_id)

    session = SessionLocal()
    try:
        args = call.data.split('_')
        if len(args) == 3:
            question_id = int(args[1])
            public_msg_id = int(args[2])
        else:
            question_id = int(args[1])
            public_msg_id = None
        print("from call data with reject : ", question_id, public_msg_id)
        question = session.query(Question).get(question_id)
        asked_query = session.query(Asked).filter_by(question_id=question_id).first()
        if not question:
            bot.answer_callback_query(call.id, "Question not found")
        question.status = 'rejected'
        session.commit()
        keyboard = InlineKeyboardMarkup()
        keyboard.row_width = 2
        keyboard.add(InlineKeyboardButton('Approve',
                                          callback_data=f"approve_{question_id}_{question.public_message_id}"))
        bot.send_message(question.user_id,
                         "Your question has been rejected",
                         reply_to_message_id=asked_query.preview_message_id)
        bot.edit_message_text(chat_id=question.user_id,
                              message_id=asked_query.preview_message_id,
                              text=f"#{question.category}\n\n{question.question}\
            \n\nBy: {name}\n ``` Status: {question.status}```",
                              parse_mode="Markdown")
        bot.edit_message_text(chat_id=ADMIN_CHANNEL_ID,
                              message_id=question.admin_message_id,
                              text=f"#{asked_query.question_category}\n\n{asked_query.user_question}\
        \n\nBy: {name}\n ``` Status: {question.status}```",
                              parse_mode="Markdown", reply_markup=keyboard)
        bot.delete_message(PUBLIC_CHANNEL_ID, public_msg_id)
        question.public_message_id = None
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
