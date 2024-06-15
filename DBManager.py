from sqlalchemy import create_engine, Engine, MetaData
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session, Query

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
    interval = Column(Integer)
    message_to_send = Column(String)
    last_statistic_start = Column(Integer)
    last_statistic_out = Column(Integer)
    last_statistic_sended = Column(Integer)
    speed = Column(Integer)

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String)
    send_status = Column(Boolean)
    account_status = Column(Boolean)

# psql_database = 'sqlite:///database.db'
# engine = create_engine(psql_database)
# session = Session(autoflush=False, bind=engine)
# Base.metadata.create_all(bind=engine)

class DBManager:
    def __init__(self, psql_database: str):
        self._engine = create_engine(psql_database)
        self._session = Session(autoflush=False, bind=self._engine)

    def add_user(self, user_id:int, username:str, referal_link:str, balance:int, referal_parent_id:str):
        if self.is_user_exist(user_id):
            return False
        new_user = User()
        new_user.user_id = user_id
        new_user.username = username
        new_user.referal_link = referal_link
        new_user.balance = balance
        new_user.referal_parent_id = referal_parent_id
        self._session.add(new_user)
        self._session.commit()
        return True

    def get_user_by_user_id(self, user_id:int) -> User:
        return self._session.query(User).filter(User.user_id==user_id).first()

    def is_user_exist(self, user_id:int) -> bool:
        return False if self.get_user_by_user_id(user_id) is None else True