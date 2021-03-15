import os
import telegram
import requests
import email
import base64
import flask
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.auth.transport.requests import Request
from werkzeug.utils import redirect
from flask import Flask, request
from telebot.command import (Command_handler, start_command, help_command, hello_command, punish_command,
                             punish_hard_command, meme_command, stock_command)
from telebot.credentials import (bot_token, URL, test_group_chat_id, servant_group_chat_id, sa52_group_chat_id)
from google.auth.exceptions import GoogleAuthError
from gmail.utils import get_msg_from_att
from db_lib.db_access import (get_creds_from_db,
                              save_creds_to_db,
                              delete_creds_from_db,
                              get_history_id_from_db,
                              save_history_id_to_db)

# Telegram bot token and create bot instance
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

handler = Command_handler()
handler.add_command('/start', start_command)
handler.add_command('/help', help_command)
handler.add_command('/hello', hello_command)
handler.add_command('/punish', punish_command)
handler.add_command('/hardpunish', punish_hard_command)
handler.add_command('/meme', meme_command)
handler.add_command('/stock', stock_command)

# Gmail client credentials
CLIENT_SECRETS_FILE = 'gmail/client_id.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

# PostgresDB connection on heroku server
DATABASE_URL = os.environ['DATABASE_URL']


# start Flask app
app = Flask(__name__)
# set secret_key for sessions
app.secret_key = b'3fds9*(#*)(fl232#(LK!@_fdAavnmk:'


@app.route('/')
def index():
    return 'Welcome'


@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(), bot)
    print(request.get_json())
    try:
        handler(bot, update)
    except Exception as e:
        print(e)
    return 'ok'


@app.route('/get_webhook_info')
def get_webhook_info():
    webhook_info = bot.get_webhook_info()
    return vars(webhook_info)


@app.route('/clear_updates/<int:update_id>')
def clear_updates(update_id):
    r = requests.get(
        f'https://api.telegram.org/bot{bot_token}/setWebhook?url=')
    print(r)
    r = requests.get(
        f'https://api.telegram.org/bot{bot_token}/getUpdates?offset={update_id}')
    print(r)
    return update_id


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.set_webhook(f'{URL}/{TOKEN}')
    if s:
        return "webhook set successfully"
    else:
        return "webhook set unsuccessfully"


@app.route('/gmail')
def gmail_index():
    return print_index_table()


@app.route('/gmail/call_watch')
def call_watch():
    creds = get_creds_from_db()
    gmail = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=creds)

    request_body = {
        'labelIds': ['INBOX'],
        'topicName': 'projects/thinking-banner-284203/topics/luminus-gmail-forward'
    }
    # save global history_id returned by watch() call
    history_id = gmail.users().watch(
        userId='me', body=request_body).execute()['historyId']
    save_history_id_to_db(history_id)
    print(
        f'Expiry: {creds.expiry}, Refresh token: {creds.refresh_token}, Expired: {creds.expired}')
    return f'HistoryId = {history_id}'


@app.route('/gmail/test')
def test_api_request():
    # check if pickled credential is in DB, if not redirect to /authorize
    creds = get_creds_from_db()
    if not creds:
        return redirect(flask.url_for('authorize'))

    # load pickle into creds, check if still valid
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except GoogleAuthError as e:
                print(f'An error occured: {e}')
                return redirect(flask.url_for('authorize', next='test_api_request'))
        else:
            return redirect(flask.url_for('authorize', next='test_api_request'))

    # call Gmail API using creds credential
    gmail = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=creds)
    msg_list = gmail.users().messages().list(
        userId='me', labelIds=['INBOX']).execute()

    # save creds to pickle in case access token is refreshed
    save_creds_to_db(creds)
    print(
        f'Expiry: {creds.expiry}, Refresh token: {creds.refresh_token}, Expired: {creds.expired}')
    return flask.jsonify(msg_list)


@app.route('/gmail/authorize')
def authorize():
    # get next variable from request query
    next = request.args.get('next')
    if not next:
        next = 'gmail_index'
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = flask.url_for(
        'oauth2callback', next=next, _external=True)

    authorization_url, state = flow.authorization_url(access_type='offline')
    # Store state so the callback can verify the auth server response.
    flask.session['state'] = state

    return redirect(authorization_url)


@app.route('/gmail/oauth2callback')
def oauth2callback():
    # get next variable from request query
    next = request.args.get('next')
    # Specify the state when creating the flow in the callback so that it can
    # verify the authorization server response.
    state = flask.session['state']
    authorization_response = flask.request.url

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for(
        'oauth2callback', next=next, _external=True)
    # state is used to verify reponse here
    flow.fetch_token(authorization_response=authorization_response)

    creds = flow.credentials
    save_creds_to_db(creds)
    print(
        f'Expiry: {creds.expiry}, Refresh token: {creds.refresh_token}, Expired: {creds.expired}')
    return flask.redirect(flask.url_for(next))


@app.route('/gmail/revoke')
def revoke():
    creds = get_creds_from_db()
    if not creds:
        return ('You need to <a href="/gmail/authorize">authorize</a> before testing the code to revoke credentials.')

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
                           params={'token': creds.token},
                           headers={
                               'content-type': 'application/x-www-form-urlencoded'}
                           )

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return('Credentials successfully revoked.' + print_index_table())
    else:
        return ('An error occurred.' + print_index_table())


@app.route('/gmail/clear')
def clear_credentials():
    if delete_creds_from_db():
        return ('Credentials have been cleared.<br><br>' + print_index_table())
    else:
        return ('No credentials to be cleared.<br><br>' + print_index_table())


