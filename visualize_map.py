from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QGraphicsPixmapItem
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPen, QPainterPath, QPainter, QBrush, QPixmap
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
            self.draw_hex(hex_field, 80)
        # Fit the view to the bounding rectangle of the scene
        #self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def draw_hex(self, hex, size):

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

        # Create a scaled QPixmap object
        scale_factor = 2.35
        pixmap = QPixmap("assets/forest.png")
        scale_pixmap = pixmap.scaled(QSize(size * scale_factor, size * scale_factor), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Create a QGraphicsPixmapItem and set its pixmap
        pixmap_item = QGraphicsPixmapItem(scale_pixmap)


        # Calculate the coordinates to center the pixmap within the hex
        x_center = x_axis - pixmap_item.boundingRect().width() / 2
        y_center = y_axis - pixmap_item.boundingRect().height() / 2

        # Set the position of the pixmap item
        pixmap_item.setPos(x_center, y_center)

        # Draw the hex
        self.scene.addItem(pixmap_item)

        pen = QPen(Qt.darkGray)
        pen.setWidth(2)

        self.scene.addPath(hex_path, pen=pen)


        # Add coordinate labels

        label = QGraphicsTextItem(f"({hex.q_axis}, {hex.r_axis})")
        label.setPos(x_axis - label.boundingRect().width() / 2, y_axis - label.boundingRect().height()/2)
        self.scene.addItem(label)

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