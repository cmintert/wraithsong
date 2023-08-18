from visualize_map import MapVisualRepresentation
import database as db
import uuid

class Hex:

    def __init__(self, q, r):

        self.q = q
        self.r = r
        self.s = -q-r

    def __hash__(self):
        return hash((self.q, self.r, self.s))

    def __eq__(self, other):
        if isinstance(other, Hex):
            return self.q == other.q and self.r == other.r and self.s == other.s
        return False

    def get_axial_coord(self):

        return (self.q,self.r)

    def get_cube_coord(self):

        return(self.q, self.r, self.s)

class GameObject:

    def __init__(self, name="Not specified", type=None):

        self.internal_id = str(uuid.uuid4())
        self.name = name
        self.type = type

    def __str__(self):

       return f"ID: {self.internal_id}, Name: {self.name}"

    def get_id(self):

        return self.internal_id

class Terrain(GameObject):

    def __init__(self, name):
        super().__init__(name, type="Terrain")

class HexMap:

    def __init__(self):

        self.map={}

    def append_object(self, hex, object):

        if hex in self.map:
            self.map[hex].append(object)
        else:
            self.map[hex] = [object]

    def get_object_list(self, hex):

        return self.map[hex]

    def print_hexes(self):
        for hex in self.map.keys():
            print(f"q: {hex.q}, r: {hex.r}, s:{hex.s}")
            print(f"object: {self.map[hex]}")
    
    def initialize_map(self, left, right, top, bottom):

        for r in range(top, bottom +1):
            r_offset = int (r // 2.0)
            for q in range(left - r_offset, right - r_offset + 1):
                self.map.update({Hex(q, r):[]})

        
    

wraithsong_map = HexMap()
wraithsong_map.initialize_map(-3,3,-2,2)
wraithsong_map.append_object(Hex(0,0), Terrain("Eerie forrest"))
wraithsong_map.append_object(Hex(0,0), GameObject())
#wraithsong_map.print_hexes()


db.create_database()
db.clear_database()
db.create_gameobject_table()
for item in wraithsong_map.get_object_list(Hex(0,0)):
    db.write_gameobject(item)