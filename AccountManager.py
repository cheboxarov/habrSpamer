from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession
import os
import json

# Загружаем настройки из config.json
settings = json.loads(open("config.json", "r").read())

class AccountManager:
    _api_id = settings["api_id"]
    _api_hash = settings["api_hash"]

    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.session_file = f'accounts/{phone_number}.session'
        self.client = None
        self.auth(phone_number)

    def auth(self, phone_number):
        if not os.path.exists('accounts'):
            os.makedirs('accounts')

        if os.path.exists(self.session_file):
            with open(self.session_file, 'r') as f:
                session_string = f.read().strip()
            self.client = TelegramClient(StringSession(session_string), self._api_id, self._api_hash)
        else:
            self.client = TelegramClient(StringSession(), self._api_id, self._api_hash)

        self.client.loop.run_until_complete(self.connect_and_authorize(phone_number))

    async def connect_and_authorize(self, phone_number):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(phone_number)
            code = input('Введите код, полученный в Telegram: ')
            await self.client.sign_in(phone_number, code)

            with open(self.session_file, 'w') as f:
                f.write(self.client.session.save())

    async def get_chats_from(self, folder_name="True mail"):
        result = await self.client(functions.messages.GetDialogFiltersRequest())
        folders = result.filters
        peer_ids = []
        if folders:
            for folder in folders:
                try:
                    if folder.title == folder_name:
                        for peer in folder.include_peers:
                            peer_ids.append(peer.channel_id)
                except:
                    pass
        return peer_ids

    def spam(self, chats):
        # Реализация отправки сообщений в чаты
        pass

if __name__ == "__main__":
    phone_number = "+79333233171"
    acc = AccountManager(phone_number)
    chats = acc.client.loop.run_until_complete(acc.get_chats_from())
    print(f"Чаты из папки 'True mail': {chats}")
