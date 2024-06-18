import re

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon import functions, types
import json
from telethon.tl.types import MessageEntityCustomEmoji, InputPeerUser
from telethon.tl.functions.messages import SendMessageRequest
from telethon.extensions import html, markdown
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

# Вставьте свои API ID и API Hash, которые можно получить у Telegram
settings = json.loads(open("config.json", "r").read())

# Создаем и подключаемся к клиенту
client = TelegramClient(StringSession(open("accounts/+79956470706.session", "r").read().strip()), settings["api_id"], settings["api_hash"])

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

async def main():
    await client.connect()
    client.parse_mode = CustomMarkdown()
    # Укажите ID чата или username
    chat_id = 'wlovemm'

    # Премиум эмодзи в формате HTML
    premium_emoji_id = 5348499619540119956  # Пример ID эмодзи

    # Получаем объект пользователя/чата
    entity = await client.get_input_entity(chat_id)
    smile = "[❤️](emoji/10002345)"
    # Создаем объект премиум эмодзи
    emoji_entity = MessageEntityCustomEmoji(offset=0, length=1, document_id=premium_emoji_id)
    text = '<tg-emoji emoji-id="5447183459602669338">🔽</tg-emoji><tg-emoji emoji-id="5244837092042750681">📈</tg-emoji><tg-emoji emoji-id="5447410659077661506">🌐</tg-emoji><tg-emoji emoji-id="5438169607443599829">🤩</tg-emoji><tg-emoji emoji-id="5422369870165584898">🥰</tg-emoji><tg-emoji emoji-id="5253800186278325174">🤩</tg-emoji><tg-emoji emoji-id="5357314112202224814">😛</tg-emoji><tg-emoji emoji-id="5440422734402173876">😉</tg-emoji><b>привет</b> <code>привет жажазвхпээа</code><blockquote>пззу</blockquote><span class="tg-spoiler">поза</span>'
    print(html_to_markdown(text))
    t, e = html.parse(html_to_markdown(text))
    txt = markdown.unparse(t, e)
    print(txt)
    message_text = '🙃'  # Можно использовать любой текст или символ в
    await client.send_message(chat_id, txt)
    # Отправляем сообщение с премиум эмодзи
    # await client(SendMessageRequest(
    #     peer=entity,
    #     message=message_text,
    #     entities=[emoji_entity]
    # ))


with client:
    client.loop.run_until_complete(main())