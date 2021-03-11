import telegram
from telebot.credentials import bot_token


TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)


def send_announcement(chat_id, msg):
    result = bot.send_message(chat_id=chat_id, text=msg)
    print(result)


if __name__ == '__main__':
    msg = input('Enter msg: ')
    chat_id = input('Enter chat id: ')
    send_announcement(chat_id, msg)
