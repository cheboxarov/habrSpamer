from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession
import os
import json
import asyncio
from telethon.tl.types import PeerChannel, DialogFilter

# Загружаем настройки из config.json
settings = json.loads(open("config.json", "r").read())

class AccountManager:
    _api_id = settings["api_id"]
    _api_hash = settings["api_hash"]

    def __init__(self, phone_number, proxy = None):
        self._session_str = None
        self._code_hash = None
        self.phone_number = phone_number
        self.session_file = f'accounts/{phone_number}.session'
        self.client = None
        self._proxy = proxy

    async def auth(self):
        try:
            if not os.path.exists('accounts'):
                os.makedirs('accounts')
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    session_string = f.read().strip()
                self.client = TelegramClient(StringSession(session_string), self._api_id, self._api_hash, proxy=self._proxy)
            else:
                self.client = TelegramClient(StringSession(), self._api_id, self._api_hash, proxy=self._proxy)

            await self.client.connect()

            if self.client.is_connected():
                if await self.client.is_user_authorized():
                    return True
                else:
                    result = await self.client.send_code_request(phone=self.phone_number)
                    self._code_hash = result.phone_code_hash
                    self._session_str = self.client.session.save()
                    return True
            return False
        except Exception as e:
            print(f"Authentication error: {e}")
            return False

    async def connect_and_authorize(self, code):
        try:
            self.client = TelegramClient(StringSession(self._session_str), self._api_id, self._api_hash, proxy=self._proxy)
            await self.client.connect()

            if not await self.client.is_user_authorized():
                await self.client.sign_in(self.phone_number, code, phone_code_hash=self._code_hash)

                with open(self.session_file, 'w') as f:
                    f.write(self.client.session.save())
            return True
        except Exception as e:
            print(f"Authorization error: {e}")
            return False

    async def get_chats_from(self, folder_name="True mail"):
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                print("User is not authorized")
                return []

            result = await self.client(functions.messages.GetDialogFiltersRequest())
            folders = result.filters
            peers = []
            if folders:
                for folder in folders:
                    if isinstance(folder, DialogFilter) and folder.title == folder_name:
                        for peer in folder.include_peers:
                            try:
                                chanPeer = PeerChannel(channel_id=peer.channel_id)
                                channel_entity = await self.client.get_entity(chanPeer)
                                peers.append({"id": peer.channel_id, "name": channel_entity.title})
                            except Exception as e:
                                print(f"Error fetching chat: {e}")
            return peers
        except Exception as e:
            print(f"Error in get_chats_from: {e}")
            return []

    async def send_messages(self, message, interval, folder_name="True mail"):
        try:
            peers = await self.get_chats_from(folder_name)
            if not peers:
                print("No chats found")
                return

            for peer in peers:
                try:
                    await self.client.send_message(peer['id'], message)
                    print(f"Message sent to {peer['name']}")
                except Exception as e:
                    print(f"Error sending message to {peer['name']}: {e}")
                await asyncio.sleep(interval)
        except Exception as e:
            print(f"Error in send_messages: {e}")

    def get_phone(self):
        return self.phone_number

async def main():
    phone_number = "+79333233171"
    message = "Привет всем"
    interval = 1000  # Интервал в секундах

    acc = AccountManager(phone_number)
    if await acc.auth():
        print("Authenticated successfully")
        await acc.send_messages(message, interval)
    else:
        print("Authentication failed")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
