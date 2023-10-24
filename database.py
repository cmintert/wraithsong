import sqlite3
from datetime import datetime


def generate_db_name(prefix="wraithsong"):
    current_time = datetime.now().strftime("%d_%m_%Y_%H_%M_dev")
    return f"{prefix}_{current_time}"


class GameDatabase:
    _instance = None

    def __new__(cls, db_name=None):
        if cls._instance is None:
            data_base_name = db_name or generate_db_name()
            cls._instance = super(GameDatabase, cls).__new__(cls)
            cls._instance.conn = sqlite3.connect(data_base_name)
            cls._instance.create_tables()
        return cls._instance

    def create_tables(self):
        connection = self.conn.cursor()

        connection.execute(
            """
        CREATE TABLE IF NOT EXISTS Hexes (
            object_id TEXT PRIMARY KEY,
            q_axis TEXT,
            r_axis TEXT
        )
        """
        )

        connection.execute(
            """
        CREATE TABLE IF NOT EXISTS HexMap_size (
            left INTEGER,
            right INTEGER,
            top INTEGER,
            bottom INTEGER
        )
        """
        )

        connection.execute(
            """
        CREATE TABLE IF NOT EXISTS TerrainObjects (
            object_id TEXT PRIMARY KEY,
            internal_id TEXT,
            name TEXT,
            object_type TEXT,
            terrain_type TEXT,
            elevation INTEGER
        )
        """
        )
        self.conn.commit()

    def save_hex_object(self, hex_obj):
        connection = self.conn.cursor()
        connection.execute(
            """
        INSERT OR REPLACE INTO Hexes (object_id, q_axis, r_axis)
        VALUES (?, ?, ?)
        """,
            (
                hex_obj.object_id,
                hex_obj.q_axis,
                hex_obj.r_axis,
            ),
        )
        self.conn.commit()

    def save_hex_map_size(self, hex_map):
        connection = self.conn.cursor()
        connection.execute(
            """
        INSERT OR REPLACE INTO HexMap_size (left, right, top, bottom)
        VALUES (?, ?, ?, ?)
        """,
            (
                hex_map.left,
                hex_map.right,
                hex_map.top,
                hex_map.bottom,
            ),
        )
        self.conn.commit()

    def save_terrain_object(self, terrain_object):
        connection = self.conn.cursor()
        connection.execute(
            """
        INSERT OR REPLACE INTO TerrainObjects (object_id, internal_id, name, object_type, terrain_type, elevation)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                terrain_object.object_id,
                terrain_object.internal_id,
                terrain_object.name,
                terrain_object.object_type,
                terrain_object.terrain_type,
                terrain_object.elevation,
            ),
        )
        self.conn.commit()

    def load_terrain_object(self, object_id, terrain_class):
        connection = self.conn.cursor()
        connection.execute(
            "SELECT * FROM TerrainObjects WHERE object_id = ?", (object_id,)
        )
        row = connection.fetchone()

        if row:
            obj = terrain_class()
            (
                obj.object_id,
                obj.internal_id,
                obj.name,
                obj.object_type,
                obj.terrain_type,
                obj.elevation,
            ) = row
            return obj
        else:
            return None
