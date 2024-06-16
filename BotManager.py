from telebot.async_telebot import AsyncTeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from TMessagesManager import TMessagesManager
import time
from DBManager import DBManager, User, Account
from AccountManager import AccountManager
from typing import Dict


class BotManager:
    def __init__(self, bot:AsyncTeleBot, db_url:str):
        self._tm_manager = TMessagesManager()
        self._bot = bot
        self._db = DBManager(db_url)
        self._connecting_accounts:Dict[int, AccountManager] = {}
        self._edit_account:Dict[int, Account] = {}


    async def new_user(self, message):
        user_id = message.chat.id
        username = message.from_user.username
        if self._db.add_user(user_id, username, "", 0, "", 0):
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton("👤 Мой профиль"))
            await self._bot.send_message(user_id, self._tm_manager.get_start_message(), reply_markup=markup)
        else:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton("👤 Мой профиль"))
            await self._bot.send_message(user_id, "👋🏻 С возвращением!🤓\nПриятно видеть Вас снова!", reply_markup=markup)

    async def user_info(self, user_id, message_id = None):
        user = self._db.get_user_by_user_id(user_id)
        days_left = user.days_left
        reply_message = self._tm_manager.get_user_info_message(1,1,1, 0, days_left)
        if not message_id is None:
            await self._bot.edit_message_text(chat_id=user_id, message_id=message_id, text=reply_message,
                                              reply_markup=self._user_info_markup_gen(user_id, message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите")
            print(message)
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id, message_id=message_id, text=reply_message, reply_markup=self._user_info_markup_gen(user_id, message_id))

    def _user_info_markup_gen(self, user_id, message_id:int):
        user = self._db.get_user_by_user_id(user_id)
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(InlineKeyboardButton("Профиль", callback_data="profile:"+str(message_id)))
        if user.days_left > 0:
            markup.add(InlineKeyboardButton("Мои аккаунты", callback_data="account-0:" + str(message_id)))
        markup.add(InlineKeyboardButton("Об оплате", callback_data="about_payment:" + str(message_id)))
        markup.add(InlineKeyboardButton("Информация", callback_data="info:" + str(message_id)))
        return markup

    async def profile_info(self, user_id, username, message_id = None):
        user = self._db.get_user_by_user_id(user_id)
        date_to_join = time.ctime()
        balance = user.balance
        accounts_count = 0
        referals_count = 0
        reply_message = self._tm_manager.get_profile_info_message(user_id, username, date_to_join, balance,
                                                                  accounts_count, referals_count)
        if not message_id is None:
            await self._bot.edit_message_text(chat_id=user_id, message_id=message_id, text=reply_message,
                                              reply_markup=self._profile_info_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите")
            print(message)
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id, message_id=message_id, text=reply_message, reply_markup=self._profile_info_markup_gen(message_id))

    def _profile_info_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Пополнить баланс", callback_data="top_up_balance:"+str(message_id)))
        markup.add(InlineKeyboardButton("Реферальная программа", callback_data="referal_program:"+str(message_id)))
        markup.add(InlineKeyboardButton("Назад", callback_data="back_for_profile_info:"+str(message_id)))
        return markup

    async def top_up_balance(self, user_id, message_id = None):
        if message_id:
            await self._bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Выберете способ оплаты:",
                                              reply_markup=self._top_up_balance_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Выберете способ оплаты:", reply_markup=self._top_up_balance_markup_gen(message_id))

    def _top_up_balance_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Cryptobot", callback_data="cryptobot_top_up:"+str(message_id)))
        markup.add(InlineKeyboardButton("Назад", callback_data="back_from_top_up_balance:"+str(message_id)))
        return markup

    async def referal_info(self, user_id, message_id = None):
        referal_count = 0
        referal_link = "123"
        if message_id:
            await self._bot.edit_message_text(chat_id=user_id, text=self._tm_manager.get_referal_info_message(referal_count, referal_link),
                                              message_id=message_id, reply_markup=self._referal_info_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=self._tm_manager.get_referal_info_message(referal_count,
                                                                                             referal_link),
                                              message_id=message_id,
                                              reply_markup=self._referal_info_markup_gen(message_id))

    def _referal_info_markup_gen(self, message_id:int):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Назад", callback_data="back_from_referal_info:"+str(message_id)))
        return markup

    async def bot_info(self, user_id:int, message_id = None):
        if message_id:
            await self._bot.edit_message_text(chat_id=user_id, text=self._tm_manager.get_bot_info(),
                                              message_id=message_id, reply_markup=self._bot_info_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=self._tm_manager.get_bot_info(),
                                              message_id=message_id,
                                              reply_markup=self._bot_info_markup_gen(message_id))
    def _bot_info_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Техническая поддержка", callback_data="support:" + str(message_id)))
        markup.add(InlineKeyboardButton("Назад", callback_data="back_from_bot_info:" + str(message_id)))
        return markup

    async def pay_info(self, user_id, message_id = None):
        if message_id:
            await self._bot.edit_message_text(chat_id=user_id, text=self._tm_manager.get_pay_info(),
                                              message_id=message_id, reply_markup=self._pay_info_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=self._tm_manager.get_pay_info(),
                                              message_id=message_id,
                                              reply_markup=self._pay_info_markup_gen(message_id))

    def _pay_info_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Назад", callback_data="back_from_pay_info:" + str(message_id)))
        return markup

    async def support_info(self, user_id, message_id = None):
        if message_id:
            await self._bot.edit_message_text(chat_id=user_id, text=self._tm_manager.get_support_info(),
                                              message_id=message_id, reply_markup=self._support_info_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=self._tm_manager.get_support_info(),
                                              message_id=message_id,
                                              reply_markup=self._support_info_markup_gen(message_id))
    def _support_info_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Написать в тех поддержку", url="vk.com"))
        markup.add(InlineKeyboardButton("Назад", callback_data="back_from_support:" + str(message_id)))
        return markup

    async def accounts(self, user_id:int, account_index:int, message_id = None):
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
                                              message_id=message_id, reply_markup=self._accounts_markup_gen(message_id, account_index, accounts_count))
        else:
            message = await self._bot.send_message(user_id, "Подождите")
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id,
                                              text=self._tm_manager.accounts_view(account_index+1, accounts_count, account),
                                              message_id=message_id,
                                              reply_markup=self._accounts_markup_gen(message_id, account_index, accounts_count))

    def _accounts_markup_gen(self, message_id, account_index: int, max_accounts: int):
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("⬅️", callback_data="account-" + str(
                account_index - 1 if account_index > 0 else account_index) + ":" + str(message_id)),
            InlineKeyboardButton("⚙️", callback_data="account_settings-" + str(account_index) + ":" + str(message_id)),
            InlineKeyboardButton("➡️", callback_data="account-" + str(
                account_index + 1 if account_index < max_accounts else account_index) + ":" + str(message_id))
        )
        markup.add(InlineKeyboardButton("Добавить аккаунт", callback_data="add_account:" + str(message_id)))
        markup.add(InlineKeyboardButton("Назад", callback_data="back_from_account_view:" + str(message_id)))
        return markup

    async def add_account(self, user_id, message_id):
        if message_id:
            message = await self._bot.edit_message_text(chat_id=user_id, text="Введите номер телефона в формате \"+79999999999\"",
                                              message_id=message_id, reply_markup=self._add_account_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите")
            message_id = message.message_id
            message = await self._bot.edit_message_text(chat_id=user_id,
                                              text="Введите номер телефона в формате \"+79999999999\"",
                                              message_id=message_id,
                                              reply_markup=self._add_account_markup_gen(message_id))
    def _add_account_markup_gen(self, message_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Назад", callback_data="back_from_account_view:"+str(message_id)))
        return markup

    async def phone_entered(self, user_id, phone):
        if self._db.is_account_exist(phone):
            await self._bot.send_message(user_id, "Этот аккаунт уже подключен.")
            return False
        account = AccountManager(phone)
        await account.auth()
        self._connecting_accounts[user_id] = account
        await self._bot.send_message(user_id, "Введите код который прийдет в на ваш аккаунт.")
        return True

    async def code_entered(self, user_id, code):
        account = self._connecting_accounts[user_id]
        if await account.connect_and_authorize(code):
            self._db.add_account(account.get_phone(), user_id, False, True)
            await self._bot.send_message(user_id, "Аккаунт подключен.")

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
        if await acc.auth():
            print("Authenticated successfully")
            chats = await acc.get_chats_from()
        else:
            await self._bot.send_message(user_id, "Не удалось подключиться к аккаунту! Аккаунт будет автоматически удален.")
        for chat in chats:
            groups += "\n"+chat["name"]
        if message_id is not None:
            await self._bot.edit_message_text(chat_id=user_id, text=self._tm_manager.account_settings(phone, groups, interval, message, speed, cooldown),
                                              message_id=message_id, reply_markup=self._account_settings_markup_gen(user_id, message_id, account_index))
        else:
            message = await self._bot.send_message(user_id, "Подождите")
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
            markup.add(InlineKeyboardButton("Остановить",
                                            callback_data="stop_account-" + str(account_index) + ":" + str(
                                                message_id)))
        else:
            markup.add(InlineKeyboardButton("Запустить", callback_data="start_account-"+str(account_index)+":"+str(message_id)))
        markup.add(
            InlineKeyboardButton("Удалить", callback_data="delete_account-" + str(account_index) + ":" + str(message_id)))
        markup.add(
            InlineKeyboardButton("Изменить сообщение", callback_data="change_message-" + str(account_index) + ":" + str(message_id)))
        markup.add(
            InlineKeyboardButton("Изменить интервал",
                                 callback_data="change_interval-" + str(account_index) + ":" + str(message_id)))
        markup.add(
            InlineKeyboardButton("Изменить скорость",
                                 callback_data="change_speed-" + str(account_index) + ":" + str(message_id)))
        markup.add(
            InlineKeyboardButton("Назад",
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
        markup.add(InlineKeyboardButton("Назад", callback_data="account-"+str(account_index)+":"+str(message_id)))
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
        self._db.update_account_send_status(account.phone, True)
        await self.account_settings(user_id, account_index, message_id)

    async def stop_account(self, user_id, account_index, message_id):
        account = self._db.get_account_by_index(user_id, account_index)
        self._db.update_account_send_status(account.phone, False)
        await self.account_settings(user_id, account_index, message_id)
