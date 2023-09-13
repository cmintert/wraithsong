from PySide6.QtWidgets import QApplication

import sys

from map_logic import HexMap, EdgeMap, Hex, MoveCalculator, Graph
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


hexmap.initialize_hex_map(-2, 1, -2, 1)
edgemap.initialize_edge_map(hexmap.hex_map)
hexmap.fill_map_with_terrain(game)


edgemap.append_object_to_edge(
    Hex.hex_obj_from_string("0,0").get_edge_by_direction(0),
    Terrain(game.object_id_generator, "Generated_Terrain", "river"),
)
# edgemap.append_object_to_edge(Hex.hex_obj_from_string("0,0").get_edge_by_direction(1), Terrain(game.object_id_generator, "Generated_Terrain", "river"))
edgemap.append_object_to_edge(
    Hex.hex_obj_from_string("0,0").get_edge_by_direction(2),
    Terrain(game.object_id_generator, "Generated_Terrain", "river"),
)
edgemap.append_object_to_edge(
    Hex.hex_obj_from_string("0,0").get_edge_by_direction(3),
    Terrain(game.object_id_generator, "Generated_Terrain", "river"),
)
edgemap.append_object_to_edge(
    Hex.hex_obj_from_string("0,0").get_edge_by_direction(4),
    Terrain(game.object_id_generator, "Generated_Terrain", "river"),
)
edgemap.append_object_to_edge(
    Hex.hex_obj_from_string("0,0").get_edge_by_direction(5),
    Terrain(game.object_id_generator, "Generated_Terrain", "river"),
)


move_calculator = MoveCalculator(hexmap, edgemap)
graph = Graph(move_calculator)


players.append("Player 1")
players.append("Player 2")


app = QApplication(sys.argv)

window = HexMapApp(hexmap, edgemap, graph)
window.setStyleSheet("QMainWindow { background-color: gray; }")
window.show()

sys.exit(app.exec())
