import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

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

class Layout:
    
    def __init__(self, orientation = np.radians(0), size = 2, origin = (0, 0)):
            
        self.orientation = orientation
        self.size = size
        self.origin = origin

    def draw_map(self):
        
        fig, ax = plt.subplots()
        hexagon = patches.RegularPolygon(self.origin, 6, self.size, self.orientation, facecolor='none', edgecolor='black')
        ax.add_patch(hexagon)
        plt.autoscale()
        plt.show()


wraithsong_map = Layout()
wraithsong_map.draw_map()

