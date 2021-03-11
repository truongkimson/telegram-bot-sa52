from telebot.credentials import bot_user_name, yamete_file_id
from telebot import meme, stock


class Command_handler():
    def __init__(self):
        self.commands = {}

    def __call__(self, bot, update):
        if hasattr(update, 'message'):
            update_message = update.message
        elif hasattr(update, 'edited_message'):
            update_message = update.edited_message
        else:
            return
        chat_id = update_message.chat.id
        msg_id = update_message.message_id
        text = update_message.text.encode('utf-8').decode()
        print(text)
        for command in self.commands:
            if text.startswith(command) or text.startswith(f'{command}@{bot_user_name}'):
                print(f'Matched {command}')
                return self.commands[command](bot, update_message, chat_id, msg_id)
        print('No matched commands')
        return

    def add_command(self, command_text, callback):
        if command_text in self.commands:
            raise ValueError(f'Command "{command_text}" already exists in handler\'s dict.')
        else:
            self.commands.update({command_text: callback})


def start_command(bot, update_message, chat_id, msg_id):
    # /start command
    welcome_msg = '''
Hi there!
I'm Ale's assistant.
'''
    return bot.send_message(chat_id=chat_id, text=welcome_msg, reply_to_message_id=msg_id)


def help_command(bot, update_message, chat_id, msg_id):
    # /help command
    help_msg = '''
Commands available
/help - Show help
/hello - Say hello to you
/meme - Send a random meme scraped from reddit
/stock - Check stock price. Usage: /stock [symbol]
'''
    return bot.send_message(chat_id=chat_id, text=help_msg, reply_to_message_id=msg_id)


def hello_command(bot, update_message, chat_id, msg_id):
    # /hello command
    user_first_name = update_message.from_user.first_name
    hello_msg = f'Hello {user_first_name}!'
    bot.send_message(chat_id=chat_id, text=hello_msg,
                     reply_to_message_id=msg_id)


def punish_command(bot, update_message, chat_id, msg_id):
    # /punish command
    user_first_name = update_message.from_user.first_name
    punish_msg = f'Yamete kudasai~ Sama {user_first_name}~'
    bot.send_message(chat_id=chat_id, text=punish_msg,
                     reply_to_message_id=msg_id)


def punish_hard_command(bot, update_message, chat_id, msg_id):
    # /punish_hard command
    try:
        bot.send_voice(chat_id=chat_id, voice=yamete_file_id,
                       reply_to_message_id=msg_id)
    except Exception as e:
        print(e)


def meme_command(bot, update_message, chat_id, msg_id):
    url = meme.get_random_meme()
    bot.send_photo(chat_id=chat_id, photo=url)


def stock_command(bot, update_message, chat_id, msg_id):
    text = update_message.text.encode('utf-8').decode()
    try:
        symbol = text.strip().split()[1]
        quote_msg = stock.get_quote(symbol)
    except IndexError:
        quote_msg = "Command usage: /stock [symbol]"
    bot.send_message(chat_id=chat_id, text=quote_msg, reply_to_message_id=msg_id,
                     parse_mode='HTML', disable_web_page_preview=True)


def default_reply(bot, update_message, chat_id, msg_id):
    reply_msg = 'Sorry I don\'t understand'
    bot.send_message(chat_id=chat_id, text=reply_msg,
                     reply_to_message_id=msg_id)
