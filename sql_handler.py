# -*- coding: utf-8 -*-

import pymysql
import random
import os
import logging

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')


def create_connection():
    try:
        if os.environ.get('GAE_ENV') == 'standard':
            # If deployed, use the local socket interface for accessing Cloud SQL
            unix_socket = '/cloudsql/{}'.format(db_connection_name)
            cnx = pymysql.connect(user=db_user, password=db_password,
                                  unix_socket=unix_socket, db=db_name,
                                  cursorclass=pymysql.cursors.DictCursor)
        else:
            # If running locally, use the TCP connections instead
            # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
            # so that your application can use 127.0.0.1:3306 to connect to your
            # Cloud SQL instance
            host = '127.0.0.1'
            cnx = pymysql.connect(user=db_user, password=db_password,
                                  host=host, db=db_name, cursorclass=pymysql.cursors.DictCursor)
        return cnx
    except Exception as e:
        logger = logging.getLogger("flask.app")
        logger.exception("Error in MySQL connection. {}".format(e))


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
    except Exception as e:
        print(e)


def execute_select(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        return c
    except Exception as e:
        print(e)


def prepare_schema(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS gifts(
        id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
        from_gift VARCHAR(40),
        for_gift VARCHAR(40)
    );
    """
    execute_sql(conn, sql)

    sql = """
    CREATE TABLE IF NOT EXISTS auth(
        id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
        person VARCHAR(40),
        got_reminder_pin INT DEFAULT 0,
        pin INT,
        reminder_pin INT,
        is_available INT DEFAULT 1
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
    return execute_select(conn, sql).fetchone()['got_reminder_pin']


def get_person_pin(conn, person):
    sql = 'SELECT pin FROM auth WHERE person = "{person}";'.format(**{"person": person})
    return execute_select(conn, sql).fetchone()['pin']


def get_person_reminder_pin(conn, person):
    sql = 'SELECT reminder_pin FROM auth WHERE person = "{person}";'.format(**{"person": person})
    return execute_select(conn, sql).fetchone()['reminder_pin']


def get_person_and_reminder_pin(conn, person):
    sql = 'SELECT person FROM auth WHERE is_available = 1 AND person != "{person}";'.format(**{"person": person})
    available_people = []
    print(execute_select(conn, sql).fetchall())
    for p in execute_select(conn, sql).fetchall():
        available_people.append(p['person'])
    person_to_return = random.choice(available_people)

    sql = 'UPDATE auth SET is_available = 0 WHERE person = "{person}";'.format(**{"person": person_to_return})
    execute_sql(conn, sql)

    sql = 'UPDATE auth SET got_reminder_pin = 1 WHERE person = "{person}";'.format(**{"person": person})
    execute_sql(conn, sql)

    sql = 'INSERT INTO gifts(from_gift, for_gift) VALUES ("{person}","{person_to_return}");'.format(
        **{"person": person, "person_to_return": person_to_return})
    execute_sql(conn, sql)

    sql = 'SELECT reminder_pin FROM auth WHERE person = "{person}";'.format(**{"person": person})
    reminder_pin = execute_select(conn, sql).fetchone()['reminder_pin']
    return person_to_return, reminder_pin


def get_person_to_gift(conn, person):
    sql = 'SELECT for_gift FROM gifts WHERE from_gift = "{person}";'.format(**{"person":person})
    return execute_select(conn, sql).fetchone()['for_gift']
