from PySide6.QtWidgets import QApplication

import sys

from map_logic import HexMap, EdgeMap, Hex, Edge, MoveCalculator
from visualize_map import HexMapApp
from gameobjects import Terrain, ObjectIDGenerator

class Game:

    def __init__(self, name):

        self.name = name
        self.hexmap = HexMap()
        self.edgemap = EdgeMap()
        self.players = []
        self.object_id_generator = ObjectIDGenerator()
        self.hexmap.initialize_hex_map(-2, 2, -2, 2)
        self.move_calculator = MoveCalculator(self.hexmap, self.edgemap)

game = Game("Wraithsong")
hexmap = game.hexmap
edgemap = game.edgemap
players = game.players
move_calculator = game.move_calculator

edgemap.initialize_edge_map(hexmap.hex_map)

edgemap.append_object_to_edge(Hex.hex_obj_from_string("0,0").get_edge_by_direction(0), Terrain(game.object_id_generator, "Generated_Terrain", "river"))
edgemap.append_object_to_edge(Hex.hex_obj_from_string("0,0").get_edge_by_direction(1), Terrain(game.object_id_generator, "Generated_Terrain", "river"))
edgemap.append_object_to_edge(Hex.hex_obj_from_string("0,0").get_edge_by_direction(2), Terrain(game.object_id_generator, "Generated_Terrain", "river"))
edgemap.append_object_to_edge(Hex.hex_obj_from_string("0,0").get_edge_by_direction(3), Terrain(game.object_id_generator, "Generated_Terrain", "river"))
edgemap.append_object_to_edge(Hex.hex_obj_from_string("0,0").get_edge_by_direction(4), Terrain(game.object_id_generator, "Generated_Terrain", "river"))

for hex_object in hexmap.get_hex_object_list(Hex.hex_obj_from_string("0,0")):
    print(hex_object)

players.append("Player 1")
players.append("Player 2")

hexmap.fill_map_with_terrain(game)


hexmap.print_content_of_all_hexes()
edgemap.print_content_of_all_edges()

print (game.object_id_generator.used_counters)
print(move_calculator.get_neighbour_conditions(Hex.hex_obj_from_string("0,0")))

app = QApplication(sys.argv)

window = HexMapApp(hexmap, edgemap)
window.show()

sys.exit(app.exec())



db.create_database()
db.clear_database()
db.create_gameobject_table()
for map_hex, object_inventory in hexmap.hex_map.items():
    for item in object_inventory:
        db.write_gameobject(item, hexmap)
