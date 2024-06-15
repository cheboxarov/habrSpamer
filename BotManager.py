from telebot.async_telebot import AsyncTeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from TMessagesManager import TMessagesManager
import time
from DBManager import DBManager, User
from typing import List


class BotManager:
    def __init__(self, bot:AsyncTeleBot, db_url:str):
        self._tm_manager = TMessagesManager()
        self._bot = bot
        self._db = DBManager(db_url)

    async def new_user(self, message):
        user_id = message.chat.id
        username = message.from_user.username
        if self._db.add_user(user_id, username, "", 0, ""):
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton("👤 Мой профиль"))
            await self._bot.send_message(user_id, self._tm_manager.get_start_message(), reply_markup=markup)
        else:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton("👤 Мой профиль"))
            await self._bot.send_message(user_id, "👋🏻 С возвращением!🤓\nПриятно видеть Вас снова!", reply_markup=markup)

    async def user_info(self, user_id, message_id = None):
        user = self._db.get_user_by_user_id(user_id)
        balance = user.balance
        reply_message = self._tm_manager.get_user_info_message(1,1,1,balance,1)
        if not message_id is None:
            await self._bot.edit_message_text(chat_id=user_id, message_id=message_id, text=reply_message,
                                              reply_markup=self._user_info_markup_gen(message_id))
        else:
            message = await self._bot.send_message(user_id, "Подождите")
            print(message)
            message_id = message.message_id
            await self._bot.edit_message_text(chat_id=user_id, message_id=message_id, text=reply_message, reply_markup=self._user_info_markup_gen(message_id))

    def _user_info_markup_gen(self, message_id:int):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(InlineKeyboardButton("Профиль", callback_data="profile:"+str(message_id)))
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
            InlineKeyboardButton("⚙️", callback_data="account_settings-" + str(
                account_index - 1 if account_index > 0 else account_index) + ":" + str(message_id)),
            InlineKeyboardButton("➡️", callback_data="account-" + str(
                account_index + 1 if account_index < max_accounts else account_index) + ":" + str(message_id))
        )
        markup.add(InlineKeyboardButton("Добавить аккаунт", callback_data="add_account:" + str(message_id)))
        markup.add(InlineKeyboardButton("Назад", callback_data="back_from_account_view:" + str(message_id)))
        return markup