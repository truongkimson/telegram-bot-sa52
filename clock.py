import time
import telegram
from telebot.credentials import (bot_token,
                                servant_group_chat_id,
                                test_group_chat_id,
                                sa52_group_chat_id, )
from apscheduler.schedulers.blocking import BlockingScheduler
from telebot.announcement import temp_reminder


TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)
sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=8, minute=0)
def temperature_reminder():
    msg = f"Hi All,\nRemember to submit your temperature before class today \U0001F60A.\n\n{time.strftime('%H:%M:%S', time.localtime())}"
    result = bot.send_message(chat_id=sa52_group_chat_id, text=msg)
    print(result)

@sched.scheduled_job('cron', hour=10, minute=18)
def temperature_reminder_everyday():
    msg = f"Hi All,\nRemember to submit your temperature before class today \U0001F60A.\n\n{time.strftime('%H:%M:%S', time.localtime())}"
    temp_reminder(test_group_chat_id, msg)

sched.start()