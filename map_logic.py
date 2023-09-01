import math
import random

from gameobjects import Terrain

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

    def get_cornerpixel_coordinates(self, size):

        x_axis, y_axis = self.get_pixel_coordinates(size)

        # Calculate the pixel corner points for the hex
        corners = []
        for corner_number in range(6):
            angle_deg = (60 * corner_number - 90) % 360
            angle_rad = math.pi / 180 * angle_deg  
            corners.append((x_axis + size * math.cos(angle_rad), y_axis + size * math.sin(angle_rad)))
        return corners

    def get_edgecenter_pixel_coordinates(self, size):
    
        corners = self.get_cornerpixel_coordinates(size)
        edge_centers = []

        # Calculate the coordinates of the edge centers
        for i in range(len(corners)):
            x1, y1 = corners[i]
            x2, y2 = corners[(i + 1) % 6]  # Loop back to the first corner after the last one
            edge_centers.append(((x1 + x2) / 2, (y1 + y2) / 2))
        return edge_centers

    def get_edge_by_direction(self,direction):

        if direction < 0 or direction > 5:
            raise ValueError("Direction must be between 0 and 5")

        #as the the edges are generated in order we need to keep that order

        neighbour_hex = Hex.get_neighbour_hex(self, direction)
        ordered_hex_pair = Hex.ordered_hex_pair(self, neighbour_hex)

        return Edge(ordered_hex_pair[0], ordered_hex_pair[1], direction)

    # ordered_hex_pair is used for keeping direction of Edge objects consistent
    @staticmethod
    def ordered_hex_pair(hex1, hex2):
        if hex1.q_axis < hex2.q_axis or (hex1.q_axis == hex2.q_axis and hex1.r_axis < hex2.r_axis):
            return (hex1, hex2)
        return (hex2, hex1)

    @classmethod
    def hex_direction(cls, hex_field_1, hex_field_2):

        # Determine the direction from hex1 to hex2. They have to be direct neighbors.

        delta_q = hex_field_2.q_axis - hex_field_1.q_axis
        delta_r = hex_field_2.r_axis - hex_field_1.r_axis

        if delta_q == 1 and delta_r == -1:
            return 0  # North-East
        elif delta_q == 1 and delta_r == 0:
            return 1  # East
        elif delta_q == 0 and delta_r == 1:
            return 2  # South-East
        elif delta_q == -1 and delta_r == 1:
            return 3  # South-West
        elif delta_q == -1 and delta_r == 0:
            return 4  # West
        elif delta_q == 0 and delta_r == -1:
            return 5  # North-West
        else:
            # This condition should not be reached if hex2 is a direct neighbor of hex1
            return None

    @classmethod
    def get_neighbour_hex(cls, hex_field, direction):
        neighbour_hex = Hex(hex_field.q_axis + cls.directions_axial[direction][0],
                            hex_field.r_axis + cls.directions_axial[direction][1])
        return neighbour_hex

    @classmethod
    def hex_obj_from_string(cls, string):

        return Hex(int(string.split(",")[0]), int(string.split(",")[1]))


class Edge:
    """
    Defines an edge between two hexes. The hexes are ordered in the Edge object to keep the direction consistent. 
    Two hexes are used to define the position of the edge to quickly access the hexes from the edge.
    
    The spawn_hex is the hex from which the edge is spawned. 
    The spawn_direction is the direction of the edge from the spawn_hex.
    
    Args:

        hex_field_1 (Hex): The first hex of the edge
        hex_field_2 (Hex): The second hex of the edge
        spawn_direction (int): The direction to spwan the edge from the spawn_hex
    
    Methods:

        get_hex_fields: Returns the hexes of the edge in a tuple
    """
    def __init__(self, hex_field_1, hex_field_2,spawn_direction):
        self.spawn_hex = hex_field_1
        self.spawn_direction = spawn_direction
        self.hex_field_1, self.hex_field_2 = Hex.ordered_hex_pair(hex_field_1, hex_field_2)

    def __hash__(self):
        return hash((self.hex_field_1, self.hex_field_2))

    def __eq__(self, other):
        if isinstance(other, Edge):
            return self.hex_field_1 == other.hex_field_1 and self.hex_field_2 == other.hex_field_2 and self.spawn_direction == other.spawn_direction
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

    def append_object_to_hex(self, hex_field, game_object):

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

    def fill_map_with_terrain(self, game):

        for hex_field in self.hex_map.keys():
            choice = random.choice(["plain", "mountain", "forest", "water"])
            self.append_object_to_hex(hex_field, Terrain(game.object_id_generator, "Generated_Terrain", choice))


class EdgeMap:

    def __init__(self):

        self.edge_map = {}

    def initialize_edge_map(self, hex_map):

        for hex_field in hex_map.keys():
            for direction in range(6):
                neighbour_hex = Hex.get_neighbour_hex(hex_field, direction)
                if Edge(hex_field, neighbour_hex, direction) not in self.edge_map.keys():
                    self.edge_map.update({Edge(hex_field, neighbour_hex,direction): []})

    def append_object_to_edge(self, edge, game_object):

        if isinstance(game_object, Terrain) and self.has_terrain(edge):
            raise ValueError("There is already a terrain game_object in this hex_field")

        if edge in self.edge_map:
            self.edge_map[edge].append(game_object)
        else:
            self.edge_map[edge] = [game_object]

    def get_edge_object_list(self, edge):

        return self.edge_map[edge]

    def has_terrain(self, edge):

        for game_object in self.edge_map[edge]:
            if isinstance(game_object, Terrain):
                return True
        return False

    def print_content_of_all_edges(self):

        for edge, game_objects in self.edge_map.items():
            print(edge)
            for game_object in game_objects:
                print(game_object)
        print(f"There are {len(self.edge_map)} edges in the edge map")

class MoveCalculator:

    def __init__(self, hex_map, edge_map):

        self.hex_map = hex_map
        self.edge_map = edge_map    
    
    def get_move_to_neighbour_cost(self, hex_field):
                
             #cost_list is a list of movecost while direction equals the index
        cost_list = []
        
        for direction in range(6):
            
            neighbour_hex = Hex.get_neighbour_hex(hex_field, direction)
            hex_objects = self.hex_map.get_hex_object_list(neighbour_hex)
            
            edge_objects = self.edge_map.get_edge_object_list(hex_field.get_edge_by_direction(direction))
            print(hex_field.get_edge_by_direction(direction))

            impassable = False

            for game_object in hex_objects:
                if isinstance(game_object, Terrain):
                    movement_cost = game_object.movement_cost
                    if game_object.movement_cost <= -1:
                        impassable = True
            
            for game_object in edge_objects:
                if isinstance(game_object, Terrain):                
                    movement_cost += game_object.movement_cost
                    if game_object.movement_cost <= -1:
                        impassable = True
            
            if impassable == True:
                movement_cost = -1            

            cost_list.append(movement_cost)
           
        return cost_list