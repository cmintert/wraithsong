import json
import math
import database as db
import random

from visualize_map import *
from gameobjects import *


class Hex:

    directions_axial = [(+1, -1), (+1, 0), (0, +1), (-1, +1), (-1, 0), (0, -1)]  # Clockwise from pointy-top

    def __init__(self, q_axis, r_axis):

        self.q_axis = q_axis
        self.r_axis = r_axis
        self.s_axis = -q_axis - r_axis



    def __hash__(self):

        return hash((self.q_axis, self.r_axis, self.s_axis))

    def __eq__(self, other):

        if isinstance(other, Hex):
            return self.q_axis == other.q_axis and self.r_axis == other.r_axis and self.s_axis == other.s_axis
        return False

    def __str__(self):

        return f"Hex at coordinates q:{self.q_axis}, r:{self.r_axis}"

    def get_axial_coordinates(self):

        return (self.q_axis, self.r_axis)

    def get_cube_coordinates(self):

        return (self.q_axis, self.r_axis, self.s_axis)

    def get_pixel_coordinates(self, size):

        x_axis = size * (3**0.5) * (self.q_axis + self.r_axis / 2)
        y_axis = size * 1.5 * self.r_axis
        return (x_axis, y_axis)

    # ordered_hex_pair is used for keeping direction of Edge objects consistent

    def ordered_hex_pair(hex1, hex2):
        if hex1.q_axis < hex2.q_axis or (hex1.q_axis == hex2.q_axis and hex1.r_axis < hex2.r_axis):
            return (hex1, hex2)
        return (hex2, hex1)

    @classmethod
    def get_neighbour_hex(cls, hex_field, direction):
        neighbour_hex = Hex(hex_field.q_axis + cls.directions_axial[direction][0],
                            hex_field.r_axis + cls.directions_axial[direction][1])
        return neighbour_hex

    @classmethod
    def hex_obj_from_string(cls, string):

        return Hex(int(string.split(",")[0]), int(string.split(",")[1]))

class Edge:

    def __init__(self, hex_field_1, hex_field_2):
        self.hex_field_1, self.hex_field_2 = Hex.ordered_hex_pair(hex_field_1, hex_field_2)

    def __hash__(self):
        return hash((self.hex_field_1, self.hex_field_2))

    def __eq__(self, other):
        if isinstance(other, Edge):
            return self.hex_field_1 == other.hex_field_1 and self.hex_field_2 == other.hex_field_2
        return False

    def __str__(self):
        return f"Edge between {self.hex_field_1} and {self.hex_field_2}"

    def get_hex_fields(self):
        return (self.hex_field_1, self.hex_field_2)

class HexMap:

    def __init__(self):
        # named this hex_map to avoid confusion with edge_map
        self.hex_map = {}

    def initialize_hex_map(self, left, right, top, bottom):

        for r_axis in range(top, bottom + 1):
            r_offset = int(r_axis // 2.0)
            for q_axis in range(left - r_offset, right - r_offset + 1):
                self.hex_map.update({Hex(q_axis, r_axis): []})

    def has_terrain(self, hex_field):

        for game_object in self.hex_map[hex_field]:
            if isinstance(game_object, Terrain):
                return True
        return False

    def append_object(self, hex_field, game_object):

        if isinstance(game_object, Terrain) and self.has_terrain(hex_field):
            raise ValueError("There is already a terrain game_object in this hex_field")

        if hex_field in self.hex_map:
            self.hex_map[hex_field].append(game_object)
        else:
            self.hex_map[hex_field] = [game_object]

    def get_hex_object_list(self, hex_field):

        return self.hex_map[hex_field]

    def get_object_by_id(self, object_id):

        for hex_field, game_objects in self.hex_map.items():
            for game_object in game_objects:
                if game_object.object_id == object_id:
                    return game_object
        return None


    def print_content_of_all_hexes(self):

        for hex_field,game_objects in self.hex_map.items():
            print(hex_field)
            for game_object in game_objects:
                print(game_object)

    def fill_map_with_terrain(self):

        for hex_field in self.hex_map.keys():
            choice = random.choice(["plain", "mountain", "forest", "water"])
            self.append_object(hex_field, Terrain(game.object_id_generator,"Generated_Terrain", choice))

class EdgeMap:

    def __init__(self):

        self.edge_map = {}

    def initialize_edge_map(self, hex_map):

        for hex_field in hex_map.keys():
            for direction in range(6):
                neighbour_hex = Hex.get_neighbour_hex(hex_field, direction)
                if Edge(hex_field, neighbour_hex) not in self.edge_map.keys():
                    self.edge_map.update({Edge(hex_field, neighbour_hex): []})

    def print_edge_map(self):

        print(len(self.edge_map))
        for edge in self.edge_map.keys():
            print(edge)
            print(self.edge_map[edge])


class Game:

    def __init__(self, name):

        self.name = name
        self.hexmap = HexMap()
        self.edgemap = EdgeMap()
        self.players = []
        self.object_id_generator = ObjectIDGenerator()
        self.hexmap.initialize_hex_map(-1, 1, -1, 1)



game = Game("Wraithsong")
hexmap = game.hexmap
edgemap = game.edgemap
players = game.players

edgemap.initialize_edge_map(hexmap.hex_map)
edgemap.print_edge_map()

players.append("Player 1")
players.append("Player 2")

hexmap.fill_map_with_terrain()


hexmap.print_content_of_all_hexes()


print (game.object_id_generator.used_counters)

app = QApplication(sys.argv)

window = HexMapApp(hexmap)
window.show()

sys.exit(app.exec())




#db.create_database()
#db.clear_database()
#db.create_gameobject_table()
#for map_hex, object_inventory in hexmap.hex_map.items():
#    for item in object_inventory:
#        db.write_gameobject(item, hexmap)
