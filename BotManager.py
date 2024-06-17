from telebot.async_telebot import AsyncTeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from TMessagesManager import TMessagesManager
import time
from DBManager import DBManager, User, Account
from AccountManager import AccountManager
from typing import Dict
import random
import string


def generate_string(length):
    all_symbols = string.ascii_uppercase + string.digits
    result = ''.join(random.choice(all_symbols) for _ in range(length))
    return result

class BotManager:
    def __init__(self, bot:AsyncTeleBot, db_url:str, admin_id:int):
        self._tm_manager = TMessagesManager()
        self._bot = bot
        self._db = DBManager(db_url)
        self._connecting_accounts:Dict[int, AccountManager] = {}
        self._edit_account:Dict[int, Account] = {}
        self._admin_id = admin_id


    def is_admin(self, id:int) -> bool:
        return self._admin_id == id

    async def new_user(self, message):
        user_id = message.from_user.id
        referrer_candidate = ""
        if " " in message.text:
            referrer_candidate = message.text.split()[1]
            print(referrer_candidate)
        username = message.from_user.username
        if self._db.add_user(user_id, username, str(message.from_user.id), 0, referrer_candidate, 0):
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton("👤 Мой профиль"))
            await self._bot.send_message(user_id, self._tm_manager.get_start_message(), reply_markup=markup)
        else:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton("👤 Мой профиль"))
            await self._bot.send_message(user_id, "👋🏻 С возвращением!🤓\nПриятно видеть Вас снова!", reply_markup=markup)

    async def user_info(self, user_id, message_id = None):
        user = self._db.get_user_by_user_id(user_id)
        days_left = int(user.minutes_left / 1440) + 1
        accounts = self._db.get_accounts_by_user_id(user_id)
        accounts_count = len(accounts)
        work_accounts = [account for account in accounts if account.send_status == True]
        work_accounts_count = len(work_accounts)
        reply_message = self._tm_manager.get_user_info_message(accounts_count,work_accounts_count,1, 0, days_left)
        if not message_id is None:
            await self._bot.edit_message_text(chat_id=user_id, message_id=message_id, text=reply_message,
                                              reply_markup=self._user_info_markup_gen(user_id, message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            print(message)
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id, message_id=message_id, text=reply_message, reply_markup=self._user_info_markup_gen(user_id, message_id))

    def _user_info_markup_gen(self, user_id, message_id:int):
        user = self._db.get_user_by_user_id(user_id)
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        if user.minutes_left > 0:
            markup.row(InlineKeyboardButton("👤 Профиль", callback_data="profile:"+str(message_id)),
                       InlineKeyboardButton("👥 Мои аккаунты", callback_data="account-0:" + str(message_id)))
        else:
            markup.add(InlineKeyboardButton("👤 Профиль", callback_data="profile:" + str(message_id)))
        markup.row(InlineKeyboardButton("💳 Об оплате", callback_data="about_payment:" + str(message_id)),
                   InlineKeyboardButton("ⓘ Информация", callback_data="info:" + str(message_id)))
        return markup

    async def profile_info(self, user_id, username, message_id = None):
        user = self._db.get_user_by_user_id(user_id)
        date_to_join = time.ctime()
        accounts = self._db.get_accounts_by_user_id(user_id)
        accounts_count = len(accounts)
        referals_count = 0
        reply_message = self._tm_manager.get_profile_info_message(user_id, username, date_to_join,
                                                                  accounts_count, referals_count)
        if not message_id is None:
            await self._bot.edit_message_text(chat_id=user_id, message_id=message_id, text=reply_message,
                                              reply_markup=self._profile_info_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            print(message)
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id, message_id=message_id, text=reply_message, reply_markup=self._profile_info_markup_gen(message_id))

    def _profile_info_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💰 Пополнить баланс", callback_data="top_up_balance:"+str(message_id)))
        markup.add(InlineKeyboardButton("🧑‍🤝‍🧑 Реферальная программа", callback_data="referal_program:"+str(message_id)))
        markup.add(InlineKeyboardButton(" 🔙 Назад", callback_data="back_for_profile_info:"+str(message_id)))
        return markup

    async def top_up_balance(self, user_id, message_id = None):
        if message_id:
            await self._bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Выберете способ оплаты:",
                                              reply_markup=self._top_up_balance_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Выберете способ оплаты:", reply_markup=self._top_up_balance_markup_gen(message_id))

    def _top_up_balance_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("₿ Cryptobot", callback_data="cryptobot_top_up:"+str(message_id)))
        markup.add(InlineKeyboardButton(" 🔙 Назад", callback_data="back_from_top_up_balance:"+str(message_id)))
        return markup

    async def referal_info(self, user_id, message_id = None):
        user = self._db.get_user_by_user_id(user_id)
        referals = self._db.get_user_referals(user_id)
        referal_count = len(referals)
        referal_link = "https://t.me/parserhb_bot?start="+user.referal_link
        if message_id:
            await self._bot.edit_message_text(chat_id=user_id, text=self._tm_manager.get_referal_info_message(referal_count, referal_link),
                                              message_id=message_id, reply_markup=self._referal_info_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=self._tm_manager.get_referal_info_message(referal_count,
                                                                                             referal_link),
                                              message_id=message_id,
                                              reply_markup=self._referal_info_markup_gen(message_id))

    def _referal_info_markup_gen(self, message_id:int):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(" 🔙 Назад", callback_data="back_from_referal_info:"+str(message_id)))
        return markup

    async def bot_info(self, user_id:int, message_id = None):
        if message_id:
            await self._bot.edit_message_text(chat_id=user_id, text=self._tm_manager.get_bot_info(),
                                              message_id=message_id, reply_markup=self._bot_info_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=self._tm_manager.get_bot_info(),
                                              message_id=message_id,
                                              reply_markup=self._bot_info_markup_gen(message_id))
    def _bot_info_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👨🏻‍💻 Техническая поддержка", callback_data="support:" + str(message_id)))
        markup.add(InlineKeyboardButton(" 🔙 Назад", callback_data="back_from_bot_info:" + str(message_id)))
        return markup

    async def pay_info(self, user_id, message_id = None):
        if message_id:
            await self._bot.edit_message_text(chat_id=user_id, text=self._tm_manager.get_pay_info(),
                                              message_id=message_id, reply_markup=self._pay_info_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=self._tm_manager.get_pay_info(),
                                              message_id=message_id,
                                              reply_markup=self._pay_info_markup_gen(message_id))

    def _pay_info_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(" 🔙 Назад", callback_data="back_from_pay_info:" + str(message_id)))
        return markup

    async def support_info(self, user_id, message_id = None):
        if message_id:
            await self._bot.edit_message_text(chat_id=user_id, text=self._tm_manager.get_support_info(),
                                              message_id=message_id, reply_markup=self._support_info_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=self._tm_manager.get_support_info(),
                                              message_id=message_id,
                                              reply_markup=self._support_info_markup_gen(message_id))
    def _support_info_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🎫 Написать в тех поддержку", url="vk.com"))
        markup.add(InlineKeyboardButton(" 🔙 Назад", callback_data="back_from_support:" + str(message_id)))
        return markup

    async def accounts(self, user_id:int, account_index:int, message_id = None):
        from DBManager import Account
        accounts = self._db.get_accounts_by_user_id(user_id)
        if len(accounts) == 0:
            accounts_count = 0
            account_index = 0
            account = None
        else:
            account = accounts[account_index]
            accounts_count = len(accounts)
        if message_id:
            await self._bot.edit_message_text(chat_id=user_id, text=self._tm_manager.accounts_view(account_index+1, accounts_count, account),
                                              message_id=message_id, reply_markup=self._accounts_markup_gen(message_id, account_index, accounts_count, account.account_status))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=self._tm_manager.accounts_view(account_index+1, accounts_count, account),
                                              message_id=message_id,
                                              reply_markup=self._accounts_markup_gen(message_id, account_index, accounts_count, account.account_status))

    def _accounts_markup_gen(self, message_id, account_index: int, max_accounts: int, is_active:bool):
        markup = InlineKeyboardMarkup()
        if is_active:
            settings_btn = InlineKeyboardButton("⚙️", callback_data="account_settings-" + str(account_index) + ":" + str(message_id))
        else:
            settings_btn = InlineKeyboardButton("Активировать",
                                                callback_data="reactivate_account-" + str(account_index) + ":" + str(
                                                    message_id))
        markup.row(
            InlineKeyboardButton("⬅️", callback_data="account-" + str(
                account_index - 1 if account_index > 0 else account_index) + ":" + str(message_id)),
            settings_btn,
            InlineKeyboardButton("➡️", callback_data="account-" + str(
                account_index + 1 if account_index < max_accounts else account_index) + ":" + str(message_id))
        )
        markup.add(InlineKeyboardButton("Деактивировать аккаунт", callback_data="deactive_account-"+str(account_index)+":" + str(message_id)))
        markup.add(InlineKeyboardButton("➕ Добавить аккаунт", callback_data="add_account:" + str(message_id)))
        markup.add(InlineKeyboardButton(" 🔙 Назад", callback_data="back_from_account_view:" + str(message_id)))
        return markup

    async def reactivate_account(self, user_id, account_index, message_id):
        account = self._db.get_account_by_index(user_id, account_index)
        await self.phone_entered(user_id, account.phone, True)

    async def deactive_account(self, user_id, account_index, message_id):
        account = self._db.get_account_by_index(user_id, account_index)
        self._db.deactive_account(account.phone)
        await self.accounts(user_id, account_index, message_id)

    async def add_account(self, user_id, message_id):
        if message_id:
            message = await self._bot.edit_message_text(chat_id=user_id, text="Введите номер телефона в формате \"+79999999999\"",
                                              message_id=message_id, reply_markup=self._add_account_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            message_id = message.message_id
            message = await self._bot.edit_message_text(chat_id=user_id,
                                              text="Введите номер телефона в формате \"+79999999999\"",
                                              message_id=message_id,
                                              reply_markup=self._add_account_markup_gen(message_id))
    def _add_account_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(" 🔙 Назад", callback_data="back_from_account_view:"+str(message_id)))
        return markup

    async def phone_entered(self, user_id, phone, reactivate = False):
        if self._db.is_account_exist(phone) and not reactivate:
            await self._bot.send_message(user_id, "Этот аккаунт уже подключен.")
            return False
        if len(self._db.get_unused_proxy()) == 0:
            await self._bot.send_message(user_id, "У нас нет свободных прокси( Попробуйте позже.")
            await self._bot.delete_state(user_id)
        proxy = self._db.get_unused_proxy()[0]
        account = AccountManager(phone, proxy)
        await account.auth()
        self._connecting_accounts[user_id] = {"account":account,"proxy_id":proxy.id}
        await self._bot.send_message(user_id, "Введите код который прийдет в на ваш аккаунт.")
        return True

    async def code_entered(self, user_id, code):
        account = self._connecting_accounts[user_id]["account"]
        proxy_id = self._connecting_accounts[user_id]["proxy_id"]
        if await account.connect_and_authorize(code):
            if self._db.is_account_exist(account.get_phone()):
                message = await self._bot.send_message(user_id, "Аккаунт подключен.")
                self._db.activate_account(account.phone_number)
                self._db.set_account_proxy(account.phone_number, proxy_id)
                await self.accounts(user_id, 0, message.message_id)
                return
            if DBManager.GOOD == self._db.add_account(account.get_phone(), user_id, proxy_id,False, True):
                message = await self._bot.send_message(user_id, "Аккаунт подключен.")
            elif DBManager.EXIST == self._db.add_account(account.get_phone(), user_id, proxy_id,False, True):
                message = await self._bot.send_message(user_id, "Аккаунт уже подключен.")
            elif DBManager.EXIST == self._db.add_account(account.get_phone(), user_id, proxy_id,False, True):
                message = await self._bot.send_message(user_id, "У нас не хватает прокси, добавьте аккаунт позднее!")
            await self.accounts(user_id, 0, message.message_id)

    async def account_settings(self, user_id, account_index, message_id = None):
        accounts = self._db.get_accounts_by_user_id(user_id)
        account = accounts[account_index]
        phone = account.phone
        interval = str(account.interval)
        message = account.message_to_send
        speed = str(account.speed)
        cooldown = str(account.cooldown)
        groups = ""
        acc = AccountManager(phone)
        if await acc.auth() == AccountManager.AUTHORISED:
            print("Authenticated successfully")
            chats = await acc.get_chats_from()
        else:
            await self._bot.send_message(user_id, "Не удалось подключиться к аккаунту! Аккаунт будет автоматически удален.")
            self._db.delete_account(phone)
        for chat in chats:
            groups += "\n"+chat["name"]
        if message_id is not None:
            await self._bot.edit_message_text(chat_id=user_id, text=self._tm_manager.account_settings(phone, groups, interval, message, speed, cooldown),
                                              message_id=message_id, reply_markup=self._account_settings_markup_gen(user_id, message_id, account_index))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=self._tm_manager.account_settings(phone, groups, interval, message, speed, cooldown),
                                              message_id=message_id,
                                              reply_markup=self._account_settings_markup_gen(user_id, message_id, account_index))
    def _account_settings_markup_gen(self,user_id, message_id, account_index):
        account = self._db.get_account_by_index(user_id, account_index)
        is_sending = account.send_status
        markup = InlineKeyboardMarkup()
        if is_sending:
            markup.add(InlineKeyboardButton("⛔ Остановить",
                                            callback_data="stop_account-" + str(account_index) + ":" + str(
                                                message_id)))
        else:
            markup.add(InlineKeyboardButton("🚀 Запустить", callback_data="start_account-"+str(account_index)+":"+str(message_id)))
        markup.add(
            InlineKeyboardButton("🗑️ Удалить", callback_data="delete_account-" + str(account_index) + ":" + str(message_id)))
        markup.add(
            InlineKeyboardButton("✉️ Изменить сообщение", callback_data="change_message-" + str(account_index) + ":" + str(message_id)))
        markup.add(
            InlineKeyboardButton("🕒 Изменить интервал",
                                 callback_data="change_interval-" + str(account_index) + ":" + str(message_id)))
        markup.add(
            InlineKeyboardButton("🏎️ Изменить скорость",
                                 callback_data="change_speed-" + str(account_index) + ":" + str(message_id)))
        markup.add(
            InlineKeyboardButton("🔄 Обнулить к/д",
                                 callback_data="skip_cooldown-" + str(account_index) + ":" + str(message_id)))
        markup.add(
            InlineKeyboardButton(" 🔙 Назад",
                                 callback_data="account-" + str(account_index) + ":" + str(message_id)))
        return markup

    async def change_account_message_start(self, user_id, account_index, message_id):
        account = self._db.get_account_by_index(user_id, account_index)
        self._edit_account[user_id] = account
        await self._bot.edit_message_text(chat_id=user_id, text="Напишите текст, который аккаунт должен отправлять.",
                                          message_id=message_id, reply_markup=self._change_account_markup_gen(message_id, account_index))

    async def change_account_message_end(self, user_id, message):
        account = self._edit_account[user_id]
        self._db.update_account_message(account.phone, message)
        message = await self._bot.send_message(user_id, "Сообщение установлено!")
        await self.account_settings(user_id, self._db.get_account_index(user_id, account.phone), message.message_id)

    def _change_account_markup_gen(self, message_id, account_index):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(" 🔙 Назад", callback_data="account-"+str(account_index)+":"+str(message_id)))
        return markup

    async def delete_account(self, user_id, account_index, message_id):
        self._db.delete_account(self._db.get_account_by_index(user_id, account_index).phone)
        await self.accounts(user_id, 0, message_id)

    async def change_account_interval_start(self, user_id, account_index, message_id):
        account = self._db.get_account_by_index(user_id, account_index)
        self._edit_account[user_id] = account
        await self._bot.edit_message_text(chat_id=user_id, text="Напишите интервал. (Интервал - промежуток времени между рассылкой во все группы)",
                                          message_id=message_id,
                                          reply_markup=self._change_account_markup_gen(message_id, account_index))

    async def change_account_interval_end(self, user_id, message):
        interval = ""
        for ch in message:
            if ch in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                interval += ch
        account = self._edit_account[user_id]
        self._db.update_account_interval(account.phone, int(interval))
        message = await self._bot.send_message(user_id, "Интервал установлен!")
        await self.account_settings(user_id, self._db.get_account_index(user_id, account.phone), message.message_id)

    async def change_account_speed_start(self, user_id, account_index, message_id):
        account = self._db.get_account_by_index(user_id, account_index)
        self._edit_account[user_id] = account
        await self._bot.edit_message_text(chat_id=user_id, text="Укажите новую скорость рассылки (Скорость рассылки - промежуток времени между отправкой сообщений).",
                                          message_id=message_id,
                                          reply_markup=self._change_account_markup_gen(message_id, account_index))

    async def change_account_speed_end(self, user_id, message):
        speed = ""
        for ch in message:
            if ch in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                speed += ch
        account = self._edit_account[user_id]
        self._db.update_account_speed(account.phone, int(speed))
        message = await self._bot.send_message(user_id, "Скорость установлена!")
        await self.account_settings(user_id, self._db.get_account_index(user_id, account.phone), message.message_id)

    async def start_account(self, user_id, account_index, message_id):
        account = self._db.get_account_by_index(user_id, account_index)
        self._db.set_user_first_start(user_id, 1)
        self._db.update_account_send_status(account.phone, True)
        await self.account_settings(user_id, account_index, message_id)

    async def stop_account(self, user_id, account_index, message_id):
        account = self._db.get_account_by_index(user_id, account_index)
        self._db.update_account_send_status(account.phone, False)
        await self.account_settings(user_id, account_index, message_id)

    async def skip_cooldown(self, user_id, account_index, message_id):
        account = self._db.get_account_by_index(user_id, account_index)
        if account:
            self._db.clear_account_cooldown(account.phone)
            await self.account_settings(user_id, account_index, message_id)
        else:
            await self.user_info(user_id, message_id)

    async def admin_panel(self, user_id, message_id=None):
        if message_id is not None:
            await self._bot.edit_message_text(chat_id=user_id, text="Выберите действие",
                                              message_id=message_id, reply_markup=self._admin_panel_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text="Выберите действие",
                                              message_id=message_id,
                                              reply_markup=self._admin_panel_markup_gen(message_id))

    def _admin_panel_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Прокси", callback_data="admin-proxy:"+str(message_id)))
        markup.add(InlineKeyboardButton("Аккаунты", callback_data="admin-accounts:" + str(message_id)))
        markup.add(InlineKeyboardButton("Юзеры", callback_data="admin-users:" + str(message_id)))
        markup.add(InlineKeyboardButton("Редактировать сообщения", callback_data="admin-messages:" + str(message_id)))
        return markup

    async def edit_messages(self, user_id, message_id=None):
        text = "Редактирование шаблонов сообщений"
        if message_id is not None:
            await self._bot.edit_message_text(chat_id=user_id, text=text,
                                              message_id=message_id, reply_markup=self._edit_messages_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=text,
                                              message_id=message_id,
                                              reply_markup=self._edit_messages_markup_gen(message_id))

    def _edit_messages_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Об оплате", callback_data="admin-edit_message-about_pay:"+str(message_id)))
        markup.add(InlineKeyboardButton("Настройки аккаунта", callback_data="admin-edit_message-account_settings:" + str(message_id)))
        markup.add(InlineKeyboardButton("Панель аккаунтов", callback_data="admin-edit_message-accounts_view:" + str(message_id)))
        markup.add(InlineKeyboardButton("Первое сообщение", callback_data="admin-edit_message-first_message:" + str(message_id)))
        markup.add(InlineKeyboardButton("Информация", callback_data="admin-edit_message-info:" + str(message_id)))
        markup.add(InlineKeyboardButton("Окно профиля", callback_data="admin-edit_message-profile_info:" + str(message_id)))
        markup.add(InlineKeyboardButton("Окно реферальной системы", callback_data="admin-edit_message-referal_info:" + str(message_id)))
        markup.add(InlineKeyboardButton("Поддержка", callback_data="admin-edit_message-support:" + str(message_id)))
        markup.add(InlineKeyboardButton("Окно юзера", callback_data="admin-edit_message-user_info:" + str(message_id)))
        markup.add(InlineKeyboardButton("Назад", callback_data="admin-back:" + str(message_id)))
        return markup

    async def edit_msg_start(self, user_id, message_id, msg):
        print(msg)
        text = "Шаблон сообщения: "
        if msg == "about_pay":
            text = text + self._tm_manager.get_default_about_pay()
        if msg == "account_settings":
            text = text + self._tm_manager.get_default_accounts_settings()
        if msg == "accounts_view":
            text = text + self._tm_manager.get_default_accounts_view()
        if msg == "first_message":
            text = text + self._tm_manager.get_default_start_message()
        if msg == "info":
            text = text + self._tm_manager.get_default_bot_info()
        if msg == "profile_info":
            text = text + self._tm_manager.get_default_profile_info_template()
        if msg == "referal_info":
            text = text + self._tm_manager.get_default_referal_info()
        if msg == "support":
            text = text + str(self._tm_manager.get_default_support())
        if msg == "user_info":
            text = text + self._tm_manager._user_info_temlate()
        await self._bot.edit_message_text(chat_id=user_id,
                                          text=text,
                                          message_id=message_id,
                                          reply_markup=self._edit_msg_markup_gen(message_id))

    def _edit_msg_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Назад", callback_data="admin-back:" + str(message_id)))
        return markup


    async def admin_proxy(self, user_id, message_id):
        proxies = self._db.get_all_proxies()
        text = "Кол-во прокси: " + str(len(proxies))
        work_proxies = self._db.get_used_proxy()
        text += "\nКол-во работающих прокси: " + str(len(work_proxies))
        for proxy in proxies:
            text += f"\n{proxy.host}:{proxy.port}@{proxy.username}:{proxy.password}"
        if message_id is not None:
            await self._bot.edit_message_text(chat_id=user_id, text=text,
                                              message_id=message_id, reply_markup=self._admin_proxy_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=text,
                                              message_id=message_id,
                                              reply_markup=self._admin_proxy_markup_gen(message_id))

    def _admin_proxy_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Добавить прокси", callback_data="admin-add_proxy:" + str(message_id)))
        markup.add(InlineKeyboardButton("Назад", callback_data="admin-back:"+str(message_id)))
        return markup

    async def admin_add_proxy_start(self, user_id, message_id = None):
        text = "Отправьте пожалуйста прокси в формате:\nlogin:password@host:port\nlogin:password@host:port"
        if message_id is not None:
            await self._bot.edit_message_text(chat_id=user_id, text=text,
                                              message_id=message_id,
                                              reply_markup=self._back_to_admin_markup(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=text,
                                              message_id=message_id,
                                              reply_markup=self._back_to_admin_markup(message_id))

    def _back_to_admin_markup(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Назад", callback_data="admin-back:" + str(message_id)))
        return markup

    async def admin_add_proxy_end(self, user_id, proxies_str):
        proxies = proxies_str.split("\n")
        for proxy in proxies:
            try:
                proxy_login = proxy.split("@")[0].split(":")[0]
                proxy_password = proxy.split("@")[0].split(":")[1]
                proxy_host = proxy.split("@")[1].split(":")[0]
                proxy_port = proxy.split("@")[1].split(":")[1]
                self._db.add_proxy(proxy_host, proxy_port, proxy_login, proxy_password)
            except:
                pass
        await self.admin_panel(user_id)

    async def admin_users(self, user_id, message_id = None):
        text = "Информация о юзерах"
        if message_id is not None:
            await self._bot.edit_message_text(chat_id=user_id, text=text,
                                              message_id=message_id, reply_markup=self._admin_users_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=text,
                                              message_id=message_id,
                                              reply_markup=self._admin_users_markup_gen(message_id))

    def _admin_users_markup_gen(self,message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Назад", callback_data="admin-back:" + str(message_id)))
        return markup

    async def admin_accounts(self, user_id, message_id = None):
        text = "Информация о аккаунтах"
        if message_id is not None:
            await self._bot.edit_message_text(chat_id=user_id, text=text,
                                              message_id=message_id, reply_markup=self._admin_accounts_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите ↻")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=text,
                                              message_id=message_id,
                                              reply_markup=self._admin_accounts_markup_gen(message_id))

    def _admin_accounts_markup_gen(self,message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Назад", callback_data="admin-back:" + str(message_id)))
        return markup