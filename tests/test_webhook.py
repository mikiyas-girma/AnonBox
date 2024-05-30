#!/usr/bin/env python3

import requests
import time

# Webhook URL for your Telegram bot
# webhook_url = os.getenv('WEBHOOK_URL')
webhook_url = 'https://faithful-wealthy-bullfrog.ngrok-free.app/webhook'

# Number of requests to send
num_requests = 50

# Delay between requests to simulate rate limit
delay_between_requests = 0.05  # 50ms


def send_register_requests():
    for i in range(num_requests):
        try:
            payload = {
                'update_id': i + 1,
                'message': {
                    'message_id': i + 1,
                    'from': {
                        'id': i + 1000,  # Simulating different user IDs
                        'is_bot': False,
                        'first_name': 'TestUser',
                        'username': f'testuser{i+1}',
                    },
                    'chat': {
                        'id': 796663862,  # Simulating different chat IDs
                        'first_name': 'TestUser',
                        'username': f'testuser{i+1}',
                        'type': 'private',
                    },
                    'date': int(time.time()),
                    'text': 'Browse Questions',
                    'entities': [{'type': 'bot_command', 'offset': 0,
                                  'length': 9}],
                },
            }
            response = requests.post(webhook_url, json=payload)
            print(f'Sent request {i+1}, Response: {response.status_code}')
            if response.status_code == 429:
                print('Rate limit exceeded. retryingn...')
                time.sleep(2)
                retry_response = requests.post(webhook_url, json=payload)
                print(f'retrying if 200 good {retry_response.status_code}')
            time.sleep(delay_between_requests)
        except Exception as e:
            print(f'Error on request {i+1}: {e}')


if __name__ == '__main__':
    start_time = time.time()
    send_register_requests()
    end_time = time.time()
    print(f'Time taken: {end_time - start_time} seconds')
