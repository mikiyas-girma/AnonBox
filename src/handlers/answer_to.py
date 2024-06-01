from main_bot import bot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from models.engine.storage import SessionLocal
from models.question import Question
from models.answer import Answer
from models.asked import Asked

name = 'Anonymous'
first_name = 'Anonymous'
last_name = 'Anonymous'

bot = bot.bot


def answer_callback(message):
    global name

    if message.text.startswith('/start answer_'):
        keyboard = ReplyKeyboardMarkup(one_time_keyboard=True)
        keyboard.resize_keyboard = True
        keyboard.row_width = 1
        keyboard.add(KeyboardButton('Cancel'))
        question_id = int(message.text.split('_')[-1])
        # print(question_id)
        session = SessionLocal()
        try:
            question = session.query(Question).get(question_id)
            asked_query = session.query(Asked).filter_by(
                question_id=question_id).first()
            if question:
                kbd = InlineKeyboardMarkup()
                kbd.row_width = 2
                kbd.add(InlineKeyboardButton(
                    'Browse (5)',
                    url=f"https://t.me/{bot.get_me().username}?start=browse_{question_id}"),
                        InlineKeyboardButton(
                            'Subscribe', callback_data='subscribe'))
                the_question = bot.send_message(
                    chat_id=message.chat.id,
                    text=f"#{asked_query.question_category}\n\n{asked_query.user_question}\
            \n\nBy: {name}\n ``` Status: {question.status}```",
                    reply_markup=kbd,
                    parse_mode="Markdown")
                msg = bot.reply_to(
                    the_question,
                    text="Send me your answer  ``` Note that you can send your\
 answers through voice messages, images, videos, and documents```",
                    parse_mode='Markdown',
                    reply_markup=keyboard)

                bot.register_next_step_handler(msg, process_answer,
                                               question_id)
            else:
                bot.reply_to(message, "Question not found")
        except Exception as e:
            bot.reply_to(message, "An error occurred")
            print(e)
        finally:
            session.close()


def process_answer(message, question_id):
    global name

    if message.text.startswith('/start answer_'):
        answer_callback(message)
        return
    elif message.text.startswith('/start browse_'):
        from handlers.browse_anwers import browse_callback
        browse_callback(message)
        return
    else:
        if message.text == 'Cancel':
            from handlers.message_handlers import send_welcome
            send_welcome(message)
            return

    answer = message.text
    session = SessionLocal()
    try:
        new_answer = Answer(
            answer_id=message.message_id,
            question_id=question_id,
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id,
            answer=answer,
            status='draft',
            reply_to=None,
            reputation=0,
        )
        anw_keyboard = create_answer_keyboard(answer_id=new_answer.answer_id)

        session.add(new_answer)
        session.commit()
        sent_message = bot.send_message(message.chat.id,
                                        f"{new_answer.answer}\n\nBy: {name}",
                                        reply_markup=anw_keyboard)
        new_answer.tg_msg_id = sent_message.message_id
        session.commit()
        bot.register_next_step_handler(
            message, process_post_answer,
            new_answer.answer_id, message.message_id)
        from handlers.message_handlers import send_welcome
        send_welcome(message=message)
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
def edit_answer(call):
    answer_id = int(call.data.split('_')[-1])
    cancel_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True)
    cancel_keyboard.resize_keyboard = True
    cancel_keyboard.row_width = 1
    cancel_keyboard.add(KeyboardButton('Cancel'))
    bot.send_message(
        chat_id=call.message.chat.id,
        text="Send me your edit.. \n ``` Note that you can send your edit \
through voice messages, images, videos, and documents```",
        reply_markup=cancel_keyboard,
        parse_mode='Markdown')
    bot.register_next_step_handler(call.message, process_edit_answer,
                                   answer_id, call.message.message_id)


def process_edit_answer(message, answer_id, original_message_id):
    global name
    if message.text == 'Cancel':
        from handlers.message_handlers import send_welcome
        send_welcome(message)
        return
    answer_id = int(answer_id)
    session = SessionLocal()
    try:
        answer = session.query(Answer).get(answer_id)
        answer.answer = message.text
        answer.status = 'draft'
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session = SessionLocal()
        answer_data = session.query(Answer)\
            .filter_by(answer_id=answer_id).first()
        answer_data.status = 'draft'
        answer_data.answer = message.text
        answer_data.username = name
        anw_keyboard = create_answer_keyboard(answer_id=answer_id)
        bot.send_message(
            chat_id=message.chat.id,
            text="Preview your edit and click on post to save changes",
        )
        bot.send_message(
            chat_id=message.chat.id,
            text=f"{answer_data.answer}\n\nBy: {name}",
            reply_markup=anw_keyboard
        )
        # bot.edit_message_text(
        #     chat_id=message.chat.id,
        #     message_id=original_message_id,
        #     text=f"{answer_data.answer}\n\nBy: {username}"
        # )
        # bot.edit_message_reply_markup(
        #     chat_id=message.chat.id,
        #     message_id=original_message_id,
        #     reply_markup=anw_keyboard
        # )
        bot.delete_message(chat_id=message.chat.id,
                           message_id=original_message_id)

        session.commit()
        session.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('post_'))
def post_answer(call):
    answer_id = int(call.data.split('_')[-1])
    session = SessionLocal()
    try:
        answer = session.query(Answer).get(answer_id)
        answer.status = 'posted'
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        session.close()


def process_post_answer(message, answer_id, original_message_id):
    session = SessionLocal()
    try:
        answer = session.query(Answer).get(answer_id)
        answer.status = 'posted'
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session.close()
        bot.delete_message(chat_id=message.chat.id,
                           message_id=original_message_id)
        from handlers.message_handlers import send_welcome
        send_welcome(message)


@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_callback(call):
    bot.delete_message(chat_id=call.message.chat.id,
                       message_id=call.message.message_id)
    from handlers.message_handlers import send_welcome
    send_welcome(call.message)


def create_answer_keyboard(answer_id):
    anw_keyboard = InlineKeyboardMarkup()
    anw_keyboard.row_width = 2
    anw_keyboard.add(InlineKeyboardButton(
        'Edit', callback_data=f'edit_{answer_id}'),
        InlineKeyboardButton(
        'Notify Settings', callback_data='notify'),
        InlineKeyboardButton(
        'Cancel', callback_data=f'cancel_{answer_id}'),
        InlineKeyboardButton(
        'Post', callback_data=f'post_{answer_id}')
        )
    return anw_keyboard
