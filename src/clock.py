import time
import telegram
from telebot.credentials import bot_token, bot_user_name, servant_group_chat_id, test_group_chat_id
from apscheduler.schedulers.blocking import BlockingScheduler


TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)
sched = BlockingScheduler()

def test_scheduled_reminder():
    msg = f"** TESTING **\nGood Morning! This message is scheduled every morning.\nThis message was sent at {time.strftime('%H:%M:%S', time.localtime())}\nHosted on Heroku."
    bot.send_message(chat_id=test_group_chat_id, text=msg)

# @sched.scheduled_job('interval', seconds=5)
# def test_interval():
#     test_scheduled_reminder()

@sched.scheduled_job('cron', days_of_week='mon-fri', hour=14, minute=24)
def test_cron():
    test_scheduled_reminder()

sched.start()