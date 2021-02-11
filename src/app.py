import time
import telegram
from telebot.credentials import bot_token, bot_user_name, servant_group_chat_id, test_group_chat_id


TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

def test_scheduled_reminder():
    msg = f"** TESTING **\nGentle reminder to submit your temperature.\nThis message is sent at {time.strftime('%H:%M:%S', time.localtime())}"
    bot.send_message(chat_id=test_group_chat_id, text=msg)


def main():
    test_scheduled_reminder()

if __name__ == '__main__':
    main()