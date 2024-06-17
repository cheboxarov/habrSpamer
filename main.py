from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_filters
import json
from BotManager import BotManager
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from DBManager import DBManager
import SpamManager

settings = json.loads(open("config.json", "r").read())
bot = AsyncTeleBot(settings["token"], state_storage=StateMemoryStorage())
bot_manager = BotManager(bot, 'sqlite:///database.db', settings["admin"])
db = DBManager('sqlite:///database.db')

class MyStates(StatesGroup):
    phone = State()
    code = State()
    account_message = State()
    account_interval = State()
    account_speed = State()
    proxy_add = State()

@bot.message_handler(commands=["start"])
async def start_message(msg):
    await bot_manager.new_user(msg)

@bot.message_handler(state=MyStates.phone)
async def phone_handler(message):
    if await bot_manager.phone_entered(message.from_user.id, message.text):
        await bot.set_state(message.from_user.id, MyStates.code)

@bot.message_handler(state=MyStates.code)
async def code_handler(message):
    await bot_manager.code_entered(message.from_user.id, message.text.replace("_", ""))
    await bot.delete_state(message.from_user.id)

@bot.message_handler(state=MyStates.account_message)
async def code_handler(message):
    await bot_manager.change_account_message_end(message.from_user.id, message.text)
    await bot.delete_state(message.from_user.id)

@bot.message_handler(state=MyStates.account_interval)
async def code_handler(message):
    await bot_manager.change_account_interval_end(message.from_user.id, message.text)
    await bot.delete_state(message.from_user.id)

@bot.message_handler(state=MyStates.account_speed)
async def code_handler(message):
    await bot_manager.change_account_speed_end(message.from_user.id, message.text)
    await bot.delete_state(message.from_user.id)

@bot.message_handler(state=MyStates.proxy_add)
async def proxy_add_handler(message):
    await bot_manager.admin_add_proxy_end(message.from_user.id, message.text)

@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call):
    await bot.delete_state(call.from_user.id)
    user_id = call.from_user.id
    user_username = call.from_user.username
    call_type = call.data.split(":")[0]
    message_id = int(call.data.split(":")[1])
    user = db.get_user_by_user_id(user_id)
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
    if user.minutes_left <= 0:
        await bot.answer_callback_query(call.id)
        return
    if call_type == "add_account":
        await bot_manager.add_account(user_id, message_id)
        await bot.set_state(user_id, MyStates.phone)

    if call_type.split("-")[0] == "account":
        try:
            await bot_manager.accounts(user_id, int(call_type.split("-")[1]), message_id)
        except:
            pass

    if call_type.split("-")[0] == "account_settings":
        await bot_manager.account_settings(user_id, int(call_type.split("-")[1]), message_id)

    if call_type.split("-")[0] == "stop_account":
        await bot_manager.stop_account(user_id, int(call_type.split("-")[1]), message_id)

    if call_type.split("-")[0] == "reactivate_account":
        await bot_manager.reactivate_account(user_id, int(call_type.split("-")[1]), message_id)
        await bot.set_state(user_id, MyStates.code)

    if call_type.split("-")[0] == "deactive_account":
        await bot_manager.deactive_account(user_id, int(call_type.split("-")[1]), message_id)

    if call_type.split("-")[0] == "start_account":
        await bot_manager.start_account(user_id, int(call_type.split("-")[1]), message_id)

    if call_type.split("-")[0] == "change_message":
        await bot_manager.change_account_message_start(user_id, int(call_type.split("-")[1]), message_id)
        await bot.set_state(user_id, MyStates.account_message)

    if call_type.split("-")[0] == "skip_cooldown":
        await bot_manager.skip_cooldown(user_id, int(call_type.split("-")[1]), message_id)

    if call_type.split("-")[0] == "change_interval":
        await bot_manager.change_account_interval_start(user_id, int(call_type.split("-")[1]), message_id)
        await bot.set_state(user_id, MyStates.account_interval)

    if call_type.split("-")[0] == "change_speed":
        await bot_manager.change_account_speed_start(user_id, int(call_type.split("-")[1]), message_id)
        await bot.set_state(user_id, MyStates.account_speed)

    if call_type.split("-")[0] == "delete_account":
        await bot_manager.delete_account(user_id, int(call_type.split("-")[1]), message_id)

    if call_type.split("-")[0] == "admin":
        if user_id != settings["admin"]:
            print(user_id, "Попытался зайти в админ")
            await bot.answer_callback_query(call.id)
            return
        if call_type.split("-")[1] == "proxy":
            await bot_manager.admin_proxy(user_id, message_id)
        if call_type.split("-")[1] == "add_proxy":
            await bot_manager.admin_add_proxy_start(user_id, message_id)
            await bot.set_state(user_id, MyStates.proxy_add)
        if call_type.split("-")[1] == "users":
            await bot_manager.admin_users(user_id, message_id)
        if call_type.split("-")[1] == "accounts":
            await bot_manager.admin_accounts(user_id, message_id)
        if call_type.split("-")[1] == "back":
            await bot_manager.admin_panel(user_id, message_id)
        if call_type.split("-")[1] == "messages":
            await bot_manager.edit_messages(user_id, message_id)
        if call_type.split("-")[1] == "edit_message":
            edit_msg = call_type.split("-")[2]
            await bot_manager.edit_msg_start(user_id, message_id, edit_msg)

    await bot.answer_callback_query(call.id)

@bot.message_handler(content_types=["text"])
async def main_text_handler(message):
    if message.text == "👤 Мой профиль":
        await bot_manager.profile_info(message.from_user.id, message.from_user.username)
    if message.text == "Админка":
        await bot_manager.admin_panel(message.from_user.id)




if __name__ == "__main__":
    import asyncio
    from multiprocessing import Process
    bot.add_custom_filter(asyncio_filters.StateFilter(bot))
    bot.add_custom_filter(asyncio_filters.IsDigitFilter())
    spam_manager_process = Process(target=SpamManager.run)
    spam_manager_process.start()
    asyncio.run(bot.polling())
