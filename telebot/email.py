from .credentials import test_group_chat_id, servant_group_chat_id

def get_luminus_announcement(email):
    sender = email['sender']
    subject = email['subject']
    body = email['body']

    announce_message = f"""
Update from {sender}!
{subject}
{body}
"""

    chat_id = servant_group_chat_id
    return announce_message, chat_id