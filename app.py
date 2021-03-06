import os
import telegram
import requests
import email
import base64
import pickle
import flask
import google_auth_oauthlib.flow
import googleapiclient.discovery
from datetime import datetime
from google.auth.transport.requests import Request
from werkzeug.utils import redirect
from dateutil import parser
from flask import Flask, request
from requests.api import get
from telebot.credentials import bot_token, bot_user_name, URL, yamete_file_id, test_group_chat_id
from telebot import meme, stock
from gmail.utils import trim_message

# Telegram bot token and create bot instance
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

# Gmail client credentials
CLIENT_SECRETS_FILE = 'gmail/client_id.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'
history_id = None
client_ready = False
gmail = None

def run_gmail_client():
    global client_ready, history_id, gmail
    with open('gmail/gmail_token.pickle', 'rb') as token:
        creds = pickle.load(token)
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                
    gmail = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=creds)
    request_body = {
        'labelIds': ['INBOX'],
        'topicName': 'projects/thinking-banner-284203/topics/luminus-gmail-forward'
    }
    # save history_id returned by watch() call
    history_id = gmail.users().watch(userId='me', body=request_body).execute()['historyId']

    # save creds to pickle in case access token is refreshed
    with open('gmail/gmail_token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    client_ready = True
    print(f'Gmail client is ready. HistoryId={history_id}')

try:
    run_gmail_client()
except Exception as e:
    print(f'Gmail client not instantiated. Error occured: {e}')
    client_ready = False

# start Flask app
app = Flask(__name__)
# set secret_key for sessions
app.secret_key = b'3fds9*(#*)(fl232#(LK!@_fdAavnmk:'



@app.route('/')
def index():
    return 'Welcome'


@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    print(request.get_json())
    update = telegram.Update.de_json(request.get_json(), bot)

    try:
        if update.message:
            update_message = update.message
        elif update.edited_message:
            update_message = update.edited_message
        else:
            return 'ok'
        chat_id = update_message.chat.id
        msg_id = update_message.message_id
        text = update_message.text.encode('utf-8').decode()
    except AttributeError as e:
        print(e)
        print(update_message)
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

    elif text == '/punish' or text == f'/punish@{bot_user_name}':
        user_first_name = update.message.from_user.first_name
        punish_msg = 'Yamete kudasai~'
        bot.send_message(chat_id=chat_id, text=punish_msg, reply_to_message_id=msg_id)

    elif text == '/punish_hard' or text == f'/punish_hard@{bot_user_name}':
        user_first_name = update.message.from_user.first_name
        try:
            bot.send_voice(chat_id=chat_id, voice=yamete_file_id, reply_to_message_id=msg_id)
        except Exception as e:
            print(e)
    

    elif text == '/meme' or text == f'/meme@{bot_user_name}':
        url = meme.get_random_meme()
        bot.send_photo(chat_id=chat_id, photo=url)

    elif text.startswith('/stock') or text.startswith(f'/stock@{bot_user_name}'):
        try:
            symbol = text.strip().split()[1]
            quote_msg = stock.get_quote(symbol)
        except IndexError:
            quote_msg = "Command usage: /stock [symbol]"
        bot.send_message(chat_id=chat_id, text=quote_msg, reply_to_message_id=msg_id,
                        parse_mode='HTML', disable_web_page_preview=True)
        
    elif update.message.reply_to_message:
        reply_msg = 'Sorry I don\'t understand'
        bot.send_message(chat_id=chat_id, text=reply_msg, reply_to_message_id=msg_id)

    return 'ok'


@app.route('/get_webhook_info')
def get_webhook_info():
    webhook_info = bot.get_webhook_info()
    return vars(webhook_info)


@app.route('/clear_updates/<int:update_id>')
def clear_updates(update_id):
    r = requests.get(f'https://api.telegram.org/bot{bot_token}/setWebhook?url=')
    print(r)
    r = requests.get(f'https://api.telegram.org/bot{bot_token}/getUpdates?offset={update_id}')
    print(r)
    return update_id


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.set_webhook(f'{URL}/{TOKEN}')
    if s:
        return "webhook set successfully"
    else:
        return "webhook set unsuccessfully"

# gmail API
@app.route('/gmail')
def gmail_index():
    return print_index_table()


@app.route('/gmail/test')
def test_api_request():
    # check if pickled credential object is available, if not redirect to /authorize
    if not os.path.exists('gmail/gmail_token.pickle'):
        return redirect(flask.url_for('authorize'))

    # load pickle into creds, check if still valid
    with open('gmail/gmail_token.pickle', 'rb') as token:
        creds = pickle.load(token)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            return redirect(flask.url_for('authorize'))

    # call Gmail API using creds credential
    gmail = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=creds)
    msg_list = gmail.users().messages().list(userId='me', labelIds=['INBOX']).execute()

    # save creds to pickle in case access token is refreshed
    with open('gmail/gmail_token.pickle', 'wb') as token:
        pickle.dump(creds, token)

    return flask.jsonify(msg_list)


