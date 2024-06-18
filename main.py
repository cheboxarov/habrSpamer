from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_filters, types
import json
from BotManager import BotManager
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from DBManager import DBManager
import SpamManager

settings = json.loads(open("config.json", "r").read())
bot = AsyncTeleBot(settings["token"], state_storage=StateMemoryStorage(), parse_mode="MARKDOWN")
bot_manager = BotManager(bot, 'sqlite:///database.db', settings["admin"])
db = DBManager('sqlite:///database.db')


class MyStates(StatesGroup):
    phone = State()
    code = State()
    account_message = State()
    account_interval = State()
    account_speed = State()
    proxy_add = State()
    message_photo = State()
    message_from_all = State()
    edit_message = State()
    group_message = State()


@bot.message_handler(commands=["start"])
async def start_message(msg):
    await bot_manager.new_user(msg)


@bot.message_handler(state=MyStates.phone)
async def phone_handler(message):
    if await bot_manager.phone_entered(message.from_user.id, message.text):
        await bot.set_state(message.from_user.id, MyStates.code)
    else:
        await bot.delete_state(message.from_user.id)

@bot.message_handler(state=MyStates.message_from_all)
async def phone_handler(message):
    users = db.get_users()
    for user in users:
        await bot.send_message(user.user_id, message.text.replace(" ", ""))
    await bot.delete_state(message.from_user.id)

@bot.message_handler(state=MyStates.code)
async def code_handler(message):
    await bot_manager.code_entered(message.from_user.id, message.text.replace("_", ""))
    await bot.delete_state(message.from_user.id)


@bot.message_handler(state=MyStates.account_message)
async def code_handler(message: types.Message):
    await bot_manager.change_account_message_end(message.from_user.id, message.text)
    await bot.delete_state(message.from_user.id)

@bot.message_handler(state=MyStates.edit_message)
async def code_handler(message):
    await bot_manager.edit_msg_close(message.from_user.id, message.text)
    await bot.delete_state(message.from_user.id)

@bot.message_handler(content_types=['photo'], state=MyStates.message_photo)
async def photo(message):
    import os
    fileID = message.photo[-1].file_id
    file_info = await bot.get_file(fileID)  # Await the coroutine
    downloaded_file = await bot.download_file(file_info.file_path)  # Await the coroutine
    file_path = os.path.join("imgs", f"{message.from_user.id}.jpg")
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    await bot_manager.add_photo_end(message.from_user.id)



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
    print(call_type)
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

    if call_type == "cryptobot_top_up":
        await bot_manager.start_pay(user_id, message_id)

    if call_type.split("-")[0] == "account":
        await bot_manager.accounts(user_id, int(call_type.split("-")[1]), message_id)

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

    if call_type.split("-")[0] == "add_photo":
        await bot_manager.add_photo_start(user_id, int(call_type.split("-")[1]), message_id)
        await bot.set_state(user_id, MyStates.message_photo)

    if call_type.split("-")[0] == "delete_photo":
        await bot_manager.delete_photo(user_id, int(call_type.split("-")[1]), message_id)

    if call_type.split("-")[0] == "skip_cooldown":
        await bot_manager.skip_cooldown(user_id, int(call_type.split("-")[1]), message_id)

    if call_type.split("-")[0] == "change_interval":
        await bot_manager.change_account_interval_start(user_id, int(call_type.split("-")[1]), message_id)
        await bot.set_state(user_id, MyStates.account_interval)

    if call_type.split("-")[0] == "change_speed":
        await bot_manager.change_account_speed_start(user_id, int(call_type.split("-")[1]), message_id)
        await bot.set_state(user_id, MyStates.account_speed)
    if call_type.split("-")[0] == "groups":
        await bot_manager.groups(user_id, int(call_type.split("-")[1]), message_id)

    if call_type.split("-")[0] == "group":
        await bot_manager.group_edit(user_id,message_id,  int(call_type.split("-")[1]), int(call_type.split("-")[2]))

    if call_type.split("-")[0] == "group_settings":
        if call_type.split("-")[1] == "custom_enbale":
            await bot_manager.group_set_custom(user_id, group_id=call_type.split("-")[2], message_id=message_id, account_index=call_type.split("-")[3], custom=1)
        if call_type.split("-")[1] == "custom_disable":
            await bot_manager.group_set_custom(user_id, group_id=call_type.split("-")[2], message_id=message_id, account_index=call_type.split("-")[3], custom=0)
        if call_type.split("-")[1] == "message":
            await bot_manager.group_set_message_start(user_id, group_id=call_type.split("-")[2], message_id=message_id, account_index=call_type.split("-")[3])
            await bot.set_state(user_id, MyStates.group_message)

    if call_type.split("-")[0] == "delete_account":
        await bot_manager.delete_account(user_id, int(call_type.split("-")[1]), message_id)
    if call_type.split("|")[0] == "CQ":
        await bot_manager.select_pay_time(user_id, message_id, call_type.split("|")[1])
    if call_type.split("|")[0] == "PAY":
        await bot_manager.pay_finish(user_id, message_id, call_type.split("|")[1], call_type.split("|")[2])
    if call_type.split("|")[0] == "CHECK":
        await bot_manager.check_pay(user_id, message_id, call_type.split("|")[1], call_type.split("|")[3], call_type.split("|")[2])
    if call_type.split("-")[0] == "admin":
        if user_id != settings["admin"]:
            print(user_id, "Попытался зайти в админ")
            await bot.answer_callback_query(call.id)
            return
        if call_type.split("-")[1] == "proxy":
            await bot_manager.admin_proxy(user_id, message_id)
        if call_type.split("-")[1] == "kill_proxy":
            await bot_manager.admin_kill_proxy(user_id, message_id)
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
        if call_type.split("-")[1] == "send_message":
            await bot.send_message(user_id, "Отправьте сообщение")
            await bot.set_state(user_id, MyStates.message_from_all)
        if call_type.split("-")[1] == "edit_message":
            edit_msg = call_type.split("-")[2]
            await bot_manager.edit_msg_start(user_id, message_id, edit_msg)
            await bot.set_state(user_id, MyStates.edit_message)

    await bot.answer_callback_query(call.id)


@bot.message_handler(content_types=["text"])
async def main_text_handler(message:types.Message):
    print(message.text)
    if message.from_user.id == settings["admin"]:
        if message.text == "Админка":
            await bot_manager.admin_panel(message.from_user.id)
            return
        if message.text.split(" ")[0] == "/set_minutes":
            db.set_user_balance(int(message.text.split(" ")[1]), int(message.text.split(" ")[2]))
            return
    if message.text == "👤 Мой профиль":
        await bot_manager.profile_info(message.from_user.id, message.from_user.username)
    else:
        await bot_manager.new_user(message)


if __name__ == "__main__":
    import asyncio
    from threading import Thread

    bot.add_custom_filter(asyncio_filters.StateFilter(bot))
    bot.add_custom_filter(asyncio_filters.IsDigitFilter())
    spam_manager_process = Thread(target=SpamManager.run, daemon=True)
    spam_manager_process.start()
    asyncio.run(bot.polling())
