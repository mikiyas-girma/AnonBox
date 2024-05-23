from main_bot import bot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from models.models import User, SessionLocal


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
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
    # Your code here
    bot.send_message(
        message.chat.id,
        "Send me your question  ``` Note that you can send your questions \
through voice messages, images, videos, and documents```",
        parse_mode="Markdown")
    bot.register_next_step_handler(message, handle_question)


def handle_question(message):

    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True)
    keyboard.resize_keyboard = True
    keyboard.row_width = 2
    keyboard.add(KeyboardButton('Technology'),
                 KeyboardButton('Relationship'),
                 KeyboardButton('Health'),
                 KeyboardButton('Business'),
                 KeyboardButton('Education'),
                 KeyboardButton('Politics'),
                 KeyboardButton('Other'))
    bot.send_message(message.chat.id, "Choose a category for your question \
``` if you don't see a category that fits your question, \
choose 'Other' option```",
                     parse_mode="Markdown", reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_category, message.text)
    bot.register_next_step_handler(message, send_welcome)


def handle_category(message, question):
    category = message.text
    bot.send_message(message.chat.id, "preview your question and press submit \
once you are done")
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(InlineKeyboardButton('Edit Question', callback_data='Ask a question'),
                 InlineKeyboardButton('Cancel', callback_data='cancel'),
                 InlineKeyboardButton('Submit', callback_data='submit'))

    bot.send_message(message.chat.id, f"#{category}\n\n{question}\n\nBy: \
{message.from_user.username}\n ``` Status: previewing```",
                     parse_mode="Markdown", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'Ask a question')
def handle_edit_question(call):
    handle_ask_question(call.message)


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


@bot.message_handler(commands=['link'])
def send_link(message):
    bot.send_message(message.chat.id,
                     "link to the bot: http://t.me/Pybot_exBot")


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
