import asyncio as asyncio
from datetime import datetime
import time
import threading
import schedule as schedule
from telethon import TelegramClient, events, functions
from telethon.errors.rpcerrorlist import SessionPasswordNeededError
import openai
import os

api_id = os.environ.get("api_id")
api_hash = os.environ.get("api_hash")
phone_number = os.environ.get("phone_number")
openai.api_key = os.environ.get("openai_api_key")
# get openai.token from process.env


class TelegramConnection:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session', api_id, api_hash)

    async def authenticate(self):
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            self.client.sign_in(self.phone_number)
            try:
                await self.client.sign_in(code=input('Enter code: '))
            except SessionPasswordNeededError:
                await self.client.sign_in(password=input('Enter password: '))


class TelegramMessages:
    def __init__(self, client):
        self.client = client
        self.replies_to = {}
        self.time_span_replies = 5

    async def read_new_message(self, event):
        allowed = retrieve_ids_contained(await self.client(functions.messages.GetDialogFiltersRequest()))
        if event.chat_id not in allowed and event.is_private is False:
            return

        self.replies_to[event.message.peer_id.user_id] = datetime.timestamp(datetime.now())

    async def get_last_20_messages(self, sender):
        history = ''
        messages = await self.client.get_messages(sender, limit=50)
        me = await self.client.get_me()
        messages.reverse()
        for message in messages:
            if message.message:
                message.message = message.message.replace('\n', ' ')
                username = 'Gabry'
                if message.sender.id != me.id:
                    username = message.sender.first_name
                history += f'[{message.date.strftime("%d-%m-%Y %H:%M")}] {message.sender.first_name}#####{message.message}\n'
        return history

    async def check_replies_to(self):
        while True:
            now = datetime.timestamp(datetime.now())
            # loop replies_to and check if there is a message to reply based on now...
            for sender_id, timestamp in self.replies_to.items():
                if now - timestamp > self.time_span_replies:
                    await self.autogenerate_message(sender_id)
                    del self.replies_to[sender_id]
            await asyncio.sleep(1)

    async def autogenerate_message(self, sender_id):
        try:
            last_20_messages = await self.get_last_20_messages(sender_id)
            reply_from_bot = await Autopilot.get_response(last_20_messages)
            await self.client.send_message(sender_id, reply_from_bot)
        except Exception as e:
            print(e)


class Autopilot:
    def __init__(self):
        self.openai_api_key = openai.api_key

    async def get_response(self, message):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"aiuta a rispondere all'ultimo messaggio dai pure del tu ed usa pure emoji se "
                   f"necessario \n{message}",
            temperature=0.7,
            max_tokens=128,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        msg = response.choices[0].text
        if '#####' in msg:
            msg = msg.split('#####')[1]
        return msg


def retrieve_ids_contained(req):
    include_peers = []
    for folder in req:
        try:
            if folder.title == 'Autopilot':
                include_peers = folder.include_peers
        except Exception:
            pass

    include_peers = [x.user_id for x in include_peers if hasattr(x, 'user_id')]

    return include_peers


async def main():
    # initialize classes
    connection = TelegramConnection(api_id, api_hash, phone_number)
    messages = TelegramMessages(connection.client)
    autopilot = Autopilot()

    # authenticate and start listening for new messages
    await connection.client.connect()
    await connection.client.
    await connection.authenticate()
    messages.client.add_event_handler(messages.read_new_message, events.NewMessage)

    # start checking for messages to reply to
    messages.check_replies_to()


if __name__ == '__main__':
    asyncio.run(main())
