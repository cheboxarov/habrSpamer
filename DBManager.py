from sqlalchemy import create_engine, Engine, MetaData, ForeignKey
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session, Query
from typing import Type


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    username = Column(String)
    referal_link = Column(String)
    balance = Column(Integer)
    referal_parent_id = Column(Integer)
    minutes_left = Column(Integer)
    first_start = Column(Integer, default=0)


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String)
    send_status = Column(Boolean)
    account_status = Column(Boolean)
    interval = Column(Integer)
    message_to_send = Column(String)
    last_statistic_start = Column(Integer)
    last_statistic_out = Column(Integer)
    last_statistic_sended = Column(Integer)
    speed = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    cooldown = Column(Integer, default=0)
    proxy_id = Column(Integer)
    photo_path = Column(String)
    has_photo = Column(Boolean, default=False)
    send_id = Column(Integer)
    minutes_left = Column(Integer,default=0)


class Proxy(Base):
    __tablename__ = "proxies"
    id = Column(Integer, primary_key=True, index=True)
    host = Column(String)
    port = Column(Integer)
    username = Column(String)
    password = Column(String)
    using = Column(Integer, default=0)


class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True, index=True)
    asset = Column(String)
    price_per_day = Column(Integer)


class CustomGroup(Base):
    __tablename__ = "custom_groups"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer)
    account_id = Column(Integer)
    is_custom = Column(Boolean, default=False)
    custom_message = Column(String)
    custom_photo_path = Column(String)
    has_photo = Column(Boolean, default=False)
    cooldown = Column(Integer, default=0)
    interval = Column(Integer, default=0)


