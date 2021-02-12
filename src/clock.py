import time
import telegram
from telebot.credentials import (bot_token,
                                servant_group_chat_id,
                                test_group_chat_id,
                                sa52_group_chat_id, )
from apscheduler.schedulers.blocking import BlockingScheduler


TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)
sched = BlockingScheduler()

# def test_scheduled_reminder():
#     msg = f"Hi All,\nRemember to submit your temperature before class today \U0001F60A.\n\n{time.strftime('%H:%M:%S', time.localtime())}"
#     bot.send_message(chat_id=test_group_chat_id, text=msg)


def scheduled_temperature_reminder():
    msg = f"Hi All,\nRemember to submit your temperature before class today \U0001F60A.\n\n{time.strftime('%H:%M:%S', time.localtime())}"
    bot.send_message(chat_id=sa52_group_chat_id, text=msg)


# @sched.scheduled_job('interval', seconds=5)
# def test_interval():
#     test_scheduled_reminder()


@sched.scheduled_job('cron', day_of_week='mon-fri', hour=8, minute=0)
def cron():
    scheduled_temperature_reminder()

sched.start()