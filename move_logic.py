from typing import List, Tuple, Dict, Any

from gameobjects import Terrain, GameObject
from map_logic import Hex, HexMap, EdgeMap


class MoveCalculator:

    """
    Calculates movement costs and conditions for hex field neighbors.

    Attributes:
        hex_map: A HexMap instance representing the game map.
        edge_map: An EdgeMap instance representing the game map edges.
    """

    def __init__(self, hex_map: HexMap, edge_map: EdgeMap) -> None:
        """
        Initializes a MoveCalculator instance.

        Args:
            hex_map: A HexMap instance representing the game map.
            edge_map: An EdgeMap instance representing the game map edges.
        """
        self.hex_map = hex_map
        self.edge_map = edge_map

    def get_neighbours(self, hex_field: Hex) -> List[Hex]:
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

    def is_valid_direction(self, hex_field: Hex, direction: int) -> bool:
        """
        Checks if a given direction is valid for the specified hex field.

        Args:
            hex_field (Hex): The hex field to check.
            direction (int): The direction to validate.

        Returns:
            bool: True if the direction is valid, otherwise False.
        """
        neighbour_hex = Hex.get_neighbour_hex(hex_field, direction)
        return self.hex_map.hex_exists(neighbour_hex)

    def get_neighbour_conditions(
        self, hex_field: Hex
    ) -> List[Tuple[Hex, int, Hex, int, List[str]]]:
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

        condition_list: List[Tuple[Hex, int, Hex, int, List[str]]] = []

        for direction in range(6):
            if self.is_valid_direction(hex_field, direction):
                movement_cost = self.get_movement_cost(hex_field, direction)
                movement_conditions = self.get_movement_conditions(hex_field, direction)
                neighbour_hex = Hex.get_neighbour_hex(hex_field, direction)
                condition_list.append(
                    (
                        hex_field,
                        direction,
                        neighbour_hex,
                        movement_cost,
                        movement_conditions,
                    )
                )
        return condition_list

    @classmethod
    def check_for_condition(cls, game_object: GameObject, searched_condition: str) -> bool:

        """Check if a specified condition is met by the game object's structure or terrain.

        This method checks whether a specified condition is present in either the
        `structure_condition` or `terrain_condition` attribute of the game object.
        It's a class method, so it's bound to the class rather than a specific instance.

        Args:
            game_object (GameObject): The game object to check.
            searched_condition (str): The condition to check for.

        Returns:
            bool: True if the condition is met, False otherwise.

        """

        if searched_condition in getattr(game_object, "structure_condition", []):
            return True

        if searched_condition in getattr(game_object, "terrain_condition", []):
            return True

        return False

    def get_movement_cost(self, hex_field: Hex, direction: int) -> int:

        """Calculate the movement cost to traverse a hex field in a specified direction.

        This method sums up the movement costs associated with game objects found in
        the specified hex field and direction. It takes into account whether a bridge
        exists, which would significantly lower the movement cost. The minimum movement
        cost is 1, regardless of other calculations.

        Args:
            hex_field (Hex): The hex field to evaluate.
            direction (int): The direction of movement, represented as an integer from 0 to 5
                             starting with 0 northeast on a point up hex.

        Returns:
            int: The total movement cost to traverse the hex field in the specified direction.

        """

        hex_objects, edge_objects = self.neighbouring_hex_and_edge_objects(
            hex_field, direction
        )
        summed_movement_cost = 0

        # check for bridge
        for game_object in hex_objects + edge_objects:
            bridge = self.check_for_condition(game_object, "bridge")
            if bridge:
                print(game_object, bridge)
                break

        for game_object in hex_objects + edge_objects:

            temp_move_cost = getattr(game_object, "movement_cost", 10000)

            # if object is bridgeable and there is a bridge, movement cost is 0

            if self.check_for_condition(game_object, "bridgeable"):
                temp_move_cost = 0

            summed_movement_cost += temp_move_cost

        # movement can not be lower than 1

        if summed_movement_cost < 1:
            summed_movement_cost = 1

        return summed_movement_cost




    def get_movement_conditions(self, hex_field: Hex, direction: int) -> List[str]:
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

    def neighbouring_hex_and_edge_objects(
        self, hex_field: Hex, direction: int
    ) -> Tuple[List, List]:
        """
        Retrieve objects from the neighboring hex and its edge based on a given direction.

        Given a hex field and a direction, this method returns the objects present in the
        neighboring hex and the objects present on the edge between the current hex and its
        neighbor.

        Args:
            hex_field (Hex): The hex field from which the neighboring objects are to be
                retrieved.
            direction (int): The direction (0-5) in which we want to retrieve the objects.

        Returns:
            tuple(list, list): A tuple containing two lists:
                - The first list contains objects present in the neighboring hex.
                - The second list contains objects present on the edge between the current
                  hex and its neighbor.

        Notes:
            - The method relies on other methods like `hex_map.hex_exists`,
              `hex_map.get_hex_object_list`, and `edge_map.get_edge_object_list` to perform
              its operations.
            - If the hex doesn't exist in the map, two empty lists are returned.

        Example:
            >>> hex_instance = Hex()  # Assuming the class is named HexFieldClass
            >>> hex_objects, edge_objects = hex_instance.neighbouring_hex_and_edge_objects(
            ...     some_hex_field, 2)
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

    def collect_neighbours_for_all(self) -> Dict[Hex, List[Hex]]:
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

    def collect_all_nodes(self) -> List[Hex]:
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

    def collect_move_paths(self) -> List[Tuple[Hex, int, Hex, int, List[str]]]:
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
    def __init__(self, move_calculator: MoveCalculator) -> None:
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

        Notes:
            - The initialization process also prints "Initializing graph" for
              debugging or informational purposes.

        Example:
            >>> move_calculator_instance = MoveCalculatorClass()  # Assuming MoveCalculatorClass is the name of the move calculator class
            >>> graph_instance = GraphClass(move_calculator_instance)  # Assuming the class is named GraphClass
            >>> print(graph_instance.nodes)
            [<Node1>, <Node2>, ...]
        """
        self.edges: List[
            Tuple[Hex, int, Hex, int, List[str]]
        ] = move_calculator.collect_move_paths()

        self.neighbours: Dict[
            Any, List[Any]
        ] = move_calculator.collect_neighbours_for_all()

        self.nodes: List[Any] = move_calculator.collect_all_nodes()

    def get_movement_cost(self, node1: Hex, node2: Hex) -> int:
        """
        Retrieve the movement cost between two nodes.

        This method searches through the graph's edges to find the movement cost
        between the specified nodes, `node1` and `node2`.

        Args:
            node1: The starting node.
            node2: The ending node.

        Returns:
            int: The movement cost between `node1` and `node2`. If no edge
                          is found between the nodes, the method raises a ValueError.

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
                return int(item[3])

        raise ValueError("No movement cost found between the two nodes")

    def djikstra(self, start_hex: Hex, move_cost_limit: int = 10000):
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
        # Set all distances to infinity and start hex_field to 0

        distances: Dict[Hex, int] = {node: 10000 for node in self.neighbours.keys()}
        distances[start_hex] = 0

        # Add all hex_fields to the unvisited set

        unvisited = set(self.neighbours.keys())

        # Iterate unvisited set until it is empty
        while unvisited:
            # Select the node with the smallest distance
            current_node = min(unvisited, key=lambda node: distances[node])
            if distances[current_node] > move_cost_limit:
                break
            distances = self.update_neighbour_distances(current_node, distances)
            unvisited.remove(current_node)

        return distances

    def update_neighbour_distances(
        self, current_node: Hex, distances: Dict[Hex, int]
    ) -> Dict[Hex, int]:
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
