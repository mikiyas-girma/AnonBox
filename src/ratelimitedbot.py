import time
import threading
from queue import Queue
from telebot import TeleBot


class RateLimitedBot:
    def __init__(self, token):
        self.bot = TeleBot(token)
        self.rate_limit_queue = Queue()
        self.retry_thread = threading.Thread(
                                    target=self.retry_rate_limited_messages)
        self.retry_thread.daemon = True
        self.retry_thread.start()

    def retry_rate_limited_messages(self):
        while True:
            if not self.rate_limit_queue.empty():
                method, args, kwargs = self.rate_limit_queue.get()
                print(f"Retrying {method} with args:" +
                      f"{args} and kwargs: {kwargs}")
                self.call_method_with_rate_limit(method, *args, **kwargs)
                self.rate_limit_queue.task_done()
            else:
                time.sleep(1)  # wait 1 second before checking the queue again

    def call_method_with_rate_limit(self, method, *args, **kwargs):
        try:
            getattr(self.bot, method)(*args, **kwargs)
        except Exception as e:
            self.rate_limit_queue.put((method, args, kwargs))
            print(f"Error sending message: {e}")

    def __getattr__(self, name):
        if name in ['message_handler', 'callback_query_handler',
                    'answer_callback_query', 'inline_handler']:
            return getattr(self.bot, name)
        else:
            def method(*args, **kwargs):
                self.call_method_with_rate_limit(name, *args, **kwargs)
            return method
