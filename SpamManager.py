import asyncio
from telebot.async_telebot import AsyncTeleBot
from BotManager import BotManager
from DBManager import DBManager, Account
from AccountManager import AccountManager
import json
from telethon import TelegramClient, functions, types
from telethon.extensions import html, markdown
import re

db_manager = DBManager('sqlite:///database.db')
settings = json.loads(open("config.json", "r").read())
bot = AsyncTeleBot(settings["token"], parse_mode="MARKDOWN")
bot_manager = BotManager(bot, 'sqlite:///database.db', settings["admin"])
send_id = 0

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

async def send_messages_from_account(account: Account):
    global send_id
    send_id += 1
    try:
        db_manager.set_account_send_id(account.phone, send_id)
        proxy = db_manager.get_account_proxy(account.phone)
        try:
            acc_manager = AccountManager(account.phone, proxy, bot_manager)
        except BaseException:
            db_manager.deactive_account(account.phone)
            return
        if await acc_manager.auth():
            print(f"Authenticated for {account.phone}")
            peers = await acc_manager.get_chats_from()
            if not peers:
                print("No chats found")
                return
            i = 0
            for peer in peers:
                accs = db_manager.get_active_accounts()
                if not account.phone in [acc.phone for acc in accs]:
                    print("Account not active, stopping")
                    return
                curr_acc = None
                for acc in accs:
                    if acc.phone == account.phone:
                        curr_acc = acc
                if curr_acc.send_id != send_id:
                    return
                if i == account.interval:
                    i = 0
                    await asyncio.sleep(account.interval * 60)
                try:
                    if account.has_photo is None:
                        t, e = html.parse(html_to_markdown(account.message_to_send))
                        txt = markdown.unparse(t, e)
                        await acc_manager.client.send_message(peer['id'], txt)
                    else:
                        t, e = html.parse(html_to_markdown(account.message_to_send))
                        txt = markdown.unparse(t, e)
                        await acc_manager.client.send_file(peer['id'], account.photo_path, caption=txt)
                    print(f"Message sent to {peer['name']}")
                except Exception as e:
                    await bot_manager.account_blocked(acc_manager.phone_number)
                    return
                i += 1
                await asyncio.sleep(account.speed * 60)
        else:
            db_manager.deactive_account(account.phone)
    except Exception as e:
        print(f"Error processing account {account.phone}: {e}")

async def main_spam():
    while True:
        print("spam")
        try:
            accounts = db_manager.get_active_accounts()
            for account in accounts:
                print(account.id)
                user = db_manager.get_user_by_user_id(account.user_id)
                if user.minutes_left <= 0:
                    db_manager.deactive_account(account.phone)
                if account.send_status and account.cooldown == 0:
                    await send_messages_from_account(account)
                    db_manager.set_account_cooldown(account.phone)
                elif account.cooldown > 0:
                    db_manager.cooldown_down_minute(account.phone)
        except Exception as e:
            print(f"Error in main loop: {e}")
        db_manager.users_time_down()
        await asyncio.sleep(60)

def run():
    asyncio.run(main_spam())
