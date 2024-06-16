from DBManager import Account


class TMessagesManager:
    def __init__(self):
        import os.path
        if not os.path.exists("messages_template"):
            raise ValueError("Нет папки с шаблонами сообщений!")

        if not os.path.exists("messages_template/first_message.txt"):
            raise ValueError("Нет шаблона для первичного сообщения (messages_template/first_message.txt)!")
        self._start_message = open("messages_template/first_message.txt", "r", encoding="utf-8").read()

        if not os.path.exists("messages_template/user_info.txt"):
            raise ValueError("Нет шаблона информации по юзеру (messages_template/user_info.txt)!")
        self._user_info_temlate = open("messages_template/user_info.txt", "r", encoding="utf-8").read()

        if not os.path.exists("messages_template/profile_info.txt"):
            raise ValueError("Нет шаблона информации по профилю (messages_template/profile_info.txt)!")
        self._profile_info_template = open("messages_template/profile_info.txt", "r", encoding="utf-8").read()

        if not os.path.exists("messages_template/referal_info.txt"):
            raise ValueError("Нет шаблона информации по рефералке (messages_template/referal_info.txt)!")
        self._referal_info = open("messages_template/referal_info.txt", "r", encoding="utf-8").read()

        if not os.path.exists("messages_template/about_pay.txt"):
            raise ValueError("Нет шаблона информации по оплате (messages_template/about_pay.txt)!")
        self._about_pay = open("messages_template/about_pay.txt", "r", encoding="utf-8").read()

        if not os.path.exists("messages_template/info.txt"):
            raise ValueError("Нет шаблона информации по боту (messages_template/info.txt)!")
        self._bot_info = open("messages_template/info.txt", "r", encoding="utf-8").read()

        if not os.path.exists("messages_template/support.txt"):
            raise ValueError("Нет шаблона информации по тех. поддержке (messages_template/support.txt)!")
        self._support = open("messages_template/support.txt", "r", encoding="utf-8").read()

        if not os.path.exists("messages_template/accounts_view.txt"):
            raise ValueError("Нет шаблона отображения аккаунтов (messages_template/accounts_view.txt)!")
        self._accounts_view = open("messages_template/accounts_view.txt", "r", encoding="utf-8").read()

        if not os.path.exists("messages_template/account_settings.txt"):
            raise ValueError("Нет шаблона настройки аккаунтов (messages_template/account_settings.txt)!")
        self._accounts_settings = open("messages_template/account_settings.txt", "r", encoding="utf-8").read()

    def get_start_message(self):
        return self._start_message

    def get_user_info_message(self, accounts_count:int, work_accounts_cout:int,
                              work_accounts_sale:int, balance:int, time_to_work_accounts:int):
        user_info_str = self._user_info_temlate.replace("WORK_ACCOUNTS_COUNT", str(work_accounts_cout))
        user_info_str = user_info_str.replace("ACCOUNTS_COUNT", str(accounts_count))
        user_info_str = user_info_str.replace("WORK_ACCOUNTS_SALE", str(work_accounts_sale))
        user_info_str = user_info_str.replace("BALANCE", str(balance))
        if time_to_work_accounts <= 0:
            time_to_work_accounts = "нисколько"
        user_info_str = user_info_str.replace("TIME_TO_WORK_ACCOUNTS", str(time_to_work_accounts)+" дней")
        return user_info_str

    def get_profile_info_message(self, user_id:int, user_nickname:str, date_to_join:str, balance:int, accounts_count:int, referals_count:int):
        profile_info_str = self._profile_info_template.replace("USER_ID", str(user_id))
        profile_info_str = profile_info_str.replace("USER_NICKNAME", user_nickname)
        profile_info_str = profile_info_str.replace("DATE_TO_JOIN", date_to_join)
        profile_info_str = profile_info_str.replace("REFERALS_COUNT", str(referals_count))
        profile_info_str = profile_info_str.replace("ACCOUNTS_COUNT", str(accounts_count))
        profile_info_str = profile_info_str.replace("BALANCE", str(balance))
        return profile_info_str

    def get_referal_info_message(self, referal_count:int, referal_link:str):
        referal_info_str = self._referal_info.replace("REFERAL_COUNT", str(referal_count))
        referal_info_str = referal_info_str.replace("REFERAL_LINK", referal_link)
        return referal_info_str

    def get_pay_info(self):
        return self._about_pay

    def get_bot_info(self):
        return self._bot_info

    def get_support_info(self):
        return self._support

    def accounts_view(self, current_account, max_accounts, account:Account):
        account_view_str = self._accounts_view.replace("CURR_ACCOUNT", str(current_account))
        account_view_str = account_view_str.replace("MAX_ACCOUNTS", str(max_accounts))
        if account is None:
            return account_view_str.replace("ACCOUNT_TEMPLATE", "У вас нет подключенных аккаунтов...")
        account_info_str = f"Номер телефона: {account.phone}\n"
        account_info_str += "Статус рассылки: " + "Не работает" if not account.send_status else "Статус рассылки: " +"В работе"
        account_info_str += "\nСтатус аккаунта: " + "Подключен" if account.account_status else "Ошибка подключения"
        account_view_str = account_view_str.replace("ACCOUNT_TEMPLATE", account_info_str)
        return account_view_str

    def account_settings(self, phone, groups, interval, message, speed, cooldown):
        account_settings_view = self._accounts_settings.replace("PHONE", phone)
        account_settings_view = account_settings_view.replace("GROUPS", groups)
        account_settings_view = account_settings_view.replace("INTERVAL", str(interval))
        account_settings_view = account_settings_view.replace("MESSAGE", message)
        account_settings_view = account_settings_view.replace("SPEED", speed)
        account_settings_view = account_settings_view.replace("COOLDOWN", cooldown)
        return account_settings_view