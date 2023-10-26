import json
import math
import random
import re
from typing import Type

from database import GameDatabase
from gameobjects import ObjectIDGenerator, Terrain


class Hex:
    """
    A class representing a hexagon on a hexagonal grid.

    Attributes:
        q_axis (int): The q-axis coordinate of the hexagon.
        r_axis (int): The r-axis coordinate of the hexagon.
        s_axis (int): The s-axis coordinate of the hexagon, calculated as -q_axis - r_axis.
    """

    # Directions clockwise from pointy-top
    directions_axial = [
        (+1, -1),
        (+1, 0),
        (0, +1),
        (-1, +1),
        (-1, 0),
        (0, -1),
    ]

    def __init__(self, q_axis, r_axis):
        """
        Initializes a Hex object with the given q-axis and r-axis coordinates.

        q-axis and r-axis are the coordinates of the hexagon on the hexagonal grid.
        The s-axis coordinate is calculated as -q_axis - r_axis.

        Args:
            q_axis (int): The q-axis coordinate of the hexagon.
            r_axis (int): The r-axis coordinate of the hexagon.
        """
        self.object_id = f"{q_axis},{r_axis}"
        self.game_database = GameDatabase()
        self.q_axis = q_axis
        self.r_axis = r_axis
        self.s_axis = -q_axis - r_axis

    def __hash__(self):
        """
        Returns the hash value of the Hex object.

        Returns:
            int: The hash value of the Hex object.
        """

        return hash((self.q_axis, self.r_axis, self.s_axis))

    def __eq__(self, other):
        """
        Checks if the Hex object is equal to another object by comparing the axis values.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if the Hex object is equal to the other object, False otherwise.
        """
        if isinstance(other, Hex):
            return (
                self.q_axis == other.q_axis
                and self.r_axis == other.r_axis
                and self.s_axis == other.s_axis
            )
        return False

    def __str__(self):
        """
        Returns a string representation of the Hex object.

        Returns:
            str: A string representation of the Hex object.
        """
        return f"Hex at coordinates q:{self.q_axis}, r:{self.r_axis}"

    def get_axial_coordinates(self):
        """
        Returns the axial q and r coordinates of the Hex object.

        Returns:
            tuple: A tuple containing the q-axis and r-axis coordinates of the Hex object.
        """
        return self.q_axis, self.r_axis

    def get_cube_coordinates(self):
        """
        Returns the cube coordinates q,r and s of the Hex object.

        Returns:
            tuple: A tuple containing the q-axis, r-axis, and s-axis coordinates of the Hex object.
        """
        return self.q_axis, self.r_axis, self.s_axis

    def get_pixel_coordinates(self, size):
        """
        Convert hexagonal coordinates to pixel coordinates.

        Given a hex size, this method calculates the pixel coordinates (x, y)
        corresponding to the hex's axial coordinates (q, r).

        Args:
            size (float): The size of the hex, which may represent the hex's radius
                          or the distance from the center to a corner.

        Returns:
            tuple(float, float): A tuple containing the x and y pixel coordinates
                                 corresponding to the hex's axial coordinates.

        Notes:
            - The method uses the axial coordinate system for hexagonal grids,
              where each hex has two coordinates: q (column) and r (row).
            - The formulae used in the method are standard for converting hexagonal
              coordinates to a 2D Cartesian coordinate system.

        Example:
            >>> hex_instance = Hex(1, 2)  # Assuming axial coordinates (1, 2) and the class is named Hex
            >>> pixel_coords = hex_instance.get_pixel_coordinates(10)
            >>> print(pixel_coords)
            (x_value, y_value)
        """

        x_axis = size * (3**0.5) * (self.q_axis + self.r_axis / 2)
        y_axis = size * 1.5 * self.r_axis
        return x_axis, y_axis

    def get_cornerpixel_coordinates(self, size):
        """
        Calculate the pixel coordinates of the six corners of a hexagon.

        Given the center coordinates of a hexagon and its size, this code snippet calculates
        the pixel coordinates of all six corners of the hexagon. The coordinates are
        calculated based on a 60-degree separation between each corner, starting from
        a vertical line (which is why we subtract 90 degrees).

        Attributes:
            x_axis (float): The x-coordinate of the hexagon's center.
            y_axis (float): The y-coordinate of the hexagon's center.
            size (float): The distance from the center of the hexagon to any of its corners.

        Returns:
            list[tuple]: A list of tuples where each tuple contains the (x, y) coordinates
                         of a corner of the hexagon.

        Example:
            Assuming this code is a method inside a class, and the class instance has a
            method called `get_pixel_coordinates`:

            >>> hex_instance = HexClass()  # Assuming the class is named HexClass
            >>> corners = hex_instance.method_name(10)  # Replace method_name with actual method name
            >>> print(corners)
            [(x1, y1), (x2, y2), ...]

        Notes:
            The formula used in the snippet to calculate the angle in degrees is based on
            the hexagonal symmetry, where each corner is 60 degrees apart from the next.
        """

        x_axis, y_axis = self.get_pixel_coordinates(size)

        # Calculate the pixel corner points for the hex
        corners = []
        for corner_number in range(6):
            angle_deg = (60 * corner_number - 90) % 360
            angle_rad = math.pi / 180 * angle_deg

            corners.append(
                (
                    x_axis + size * math.cos(angle_rad),
                    y_axis + size * math.sin(angle_rad),
                )
            )
        return corners

    def get_edgecenter_pixel_coordinates(self, size):
        """
        Returns the pixel coordinates of the centers of the edges of the Hex object.

        This method is used in the visual placement of edge objects on the map.

        Args:
            size (int): The size of the Hex object. Size is the outer radius of the hexagon.

        Returns:
            list: A list of tuples containing the x-axis and y-axis coordinates of the centers of the edges of the Hex object.
        """
        corners = self.get_cornerpixel_coordinates(size)
        edge_centers = []

        # Calculate the coordinates of the edge centers
        for i in range(len(corners)):
            x1, y1 = corners[i]
            x2, y2 = corners[
                (i + 1) % 6
            ]  # Loop back to the first corner after the last one
            edge_centers.append(((x1 + x2) / 2, (y1 + y2) / 2))
        return edge_centers

    def get_edge_by_direction(self, direction):
        """
        Returns the Edge object in the given direction from the Hex object.

        Args:
            direction (int): The direction of the edge to get, between 0 and 5.

        Returns:
            Edge: The Edge object in the given direction from the Hex object.

        Raises:
            Value Error if direction is not between 0 and 5
        """
        if direction < 0 or direction > 5:
            raise ValueError("Direction must be between 0 and 5")

        # as the the edges are generated in order we need to keep that order

        neighbour_hex = Hex.get_neighbour_hex(self, direction)
        ordered_hex_pair = Hex.ordered_hex_pair(self, neighbour_hex)

        return Edge(ordered_hex_pair[0], ordered_hex_pair[1], direction)

    @staticmethod
    def ordered_hex_pair(hex1, hex2):
        """
        Returns a tuple of Hex objects in a consistent order.

        Hexes in a square grid are ordered by q-axis top to bottom first, then by r-axis left to right. This method returns a tuple of Hex objects in a consistent order, so that the same pair of Hex objects always returns the same tuple.

        Args:
            hex1 (Hex): The first Hex object.
            hex2 (Hex): The second Hex object.

        Returns:
            tuple: A tuple of Hex objects in a consistent order.
        """
        if hex1.q_axis < hex2.q_axis or (
            hex1.q_axis == hex2.q_axis and hex1.r_axis < hex2.r_axis
        ):
            return hex1, hex2
        return hex2, hex1

    @classmethod
    def hex_direction(cls, hex_field_1, hex_field_2):
        """
        Returns the direction from one Hex object to another.

        The directions are from 0 to 5 in a clockwise order, representing NE E SE SW W NW.

        Args:
            hex_field_1 (Hex): The first Hex object.
            hex_field_2 (Hex): The second Hex object.

        Returns:
            int: The direction from hex_field_1 to hex_field_2, between 0 and 5.

        Raises: ValueError if the hexes are not direct neighbors
        """
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

        raise ValueError("The hexes are not direct neighbors")

    @classmethod
    def get_neighbour_hex(cls: Type["Hex"], hex_field: "Hex", direction: int) -> "Hex":
        """
        Returns the Hex object in the given direction from another Hex object.

        Args:
            hex_field (Hex): The Hex object to start from.
            direction (int): The direction to move in, between 0 and 5.

        Returns:
            Hex: The Hex object in the given direction from the starting Hex object.
        """
        neighbour_hex = Hex(
            hex_field.q_axis + cls.directions_axial[direction][0],
            hex_field.r_axis + cls.directions_axial[direction][1],
        )
        return neighbour_hex

    @classmethod
    def hex_obj_from_string(cls, string):
        """
        Returns a Hex object from a string representation.

        Args:
            string (str): The string representation of the Hex object, in the format "q,r".

        Returns:
            Hex: The Hex object represented by the string.

        Raises:
            ValueError: If the string is not in the correct format.
        """
        # Check if the string looks like a hex coordinate using a simple regex
        if not re.match(r"^(-?\d+),(-?\d+)$", string):
            raise ValueError("The string is not in the correct format q,r ")

        return Hex(int(string.split(",")[0]), int(string.split(",")[1]))

    def save_hex_object(self):
        self.game_database.save_hex_object(self)


