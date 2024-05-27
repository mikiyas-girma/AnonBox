from main_bot import bot
from models.engine.storage import SessionLocal
from models.question import Question
import os
import logging


username = 'Anonymous'
first_name = 'Anonymous'
last_name = 'Anonymous'

ADMIN_CHANNEL_ID = os.getenv('ADMIN_CHANNEL_ID')
PUBLIC_CHANNEL_ID = os.getenv('PUBLIC_CHANNEL_ID')


def send_pending_questions():
    global username
    from handlers.message_handlers import create_admin_keyboard
    session = SessionLocal()
    try:
        pending_questions = session.query(Question).filter_by(status='pending').all()
        for question in pending_questions:
            keyboard = create_admin_keyboard(question.question_id)
            sent_message = bot.send_message(ADMIN_CHANNEL_ID, text=f"#{question.category}\n\n{question.question}\
        \n\nBy: {username}\n ``` Status: {question.status}```",
                                            reply_markup=keyboard,
                                            parse_mode="Markdown")
            question.message_id = sent_message.message_id
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def monitor_question_status():
    session = SessionLocal()
    try:
        canceled_questions = session.query(Question).filter_by(status='cancelled').all()
        for question in canceled_questions:
            if question.message_id:
                try:
                    bot.delete_message(ADMIN_CHANNEL_ID, question.message_id)
                except Exception as e:
                    logging.error(f"Error deleting message: {e}")
            question.admin_message_id = None
        session.commit()
    except Exception as e:
        logging.error(f"Error monitoring question status: {e}")
    finally:
        session.close()
