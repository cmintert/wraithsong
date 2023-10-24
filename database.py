import sqlite3


class GameDatabase:
    _instance = None

    def __new__(cls, db_name="wraithsong_24_10_23"):
        if cls._instance is None:
            cls._instance = super(GameDatabase, cls).__new__(cls)
            cls._instance.conn = sqlite3.connect(db_name)
            cls._instance.create_tables()
        return cls._instance

    def create_tables(self):
        c = self.conn.cursor()
        c.execute(
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

    def save_terrain_object(self, terrain_object):
        c = self.conn.cursor()
        c.execute(
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

    def load_terrain_object(self, object_id, TerrainClass):
        c = self.conn.cursor()
        c.execute("SELECT * FROM TerrainObjects WHERE object_id = ?", (object_id,))
        row = c.fetchone()

        if row:
            obj = TerrainClass()
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
