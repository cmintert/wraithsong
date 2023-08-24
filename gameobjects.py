import json
import uuid
import random

class ObjectIDGenerator:

    def __init__(self):
        self.used_counters = set()

    def get_random_counter(self):

        counter = random.randint(0, 999)
        formatted_counter = str(counter).zfill(3)
        return formatted_counter

    def get_unique_id(self, name, object_type):
        while True:
            random_counter = self.get_random_counter()
            unique_id = f"{object_type.upper()[0:3]}_{name}_{random_counter}"
            if unique_id not in self.used_counters:
                self.used_counters.add(unique_id)
                print(self.used_counters)
                return unique_id

class GameObject:

    def __init__(self, id_generator, name="Not specified", object_type=None):
        self.object_id = id_generator.get_unique_id(name, object_type)
        self.internal_id = str(uuid.uuid4())
        self.name = name
        self.object_type = object_type


    def __str__(self):
        return f"ID: {self.internal_id}, Name: {self.name}, Type: {self.object_type}"

    def get_id(self):
        return self.internal_id

    def get_position(self,hexmap):

        for hex_field in hexmap.map.keys():
            if self in hexmap.map[hex_field]:
                return hex_field
        return None

    def  delete(self,id_generator):

        self.used_counters.remove(self.object_id)
        del self


class Terrain(GameObject):

    def __init__(self,id_generator, name, terrain_type, elevation=0):
        super().__init__(id_generator, name, object_type="terrain")

        self.terrain_type = terrain_type
        self.elevation = elevation

        with open("terrain.json", "r") as file:
            terrain_data = json.load(file)

        attributes = terrain_data["terrain"].get(terrain_type, {})

        for key, value in attributes.items():
            setattr(self, key, value)

    def __str__(self):
        attributes = [f"{key}: {getattr(self, key)}" for key in vars(self)
                      if key not in ["internal_id", "name", "object_type"]]
        return super().__str__() + ", " + ", ".join(attributes)


class Army(GameObject):

    def __init__(self, id_generator, name, owner):
        super().__init__(id_generator, name, object_type="army")

        self.owner = owner
        self.units = []

    def __str__(self):
        attributes = [f"{key}: {getattr(self, key)}" for key in vars(self)
                      if key not in ["internal_id", "name", "object_type"]]
        return super().__str__() + ", " + ", ".join(attributes)

    def add_unit_to_army(self, unit):
        self.units.append(unit)

    def remove_unit_from_army(self, unit):
        self.units.remove(unit)

    def move_army(self, hexmap, target_hex):
        current_hex = self.get_position(hexmap)
        hexmap.map[current_hex].remove(self)
        hexmap.map[target_hex].append(self)


class   Unit(GameObject):

    def __init__(self, id_generator, name, owner):
        super().__init__(id_generator, name, object_type="unit")

    pass
