import json
import math
import random
import re

from gameobjects import Terrain


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
    def get_neighbour_hex(cls, hex_field, direction):
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


class HexMap:
    """
    A class representing a hexagonal map.

    Attributes:
    - hex_map: a dictionary containing the hexagonal map
    """

    def __init__(self):
        """
        Initializes an empty hexagonal map.
        """
        self.hex_map = {}

    def initialize_hex_map(self, left, right, top, bottom):
        """
        Initializes the hexagonal map with hexagonal fields.

        Args:
        - left: the leftmost column of the map
        - right: the rightmost column of the map
        - top: the top row of the map
        - bottom: the bottom row of the map
        """
        for r_axis in range(top, bottom + 1):
            r_offset = int(r_axis // 2.0)
            for q_axis in range(left - r_offset, right - r_offset + 1):
                self.hex_map.update({Hex(q_axis, r_axis): []})

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
        else:
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
            self.append_object_to_hex(
                hex_field,
                Terrain(game.object_id_generator, "Generated_Terrain", choice),
            )


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
                if (
                    Edge(hex_field, neighbour_hex, direction)
                    not in self.edge_map.keys()
                ):
                    self.edge_map.update(
                        {Edge(hex_field, neighbour_hex, direction): []}
                    )

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


class MoveCalculator:

    """
    Calculates movement costs and conditions for hex field neighbors.

    Attributes:
        hex_map: A HexMap instance representing the game map.
        edge_map: An EdgeMap instance representing the game map edges.
    """

    def __init__(self, hex_map, edge_map):
        """
        Initializes a MoveCalculator instance.

        Args:
            hex_map: A HexMap instance representing the game map.
            edge_map: An EdgeMap instance representing the game map edges.
        """
        self.hex_map = hex_map
        self.edge_map = edge_map

    def get_neighbours(self, hex_field):
        """
        Get a list of valid neighboring hexes for the given hex field.

        The method identifies and returns all neighboring hexes in valid directions
        from the provided hex field. A direction is considered valid if a neighboring
        hex exists in that direction.

        Args:
            hex_field (Hex): The hex field for which we want to find the neighbors.

        Returns:
            list[Hex]: A list of Hex objects representing the neighboring hexes.

        Example:
            >>> neighbours = obj.get_neighbours(some_hex_field)
            >>> print(neighbours)
            [<Hex object at 0x...>, <Hex object at 0x...>, ...]

        Notes:
            The method relies on other methods like `hex_map.hex_exists` and
            `Hex.get_neighbour_hex` to determine the neighboring hexes.
        """

        neighbours = []

        for direction in range(6):
            neighbour_hex = Hex.get_neighbour_hex(hex_field, direction)
            if self.hex_map.hex_exists(neighbour_hex):
                neighbours.append(neighbour_hex)

        return neighbours

    def get_neighbour_conditions(self, hex_field):
        """
        Get a list of valid conditions for neighboring hexes of the given hex field.

        The method calculates the movement cost and conditions for each valid direction
        from the given hex field. A valid direction is one where a neighboring hex exists.

        Args:
            hex_field (Hex): The hex field for which we want to find the neighbor conditions.

        Returns:
            list[tuple]: A list of tuples, where each tuple contains:
                - hex_field (Hex): The original hex field.
                - direction (int): The direction of the neighboring hex (0-5).
                - move_target (Hex): The neighboring hex in the specified direction.
                - movement_cost (int): The cost of moving to the neighboring hex.
                - movement_conditions (list): List of conditions needed to move to the neighboring hex.

        Example:
            >>> conditions = obj.get_neighbour_conditions(some_hex_field)
            >>> print(conditions)
            [(<Hex object>, 0, <Hex object>, 5, ['condition1', 'condition2']), ...]

        Notes:
            The method relies on other methods like `hex_map.hex_exists`, `get_movement_cost`,
            `get_movement_conditions`, and `Hex.get_neighbour_hex` to perform its operations.
        """

        condition_list = []

        valid_directions = []

        for direction in range(6):
            neighbour_hex = Hex.get_neighbour_hex(hex_field, direction)
            if self.hex_map.hex_exists(neighbour_hex):
                valid_directions.append(direction)

        for direction in valid_directions:
            movement_cost = self.get_movement_cost(hex_field, direction)
            movement_conditions = self.get_movement_conditions(hex_field, direction)
            move_target = Hex.get_neighbour_hex(hex_field, direction)
            condition_list.append(
                (hex_field, direction, move_target, movement_cost, movement_conditions)
            )

        return condition_list

    def get_movement_cost(self, hex_field, direction):
        """
        Calculate the movement cost for moving in a specified direction from a given hex field.

        This method determines the movement cost based on the `Terrain` objects present
        in the specified direction from the given hex field. It accumulates the movement costs
        of the terrain objects in both the target hex and any terrain objects on the edge
        between the current and target hex.

        Args:
            hex_field (Hex): The starting hex field from which we want to determine
                             the movement cost.
            direction (int): The direction (0-5) in which we want to move.

        Returns:
            int: The total movement cost for moving in the specified direction
                 from the given hex field.

        Notes:
            - The method relies on the `neighbouring_hex_and_edge_objects` method
              to get the neighboring hex and edge objects.
            - The movement costs of all `Terrain` objects in the hex and on the edge
              are accumulated to calculate the total cost.

        Example:
            >>> hex_instance = Hex()
            >>> cost = hex_instance.get_movement_cost(some_hex_field, 2)
            >>> print(cost)
            7
        """

        hex_objects, edge_objects = self.neighbouring_hex_and_edge_objects(
            hex_field, direction
        )
        summed_movement_cost = 0

        for game_object in hex_objects + edge_objects:
            if isinstance(game_object, Terrain):
                summed_movement_cost += game_object.movement_cost

        return summed_movement_cost

    def get_movement_conditions(self, hex_field, direction):
        """
        Retrieve movement conditions for a given direction from a specified hex field.

        This method extracts the movement conditions from `Terrain` objects present
        in the specified direction from the given hex field. It gathers conditions
        from the terrain objects in both the target hex and any terrain objects on the edge
        between the current and target hex.

        Args:
            hex_field (Hex): The starting hex field from which we want to extract
                             the movement conditions.
            direction (int): The direction (0-5) in which we want to check the conditions.

        Returns:
            list[str]: A list of movement conditions derived from the `Terrain` objects
                       in the specified direction from the hex field.

        Notes:
            - The method relies on the `neighbouring_hex_and_edge_objects` method
              to get the neighboring hex and edge objects.
            - Only `Terrain` objects that have a "terrain_condition" attribute will
              be considered.

        Example:
            >>> hex_instance = HexFieldClass()  # Assuming the class is named HexFieldClass
            >>> conditions = hex_instance.get_movement_conditions(some_hex_field, 2)
            >>> print(conditions)
            ['condition1', 'condition2', ...]
        """

        hex_objects, edge_objects = self.neighbouring_hex_and_edge_objects(
            hex_field, direction
        )

        conditions = [
            game_object.terrain_condition
            for game_object in hex_objects + edge_objects
            if isinstance(game_object, Terrain)
            and hasattr(game_object, "terrain_condition")
        ]

        return conditions

    def neighbouring_hex_and_edge_objects(self, hex_field, direction):
        """
        Retrieve objects from the neighboring hex and its edge based on a given direction.

        Given a hex field and a direction, this method returns the objects present
        in the neighboring hex and the objects present on the edge between the current
        hex and its neighbor.

        Args:
            hex_field (Hex): The hex field from which the neighboring objects are to be retrieved.
            direction (int): The direction (0-5) in which we want to retrieve the objects.

        Returns:
            tuple(list, list): A tuple containing two lists:
                - The first list contains objects present in the neighboring hex.
                - The second list contains objects present on the edge between the current
                  hex and its neighbor.

        Notes:
            - The method relies on other methods like `hex_map.hex_exists`, `hex_map.get_hex_object_list`,
              and `edge_map.get_edge_object_list` to perform its operations.
            - If the hex doesn't exist in the map, two empty lists are returned.

        Example:
            >>> hex_instance = Hex()  # Assuming the class is named HexFieldClass
            >>> hex_objects, edge_objects = hex_instance.neighbouring_hex_and_edge_objects(some_hex_field, 2)
            >>> print(hex_objects, edge_objects)
            [<GameObject1>, <GameObject2>, ...], [<EdgeObject1>, <EdgeObject2>, ...]
        """

        # Return empty lists if the hex doesn't exist in the map.
        if not self.hex_map.hex_exists(hex_field):
            return [], []

        neighbour_hex = Hex.get_neighbour_hex(hex_field, direction)
        hex_objects = self.hex_map.get_hex_object_list(neighbour_hex)
        edge_objects = self.edge_map.get_edge_object_list(
            hex_field.get_edge_by_direction(direction)
        )

        return hex_objects, edge_objects

    def collect_neighbours_for_all(self):
        """
        Collect the neighbouring nodes for all nodes in the system.

        This method iterates through all nodes in the system and determines their
        respective neighbours. The results are returned as a dictionary where each key
        is a node and its value is a list of its neighbouring nodes.

        Returns:
            dict: A dictionary where each key is a node and the corresponding value
                  is a list of its neighbouring nodes.

        Notes:
            - The method relies on other methods like `collect_all_nodes` and `get_neighbours`
              to perform its operations.
            - If a node doesn't have any neighbours, it will still be included in the returned
              dictionary with an empty list as its value.

        Example:
            >>> neighbours = MoveCalculator_instance.collect_neighbours_for_all()
            >>> print(neighbours)
            {<Node1>: [<Neighbour1>, <Neighbour2>, ...], <Node2>: [<Neighbour3>, ...], ...}
        """

        all_nodes = self.collect_all_nodes()
        neighbour_list = {}

        for node in all_nodes:
            neighbours = self.get_neighbours(node)
            neighbour_list.update({node: neighbours})

        return neighbour_list

    def collect_all_nodes(self):
        """
        Collect all nodes (hex fields) present in the hex map.

        This method retrieves all the nodes, or hex fields, from the system's hex map
        and returns them in a list.

        Returns:
            list: A list containing all nodes (hex fields) present in the system's hex map.

        Notes:
            - The method directly accesses the `hex_map` attribute of the system,
              assuming it's a dictionary-like object with a `keys` method.
            - Each hex field is treated as a node in the context of this method.

        Example:
            >>> all_nodes = MoveCalculator_instance.collect_all_nodes()
            >>> print(all_nodes)
            [<HexField1>, <HexField2>, ...]
        """

        all_nodes = []

        for hex_field in self.hex_map.hex_map.keys():
            all_nodes.append(hex_field)

        return all_nodes

    def collect_move_paths(self):
        """
        Collect all possible movement paths from each node (hex field) in the system.

        This method retrieves all nodes (hex fields) from the system and, for each node,
        determines the possible movement paths based on neighbouring conditions. All
        these paths are then aggregated and returned as a list.

        Returns:
            list: A list containing all possible movement paths from each node in the system.

        Notes:
            - The method relies on other methods like `collect_all_nodes` and `get_neighbour_conditions`
              to perform its operations.
            - A movement path is determined by the conditions required to move from a node to its
              neighbouring nodes.
            - The method prints out the number of nodes being processed for debugging or informational purposes.

        Example:
            >>> system_instance = MoveCalculator()
            >>> move_paths = system_instance.collect_move_paths()
            >>> print(move_paths)
            [(<Node1>, <Direction1>, <TargetNode1>, ...), (<Node2>, <Direction2>, <TargetNode2>, ...), ...]
        """

        all_move_paths = []

        all_nodes = self.collect_all_nodes()

        for node in all_nodes:
            paths = self.get_neighbour_conditions(node)

            for path in paths:
                all_move_paths.append(path)

        return all_move_paths


class Graph:
    def __init__(self, move_calculator):
        """
        Initialize the graph object with move paths, neighbours, and nodes.

        This constructor initializes the graph by using a provided move calculator
        to gather move paths, neighbours for all nodes, and all nodes present in the system.

        Args:
            move_calculator: An object that provides methods to collect move paths,
                             neighbours, and nodes for the graph. It should have
                             the following methods:
                             - collect_move_paths()
                             - collect_neighbours_for_all()
                             - collect_all_nodes()

        Attributes:
            edges (list): A list of move paths collected from the move calculator.
            neighbours (dict): A dictionary with nodes as keys and their neighbours
                               as values, collected from the move calculator.
            nodes (list): A list of all nodes collected from the move calculator.

        Notes:
            - The initialization process also prints "Initializing graph" for
              debugging or informational purposes.

        Example:
            >>> move_calculator_instance = MoveCalculatorClass()  # Assuming MoveCalculatorClass is the name of the move calculator class
            >>> graph_instance = GraphClass(move_calculator_instance)  # Assuming the class is named GraphClass
            >>> print(graph_instance.nodes)
            [<Node1>, <Node2>, ...]
        """
        self.edges = move_calculator.collect_move_paths()
        self.neighbours = move_calculator.collect_neighbours_for_all()
        self.nodes = move_calculator.collect_all_nodes()

    def get_movement_cost(self, node1, node2):
        """
        Retrieve the movement cost between two nodes.

        This method searches through the graph's edges to find the movement cost
        between the specified nodes, `node1` and `node2`.

        Args:
            node1: The starting node.
            node2: The ending node.

        Returns:
            int or float: The movement cost between `node1` and `node2`. If no edge
                          is found between the nodes, the method returns `None`.

        Notes:
            - The method assumes that edges are represented as a list of tuples where:
                * The first item is the starting node.
                * The third item is the ending node.
                * The fourth item is the movement cost.
            - Only the first matching edge found is considered.

        Example:
            >>> graph_instance = Graph(move_calculator_instance)
            >>> cost = graph_instance.get_movement_cost(nodeA, nodeB)
            >>> print(cost)
            5
        """

        for item in self.edges:
            if item[0] == node1 and item[2] == node2:
                return item[3]

    def djikstra(self, start_hex, move_cost_limit=math.inf):
        """
        Implement the Dijkstra's shortest path algorithm starting from a given hex field.

        This method determines the shortest distance from a given starting hex field (`start_hex`)
        to all other hex fields in the system using Dijkstra's algorithm.

        Args:
            start_hex (Hex): The starting hex field from which shortest distances to all
                             other hex fields are to be calculated.
            move_cost_limit (int): The maximum movement cost allowed for a path to be considered.

        Returns:
            dict: A dictionary containing hex fields as keys and their shortest distances
                  from the `start_hex` as values.

        Notes:
            - The method relies on the `update_neighbour_distances` method to update the
              distances of neighboring hex fields of the currently processed node.
            - The `neighbours` attribute, expected to be a dictionary with hex fields
              as keys and their neighbors as values, is used to determine the hex field
              neighbors.
            - The method assumes that if there's no path to a hex field, its distance
              remains set to infinity.

        Example:
            >>> system_instance = Graph(move_calculator_instance)
            >>> distances = system_instance.djikstra(some_start_hex)
            >>> print(distances)
            {<HexField1>: 5, <HexField2>: 10, ...}
        """

        distances = {}

        # Set all distances to infinity and start hex_field to 0

        distances = {node: math.inf for node in self.neighbours.keys()}
        distances[start_hex] = 0

        # Add all hex_fields to the unvisited set

        unvisited = set(self.neighbours.keys())

        # Iterate unvisited set until it is empty
        while unvisited:
            # Select the node with the smallest distance
            current_node = min(unvisited, key=lambda node: distances[node])
            if distances[current_node] > move_cost_limit:
                break
            distance = self.update_neighbour_distances(current_node, distances)
            unvisited.remove(current_node)

        return distance

    def update_neighbour_distances(self, current_node, distances):
        """
        Update the distances of neighboring nodes based on the current node's distance.

        Given a current node and its known shortest distances to other nodes, this method
        updates the distances of its neighboring nodes by considering the movement cost
        from the current node to each neighbor.

        Args:
            current_node: The node currently being processed.
            distances (dict): A dictionary containing nodes as keys and their current shortest
                              distances as values.

        Returns:
            dict: The updated distances dictionary with potentially shorter distances for
                  the neighboring nodes of the current node.

        Notes:
            - The method utilizes the `get_movement_cost` function to determine the movement
              cost between the current node and each of its neighbors.
            - Only neighbors with a shorter new distance (compared to their current shortest
              distance) are updated in the distances dictionary.

        Example:
            >>> graph_instance = Graph(move_calculator_instance)
            >>> distances = {nodeA: 0, nodeB: 5, nodeC: 10}
            >>> updated_distances = graph_instance.update_neighbour_distances(nodeA, distances)
            >>> print(updated_distances)
            {nodeA: 0, nodeB: 3, nodeC: 8}
        """

        for neighbour in self.neighbours[current_node]:
            if neighbour in distances:
                new_distance = distances[current_node] + self.get_movement_cost(
                    current_node, neighbour
                )

                if new_distance < distances[neighbour]:
                    distances[neighbour] = new_distance

        return distances
