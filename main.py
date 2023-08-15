from visualize_map import MapVisualRepresentation


class Hex:

    def __init__(self, q, r):

        self.q = q
        self.r = r
        self.s = -q-r

    def get_axial_coord(self):

        return (q,r)

    def get_cube_coord(self):

        return(q,r,s)

class HexMap:

    def __init__(self):

        self.map={}

    def print_hexes(self):
        for hex in self.map.keys():
            print(f"q: {hex.q}, r: {hex.r}, s:{hex.s}")
    
    
    def initialize_map(self, left, right, top, bottom):

        for r in range(top, bottom +1):
            print(r)
            r_offset = int (r // 2.0)
            for q in range(left - r_offset, right - r_offset + 1):
                print(q)
                self.map.update({Hex(q, r):None})

        
    

wraithsong_map = HexMap()
wraithsong_map.initialize_map(-3,3,-2,2)
wraithsong_map.print_hexes()

print(wraithsong_map)

