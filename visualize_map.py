from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen, QPainterPath, QPainter
import math
import sys

class HexMapVisualization(QGraphicsView):
    def __init__(self, hex_map):
        super().__init__()
        self.hex_map = hex_map
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.init_map()

    def init_map(self):

        for hex_field,game_objects in self.hex_map.map.items():
            self.draw_hex(hex_field)

    def draw_hex(self, hex, size = 20):

        # Hex center coordinates

        x_axis, y_axis = hex.get_pixel_coordinates(size)

        # Define hex corners

        corners = [self.hex_corner(size, corner_number, x_axis, y_axis) for corner_number in range(6)]

        # Create a path for the hex shape

        hex_path = QPainterPath()
        hex_path.moveTo(*corners[0])
        for corner in corners[1:]:
            hex_path.lineTo(*corner)
        hex_path.closeSubpath()

        # Draw the hex (green color for now)
        self.scene.addPath(hex_path, pen=QPen(Qt.black), brush=QColor("green"))

        # TODO: Add coordinate labels or other details as needed

    def hex_corner(self, size, corner_number, x_axis, y_axis):

        # Calculate the corner points for the hex

        angle_deg = 60 * corner_number - 30
        angle_rad = math.pi / 180 * angle_deg
        return (x_axis + size * math.cos(angle_rad), y_axis + size * math.sin(angle_rad))

class HexMapApp(QMainWindow):
    def __init__(self, hex_map):
        super().__init__()
        self.visualization = HexMapVisualization(hex_map)
        self.setCentralWidget(self.visualization)
        self.setWindowTitle("Hex Map Visualization")