@app.route('/gmail/luminus_announcement', methods=['POST'])
def luminus_announcement():
    msg = ''

    creds = get_creds_from_db()
    history_id = get_history_id_from_db()
    if not creds:
        print('Pickle not found in db')
        msg = f'Pickle not found in db. {flask.url_for("authorize", next="test_api_request", _external=True)}'
        bot.send_message(chat_id=test_group_chat_id, text=msg,
                         disable_web_page_preview=True)
        return 'Client unavailable'

    # load pickle into creds, check if still valid
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except GoogleAuthError as e:
                print(f'An error occured: {e}')
                print(
                    f'Credential invalid. Expiry: {creds.expiry}, Expired: {creds.expired}, Refresh token: {creds.refresh_token}')
                msg = (f'An error occured: {e}. Expiry: {creds.expiry}, Expired: {creds.expired}, Refresh token: {creds.refresh_token}.' +
                       f'{flask.url_for("authorize", next="test_api_request", _external=True)}')
                bot.send_message(chat_id=test_group_chat_id,
                                 text=msg, disable_web_page_preview=True)
                return 'Refresh error'

        else:
            print(
                f'Credential invalid. Expiry: {creds.expiry}, Expired: {creds.expired}, Refresh token: {creds.refresh_token}')
            msg = (f'Credential invalid. Expiry: {creds.expiry}, Expired: {creds.expired}, Refresh token: {creds.refresh_token}.' +
                   f'{flask.url_for("authorize", next="test_api_request", _external=True)}')
            bot.send_message(chat_id=test_group_chat_id,
                             text=msg, disable_web_page_preview=True)
            return 'Client unavailable'

    gmail = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=creds)
    history_list = gmail.users().history().list(userId='me', historyTypes=['messageAdded'],
                                                labelId='INBOX', startHistoryId=history_id).execute()
    if 'history' in history_list:
        for history in history_list['history']:
            if 'messagesAdded' in history:
                for added_message in history['messagesAdded']:
                    id = added_message['message']['id']
                    message = gmail.users().messages().get(
                        userId='me', id=id, format='raw').execute()
                    msg_bytes = base64.urlsafe_b64decode(
                        message['raw'].encode('ASCII'))
                    mime_msg = email.message_from_bytes(
                        msg_bytes, policy=email.policy.default)

                    if list(mime_msg.iter_attachments()).__len__() > 0:
                        attachments = list(mime_msg.iter_attachments())
                        for att in attachments:
                            msg = get_msg_from_att(att)
                            if (msg != ''):
                                bot.send_message(
                                    chat_id=test_group_chat_id, text=msg, parse_mode='HTML', disable_web_page_preview=True)
                                bot.send_message(
                                    chat_id=sa52_group_chat_id, text=msg, parse_mode='HTML', disable_web_page_preview=True)
    if msg == '':
        print('Non-MessageAdded webhook')
    history_id = history_list['historyId']
    save_history_id_to_db(history_id)
    save_creds_to_db(creds)
    print(
        f'Expiry: {creds.expiry}, Refresh token: {creds.refresh_token}, Expired: {creds.expired}')
    return 'ok'


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
            f'<tr><td><a href="{flask.url_for("call_watch")}">Call watch() method on gmail client</a></td>' +
            '<td>Call watch() and get HistoryId</td></tr>' +
            f'<tr><td><a href="{flask.url_for("clear_credentials")}">Clear Flask session credentials</a></td>' +
            '<td>Clear the access token currently stored in the user session. ' +
            f'    After clearing the token, if you <a href="{flask.url_for("test_api_request")}">test the ' +
            '    API request</a> again, you should go back to the auth flow.' +
            '</td></tr></table>')


def run_gmail_client_and_watch():
    creds = get_creds_from_db()
    if creds:
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except GoogleAuthError as e:
                    print(
                        f'{e}. Expiry: {creds.expiry}, Expired: {creds.expired}, Refresh token: {creds.refresh_token}')
                    msg = (f'{e}. Expiry: {creds.expiry}, Expired: {creds.expired}, Refresh token: {creds.refresh_token}.' +
                           'https://polar-ridge-56723.herokuapp.com/gmail/authorize?next=call_watch')
                    bot.send_message(chat_id=test_group_chat_id,
                                     text=msg, disable_web_page_preview=True)
                    return False

            else:
                print(
                    f'Credential invalid. Expiry: {creds.expiry}, Expired: {creds.expired}, Refresh token: {creds.refresh_token}')
                msg = (f'Credential invalid. Expiry: {creds.expiry}, Expired: {creds.expired}, Refresh token: {creds.refresh_token}.' +
                       'https://polar-ridge-56723.herokuapp.com/gmail/authorize?next=call_watch')
                bot.send_message(chat_id=test_group_chat_id,
                                 text=msg, disable_web_page_preview=True)
                return False

        gmail = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=creds)

        request_body = {
            'labelIds': ['INBOX'],
            'topicName': 'projects/thinking-banner-284203/topics/luminus-gmail-forward'
        }
        # save global history_id returned by watch() call
        history_id = gmail.users().watch(
            userId='me', body=request_body).execute()['historyId']

        # save creds to pickle in case access token is refreshed
        save_creds_to_db(creds)
        save_history_id_to_db(history_id)
        print(
            f'Expiry: {creds.expiry}, Refresh token: {creds.refresh_token}, Expired: {creds.expired}')
        print(f'Gmail client is ready. HistoryId={history_id}')
        return True
    else:
        print('Token not found in DB.')
        msg = 'Token not found in DB. https://polar-ridge-56723.herokuapp.com/gmail'
        bot.send_message(chat_id=test_group_chat_id, text=msg,
                         disable_web_page_preview=True)
        return False


if not run_gmail_client_and_watch():
    print('Gmail client not instantiated.')


if __name__ == '__main__':
    # os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    # app.run('localhost', 8080, threaded=True, debug=True)
    app.run(threaded=True)
