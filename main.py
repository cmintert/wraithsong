from PySide6.QtWidgets import QApplication

import sys

from map_logic import HexMap, EdgeMap, Hex, Edge
from visualize_map import HexMapApp
from gameobjects import Terrain, ObjectIDGenerator

class Game:

    def __init__(self, name):

        self.name = name
        self.hexmap = HexMap()
        self.edgemap = EdgeMap()
        self.players = []
        self.object_id_generator = ObjectIDGenerator()
        self.hexmap.initialize_hex_map(-3, 3, -3, 3)

game = Game("Wraithsong")
hexmap = game.hexmap
edgemap = game.edgemap
players = game.players

edgemap.initialize_edge_map(hexmap.hex_map)

edgemap.append_object_to_edge(Hex.hex_obj_from_string("0,0").get_edge_by_direction(0), Terrain(game.object_id_generator, "Generated_Terrain", "river"))

players.append("Player 1")
players.append("Player 2")

hexmap.fill_map_with_terrain(game)


hexmap.print_content_of_all_hexes()
edgemap.print_content_of_all_edges()

print (game.object_id_generator.used_counters)

app = QApplication(sys.argv)

window = HexMapApp(hexmap, edgemap)
window.show()

sys.exit(app.exec())




#db.create_database()
#db.clear_database()
#db.create_gameobject_table()
#for map_hex, object_inventory in hexmap.hex_map.items():
#    for item in object_inventory:
#        db.write_gameobject(item, hexmap)
