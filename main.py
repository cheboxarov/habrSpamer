from telebot.async_telebot import AsyncTeleBot
import json
from BotManager import BotManager

settings = json.loads(open("config.json", "r").read())
bot = AsyncTeleBot(settings["token"])
bot_manager = BotManager(bot, 'sqlite:///database.db')

@bot.message_handler(commands=["start"])
async def start_message(message):
    await bot_manager.new_user(message)

@bot.message_handler(commands=["user"])
async def user_info(message):
    await bot_manager.user_info(message)

@bot.message_handler(commands=["profile"])
async def profile_info(message):
    await bot_manager.profile_info(message)

@bot.message_handler(content_types=["text"])
async def main_text_handler(message):
    if message.text == "👤 Мой профиль":
        await bot_manager.profile_info(message.from_user.id, message.from_user.username)

@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call):

    user_id = call.from_user.id
    user_username = call.from_user.username
    call_type = call.data.split(":")[0]
    message_id = int(call.data.split(":")[1])

    if call_type == "top_up_balance":
        await bot_manager.top_up_balance(user_id, message_id)

    if call_type == "back_from_top_up_balance":
        await bot_manager.profile_info(user_id, user_username, message_id)

    if call_type == "back_from_referal_info":
        await bot_manager.profile_info(user_id, user_username, message_id)

    if call_type == "referal_program":
        await bot_manager.referal_info(user_id, message_id)

    if call_type == "profile":
        await bot_manager.profile_info(user_id, user_username, message_id)

    if call_type == "back_for_profile_info":
        await bot_manager.user_info(user_id, message_id)

    if call_type == "back_from_bot_info":
        await bot_manager.user_info(user_id, message_id)

    if call_type == "back_from_pay_info":
        await bot_manager.user_info(user_id, message_id)

    if call_type == "back_from_account_view":
        await bot_manager.user_info(user_id, message_id)

    if call_type == "info":
        await bot_manager.bot_info(user_id, message_id)

    if call_type == "about_payment":
        await bot_manager.pay_info(user_id, message_id)

    if call_type == "support":
        await bot_manager.support_info(user_id, message_id)

    if call_type == "back_from_support":
        await bot_manager.bot_info(user_id, message_id)

    if call_type.split("-")[0] == "account":
        await bot_manager.accounts(user_id, int(call_type.split("-")[1]), message_id)

    await bot.answer_callback_query(call.id)

if __name__ == "__main__":
    import asyncio
    asyncio.run(bot.polling())