class Edge:
    """
    Defines an edge between two hexes. The hexes are ordered in the Edge object to keep the direction consistent.
    Two hexes are used to define the position of the edge to quickly access the hexes from the edge.

    The spawn_hex is the hex from which the edge is spawned. The spawn hex is not necessarily the first hex in the edge.

    The spawn_direction is the direction of the edge from the spawn_hex.

    Args:

        hex_field_1 (Hex): The first hex of the edge
        hex_field_2 (Hex): The second hex of the edge
        spawn_direction (int): The direction to spwan the edge from the spawn_hex

    Methods:

        get_hex_fields: Returns the hexes of the edge in a tuple
    """

    def __init__(self, hex_field_1, hex_field_2, spawn_direction):
        """
        Initializes a Edge object with the given hexes and direction.

        Args:
            hex_field_1 (Hex): The first hex of the edge
            hex_field_2 (Hex): The second hex of the edge
            spawn_direction (int): The direction to spwan the edge from the spawn_hex
        """
        self.spawn_hex = hex_field_1
        self.spawn_direction = spawn_direction
        self.hex_field_1, self.hex_field_2 = Hex.ordered_hex_pair(
            hex_field_1, hex_field_2
        )
        self.object_id = f"{self.hex_field_1.object_id},{self.hex_field_2.object_id}"
        self.game_database = GameDatabase()

    def __hash__(self):
        """
        Returns the hash value of the Edge object.

        Returns:
            int: The hash value of the Edge object.
        """
        return hash((self.hex_field_1, self.hex_field_2))

    def __eq__(self, other):
        """
        Checks if the Edge object is equal to another edge object by comparing the hex objects and direction.

        Args:
            other (object): The edge object to compare with.
        """
        if isinstance(other, Edge):
            return (
                self.hex_field_1 == other.hex_field_1
                and self.hex_field_2 == other.hex_field_2
            )
        return False

    def __str__(self):
        """
        Returns a string representation of the Edge object.

        Returns:
            str: A string representation of the Edge object.
        """
        return f"Edge between {self.hex_field_1} and {self.hex_field_2}"

    def get_hex_fields(self):
        """
        Returns the hexes of the edge in a tuple.

        The tuple is ordered by the axis coordinates of the hexes from top to bottom and left to right.

        Returns:
            tuple: A tuple containing the two hexes of the edge.
        """
        return self.hex_field_1, self.hex_field_2

    def save_edge_object(self):
        self.game_database.save_edge_object(self)