psql_database = 'sqlite:///database.db'
engine = create_engine(psql_database)
session = Session(autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


class DBManager:
    NO_PROXY = -400
    GOOD = 0
    BAD_AUTH = -1
    EXIST = -3
    NOT_FOUND = -4
    NO_MONEY = -6

    def __init__(self, psql_database: str):
        self._engine = create_engine(psql_database)
        self._session = Session(autoflush=False, bind=self._engine)

    def add_group(self, group_id: int, account_id: int):
        if not self.is_group_exist(group_id, account_id):
            self._session.add(CustomGroup(group_id=group_id, account_id=account_id))
            self._session.commit()
            return self.GOOD
        return self.EXIST

    def edit_group_message(self,id:int, message: str):
        group = self.get_group_by_id(id)
        if group:
            group.custom_message = message
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def group_set_has_photo(self, id, has_photo):
        group = self.get_group_by_id(id)
        if group:
            group.has_photo = has_photo
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def group_set_photo_path(self, id, path):
        group = self.get_group_by_id(id)
        if group:
            group.custom_photo_path = path
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def group_set_interval(self, id, interval):
        group = self.get_group_by_id(id)
        if group:
            group.interval = interval
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def all_groups_cooldown_down(self):
        groups = self.get_all_groups()
        for group in groups:
            if group.cooldown > 0:
                group.cooldown = group.cooldown - 1
        self._session.commit()
        return self.GOOD

    def set_group_cooldown(self, id, cd):
        group = self.get_group_by_id(id)
        if group:
            group.cooldown = cd
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def get_all_groups(self):
        return self._session.query(CustomGroup).all()

    def group_cooldown_down(self, group_id, phone):
        account = self.get_account_by_phone(phone)
        if not account:
            return self.NOT_FOUND
        group = self.get_group_by_group_id(group_id, account.id)
        if not group:
            return self.NOT_FOUND
        group.cooldown = group.cooldown - 1
        self._session.commit()
        return self.GOOD

    def get_group_cooldown(self, group_id, phone):
        account = self.get_account_by_phone(phone)
        if not account:
            return self.NOT_FOUND
        group = self.get_group_by_group_id(group_id, account.id)
        if not group:
            return self.NOT_FOUND
        return group.cooldown

    def is_group_exist(self, group_id: int, account_id: int):
        return self._session.query(CustomGroup).filter(CustomGroup.group_id==group_id, CustomGroup.account_id==account_id).first() is not None

    def get_group_by_id(self, id: int):
        return self._session.query(CustomGroup).filter_by(id=id).first()

    def get_group_by_group_id(self, group_id: int, account_id: int):
        return self._session.query(CustomGroup).filter_by(group_id=group_id).filter_by(account_id=account_id).first()

    def group_set_custom(self, id, custom):
        group = self.get_group_by_id(id)
        if group is None:
            return self.NOT_FOUND
        group.is_custom = custom
        self._session.commit()
        return self.GOOD

    def get_price_per_day_by_asset(self, asset):
        return self._session.query(Price).filter_by(asset=asset).first().price_per_day

    def add_user(self, user_id: int, username: str, referal_link: str, balance: int, referal_parent_id: str,
                 minutes_left: int):
        if self.is_user_exist(user_id):
            return False
        new_user = User()
        new_user.user_id = user_id
        new_user.username = username
        new_user.referal_link = referal_link
        new_user.balance = balance
        new_user.referal_parent_id = referal_parent_id
        new_user.minutes_left = minutes_left
        self._session.add(new_user)
        self._session.commit()
        return True

    def get_users(self):
        return self._session.query(User).all()

    def add_user_minutes(self, user_id: int, minutes_left: int):
        user = self.get_user_by_user_id(user_id)
        if user:
            user.minutes_left = user.minutes_left + minutes_left
            session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def add_user_balance(self, user_id, money):
        user = self.get_user_by_user_id(user_id)
        if user:
            if user.referal_parent_id:
                if self.get_user_by_user_id(user.referal_parent_id):
                    us = self.get_user_by_user_id(user.referal_parent_id)
                    us.balance = us.balance + money / 100 * 10
            print("bal" + str(money))
            user.balance = user.balance + money
            session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def get_referals(self, refer):
        return self._session.query(User).filter(User.referal_parent_id==refer).all()

    def get_user_by_user_id(self, user_id: int) -> User:
        return self._session.query(User).filter(User.user_id == user_id).first()

    def is_user_exist(self, user_id: int) -> bool:
        return False if self.get_user_by_user_id(user_id) is None else True

    def is_user_first_start(self, user_id: int) -> bool:
        user = self.get_user_by_user_id(user_id)
        if user:
            return True if user.first_start == 1 else False
        return False

    def set_user_first_start(self, user_id: int, state: int):
        user = self.get_user_by_user_id(user_id)
        if user:
            user.first_start = state
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def get_user_referals(self, user_id: int):
        return self._session.query(User).filter(User.referal_parent_id == str(user_id)).all()

    def users_time_down(self):
        users = self.get_users()
        for user in users:
            if user.first_start == 1:
                if user.minutes_left > 0:
                    user.minutes_left = user.minutes_left - 1
        self._session.commit()

    def add_account(self, phone: str, user_id: int, proxy_id: int, send_status: bool, account_status: bool,
                    interval: int = 5,
                    message_to_send: str = "Всем привет!", last_statistic_start: int = 0, last_statistic_out: int = 0,
                    speed: int = 0):
        if self.is_account_exist(phone):
            return self.EXIST
        new_account = Account()
        new_account.phone = phone
        new_account.send_status = send_status
        new_account.account_status = account_status
        new_account.interval = interval
        new_account.message_to_send = message_to_send
        new_account.last_statistic_start = last_statistic_start
        new_account.last_statistic_out = last_statistic_out
        new_account.speed = speed
        new_account.user_id = user_id
        if len(self.get_unused_proxy()) == 0:
            return self.NO_PROXY
        new_account.proxy_id = self.get_unused_proxy()[0].id
        self.set_using_proxy(new_account.proxy_id, 1)
        self._session.add(new_account)
        self._session.commit()
        return self.GOOD

    def account_add_bonus(self, user_id, account_index):
        account = self.get_account_by_index(user_id, account_index)
        if account:
            account.minutes_left = account.minutes_left + 120
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def account_add_minutes(self, user_id, account_index, days, price):
        user = self.get_user_by_user_id(user_id)
        account = self.get_account_by_index(user_id, account_index)
        if account:
            if (user.balance - price) < 0:
                print(user.balance - price)
                return self.NO_MONEY
            user.balance = user.balance - price
            account.minutes_left = account.minutes_left + (days * 1440)
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def down_all_accounts_minute(self):
        accounts = self._session.query(Account).all()
        for account in accounts:
            if account.minutes_left > 0:
                account.minutes_left = account.minutes_left - 1
        self._session.commit()

    def update_account_photo_path(self, phone, photo_path):
        if self.is_account_exist(phone):
            account = self.get_account_by_phone(phone)
            account.has_photo = True
            account.photo_path = photo_path
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def delete_account_photo_path(self, phone):
        if self.is_account_exist(phone):
            account = self.get_account_by_phone(phone)
            account.has_photo = False
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def get_active_accounts(self):
        return self._session.query(Account).filter(Account.send_status == True).all()

    def get_all_accounts(self):
        return self._session.query(Account).all()

    def get_accounts_with_minutes(self):
        return self._session.query(Account).filter(Account.minutes_left > 0).all()

    def get_account_by_phone(self, phone: str) -> Account:
        return self._session.query(Account).filter(Account.phone == phone).first()

    def is_account_exist(self, phone: str) -> bool:
        return False if self.get_account_by_phone(phone) is None else True

    def get_accounts_by_user_id(self, user_id: int):
        return self._session.query(Account).filter(Account.user_id == user_id).all()

    def get_account_by_index(self, user_id: int, account_index: int):
        accounts = self.get_accounts_by_user_id(user_id)
        try:
            return accounts[int(account_index)]
        except:
            return None

    def deactive_account(self, phone):
        account = self.get_account_by_phone(phone)
        if account:
            try:
                import os
                file_path = "accounts/" + phone + ".session"
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        pass
            except:
                pass
            self.set_using_proxy(account.proxy_id, 0)
            account.account_status = 0
            account.send_status = 0
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def activate_account(self, phone):
        account = self.get_account_by_phone(phone)
        if account:
            account.account_status = 1
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def set_account_proxy(self, phone, proxy_id):
        account = self.get_account_by_phone(phone)
        proxy = self.get_proxy(proxy_id)
        if account and proxy:
            proxy.using = 1
            account.proxy_id = proxy_id
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def is_account_active(self, phone):
        account = self.get_account_by_phone(phone)
        return True if account.account_status == 1 else False

    def get_account_index(self, user_id, phone):
        accounts = self.get_accounts_by_user_id(user_id)
        i = 0
        for account in accounts:
            if account.phone == phone:
                return i
            i += 1
        return -1

    def update_account_send_status(self, phone: str, send_status: bool) -> bool:
        account = self.get_account_by_phone(phone)
        if account:
            account.send_status = send_status
            self._session.commit()
            return True
        return False

    def cooldown_down_minute(self, phone):
        account = self.get_account_by_phone(phone)
        if account:
            account.cooldown = account.cooldown - 1
            self._session.commit()
            return True
        return False

    def set_account_cooldown(self, phone):
        account = self.get_account_by_phone(phone)
        if account:
            account.cooldown = account.interval
            self._session.commit()
            return True
        return False

    def clear_account_cooldown(self, phone):
        account = self.get_account_by_phone(phone)
        groups = self.get_all_groups()
        if account:
            for group in groups:
                if group.account_id == account.id:
                    group.cooldown = 0

            self._session.commit()
            return True
        return False

    def update_account_status(self, phone: str, account_status: bool) -> bool:
        account = self.get_account_by_phone(phone)
        if account:
            account.account_status = account_status
            self._session.commit()
            return True
        return False

    def update_account_interval(self, phone: str, interval: int) -> bool:
        account = self.get_account_by_phone(phone)
        if account:
            account.interval = interval
            self._session.commit()
            return True
        return False

    def update_account_message(self, phone: str, message_to_send: str) -> bool:
        account = self.get_account_by_phone(phone)
        if account:
            account.message_to_send = message_to_send
            self._session.commit()
            return True
        return False

    def update_account_last_statistic_start(self, phone: str, last_statistic_start: int) -> bool:
        account = self.get_account_by_phone(phone)
        if account:
            account.last_statistic_start = last_statistic_start
            self._session.commit()
            return True
        return False

    def update_account_last_statistic_out(self, phone: str, last_statistic_out: int) -> bool:
        account = self.get_account_by_phone(phone)
        if account:
            account.last_statistic_out = last_statistic_out
            self._session.commit()
            return True
        return False

    def update_account_last_statistic_sended(self, phone: str, last_statistic_sended: int) -> bool:
        account = self.get_account_by_phone(phone)
        if account:
            account.last_statistic_sended = last_statistic_sended
            self._session.commit()
            return True
        return False

    def update_account_speed(self, phone: str, speed: int) -> bool:
        account = self.get_account_by_phone(phone)
        if account:
            account.speed = speed
            self._session.commit()
            return True
        return False

    def delete_account(self, phone: str) -> bool:
        import os
        file_path = "accounts/" + phone + ".session"
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                pass
        account = self.get_account_by_phone(phone)
        if not account:
            return False
        self.set_using_proxy(account.proxy_id, 0)
        self._session.delete(account)
        self._session.commit()
        return True

    def add_proxy(self, host: str, port: int, username: str = None, password: str = None):
        new_proxy = Proxy()
        new_proxy.host = host
        new_proxy.port = port
        new_proxy.username = username
        new_proxy.password = password
        self._session.add(new_proxy)
        self._session.commit()
        return True

    def delete_proxy(self, ip):
        proxy = self.get_proxy_by_ip(ip)
        if proxy:
            self._session.delete(proxy)
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def get_proxy(self, proxy_id: int) -> Proxy:
        return self._session.query(Proxy).filter(Proxy.id == proxy_id).first()

    def get_proxy_by_ip(self, ip: str) -> Proxy:
        return self._session.query(Proxy).filter(Proxy.host == ip).first()

    def get_all_proxies(self):
        return self._session.query(Proxy).all()

    def set_using_proxy(self, proxy_id: int, using: int):
        proxy = self.get_proxy(proxy_id)
        if proxy:
            proxy.using = using
            self._session.commit()
            return True
        return False

    def get_unused_proxy(self):
        return self._session.query(Proxy).filter(Proxy.using == 0).all()

    def get_used_proxy(self):
        return self._session.query(Proxy).filter(Proxy.using == 1).all()

    def get_account_proxy(self, phone):
        if not self.is_account_exist(phone):
            return self.NOT_FOUND
        return self._session.query(Proxy).filter(Proxy.id == self.get_account_by_phone(phone).proxy_id).first()

    def set_user_balance(self, user_id, minutes: int):
        user = self.get_user_by_user_id(user_id)
        if user:
            user.balance = minutes
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND

    def set_account_send_id(self, phone, send_id):
        account = self.get_account_by_phone(phone)
        if account:
            account.send_id = send_id
            self._session.commit()
            return self.GOOD
        return self.NOT_FOUND
