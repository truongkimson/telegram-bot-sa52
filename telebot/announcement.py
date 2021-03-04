import telegram
from telebot.credentials import bot_token


TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

def send_announcement(chat_id, msg):
    result = bot.send_message(chat_id=chat_id, text=msg)
    print(result)