from flask import Flask, request
import telegram
from telebot.credentials import bot_token, bot_user_name, URL

TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route('/')
def index():
    return 'Welcome'

@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    text = update.message.text.encode('utf-8').decode()
    print(text)

    if text == '/start':
        welcome_msg = '''
Hi there!
I'm Ale's assistant.
        '''
        bot.send_message(chat_id=chat_id, text=welcome_msg, reply_to_message_id=msg_id)
    return

if __name__ == '__main__':
    app.run(threaded=True)