@app.route('/gmail/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(access_type='offline')
    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return redirect(authorization_url)


@app.route('/gmail/oauth2callback')
def oauth2callback():
    global client_ready
    # Specify the state when creating the flow in the callback so that it can
    # verify the authorization server response.
    state = flask.session['state']
    authorization_response = flask.request.url

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    # state is used to verify reponse here
    flow.fetch_token(authorization_response=authorization_response)

    creds = flow.credentials
    with open('gmail/gmail_token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    run_gmail_client()
    
    return flask.redirect(flask.url_for('test_api_request'))

@app.route('/gmail/revoke')
def revoke():
    if not os.path.exists('gmail/gmail_token.pickle'):
        return ('You need to <a href="/gmail/authorize">authorize</a> before testing the code to revoke credentials.')

    with open('gmail/gmail_token.pickle', 'rb') as token:
        creds = pickle.load(token)

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
        params={'token': creds.token},
        headers={'content-type': 'application/x-www-form-urlencoded'}
    )

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return('Credentials successfully revoked.' + print_index_table())
    else:
        return ('An error occurred.' + print_index_table())


@app.route('/gmail/clear')
def clear_credentials():
    if os.path.exists('gmail/gmail_token.pickle'):
        os.remove('gmail/gmail_token.pickle')
    return ('Credentials have been cleared.<br><br>' + print_index_table())


@app.route('/gmail/luminus_announcement', methods=['POST'])
def luminus_announcement():
    if client_ready:
        global history_id
        msg = ''

        history_list = gmail.users().history().list(userId='me', historyTypes=['messageAdded'],
            labelId='INBOX', startHistoryId=history_id).execute()
        if 'history' in history_list:
            for history in history_list['history']:
                if 'messagesAdded' in history:
                    for added_message in history['messagesAdded']:
                        id = added_message['message']['id']
                        message = gmail.users().messages().get(userId='me', id=id, format='raw').execute()
                        msg_bytes = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
                        mime_msg = email.message_from_bytes(msg_bytes, policy = email.policy.default)
                        
                        if list(mime_msg.iter_attachments()).__len__() > 0:
                            attachments = list(mime_msg.iter_attachments())
                            for att in attachments:
                                for part in att.walk():
                                    if 'From' in part:
                                        msg += f'Update from: {part.get("From")}\n'
                                        received_date = datetime.strptime(part.get('Date'), '%a, %d %b %Y %H:%M:%S %z')
                                        msg += received_date.strftime('%a, %d %b, %y %H:%M\n')
                                        msg += f'Subject: {part.get("Subject")}\n'
                                    if (part.get_content_type() == 'text/plain'):
                                        msg += trim_message(part.get_content())
                                        msg = msg[:200] + ' --truncated'
                                        print(msg)
                                        bot.send_message(chat_id=test_group_chat_id, text=msg)
        history_id = history_list['historyId']
        return 'ok'
    else:
        msg = f'Please authorize using Gmail account. {flask.url_for("authorize", _external=True)}'
        bot.send_message(chat_id=test_group_chat_id, text=msg)
        print(client_ready)
        return flask.Response('Client unavailable', status=503)


def print_index_table():
  return ('<table>' +
          f'<tr><td><a href="{flask.url_for("test_api_request")}">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          f'<tr><td><a href="{flask.url_for("authorize")}">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          f'<tr><td><a href="{flask.url_for("revoke")}">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          f'<tr><td><a href="{flask.url_for("clear_credentials")}">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          f'    After clearing the token, if you <a href="{flask.url_for("test_api_request")}">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')




if __name__ == '__main__':
    # os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    # app.run('localhost', 8080, threaded=True, debug=True)
    app.run(threaded=True)