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
        'dow': '*',
        'hour': 11,
        'minute': 14,
        'func': send_announcement,
        'msg': f"Hi All,\nRemember to submit your temperature before class today \U0001F60A.\n\n{time.strftime('%H:%M:%S', time.localtime())}",
        'chat_id': test_group_chat_id
    }
]

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=8, minute=0)
def temperature_reminder():
    msg = f"Hi All,\nRemember to submit your temperature before class today \U0001F60A.\n\n{time.strftime('%H:%M:%S', time.localtime())}"
    result = bot.send_message(chat_id=sa52_group_chat_id, text=msg)
    print(result)

for j in job_schedule:
    sched.add_job(j['func'], j['trigger'], day_of_work=j['dow'], hour=j['hour'], minute=j['minute'], id='test0', args=(j['chat_id'], j['msg']))
sched.start()