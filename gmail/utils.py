import re
import os
import html


def trim_message(msg):
    msg = msg.strip()
    msg = re.sub(r'\n\s+', '\n', msg)[:400] + ' --truncated'
    msg = html.escape(msg)
    return msg

# for testing
if __name__ == '__main__':
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(THIS_FOLDER, 'input.txt')
    with open(input_dir, 'r') as file:
        msg = file.read()
    print(trim_message(msg))
