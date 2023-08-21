Telegram Chatbot Using Telethon and OpenAI

This repository contains Python code for a Telegram chatbot that uses the Telethon library to interact with the Telegram API and the OpenAI GPT-3 model to generate responses for incoming messages.

### Description

The code is organized into three main components: Telegram connection, message handling, and Autopilot (OpenAI integration).

1.  Telegram Connection (`TelegramConnection`): This class handles the authentication and connection to the Telegram API. It initializes the `TelegramClient` from Telethon using the provided API credentials.

2.  Message Handling (`TelegramMessages`): This class manages incoming messages, replies, and the logic for sending responses. It includes methods for reading new messages, retrieving message history, generating replies, and managing a queue of messages to reply to.

3.  Autopilot (`Autopilot`): This class interacts with the OpenAI GPT-3 model to generate responses based on the provided message. It sends a prompt to the GPT-3 engine and processes the generated response. The response is then cleaned and returned as the bot's reply.

### How It Works

The main script (`main.py`) orchestrates the interaction between the Telegram connection, message handling, and Autopilot components.

1.  The `TelegramConnection` class is used to authenticate the bot with the Telegram API.
2.  The `TelegramMessages` class listens for new incoming messages. If the message is from an allowed conversation, it is added to the queue of messages to reply to.
3.  The `Autopilot` class generates responses using the OpenAI GPT-3 model based on the message history provided.

The bot continuously checks the queue of messages to reply to and generates responses as needed.

### Setup and Configuration

Before running the code, make sure to set up the required environment variables:

-   `api_id`: Your Telegram API ID.
-   `api_hash`: Your Telegram API hash.
-   `phone_number`: Your phone number associated with the Telegram account.
-   `openai_api_key`: Your OpenAI API key.

The script uses these variables to authenticate with the Telegram API and OpenAI.

### Dependencies

-   Telethon (`telethon`): A Python Telegram client library.
-   OpenAI (`openai`): Python client for the OpenAI API.

### Running the Code

To run the code, ensure you have the required dependencies installed. Then, execute the `main.py` script.

### Note

This code provides a basic implementation of a Telegram chatbot using Telethon and OpenAI GPT-3. It's essential to review and modify the code according to your specific use case and security requirements before deploying it to a production environment.

Disclaimer: This code is provided as-is and may require further customization, optimization, and security considerations before deploying it in a real-world scenario. OpenAI API usage and Telegram API interactions should be compliant with their respective terms of service and guidelines.
