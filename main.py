from PySide6.QtWidgets import QApplication

import sys

from map_logic import HexMap, EdgeMap, Hex, Edge, MoveCalculator, Graph
from visualize_map import HexMapApp
from gameobjects import Terrain, ObjectIDGenerator

class Game:

    """A class representing a game with hex maps, edge maps, and players.

    The `Game` class initializes a hexagonal map, an edge map, and a list of players. 
    It also uses an object ID generator for generating unique IDs and a move calculator 
    for computing movements on the map.

    Attributes:
        name (str): The name of the game.
        hexmap (HexMap): An instance of the HexMap class representing the game's hexagonal map.
        edgemap (EdgeMap): An instance of the EdgeMap class representing the edges of the hex map.
        players (list): A list of players participating in the game.
        object_id_generator (ObjectIDGenerator): An instance for generating unique object IDs.
        move_calculator (MoveCalculator): A calculator for determining movement within the game.

    Args:
        name (str): The name of the game.
    """

    def __init__(self, name):

        self.name = name
        self.hexmap = HexMap()
        self.edgemap = EdgeMap()
        self.object_id_generator = ObjectIDGenerator()
        self.players = []



game = Game("Wraithsong")
hexmap = game.hexmap
edgemap = game.edgemap
players = game.players


hexmap.initialize_hex_map(-8, 8, -8, 8)
edgemap.initialize_edge_map(hexmap.hex_map)
hexmap.fill_map_with_terrain(game)
move_calculator = MoveCalculator(hexmap, edgemap)
graph=Graph(move_calculator)

graph.djikstra(Hex.hex_obj_from_string("7,-3"))

edgemap.append_object_to_edge(Hex.hex_obj_from_string("0,0").get_edge_by_direction(0), Terrain(game.object_id_generator, "Generated_Terrain", "river"))
edgemap.append_object_to_edge(Hex.hex_obj_from_string("0,0").get_edge_by_direction(1), Terrain(game.object_id_generator, "Generated_Terrain", "river"))
edgemap.append_object_to_edge(Hex.hex_obj_from_string("0,0").get_edge_by_direction(2), Terrain(game.object_id_generator, "Generated_Terrain", "river"))
edgemap.append_object_to_edge(Hex.hex_obj_from_string("0,0").get_edge_by_direction(3), Terrain(game.object_id_generator, "Generated_Terrain", "river"))
edgemap.append_object_to_edge(Hex.hex_obj_from_string("0,0").get_edge_by_direction(4), Terrain(game.object_id_generator, "Generated_Terrain", "river"))



players.append("Player 1")
players.append("Player 2")



#print(move_calculator.distance_to_all(Hex.hex_obj_from_string("0,0")))

#hexmap.print_content_of_all_hexes()
#edgemap.print_content_of_all_edges()

#print (game.object_id_generator.used_counters)
#print(move_calculator.get_neighbour_conditions(Hex.hex_obj_from_string("-1,-2")))











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
