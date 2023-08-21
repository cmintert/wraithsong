import json
import uuid

class GameObject:

    def __init__(self, name="Not specified", object_type=None):
        self.internal_id = str(uuid.uuid4())
        self.name = name
        self.object_type = object_type

    def __str__(self):
        return f"ID: {self.internal_id}, Name: {self.name}, Type: {self.object_type}"

    def get_id(self):
        return self.internal_id

    def get_position(self,hexmap):

        for hex in hexmap.map.keys():
            if self in hexmap.map[hex]:
                return hex
        return None


class Terrain(GameObject):

    def __init__(self, name, terrain_type, elevation=0):
        super().__init__(name, object_type="terrain")

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

    def __init__(self, name, owner):
        super().__init__(name, object_type="army")

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

    def __init__(self, name, owner):
        super().__init__(name, object_type="unit")

    pass
