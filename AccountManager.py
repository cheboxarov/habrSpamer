from telethon import TelegramClient, functions, types
from telethon.extensions import html, markdown
from telethon.sessions import StringSession
import os
import json
import asyncio
from telethon.tl.types import PeerChannel, DialogFilter, PeerChat
from DBManager import Proxy, DBManager
from telebot.async_telebot import AsyncTeleBot
import re

# Загружаем настройки из config.json
settings = json.loads(open("config.json", "r").read())
class CustomMarkdown:
    @staticmethod
    def parse(text):
        text, entities = markdown.parse(text)
        for i, e in enumerate(entities):
            if isinstance(e, types.MessageEntityTextUrl):
                if e.url == 'spoiler':
                    entities[i] = types.MessageEntitySpoiler(e.offset, e.length)
                elif e.url.startswith('emoji/'):
                    entities[i] = types.MessageEntityCustomEmoji(e.offset, e.length, int(e.url.split('/')[1]))
        return text, entities
    @staticmethod
    def unparse(text, entities):
        for i, e in enumerate(entities or []):
            if isinstance(e, types.MessageEntityCustomEmoji):
                entities[i] = types.MessageEntityTextUrl(e.offset, e.length, f'emoji/{e.document_id}')
            if isinstance(e, types.MessageEntitySpoiler):
                entities[i] = types.MessageEntityTextUrl(e.offset, e.length, 'spoiler')
        return markdown.unparse(text, entities)

def html_to_markdown(html):
    print(html)
    regs = re.findall(r'<tg-emoji emoji-id="\d+">.</tg-emoji>', html)
    print(regs)
    for reg in regs:
        id = re.findall(r"\d+", reg)[0]
        html = html.replace(reg, f"[❤️](emoji/{id})")
    regs = re.findall(r'<span class="tg-spoiler">.+</span>', html)
    for reg in regs:
        newreg = reg.replace('<span class="tg-spoiler">', "[").replace("</span>", "](spoiler)")
        html = html.replace(reg, newreg)
    html = html.replace('</tg-emoji>', '')
    return html

class AccountManager:
    _db = DBManager('sqlite:///database.db')
    _api_id = settings["api_id"]
    _api_hash = settings["api_hash"]
    AUTHORISED = 1
    NEED_CODE = 2
    AUTH_ERROR = 3
    def __init__(self, phone_number, proxy:Proxy = None, bot_manager = None):
        self._session_str = None
        self._code_hash = None
        self.phone_number = phone_number
        self.session_file = f'accounts/{phone_number}.session'
        self.client = None
        self._bot_manager = bot_manager
        if proxy is None:
            proxy = self._db.get_account_proxy(phone_number)
        current_proxy_dict = {
            "proxy_type": "http",
            "addr": proxy.host,
            "port": int(proxy.port),
            "username": proxy.username,
            "password": proxy.password,
        }
        self._proxy = current_proxy_dict

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
                    return self.AUTHORISED
                else:
                    result = await self.client.send_code_request(phone=self.phone_number)
                    self._code_hash = result.phone_code_hash
                    self._session_str = self.client.session.save()
                    return self.NEED_CODE
            self._db.deactive_account(self.phone_number)
            return self.AUTH_ERROR
        except Exception as e:
            print(f"Authentication error: {e}")
            return self.AUTH_ERROR

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

    async def get_chats_from(self, folder_name="true mail"):
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
                    try:
                        if folder.title.lower() == "true mail":
                            for peer in folder.include_peers:
                                try:
                                    chanPeer = PeerChannel(channel_id=peer.channel_id)
                                    channel_entity = await self.client.get_entity(chanPeer)
                                    peers.append({"id": peer.channel_id, "name": channel_entity.title})
                                except Exception as e:
                                    pass
                                try:
                                    chanPeer = PeerChat(chat_id=peer.chat_id)
                                    channel_entity = await self.client.get_entity(chanPeer)
                                    peers.append({"id": peer.chat_id, "name": channel_entity.title})
                                except Exception as e:
                                    pass
                    except:
                        pass
            return peers
        except Exception as e:
            print(f"Error in get_chats_from: {e}")
            return []

    async def send_messages(self, message, speed, interval, send_id, db, photo_path = None, folder_name="True mail"):
        try:
            self.client.parse_mode = CustomMarkdown()
            peers = await self.get_chats_from(folder_name)
            if not peers:
                print("No chats found")
                return
            i = 0
            for peer in peers:
                account = db.get_account_by_phone(self.phone_number)
                print(account.send_status)
                if account.send_status == 0:
                    return
                if account.send_id != send_id:
                    return
                if i == interval:
                    await asyncio.sleep(interval * 60)
                try:
                    if photo_path is None:
                        t, e = html.parse(html_to_markdown(message))
                        txt = markdown.unparse(t, e)
                        await self.client.send_message(peer['id'], txt)
                    else:
                        t, e = html.parse(html_to_markdown(message))
                        txt = markdown.unparse(t, e)
                        await self.client.send_file(peer['id'], photo_path, caption=txt)
                    print(f"Message sent to {peer['name']}")
                except Exception as e:
                    await self._bot_manager.account_blocked(self.phone_number)
                    return
                i += 1
                await asyncio.sleep(speed*60)
        except Exception as e:
            print(f"Error in send_messages: {e}")

    def get_phone(self):
        return self.phone_number

