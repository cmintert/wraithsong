import json
import math
import database as db


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

        return f"Hex with the coordinates q: {self.q_axis}, r: {self.r_axis}, s: {self.s_axis}"

    def get_axial_coordinates(self):

        return (self.q_axis, self.r_axis)

    def get_cube_coordinates(self):

        return (self.q_axis, self.r_axis, self.s_axis)

    def get_pixel_coordinates(self, size):

        x_axis = size * (3**0.5) * (self.q_axis + self.r_axis / 2)
        y_axis = size * 1.5 * self.r_axis
        return (x_axis, y_axis)

    @classmethod
    def get_neighbour_hex(cls, hex_field, direction):
        neighbour_hex = Hex(hex_field.q_axis + cls.directions_axial[direction][0],
                            hex_field.r_axis + cls.directions_axial[direction][1])
        return neighbour_hex

    @classmethod
    def hex_obj_from_string(cls, string):

        return Hex(int(string.split(",")[0]), int(string.split(",")[1]))

class HexMap:

    def __init__(self):

        self.map = {}

    def initialize_map(self, left, right, top, bottom):

        for r_axis in range(top, bottom + 1):
            r_offset = int(r_axis // 2.0)
            for q_axis in range(left - r_offset, right - r_offset + 1):
                self.map.update({Hex(q_axis, r_axis): []})

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

    def get_object_by_id(self, object_id):

        for hex_field, game_objects in self.map.items():
            for game_object in game_objects:
                if game_object.object_id == object_id:
                    return game_object
        return None


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
        self.object_id_generator = ObjectIDGenerator()
        self.hexmap.initialize_map(-2, 2, -2, 2)



game = Game("Wraithsong")
hexmap = game.hexmap
players = game.players

players.append("Player 1")
players.append("Player 2")

hexmap.append_object(Hex(0, 0), Terrain(game.object_id_generator, "Dark Forest","forest"))
hexmap.append_object(Hex(0, 0), Army(game.object_id_generator, "1st Dragooners",game.players[0]))

hexmap.print_content_of_all_hexes()



players.append("Player 1")
players.append("Player 2")


print (game.object_id_generator.used_counters)

app = QApplication(sys.argv)

window = HexMapApp(hexmap)
window.show()

sys.exit(app.exec())




db.create_database()
db.clear_database()
db.create_gameobject_table()
for map_hex, object_inventory in hexmap.map.items():
    for item in object_inventory:
        db.write_gameobject(item, hexmap)
