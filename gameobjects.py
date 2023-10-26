import json
import random
import uuid

from database import GameDatabase


class ObjectIDGenerator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ObjectIDGenerator, cls).__new__(cls)
            cls._instance.used_counters = set()
        return cls._instance

    @staticmethod
    def get_random_counter():
        """Generates and returns a random 4-digit counter as a string.

        Returns:
            str: A 4-digit random counter.
        """
        counter = random.randint(0, 9999)
        formatted_counter = str(counter).zfill(4)
        return formatted_counter

    def get_unique_id(self, name, object_type):
        """Generates a unique ID based on the provided name and object type.

        The generated ID is in the format: `<First 3 letters of object_type>_<name>_<random counter>`.
        This method ensures the uniqueness of the ID within the context of the current instance of
        the `ObjectIDGenerator` class.

        Args:
            name (str): The name to be included in the ID.
            object_type (str): The type of the object for which the ID is being generated.

        Returns:
            str: A unique ID.
        """

        while True:
            random_counter = self.get_random_counter()
            unique_id = f"{object_type.upper()[0:3]}_{name}_{random_counter}"
            if unique_id not in self.used_counters:
                self.used_counters.add(unique_id)
                return unique_id


class GameObject:
    """
    Represents a generic game object with unique identifiers and attributes.

    Each game object has a unique `object_id` generated using the provided `id_generator`
    as well as a universally unique identifier (`internal_id`).

    Attributes:
        object_id (str): A unique identifier generated using the id_generator.
        internal_id (str): A universally unique identifier (UUID) for the object.
        name (str): A human-readable name for the game object.
        object_type (str): The type or category of the game object.

    Args:
        id_generator (ObjectIDGenerator): An instance used to generate unique object IDs.
        name (str, optional): The name of the game object. Defaults to "Not specified".
        object_type (str, optional): The type or category of the game object. Defaults to None.
    """

    def __init__(self, id_generator, name="Not specified", object_type=None):
        self.object_id = id_generator.get_unique_id(name, object_type)
        self.internal_id = str(uuid.uuid4())
        self.name = name
        self.object_type = object_type
        self.game_database = GameDatabase()

    def __str__(self):
        """
        Returns a string representation of the game object.

        Returns:
            str: A string with the format "ID: {internal_id}, Name: {name}, Type: {object_type}".
        """
        return f"ID: {self.internal_id}, Name: {self.name}, Type: {self.object_type}"

    def get_id(self):
        """
        Retrieves the internal UUID of the game object.

        Returns:
            str: The internal UUID of the game object.
        """
        return self.internal_id

    def get_position(self, hexmap):
        """
        Retrieves the position of the game object in the provided hex map.

        Args:
            hexmap (HexMap): The hex map in which to search for the game object.

        Returns:
            HexField or None: The hex field where the game object is located, or None if not found.
        """

        for hex_field in hexmap.hex_map.keys():
            if self in hexmap.hex_map[hex_field]:
                return hex_field
        return None

    def delete(self, id_generator):
        """
        Deletes the game object and removes its unique ID from the used counters of the id_generator.

        Args:
            id_generator (ObjectIDGenerator): The generator that was used to create the object's unique ID.
        """
        id_generator.used_counters.remove(self.object_id)
        del self


class Structure(GameObject):
    def __init__(self, id_generator, name, structure_type):
        super().__init__(id_generator, name, object_type="structure")

        self.terrain_type = structure_type

        with open("structure.json", "r") as file:
            structure_data = json.load(file)

        # get all the attributes listed under "terrain" in the json file

        attributes = structure_data["structure"].get(structure_type, {})

        for key, value in attributes.items():
            setattr(self, key, value)

    def __str__(self):
        """
        Returns a detailed string representation of the structure object.

        The returned string includes the object's ID, name, type, and any dynamically loaded attributes.

        Returns:
            str: A string representation of the terrain object.
        """
        attributes = [
            f"{key}: {getattr(self, key)}"
            for key in vars(self)
            if key not in ["internal_id", "name", "object_type"]
        ]
        return super().__str__() + ", " + ", ".join(attributes)


class Terrain(GameObject):
    """
    Represents a terrain type in the game, inheriting properties from the GameObject class.

    The Terrain class describes a specific type of terrain, such as a forest or mountain,
    with additional attributes loaded dynamically from a "terrain.json" file based on the
    provided `terrain_type`.

    Attributes:
        terrain_type (str): The specific type of the terrain (e.g., "forest", "mountain").
        elevation (int): The elevation level of the terrain.
        [dynamic attributes]: Attributes loaded dynamically from the "terrain.json" file
                              based on the provided `terrain_type`.

    Args:
        id_generator (ObjectIDGenerator): An instance used to generate unique object IDs.
        name (str): The name of the terrain.
        terrain_type (str): The specific type of terrain.
        elevation (int, optional): The elevation level of the terrain. Defaults to 0.
    """

    def __init__(self, id_generator, name, terrain_type, elevation=0):
        super().__init__(id_generator, name, object_type="terrain")

        self.terrain_type = terrain_type
        self.elevation = elevation

        with open("terrain.json", "r") as file:
            terrain_data = json.load(file)

        # get all the attributes listed under "terrain" in the json file
        attributes = terrain_data["terrain"].get(terrain_type, {})

        for key, value in attributes.items():
            setattr(self, key, value)

    def __str__(self):
        """
        Returns a detailed string representation of the terrain object.

        The returned string includes the object's ID, name, type, and any dynamically loaded attributes.

        Returns:
            str: A string representation of the terrain object.
        """
        attributes = [
            f"{key}: {getattr(self, key)}"
            for key in vars(self)
            if key not in ["internal_id", "name", "object_type"]
        ]
        return super().__str__() + ", " + ", ".join(attributes)

    def save_terrain_object(self):
        self.game_database.save_terrain_object(self)

    @classmethod
    def load(cls, object_id):
        game_database = GameDatabase()  # Instantiating the singleton GameDatabase
        return game_database.load_terrain_object(object_id, cls)


class Army(GameObject):
    def __init__(self, id_generator, name, owner):
        super().__init__(id_generator, name, object_type="army")

        self.owner = owner
        self.units = []

    def __str__(self):
        attributes = [
            f"{key}: {getattr(self, key)}"
            for key in vars(self)
            if key not in ["internal_id", "name", "object_type"]
        ]
        return super().__str__() + ", " + ", ".join(attributes)

    def add_unit_to_army(self, unit):
        self.units.append(unit)

    def remove_unit_from_army(self, unit):
        self.units.remove(unit)

    def move_army(self, hexmap, target_hex):
        current_hex = self.get_position(hexmap)
        hexmap.hex_map[current_hex].remove(self)
        hexmap.hex_map[target_hex].append(self)


class Unit(GameObject):
    def __init__(self, id_generator, name, owner):
        super().__init__(id_generator, name, object_type="unit")
