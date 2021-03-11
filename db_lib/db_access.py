import psycopg2
import os
import pickle
from datetime import datetime
from dateutil.tz import gettz

# PostgresDB connection on heroku server
DATABASE_URL = os.environ['DATABASE_URL']
GMAIL_ADDRESS = 'rtcbcotprinter@gmail.com'


def get_creds_from_db():
    # conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME,
    #                         user=DB_USERNAME, password=DB_PASSWORD)
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute(
        "SELECT pickle FROM gmail WHERE name = %s;", (GMAIL_ADDRESS, ))
    result = cur.fetchone()
    if result:
        result = pickle.loads(result[0])
    cur.close()
    conn.close()
    return result


def save_creds_to_db(creds):
    pickle_byte = pickle.dumps(creds)
    # conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME,
    #                         user=DB_USERNAME, password=DB_PASSWORD)    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute(
        "SELECT EXISTS(SELECT pickle FROM gmail WHERE name = %s);", (GMAIL_ADDRESS, ))
    if cur.fetchone()[0]:
        cur.execute("UPDATE gmail SET pickle = %s;", (pickle_byte,))
    else:
        cur.execute("INSERT INTO gmail (name, pickle) VALUES (%s, %s);",
                    (GMAIL_ADDRESS, pickle_byte))
    conn.commit()
    cur.close()
    conn.close()
    return True


def delete_creds_from_db():
    result = False
    # conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME,
    #                         user=DB_USERNAME, password=DB_PASSWORD)
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute(
        "SELECT EXISTS(SELECT pickle FROM gmail WHERE name = %s);", (GMAIL_ADDRESS, ))
    if cur.fetchone()[0]:
        cur.execute(
            "DELETE FROM gmail WHERE name = %s;", (GMAIL_ADDRESS, ))
        result = True
    conn.commit()
    cur.close()
    conn.close()
    return result


def get_history_id_from_db():
    # conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME,
    #                         user=DB_USERNAME, password=DB_PASSWORD)
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT history_id FROM history ORDER BY id DESC LIMIT 1;")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else False


def save_history_id_to_db(history_id):
    # conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME,
    #                         user=DB_USERNAME, password=DB_PASSWORD)
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    ts = datetime.now(tz=gettz('Asia/Singapore'))
    cur.execute("INSERT INTO history (history_id, tstamp) VALUES (%s, %s);", (history_id, ts))
    conn.commit()
    cur.close()
    conn.close()
    return True
