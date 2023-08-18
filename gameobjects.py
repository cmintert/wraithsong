import uuid

class GameObject:

    def __init__(self, name="Not specified", type=None):
        self.internal_id = str(uuid.uuid4())
        self.name = name
        self.type = type

    def __str__(self):
        return f"ID: {self.internal_id}, Name: {self.name}, Type: {self.type}"

    def get_id(self):
        return self.internal_id

    def get_position(self,hexmap):

        for hex in hexmap.map.keys():
            if self in hexmap.map[hex]:
                return hex
        return None


class Terrain(GameObject):

    def __init__(self, name):
        super().__init__(name, type="Terrain")

    def __str__(self):
        return super().__str__()


class Army(GameObject):

    def __init__(self, name):
        super().__init__(name, type="Army")

    def __str__(self):
        return super().__str__()