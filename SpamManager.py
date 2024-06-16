# SpamManager.py

import time
import asyncio
from datetime import datetime, timedelta
from DBManager import DBManager, User, Account, Proxy
from AccountManager import AccountManager

# Initialize DBManager
db_manager = DBManager('sqlite:///database.db')

async def send_messages_from_account(account: Account):
    try:
        proxy = None

        acc_manager = AccountManager(account.phone)
        if await acc_manager.auth():
            print(f"Authenticated for {account.phone}")
            await acc_manager.send_messages(account.message_to_send, account.speed)
        else:
            print(f"Authentication failed for {account.phone}")
    except Exception as e:
        print(f"Error processing account {account.phone}: {e}")

async def main_spam():
    while True:
        print("spam")
        try:
            accounts = db_manager.get_active_accounts()
            for account in accounts:
                print(account.id)
                user = db_manager.get_user_by_user_id(account.user_id)
                if user.days_left <= 0:
                    break
                if account.send_status and account.cooldown == 0:
                    print("send from "+account.phone)
                    await send_messages_from_account(account)
                    db_manager.set_account_cooldown(account.phone)
                elif account.cooldown > 0:
                    db_manager.cooldown_down_minute(account.phone)
        except Exception as e:
            print(f"Error in main loop: {e}")

        await asyncio.sleep(60)

def run():
    asyncio.run(main_spam())
