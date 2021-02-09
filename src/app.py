import time
import schedule
import telegram
from telebot.credentials import bot_token, bot_user_name, servant_group_chat_id, test_group_chat_id


TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)


def test_scheduled_hello():
    msg = "Hello!\nThis is a test message."
    response = bot.send_message(chat_id=test_group_chat_id, text=msg)
    print("Trying to send message", response)


def test_scheduled_reminder():
    msg = "** TESTING **\nGentle reminder to submit your temperature. This message is sent every hour"
    bot.send_message(chat_id=servant_group_chat_id, text=msg)

def test_scheduled_time_reminder():
    msg = "** TESTING **\nGentle reminder to submit your temperature. This message is sent at 13:59"
    bot.send_message(chat_id=servant_group_chat_id, text=msg)


schedule.every().hour.do(test_scheduled_reminder)
schedule.every().day.at("13:59").do(test_scheduled_time_reminder)
# schedule.every(10).seconds.do(test_scheduled_hello)

while True:
    schedule.run_pending()
    time.sleep(1)