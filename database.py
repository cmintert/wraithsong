import sqlite3
import os


def create_database():
    data_path = "./"
    filename = "wraithsong"

    os.makedirs(data_path, exist_ok=True)

    conn = sqlite3.connect(os.path.join(data_path, f"{filename}.db"))
    conn.close()


def clear_database(name="wraithsong.db"):
    conn = sqlite3.connect(name)
    cursor = conn.cursor()

    sql_string = "SELECT name FROM sqlite_master WHERE type='table'"
    cursor.execute(sql_string)

    tables = cursor.fetchall()

    for table in tables:
        sql_string = f"DROP TABLE {table[0]}"
        cursor.execute(sql_string)

    conn.commit()
    conn.close()


def create_gameobject_table():
    conn = sqlite3.connect("wraithsong.db")
    cursor = conn.cursor()

    sql_string = """
        CREATE TABLE IF NOT EXISTS game_objects (
            Human_readable_id TEXT UNIQUE,
            internal_id TEXT UNIQUE NOT NULL,
            name TEXT,
            object_type TEXT,
            position TEXT
        )
    """
    cursor.execute(sql_string)

    conn.commit()
    conn.close()


def write_gameobject(game_object, hexmap):
    conn = sqlite3.connect("wraithsong.db")
    cursor = conn.cursor()

    position_object = game_object.get_position(hexmap)
    position = f"{position_object.q_axis}, {position_object.r_axis}"

    sql_string = """
        INSERT INTO game_objects (internal_id, name, object_type, position)
        VALUES (?,?,?,?)  
    """
    cursor.execute(
        sql_string,
        (game_object.internal_id, game_object.name, game_object.object_type, position),
    )

    conn.commit()
    conn.close()
