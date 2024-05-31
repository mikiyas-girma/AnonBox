from main_bot import bot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from models.engine.storage import SessionLocal
from models.question import Question
from models.answer import Answer

bot = bot.bot

username = 'Anonymous'
first_name = 'Anonymous'
last_name = 'Anonymous'


def browse_callback(message):
    global username

    print(message.text)
    if message.text.startswith('/start browse_'):
        question_id = int(message.text.split('_')[-1])
        print("browse this: ", question_id)
        session = SessionLocal()
        try:
            # the question
            question = session.query(Question).get(question_id)
            if question:
                print("Question found")
                print(question.question)
                kbd = InlineKeyboardMarkup()
                kbd.row_width = 4
                kbd.add(InlineKeyboardButton(
                    'Answer',
                    url=f"https://t.me/{bot.get_me().username}?start=answer_{question_id}"),
                        InlineKeyboardButton(
                            'Subscribe', callback_data='subscribe'))
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f"#{question.category}\n\n{question.question}\
            \n\nBy: {username}\n ``` Status: {question.status}```",
                    reply_markup=kbd,
                    parse_mode="Markdown")
            else:
                bot.reply_to(message, "Question not found")
            answers = session.query(Answer).filter(
                Answer.question_id == question_id, Answer.status == 'posted').all()
            session.commit()
            if answers:
                for answer in answers:
                    key = create_anw_key(answer_id=answer.answer_id)
                    bot.send_message(
                        chat_id=message.chat.id,
                        text=f"{answer.answer}\n\nBy: {username}",
                        reply_markup=key)
            else:
                print("No answers found")
                bot.reply_to(message, "No answers found")
        except Exception as e:
            bot.reply_to(message, "An error occurred")
            print(e)
        finally:
            session.close()


def create_anw_key(answer_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 4
    keyboard.add(InlineKeyboardButton(
        ' ✅ ', callback_data=f'like_{answer_id}'),
        InlineKeyboardButton(
            ' ❌ ', callback_data=f'dislike_{answer_id}'),
        InlineKeyboardButton(
            ' ⚠️ ', callback_data=f'comment_{answer_id}'),
        InlineKeyboardButton(
            ' ↩️ ', callback_data=f'share_{answer_id}'))
    return keyboard
