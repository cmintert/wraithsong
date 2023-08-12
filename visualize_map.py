import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

class MapVisualRepresentation:
    
    # In the future this will take a HexMap object as input and give a visual representation of the map

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
