from main_bot import bot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from models.engine.storage import SessionLocal
from models.question import Question
from models.answer import Answer
from models.asked import Asked
from models.user_reaction import UserReaction
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
            asked_query = session.query(Asked).filter_by(
                question_id=question_id).first()
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
                    text=f"#{asked_query.question_category}\n\n{asked_query.user_question}\
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
    session = SessionLocal()
    my_ans = session.query(Answer).get(answer_id)
    likes = my_ans.likes
    dislikes = my_ans.dislikes
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 4
    keyboard.add(InlineKeyboardButton(
        f' ✅ {likes} ', callback_data=f'like_{answer_id}'),
        InlineKeyboardButton(
            f' ❌ {dislikes} ', callback_data=f'dislike_{answer_id}'),
        InlineKeyboardButton(
            ' ⚠️ ', callback_data=f'comment_{answer_id}'),
        InlineKeyboardButton(
            ' ↩️ ', callback_data=f'replyto_{answer_id}'))
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith('like_'))
def on_answer(call):
    """
    Handle callback queries on each answers
    """
    answer_id = int(call.data.split('_')[-1])
    session = SessionLocal()
    try:
        answers = session.query(Answer).get(answer_id)
        user_reaction = session.query(UserReaction).filter_by(
            user_id=call.from_user.id, answer_id=answer_id).first()
        if user_reaction:
            if user_reaction.reaction_type == 'like':
                answers.likes -= 1
                bot.answer_callback_query(
                    call.id, "You have unliked this answer")
                user_reaction.reaction_type = 'none'
            elif user_reaction.reaction_type == 'dislike':
                answers.dislikes -= 1
                answers.likes += 1
                bot.answer_callback_query(
                    call.id, "You have liked this answer")
                user_reaction.reaction_type = 'like'
        else:
            answers.likes += 1
            bot.answer_callback_query(call.id, "You have liked this answer")
            session.add(UserReaction(
                user_id=call.from_user.id, answer_id=answer_id, reaction_type='like'))
        session.commit()
        key = create_anw_key(answer_id)
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=key)
    except Exception as e:
        bot.answer_callback_query(call.id, "An error occurred")
        print(e)
    finally:
        session.close()
