from visualize_map import MapVisualRepresentation


class Hex:

    def __init__(self, q, r, s):

        assert q + r + s == 0, "Invalid cube coordinates"
        self.q = q
        self.r = r
        self.s = s

    def cube_to_axial(self):

        q = self.q
        r = self.r
        return (q,r)

    def axial_to_cube(self):

        q = self.q
        r = self.r
        s = -self.q-self.r
        return(q,r,s)

class HexMap:

    def __init__(self):

        self.map={}

    def set_hex (self, hex, value):
        self.map[hex] = value

    def get_hex (self, hex):
        return self.map.get(hex,None)


wraithsong_map = MapVisualRepresentation()
wraithsong_map.draw_map()

