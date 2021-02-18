import telegram
import requests
from flask import Flask, request
from requests.api import get
from telebot.credentials import bot_token, bot_user_name, URL
from telebot import meme, stock

TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route('/')
def index():
    return 'Welcome'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.set_webhook(f'{URL}/{TOKEN}')
    if s:
        return "webhook set successfully"
    else:
        return "webhook set unsuccessfully"


@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    print(request.get_json())
    update = telegram.Update.de_json(request.get_json(), bot)

    if update.message.text:
        chat_id = update.message.chat.id
        msg_id = update.message.message_id
        text = update.message.text.encode('utf-8').decode()
    else:
        return 'ok'

    if text == '/start' or text == f'/start@{bot_user_name}':
        welcome_msg = '''
Hi there!
I'm Ale's assistant.
'''
        bot.send_message(chat_id=chat_id, text=welcome_msg, reply_to_message_id=msg_id)

    elif text == '/help' or text == f'/help@{bot_user_name}':
        help_msg = '''
Commands available
/help - Show help
/hello - Say hello to you
/meme - Send a random meme scraped from reddit
/stock - Check stock price. Usage: /stock [symbol]
'''
        bot.send_message(chat_id=chat_id, text=help_msg, reply_to_message_id=msg_id)

    elif text == '/hello' or text == f'/hello@{bot_user_name}':
        user_first_name = update.message.from_user.first_name
        hello_msg = f'Hello {user_first_name}!'
        bot.send_message(chat_id=chat_id, text=hello_msg, reply_to_message_id=msg_id)

    elif text == '/meme' or text == f'/meme@{bot_user_name}':
        url = meme.get_random_meme()
        bot.send_photo(chat_id=chat_id, photo=url)

    elif text.startswith('/stock') or text.startswith(f'/stock@{bot_user_name}'):
        try:
            symbol = text.strip().split()[1]
            quote_msg = stock.get_quote(symbol)
        except IndexError:
            quote_msg = "Command usage: /stock [symbol]"
        bot.send_message(chat_id=chat_id, text=quote_msg, reply_to_message_id=msg_id, parse_mode='HTML')
        
    elif update.message.reply_to_message:
        reply_msg = 'Sorry I don\'t understand'
        bot.send_message(chat_id=chat_id, text=reply_msg, reply_to_message_id=msg_id)

    return 'ok'


@app.route('/get_webhook_info')
def get_webhook_info():
    webhook_info = bot.get_webhook_info()
    return vars(webhook_info)

@app.route('/clear_updates')
def clear_updates():
    r = requests.get(f'https://api.telegram.org/bot{bot_token}/setWebhook?url=')
    print(r)
    r = requests.get(f'https://api.telegram.org/bot{bot_token}/getUpdate')
    print(r)

if __name__ == '__main__':
    app.run(threaded=True)