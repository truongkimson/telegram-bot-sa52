import time
import telegram
from telebot.credentials import (bot_token,
                                servant_group_chat_id,
                                test_group_chat_id,
                                sa52_group_chat_id, )
from apscheduler.schedulers.blocking import BlockingScheduler
from telebot.announcement import send_announcement


TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)
sched = BlockingScheduler()

job_schedule = [
    {
        'id': 'test0',
        'trigger': 'cron',
        'month': '*',
        'day': '*',
        'dow': '*',
        'hour': 11,
        'minute': 45,
        'func': send_announcement,
        'msg': f"Hi All,\nRemember to submit your temperature before class today \U0001F60A.\n\n",
        'chat_id': test_group_chat_id
    },
    {
        'id': 'reminder0',
        'trigger': 'cron',
        'month': '*',
        'day': '*',
        'dow': 'mon-fri',
        'hour': 8,
        'minute': 0,
        'func': send_announcement,
        'msg': f"Hi All,\nRemember to submit your temperature before class today \U0001F60A.\n\n",
        'chat_id': sa52_group_chat_id
    },
    {
        'id': 'hpbd0',
        'trigger': 'cron',
        'month': 3,
        'day': 4,
        'dow': '*',
        'hour': 14,
        'minute': 45,
        'func': send_announcement,
        'msg': f"Happy birthday @Alejandro_sXe!!!!\U0001F60A\U0001F60A\U0001F970\U0001F970\U0001F917\U0001F917",
        'chat_id': sa52_group_chat_id
    }

]

for j in job_schedule:
    sched.add_job(j['func'], args=(j['chat_id'], j['msg']), trigger=j['trigger'], month=j['month'], day=j['day'],
                    day_of_week=j['dow'], hour=j['hour'], minute=j['minute'], id=j['id'], misfire_grace_time=20)
sched.start()