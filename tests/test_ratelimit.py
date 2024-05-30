#!/usr/bin/env python3

import telebot
import time
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Create a bot
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

# Number of messages to send
num_messages = 100
delay_between_messages = 0.01  # 50 milliseconds


def send_messages():
    for i in range(num_messages):
        try:
            bot.send_message(chat_id=5844273540,
                             text=f'Test to mike safari message {i+1}')
            bot.send_message(chat_id=796663862,
                             text=f'Test to mike tele message {i+1}')
            print(f'Sent message {i+1}')
            time.sleep(delay_between_messages)
        except Exception as e:
            print(f'Error on message {i+1}: {e}')


if __name__ == '__main__':
    send_messages()
