import re
import os
import html
import html2text
from dateutil.tz import gettz
from datetime import datetime


def trim_text(msg):
    msg = msg.strip()
    msg = re.sub(r'\n\s+', '\n', msg)
    msg = html.escape(msg)
    return msg


def is_file_submit_confirmation(subject):
    if 'file submission confirmation' in subject.lower():
        return True
    return False


def get_msg_from_att(att):
    msg = ''
    for part in att.walk():
        if 'From' in part:
            if is_file_submit_confirmation(part.get('Subject')):
                msg = ''
                return msg
            msg += f'&lt;&lt;Update&gt;&gt;\n<b>From:</b> {trim_text(part.get("From"))}\n'

            received_date = datetime.strptime(part.get('Date'), '%a, %d %b %Y %H:%M:%S %z')\
                .astimezone(tz=gettz('Asia/Singapore'))
            msg += received_date.strftime(
                '%H:%M %a, %d %b, %Y \n\n')

            msg += f'<b>Subject:</b> {trim_text(part.get("Subject"))}\n\n'
        if part.get_content_type() == 'text/plain':
            msg += 'Plain text\n'
            msg += trim_text(part.get_content())[:200] + '\n--truncated'
            return msg
        elif part.get_content_type() == 'text/html':
            msg += 'Html text\n'
            plain_txt = html2text.html2text(part.get_content())
            msg += trim_text(plain_txt)[:200] + '\n--truncated'
            print(msg)
            return msg
    return msg


# for testing
if __name__ == '__main__':
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(THIS_FOLDER, 'input.txt')
    with open(input_dir, 'r') as file:
        msg = file.read()
    print(trim_text(msg))
