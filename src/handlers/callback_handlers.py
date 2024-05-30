from main_bot import bot
from telebot.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           SwitchInlineQueryChosenChat)
from telebot.util import quick_markup

bot = bot.bot


@bot.message_handler(commands=['social'])
def list_social_media(message):
    markup = quick_markup({
            'Twitter': {
                'url': 'https://t.me/botethiopia_bot',
                'callback_data': 'inBot'},
            'Facebook': {'url': 'https://facebook.com'},
            'Confirm': {'callback_data': 'confirm'},
        }, row_width=2)
    bot.send_message(message.chat.id, 'Choose a social media',
                     reply_markup=markup)


@bot.message_handler(commands=['confirm'])
def confirm_command(message):

    markup = InlineKeyboardMarkup()
    markup.row_width = 1

    markup.add(InlineKeyboardButton(
        'admin',
        switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(
            'admin', allow_user_chats=True, )),

               InlineKeyboardButton('confirm', callback_data='confirm',),
               InlineKeyboardButton('cancel', callback_data='cancel'))
    bot.send_message(message.chat.id, "Are you sure you want to confirm?",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'confirm')
def confirm_callback(call):
    bot.answer_callback_query(call.id, 'confirmed', show_alert=True)
