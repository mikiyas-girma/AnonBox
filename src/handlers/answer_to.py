from main_bot import bot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from models.engine.storage import SessionLocal
from models.user import User
from models.question import Question
from models.states import State
from models.answer import Answer


def answer_callback(message):
    print("Message Object::")
    print(message)
    print(message.text)
    if message.text.startswith('/start answer_'):
        keyboard = ReplyKeyboardMarkup(one_time_keyboard=True)
        keyboard.resize_keyboard = True
        keyboard.row_width = 1
        keyboard.add(KeyboardButton('Cancel'))
        question_id = int(message.text.split('_')[-1])
        print(question_id)
        session = SessionLocal()
        try:
            question = session.query(Question).get(question_id)
            if question:
                print('yes the question is there with id {}'.format(question_id))
                msg = bot.reply_to(message=message,
                                   text="Send me your answer  ``` Note that you can send your answers \
through voice messages, images, videos, and documents```",
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

    if message.text.startswith('/start answer_'):
        answer_callback(message)
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
            chat_id=message.chat.id,
            answer=answer,
            reputation=0,
            username=message.from_user.username
        )
        session.add(new_answer)
        session.commit()
        bot.send_message(message.chat.id, f"{new_answer.answer}\n\nBy: {new_answer.username}")
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session.close()
