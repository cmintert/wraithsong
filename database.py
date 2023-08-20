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
            Human_readable_id TEXT UNIQUE,
            internal_id TEXT UNIQUE NOT NULL,
            name TEXT,
            object_type TEXT,
            position TEXT
        )
    '''
    c.execute(sql_string)

    conn.commit()
    conn.close()

def write_gameobject(object,map):

    conn = sqlite3.connect('wraithsong.db')
    cursor = conn.cursor()

    position_object = object.get_position(map)
    position = f"{position_object.q}, {position_object.r}"

    sql_string = '''
        INSERT INTO game_objects (internal_id, name, object_type, position)
        VALUES (?,?,?,?)  
    '''
    cursor.execute(sql_string, (object.internal_id, object.name, object.object_type, position))

    conn.commit()
    conn.close()