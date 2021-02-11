import time
import schedule
import telegram
import os
from telebot.credentials import bot_token, bot_user_name, servant_group_chat_id, test_group_chat_id


PORT = int(os.environ.get('PORT', 5000))
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)


def test_scheduled_reminder():
    msg = f"** TESTING **\nGentle reminder to submit your temperature.\nThis message is sent at {time.strftime('%H:%M:%S', time.localtime())}"
    bot.send_message(chat_id=test_group_chat_id, text=msg)


schedule.every().day.at("02:25").do(test_scheduled_reminder)
# schedule.every(10).seconds.do(test_scheduled_reminder)

while True:
    schedule.run_pending()
    time.sleep(1)
