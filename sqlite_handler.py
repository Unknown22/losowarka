import sqlite3
from sqlite3 import Error
import random


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None


def execute_sql(conn, sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
    except Error as e:
        print(e)


def execute_select(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        return c
    except Error as e:
        print(e)


def prepare_schema(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS gifts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_gift TEXT,
        for_gift TEXT
    );
    """
    execute_sql(conn, sql)

    sql = """
    CREATE TABLE IF NOT EXISTS auth(
        id INTEGER PRIMARY KEY,
        person TEXT,
        got_reminder_pin INTEGER DEFAULT 0,
        pin INTEGER,
        reminder_pin INTEGER,
        is_available INTEGER DEFAULT 1
    );
    """
    execute_sql(conn, sql)


def prepare_auth(conn, people):
    for person in people:
        sql = """
        INSERT INTO auth(person, pin, reminder_pin) 
            SELECT "{person}", {pin}, {reminder_pin} 
            WHERE NOT EXISTS(SELECT 1 FROM auth WHERE person = "{person}");
        """.format(**{
            "person": person['person'],
            "pin": person['pin'],
            "reminder_pin": person['reminder_pin']
        })
        execute_sql(conn, sql)


def prepare_start_data(conn):
    people = [
        {
            "person": "Klaudia",
            "pin": 677674,
            "reminder_pin": 852590
        },
        {
            "person": "Przemek",
            "pin": 746500,
            "reminder_pin": 629079
        },
        {
            "person": "Anita",
            "pin": 119217,
            "reminder_pin": 397697
        },
        {
            "person": "Ania",
            "pin": 427951,
            "reminder_pin": 826169
        },
        {
            "person": "Karolina",
            "pin": 373632,
            "reminder_pin": 209798
        }
    ]
    prepare_auth(conn, people)


def check_if_person_got_reminder_key(conn, person):
    sql = 'SELECT got_reminder_pin FROM auth WHERE person = "{person}";'.format(**{"person": person})
    return execute_select(conn, sql).fetchone()[0]


def get_person_pin(conn, person):
    sql = 'SELECT pin FROM auth WHERE person = "{person}";'.format(**{"person": person})
    return execute_select(conn, sql).fetchone()[0]


def get_person_reminder_pin(conn, person):
    sql = 'SELECT reminder_pin FROM auth WHERE person = "{person}";'.format(**{"person": person})
    return execute_select(conn, sql).fetchone()[0]


def get_person_and_reminder_pin(conn, person):
    sql = 'SELECT person FROM auth WHERE is_available = 1 AND person != "{person}";'.format(**{"person": person})
    available_people = []
    for p in execute_select(conn, sql).fetchall():
        available_people.append(p[0])
    person_to_return = random.choice(available_people)

    sql = 'UPDATE auth SET is_available = 0 WHERE person = "{person}";'.format(**{"person": person_to_return})
    execute_sql(conn, sql)

    sql = 'UPDATE auth SET got_reminder_pin = 1 WHERE person = "{person}";'.format(**{"person": person})
    execute_sql(conn, sql)

    sql = 'INSERT INTO gifts(from_gift, for_gift) VALUES ("{person}","{person_to_return}");'.format(
        **{"person": person, "person_to_return": person_to_return})
    execute_sql(conn, sql)

    sql = 'SELECT reminder_pin FROM auth WHERE person = "{person}";'.format(**{"person": person})
    reminder_pin = execute_select(conn, sql).fetchone()[0]
    return person_to_return, reminder_pin


def get_person_to_gift(conn, person):
    sql = 'SELECT for_gift FROM gifts WHERE from_gift = "{person}";'.format(**{"person":person})
    return execute_select(conn, sql).fetchone()[0]
