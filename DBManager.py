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
    days_left = Column(Integer)

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
    cooldown = Column(Integer)

class Proxy(Base):
    __tablename__ = "proxies"
    id = Column(Integer, primary_key=True, index=True)
    host = Column(String)
    port = Column(Integer)
    username = Column(String)
    password = Column(String)

psql_database = 'sqlite:///database.db'
engine = create_engine(psql_database)
session = Session(autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

class DBManager:
    def __init__(self, psql_database: str):
        self._engine = create_engine(psql_database)
        self._session = Session(autoflush=False, bind=self._engine)

    def add_user(self, user_id:int, username:str, referal_link:str, balance:int, referal_parent_id:str, days_left:int):
        if self.is_user_exist(user_id):
            return False
        new_user = User()
        new_user.user_id = user_id
        new_user.username = username
        new_user.referal_link = referal_link
        new_user.balance = balance
        new_user.referal_parent_id = referal_parent_id
        new_user.days_left = days_left
        self._session.add(new_user)
        self._session.commit()
        return True

    def get_user_by_user_id(self, user_id:int) -> User:
        return self._session.query(User).filter(User.user_id==user_id).first()

    def is_user_exist(self, user_id:int) -> bool:
        return False if self.get_user_by_user_id(user_id) is None else True

    def add_account(self, phone:str, user_id:int, send_status:bool, account_status:bool, interval:int = 0,
                    message_to_send:str = "", last_statistic_start:int = 0, last_statistic_out:int = 0, speed:int = 0):
        if self.is_account_exist(phone):
            return False
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
        self._session.add(new_account)
        self._session.commit()
        return True
    def get_active_accounts(self):
        return self._session.query(Account).filter(Account.send_status==True).all()
    def get_account_by_phone(self, phone:str) -> Account:
        return self._session.query(Account).filter(Account.phone==phone).first()

    def is_account_exist(self, phone:str) -> bool:
        return False if self.get_account_by_phone(phone) is None else True

    def get_accounts_by_user_id(self, user_id:int):
        return self._session.query(Account).filter(Account.user_id==user_id).all()

    def get_account_by_index(self, user_id:int, account_index:int):
        accounts = self.get_accounts_by_user_id(user_id)
        try:
            return accounts[account_index]
        except:
            return None

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
        file_path = "accounts/"+phone+".session"
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                pass
        account = self.get_account_by_phone(phone)
        if not account:
            return False
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

    def get_proxy(self, proxy_id: int) -> Proxy:
        return self._session.query(Proxy).filter(Proxy.id == proxy_id).first()

    def get_all_proxies(self):
        return self._session.query(Proxy).all()
