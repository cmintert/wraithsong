import database as db
import json

from visualize_map import MapVisualRepresentation
from gameobjects import GameObject, Terrain, Army


class Hex:

    directions_axial = [(+1, -1), (+1, 0), (0, +1), (-1, +1), (-1, 0), (0, -1)]  # Clockwise from pointy-top

    def __init__(self, q, r):

        self.q = q
        self.r = r
        self.s = -q - r



    def __hash__(self):

        return hash((self.q, self.r, self.s))

    def __eq__(self, other):

        if isinstance(other, Hex):
            return self.q == other.q and self.r == other.r and self.s == other.s
        return False

    def __str__(self):

        return f"Hex with the coordinates q: {self.q}, r: {self.r}, s: {self.s}"

    def get_axial_coord(self):

        return (self.q, self.r)

    def get_cube_coord(self):

        return (self.q, self.r, self.s)

    @classmethod
    def get_neighbour_hex(cls, hex_field, direction):
        neighbour_hex = Hex(hex_field.q + cls.directions_axial[direction][0],
                            hex_field.r + cls.directions_axial[direction][1])
        return neighbour_hex

    @classmethod
    def hex_obj_from_string(cls, string):

        return Hex(int(string.split(",")[0]), int(string.split(",")[1]))

class HexMap:

    def __init__(self):

        self.map = {}

    def initialize_map(self, left, right, top, bottom):

        for r in range(top, bottom + 1):
            r_offset = int(r // 2.0)
            for q in range(left - r_offset, right - r_offset + 1):
                self.map.update({Hex(q, r): []})

    def has_terrain(self, hex_field):

        for game_object in self.map[hex_field]:
            if isinstance(game_object, Terrain):
                return True
        return False

    def append_object(self, hex_field, game_object):

        if isinstance(game_object, Terrain) and self.has_terrain(hex_field):
            raise ValueError("There is already a terrain game_object in this hex_field")

        if hex_field in self.map:
            self.map[hex_field].append(game_object)
        else:
            self.map[hex_field] = [game_object]

    def get_hex_object_list(self, hex_field):

        return self.map[hex_field]

    def print_content_of_all_hexes(self):

        for hex_field,game_objects in self.map.items():
            print(hex_field)
            for game_object in game_objects:
                print(game_object)

class Game:

    def __init__(self, name):

        self.name = name
        self.hexmap = HexMap()
        self.players = []

        self.hexmap.initialize_map(-3, 3, -2, 2)

        self.hexmap.append_object(Hex(0, 0), Terrain("Eerie forrest","forest"))
        self.hexmap.append_object(Hex(1, 0), Terrain("Black Forest","plains"))
        self.hexmap.append_object(Hex(0, 0), GameObject())

        self.players.append("Player 1")
        self.players.append("Player 2")

game = Game("Wraithsong")

game.hexmap.print_content_of_all_hexes()


db.create_database()
db.clear_database()
db.create_gameobject_table()
for map_hex, object_inventory in game.hexmap.map.items():
    for item in object_inventory:
       db.write_gameobject(item, game.hexmap)
