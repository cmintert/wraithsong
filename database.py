import sqlite3
from datetime import datetime


def generate_db_name(prefix="wraithsong"):
    """
    Generate a database name.

    Args:
        prefix (str): The prefix to use in the database name. Default is "wraithsong".

    Returns:
        str: The generated database name.

    Example:
        >>> generate_db_name()
        'wraithsong_16_04_2022_09_30_dev'
        >>> generate_db_name("mydb")
        'mydb_16_04_2022_09_30_dev'
    """
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
        CREATE TABLE IF NOT EXISTS Edges (
            object_id TEXT PRIMARY KEY,
            hex_field_1_object_id TEXT,
            hex_field_2_object_id TEXT,
            spawn_direction INTEGER
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
        CREATE TABLE IF NOT EXISTS HexMap_objects (
            hex_object_id TEXT,
            game_object_id TEXT UNIQUE
        )
        """
        )

        connection.execute(
            """
        CREATE TABLE IF NOT EXISTS EdgeMap_objects (
            edge_object_id TEXT,
            game_object_id TEXT UNIQUE
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

    def save_hex_objects(self, hexmap, hex_field):
        """
        Save hex objects to the game database.

        Args:
            hexmap: The hex map object that contains the hex objects.
            hex_field: The hex field to save the objects for.

        """
        connection = self.conn.cursor()

        object_list = hexmap.get_hex_object_list(hex_field)
        for game_object in object_list:
            connection.execute(
                """
                INSERT OR REPLACE INTO HexMap_objects (hex_object_id, game_object_id)
                VALUES (?, ?)
                """,
                (
                    hex_field.object_id,
                    game_object.object_id,
                ),
            )
            self.conn.commit()

    def save_edge_objects(self, edgemap, edge):
        connection = self.conn.cursor()
        edge_object_list = edgemap.get_edge_object_list(edge)
        for game_object in edge_object_list:
            connection.execute(
                """
                INSERT OR REPLACE INTO EdgeMap_objects (edge_object_id, game_object_id)
              VALUES (?, ?)
                """,
                (
                    edge.object_id,
                    game_object.object_id,
                ),
            )
            self.conn.commit()

    def save_edge_object(self, edge_obj):
        connection = self.conn.cursor()
        connection.execute(
            """
        INSERT OR REPLACE INTO Edges (object_id, hex_field_1_object_id, hex_field_2_object_id, spawn_direction)
        VALUES (?, ?, ?, ?)
        """,
            (
                edge_obj.object_id,
                edge_obj.hex_field_1.object_id,
                edge_obj.hex_field_2.object_id,
                edge_obj.spawn_direction,
            ),
        )
        self.conn.commit()
