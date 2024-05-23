# Flask Telegram Bot with Auto-restart

This project is a Flask application integrated with a Telegram bot. The bot can handle various commands and file uploads from users. Additionally, the project includes a script for automatically restarting the server when code modifications are detected.

## Features

- Integration of a Telegram bot with Flask application
- Handling various commands and file uploads from users
- Auto-restart functionality for the server upon code modifications

## Prerequisites

Before running the application, ensure you have the following:

- Python 3.x installed
- Required Python packages installed (install using `pip install -r requirements.txt`)
- Telegram bot token and webhook URL set up (configure in the `.env` file) in the project directory

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/mikiyas-girma/telegram-bot_Webhook
    cd telegram-bot_Webhook
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Configure environment variables:

    Create a `.env` file in the project root directory and add the following variables:

    ```dotenv
    BOT_TOKEN=your_bot_token_here
    WEBHOOK_URL=your_webhook_url_here
    ```

## Usage

1. Run the `watch.py` script to monitor code modifications for automatically start && restart the server:

    ```bash
     source .env 
    ```

    ``` 
    python watch.py 
    ``` 

2. Interact with the Telegram bot by sending commands or uploading files.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, feel free to open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
