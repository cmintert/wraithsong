import sqlite3
import os

def create_database():

    data_path = './'
    filename = 'wraithsong'

    os.makedirs(data_path, exist_ok=True)

    conn = sqlite3.connect(os.path.join(data_path, f"{filename}.db"))
    conn.close()

def clear_database(name="wraithsong.db"):

    conn = sqlite3.connect(name)
    c = conn.cursor()

    sql_string = "SELECT name FROM sqlite_master WHERE type='table'"
    c.execute(sql_string)

    tables = c.fetchall()

    for table in tables:

        sql_string = f"DROP TABLE {table[0]}"
        c.execute(sql_string)

    conn.commit()
    conn.close()

def create_gameobject_table():
    conn = sqlite3.connect('wraithsong.db')
    c = conn.cursor()

    sql_string = '''
        CREATE TABLE IF NOT EXISTS game_objects (
            internal_id TEXT PRIMARY KEY UNIQUE NOT NULL,
            name TEXT,
            type TEXT
        )
    '''
    c.execute(sql_string)

    conn.commit()
    conn.close()

def write_gameobject(object):
    conn = sqlite3.connect('wraithsong.db')
    c = conn.cursor()

    sql_string = '''
        INSERT INTO game_objects (internal_id, name, type)
        VALUES (?,?,?)  
    '''
    c.execute(sql_string, (object.internal_id, object.name, object.type))

    conn.commit()
    conn.close()