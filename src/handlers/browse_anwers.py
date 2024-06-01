from main_bot import bot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from models.engine.storage import SessionLocal
from models.question import Question
from models.answer import Answer
from models.asked import Asked
from models.user_reaction import UserReaction
from collections import deque
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
                Answer.question_id == question_id, Answer.status == 'posted',
                Answer.reply_to == None).all()
            session.commit()
            if answers:
                queue = deque(answers)
                while queue:
                    answer = queue.popleft()

                    key = create_anw_key(answer_id=answer.answer_id)
                    reply_text = f"{answer.answer}\n\nBy: {username}"
                    reply_to_message_id = None
                    if answer.reply_to is not None:
                        parent_answer = session.query(Answer).get(
                            answer.reply_to)
                        if parent_answer is not None:
                            reply_to_message_id = parent_answer.tg_msg_id
                    sent_message = bot.send_message(
                        chat_id=message.chat.id,
                        text=reply_text,
                        reply_markup=key,
                        reply_to_message_id=reply_to_message_id)
                    answer.tg_msg_id = sent_message.message_id
                    session.commit()
                    replies = session.query(Answer).filter(
                        Answer.reply_to == answer.answer_id).all()
                    queue.extend(replies)

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


@bot.callback_query_handler(func=lambda call: call.data.startswith(('like_', 'dislike_')))
def on_answer(call):
    """
    Handle callback queries on each answers
    """
    reaction_type, answer_id = call.data.split('_')
    answer_id = int(answer_id)
    user_id = call.from_user.id
    session = SessionLocal()
    try:
        answer = session.query(Answer).get(answer_id)
        if not answer:
            bot.answer_callback_query(call.id, "Answer does not exist")
            return

        user_reaction = session.query(UserReaction).filter_by(
            user_id=user_id, answer_id=answer_id).first()

        if user_reaction:
            if user_reaction.reaction_type == reaction_type:
                # User wants to undo their reaction
                if reaction_type == 'like':
                    answer.likes -= 1
                else:
                    answer.dislikes -= 1
                session.delete(user_reaction)
                bot.answer_callback_query(call.id,
                                          "You have unmarked this answer")
            else:
                # User wants to change their reaction
                if reaction_type == 'like':
                    answer.likes += 1
                    if user_reaction.reaction_type == 'dislike':
                        answer.dislikes -= 1
                else:
                    answer.likes -= 1
                    answer.dislikes += 1
                user_reaction.reaction_type = reaction_type
                bot.answer_callback_query(
                    call.id,
                    f"You have {reaction_type}d this answer")
        else:
            # User wants to add a new reaction
            if reaction_type == 'like':
                answer.likes += 1
            else:
                answer.dislikes += 1
            session.add(UserReaction(user_id=user_id,
                                     answer_id=answer_id,
                                     reaction_type=reaction_type))
            bot.answer_callback_query(call.id,
                                      f"You have {reaction_type}d this answer")

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


@bot.callback_query_handler(func=lambda call: call.data.startswith('replyto_'))
def on_reply_to(call):
    """
    Handle callback queries on each answers
    """
    answer_id = int(call.data.split('_')[-1])
    session = SessionLocal()
    try:
        answer = session.query(Answer).get(answer_id)
        if not answer:
            bot.answer_callback_query(call.id, "Answer does not exist")
            return
        keyboard = ReplyKeyboardMarkup(one_time_keyboard=True)
        keyboard.resize_keyboard = True
        keyboard.add(KeyboardButton('Cancel'))
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Send your reply:",
            reply_markup=keyboard)
        bot.register_next_step_handler(call.message, process_reply, answer_id)
    except Exception as e:
        bot.answer_callback_query(call.id, "An error occurred in on reply to")
        print(e)
    finally:
        session.close()


def process_reply(message, answer_id):
    """
    Process user's reply to an answer
    """
    if message.text == 'Cancel':
        bot.send_message(chat_id=message.chat.id, text="Cancelled")
        return

    session = SessionLocal()
    try:
        reply = message.text
        original_answer = session.query(Answer).get(answer_id)

        new_answer = Answer(
            answer_id=message.message_id,
            question_id=original_answer.question_id,
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id,
            answer=reply,
            status='posted',
            reputation=0,
            reply_to=answer_id
        )
        session.add(new_answer)
        session.commit()
        sent_message = bot.send_message(
            chat_id=message.chat.id,
            text="Your reply has been saved.")
        new_answer.tg_msg_id = sent_message.message_id
        session.commit()
    except Exception as e:
        bot.reply_to(message, "An error occurred")
        print(e)
    finally:
        session.close()
