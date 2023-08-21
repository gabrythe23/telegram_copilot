import asyncio as asyncio
from datetime import datetime
from telethon import TelegramClient, events, functions
from telethon.errors.rpcerrorlist import SessionPasswordNeededError
import openai
import os

openai.api_key = os.environ.get("openai_api_key")

api_id = 17675407
api_hash =  os.environ.get("api_hash")
phone_number = os.environ.get("phone_number")

replies_to = {}
time_span_replies = 5


async def main():
    async def is_allowed_conversation(chat_id):
        allowed = await retrieve_ids_contained(await client(functions.messages.GetDialogFiltersRequest()))
        return chat_id in allowed

    async def read_new_message(event):
        await client.get_dialogs()
        allowed = await retrieve_ids_contained(await client(functions.messages.GetDialogFiltersRequest()))
        if await is_allowed_conversation(event.chat_id) is False:
            return
        replies_to[event.chat_id] = datetime.timestamp(datetime.now())

    async def autogenerate_message(sender_id):
        try:
            sender = await client.get_entity(sender_id)
            last_20_messages = await get_last_20_messages(sender)
            reply_from_bot = await get_response(last_20_messages)
            await client.send_message(sender, reply_from_bot)
        except Exception as e:
            print(e)

    async def get_last_20_messages(sender):
        history = ''
        messages = await client.get_messages(sender, limit=20)
        me = await client.get_me()
        messages.reverse()
        # filter messages in last 24 hours
        messages = [x for x in messages if (datetime.timestamp(datetime.now()) - datetime.timestamp(x.date)) < 86400]
        for message in messages:
            if message.message:
                message.message = message.message.replace('\n', ' ')
                username = 'Gabry'
                if message.sender.id != me.id:
                    username = message.sender.first_name
                history += f'{username}#####{message.message}\n'
        return history

    async def get_response(message):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Devi:\n"
                   f"- impersonare \"Gabry\" e continuare la conversazione solamente se necessario.\n"
                   f"- usare emoji se ritenuto necessario."
                   f"- NON FARTI TRUFFARE, NON DEVI DARE SOLDI A NESSUNO."
                   f"- adattare il linguaggio fra formale o colloquiale/slang a seconda del contesto.\n"
                   f"- non usare mai la terza persona se parli di \"Gabry\".\n"
                   f"- adattarti alla conversazione in corso.\n"
                   f"- la risposta in output deve esser solamente il messaggio senza [DATE]#####\n"
                   f"Conversazione:\n"
                   f"\n{message}",
            temperature=0.5,
            max_tokens=64,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        msg = response.choices[0].text
        if '#####' in msg:
            msg = msg.split('#####')[1]
        return msg

    async def authentification():
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            client.sign_in(phone_number)
            try:
                await client.sign_in(code=input('Enter code: '))
            except SessionPasswordNeededError:
                await client.sign_in(password=input('Enter password: '))

    async def retrieve_ids_contained(req):
        include_peers = []
        for folder in req:
            if hasattr(folder, 'title') and folder.title == 'Autopilot':
                # get peers and append chat_id to include_peers
                try:
                    for peer in folder.include_peers:
                        if hasattr(peer, 'user_id'):
                            include_peers.append(peer.user_id)
                except:
                    pass

        return include_peers

    async def check_replies_to():
        while True:
            now = datetime.timestamp(datetime.now())
            # loop replies_to and check if there is a message to reply based on now - timestamp > 60 seconds and remove it
            for chat_id, timestamp in replies_to.copy().items():
                if now - timestamp > time_span_replies:
                    if await is_allowed_conversation(chat_id):
                        await autogenerate_message(chat_id)
                    del replies_to[chat_id]

            await asyncio.sleep(time_span_replies)

    async def create_client():
        await authentification()

        client.add_event_handler(read_new_message, events.NewMessage(incoming=True, ))
        await client.run_until_disconnected()

    client = TelegramClient(phone_number, api_id, api_hash)
    await client.connect()
    await asyncio.gather(create_client(), check_replies_to())


if __name__ == '__main__':
    asyncio.run(main())