class HexMap:
    """
    A class representing a hexagonal map.

    Attributes:
    - hex_map: a dictionary containing the hexagonal map
    """

    def __init__(self, left, right, top, bottom):
        """
        Initializes an empty hexagonal map.
        """
        self.game_database = GameDatabase()
        self.object_id_generator = ObjectIDGenerator()
        self.hex_map = {}

        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

        self.initialize_hex_map(left, right, top, bottom)

    def save_hex_map_size(self, hex_map):
        self.game_database.save_hex_map_size(hex_map)

    def initialize_hex_map(self, left, right, top, bottom):
        """
        Initializes the hexagonal map with hexagonal fields.

        Args:
        - left: the leftmost column of the map
        - right: the rightmost column of the map
        - top: the top row of the map
        - bottom: the bottom row of the map
        """
        self.save_hex_map_size(self)
        for r_axis in range(top, bottom + 1):
            r_offset = int(r_axis // 2.0)
            for q_axis in range(left - r_offset, right - r_offset + 1):
                temp_hex = Hex(q_axis, r_axis)
                self.hex_map.update({temp_hex: []})
                temp_hex.save_hex_object()

    def has_terrain(self, hex_field):
        """
        Checks if a hexagonal field has a terrain game object.

        Args:
        - hex_field: the hexagonal field to check

        Returns:
        - True if the hexagonal field has a terrain game object, False otherwise
        """
        for game_object in self.hex_map[hex_field]:
            if isinstance(game_object, Terrain):
                return True
        return False

    def hex_exists(self, hex_field):
        """
        Checks if a hexagonal field exists in the map.

        Args:
        - hex_field: the hexagonal field to check

        Returns:
        - True if the hexagonal field exists in the map, False otherwise
        """
        exists = False

        if hex_field in self.hex_map:
            exists = True

        return exists

    def append_object_to_hex(self, hex_field, game_object):
        """
        Appends a game object to a hexagonal field.

        Args:
        - hex_field: the hexagonal field to append the game object to
        - game_object: the game object to append to the hexagonal field

        Raises:
        - ValueError: if the hexagonal field already has a terrain game object and the game object being appended is also a terrain game object
        """
        if isinstance(game_object, Terrain) and self.has_terrain(hex_field):
            raise ValueError("There is already a terrain game_object in this hex_field")

        if hex_field in self.hex_map:
            self.hex_map[hex_field].append(game_object)
        else:
            self.hex_map[hex_field] = [game_object]

    def get_hex_object_list(self, hex_field):
        """
        Gets the list of game objects in a hexagonal field.

        Args:
        - hex_field: the hexagonal field to get the list of game objects from

        Returns:
        - the list of game objects in the hexagonal field
        """
        if hex_field not in self.hex_map:
            return []

        return self.hex_map[hex_field]

    def get_object_by_id(self, object_id):
        """
        Gets a game object by its ID.

        Args:
        - object_id: the ID of the game object to get

        Returns:
        - the game object with the specified ID, or None if no such game object exists
        """
        for hex_field, game_objects in self.hex_map.items():
            for game_object in game_objects:
                if game_object.object_id == object_id:
                    return game_object
        return None

    def print_content_of_all_hexes(self):
        """
        Prints the content of all hexagonal fields in the map.
        """
        for hex_field, game_objects in self.hex_map.items():
            print(hex_field)
            for game_object in game_objects:
                print(game_object)

    def load_terrain_data(self):
        """
        Loads the terrain data from JSON file.
        """
        with open("terrain.json", "r") as file:
            terrain_data = json.load(file)

        return terrain_data

    def filter_terrain_types(self, terrain_data):
        """
            Filter and return terrain types that do not have an "edgeobject" key.

        This method examines the terrain data and returns a list of terrain types
        where the associated data does not contain the "edgeobject" key.

        Args:
            terrain_data (dict): A dictionary containing terrain types as keys and their
                                 associated data as values. The data for each terrain type is
                                 another dictionary which may or may not contain the "edgeobject" key.

        Returns:
            list[str]: A list of terrain types that do not have the "edgeobject" key in their data.

        Example:
            >>> sample_data = {
            ...     "terrain": {
            ...         "mountain": {"color": "gray", "edgeobject": True},
            ...         "forest": {"color": "green"}
            ...     }
            ... }
            >>> result = obj.filter_terrain_types(sample_data)
            >>> print(result)
            ['forest']

        Notes:
            The method expects the terrain_data dictionary to have a "terrain" key, under which
            all the terrain types and their data are nested.
        """
        return [
            terrain_type
            for terrain_type, data in terrain_data["terrain"].items()
            if "edgeobject" not in data
        ]

    def fill_map_with_terrain(self, game):
        """
        Populate the map with random terrain types.

        This method loads the available terrain data and filters out terrain types
        that have the "edgeobject" key. It then populates each hex field on the map
        with a random choice of the filtered terrain types.

        Args:
            game (Game): An instance of the game object, which may contain utilities
                         or services such as an object ID generator.

        Side Effects:
            Each hex field in the hex map will be populated with a terrain object.
            The method modifies the internal state of the hex map by adding terrain objects to it.

        Notes:
            - The method relies on other methods like `load_terrain_data`, `filter_terrain_types`,
              and `append_object_to_hex` to perform its operations.
            - It's assumed that `game.object_id_generator` can be used to generate unique IDs
              for game objects.
            - The generated terrain object has a default name "Generated_Terrain".

        Example:
            >>> game_instance = Game()
            >>> map_obj = HexMap()  # Assuming the class is named MapClass
            >>> map_obj.fill_map_with_terrain(game_instance)
        """
        terrain_data = self.load_terrain_data()
        terrain_types = self.filter_terrain_types(terrain_data)

        for hex_field in self.hex_map.keys():
            choice = random.choice(terrain_types)
            temp_terrain = Terrain(
                game.object_id_generator, "Generated_Terrain", choice
            )
            self.append_object_to_hex(
                hex_field,
                temp_terrain,
            )
            temp_terrain.save_terrain_object()

        # save all hex objects to database
        for hex_field in self.hex_map.keys():
            self.game_database.save_hex_objects(self, hex_field)


class EdgeMap:
    """
    A class representing a map of edges between hexagonal fields.

    Attributes:
        edge_map: a dictionary containing the map of edges

    Methods:
        initialize_edge_map: initializes the edge map with edges between all hexagonal fields
        append_object_to_edge: appends a game object to an edge
        get_edge_object_list: gets the list of game objects in an edge
        has_terrain: checks if an edge has a terrain game object
        print_content_of_all_edges: prints the content of all edges in the map

    """

    def __init__(self):
        """
        Initializes an empty edge map.
        """
        self.game_database = GameDatabase()
        self.object_id_generator = ObjectIDGenerator()
        self.edge_map = {}

    def initialize_edge_map(self, hex_map):
        """
        Initializes the edge map with edges between all hexagonal fields. The hex_map has to be initialized before calling this method.

        Args:
            hex_map: the hexagonal map to initialize the edge map for
        """
        for hex_field in hex_map.keys():
            for direction in range(6):
                neighbour_hex = Hex.get_neighbour_hex(hex_field, direction)
                temp_edge = Edge(hex_field, neighbour_hex, direction)
                if temp_edge not in self.edge_map.keys():
                    self.edge_map.update({temp_edge: []})
                    temp_edge.save_edge_object()

    def append_object_to_edge(self, edge, game_object):
        """
        Appends a game object to an edge.

        Args:
            edge: the edge to append the game object to
            game_object: the game object to append to the edge

        Raises:
            ValueError: if the edge already has a terrain game object and the game object being appended is also a terrain game object
        """
        if isinstance(game_object, Terrain) and self.has_terrain(edge):
            raise ValueError("There is already a terrain game_object in this hex_field")

        if edge in self.edge_map:
            self.edge_map[edge].append(game_object)
        else:
            self.edge_map[edge] = [game_object]
        self.game_database.save_edge_objects(self, edge)

    def append_chain_of_objects_to_edges(
        self, source_hex_field, direction_list, game_object
    ):
        """
        Append a game object to a series of edges defined by a chain of directions.

        Starting from a source hex field, this method moves in the specified directions
        sequentially and appends the game object to the edge at each step. The source hex
        field is then updated to its neighbor in the current direction, and the process
        continues until all directions in the list are processed.

        Args:
            source_hex_field (Hex): The starting hex field where the chain begins.
            direction_list (list[int]): List of directions (0-5) defining the chain.
            game_object: The game object to be appended to the edges.

        Notes:
            - The method uses `Hex.get_edge_by_direction` to get the edge in a specific
              direction from a hex field.
            - It also uses `Hex.get_neighbour_hex` to update the source hex field after
              each step.

        Example:
            >>> hex_instance = HexFieldClass()
            >>> directions = [0, 2, 4]
            >>> hex_instance.append_chain_of_object_to_edges(start_hex, directions, game_obj)
        """
        sub_object = game_object
        name = game_object.name
        structure_type = game_object.terrain_type
        counter = 1

        for direction in direction_list:
            edge = Hex.get_edge_by_direction(source_hex_field, direction)
            source_hex_field = Hex.get_neighbour_hex(source_hex_field, direction)
            # create a new object with the same name and structure type, just different id
            # this is needed to save the object to the database
            sub_object = type(game_object)(
                self.object_id_generator, name + str(counter), structure_type
            )
            self.append_object_to_edge(edge, sub_object)
            counter += 1
        del sub_object

    def get_edge_object_list(self, edge):
        """
        Gets the list of game objects in an edge.

        Args:
            edge (tuple): A tuple representing the edge to get the list of game objects from.

        Returns:
            list: A list of game objects in the edge.
        """

        return self.edge_map[edge]

    def has_terrain(self, edge):
        """
        Determines if an edge has any Terrain objects.

        Args:
            edge (tuple): A tuple representing the edge to check.

        Returns:
            bool: True if the edge has at least one Terrain object, False otherwise.
        """
        for game_object in self.edge_map[edge]:
            if isinstance(game_object, Terrain):
                return True
        return False

    def print_content_of_all_edges(self):
        """
        Prints the content of all edges in the map.
        """

        for edge, game_objects in self.edge_map.items():
            print(edge)
            for game_object in game_objects:
                print(game_object)
        print(f"There are {len(self.edge_map)} edges in the edge map")
