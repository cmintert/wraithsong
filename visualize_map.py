from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QGraphicsPixmapItem, QGraphicsPathItem, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QSize, QObject,Signal
from PySide6.QtGui import QPen, QPainterPath, QPixmap, QColor
import math
import sys
import gameobjects
from map_logic import Hex

PEN_COLOR_HOVER = "#979068"
PEN_COLOR_DEFAULT = "#2b362b"

class SignalEmitter(QObject):
    hex_hovered = Signal(int, int)

class HoverableHexagon(QGraphicsPathItem):
    
    def __init__(self, path, hex):
        super().__init__(path)
        self.setAcceptHoverEvents(True)
        self.hex = hex
        self.emitter = SignalEmitter()
        
    def hoverEnterEvent(self, event):

        q,r = self.hex.get_axial_coordinates()

        self.emitter.hex_hovered.emit (q, r) # Emit the signal to the parent widget
        print(f"Hovering over hex {q},{r}")

        pen = QPen(QColor(PEN_COLOR_HOVER))
        pen.setWidth(5)

        self.setPen(pen)
        self.setZValue(10)

    def hoverLeaveEvent(self, event):
        # Reset the pen color or style when the mouse leaves the hexagon
        pen = QPen(QColor(PEN_COLOR_DEFAULT))  # Original color
        pen.setWidth(5)
        self.setPen(pen)
        self.setZValue(0)

class HexMapVisualization(QGraphicsView):
    def __init__(self, hex_map, edge_map, parent_app=None):
        super().__init__()
        self.parent_app = parent_app
        self.hex_map = hex_map
        self.edge_map = edge_map
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.draw_map()

    def draw_map(self):

        hex_size = 80

        for hex_field,game_objects in self.hex_map.hex_map.items():
            self.draw_hex_terrain(hex_field, hex_size)

        for edge,game_objects in self.edge_map.edge_map.items():
            #check if the game object is a river and a terrain
            for game_object in game_objects:
                if isinstance(game_object, gameobjects.Terrain) and game_object.terrain_type == "river":  
                    self.add_graphic_to_edge(edge, hex_size, "river.png")

    def draw_hex_terrain(self, hex, size):

        # Define hex corners

        corners = hex.get_cornerpixel_coordinates(size)

        # Create a path for the hex shape

        hex_path = QPainterPath()
        hex_path.moveTo(*corners[0])
        for corner in corners[1:]:
            hex_path.lineTo(*corner)
        hex_path.closeSubpath()

        pen = QPen(QColor("#2b362b"))
        pen.setWidth(5)

        hoverable_hex = HoverableHexagon(hex_path, hex)
        hoverable_hex.emitter.hex_hovered.connect(self.update_info_label)
        hoverable_hex.setPen(pen)
        self.scene.addItem(hoverable_hex)

        for game_object in self.hex_map.get_hex_object_list(hex):
            if isinstance(game_object, gameobjects.Terrain):
                self.add_graphic_to_hex(hex, size, game_object.texture)
                self.add_coordinate_labels(hex, size)   
    
    def add_coordinate_labels(self, hex, size):
        hex_x_coordinates, hex_y_coordinates = hex.get_pixel_coordinates(size)

        label = QGraphicsTextItem(f"({hex.q_axis}, {hex.r_axis})")
        label.setPos(hex_x_coordinates - label.boundingRect().width() / 2,
                     hex_y_coordinates - label.boundingRect().height()/2)
        self.scene.addItem(label)

    def add_graphic_to_hex(self, hex_field, size, asset="missing.png"):

        x_axis, y_axis = hex_field.get_pixel_coordinates(size)

        # Create a scaled QPixmap object

        scale_factor = 2.33 # This is the scale factor for the hexagon to fit drawn path

        pixmap = QPixmap(f"assets/{asset}")
        scale_pixmap = pixmap.scaled(QSize(size * scale_factor, size * scale_factor), Qt.KeepAspectRatio,
                                     Qt.SmoothTransformation)

        # Create a QGraphicsPixmapItem and set its pixmap

        pixmap_item = QGraphicsPixmapItem(scale_pixmap)

        # Calculate the coordinates to center the pixmap within the hex

        graphic_x_center = x_axis - pixmap_item.boundingRect().width() / 2
        graphic_y_center = y_axis - pixmap_item.boundingRect().height() / 2

        # Set the position of the pixmap item

        pixmap_item.setPos(graphic_x_center, graphic_y_center)

        # Draw the hex

        self.scene.addItem(pixmap_item)

    def add_graphic_to_edge(self, edge, size, asset="missing.png"):
        
        rotation_matrix = (-60,0,60,-60,0,60)

        source_hex = edge.spawn_hex   
        edge_center_coordinates = source_hex.get_edgecenter_pixel_coordinates(size)

        x_axis, y_axis = edge_center_coordinates[edge.spawn_direction][0], edge_center_coordinates[edge.spawn_direction][1]

        scale_factor = 1.2    # This is the scale factor for the texture to fit the hex edge
        
        pixmap = QPixmap(f"assets/{asset}")
        scale_pixmap = pixmap.scaled(QSize(size * scale_factor, size * scale_factor), Qt.KeepAspectRatio,
                                     Qt.SmoothTransformation)

        pixmap_item = QGraphicsPixmapItem(scale_pixmap)
        pixmap_item.setOffset(-pixmap_item.boundingRect().width() / 2, -pixmap_item.boundingRect().height() / 2)

        graphic_x_center = x_axis
        graphic_y_center = y_axis

        pixmap_item.setRotation(rotation_matrix[edge.spawn_direction])
        pixmap_item.setPos(graphic_x_center, graphic_y_center)

        self.scene.addItem(pixmap_item)

    def update_info_label(self, q, r):
        self.parent_app.hex_info_label.setText(f"Hex Info: {q},{r}")


class HexMapApp(QMainWindow):

    def __init__(self, hex_map, edge_map):
        super().__init__()
        self.visualization = HexMapVisualization(hex_map, edge_map, self)
        
        # Create the new widget
        self.hex_info_widget = QWidget()
        self.hex_info_widget_layout = QVBoxLayout()
        self.hex_info_widget.setLayout(self.hex_info_widget_layout)
        self.hex_info_widget.setMinimumWidth(300)

        # Create a label to contain the Hex Info
        self.hex_info_label = QLabel("Hex Info")
        self.hex_info_widget_layout.addWidget(self.hex_info_label)
        self.hex_info_widget_layout.setAlignment(Qt.AlignTop)

        # Create a horizontal layout to arrange the widgets side by side
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.visualization)
        self.layout.addWidget(self.hex_info_widget)

        # Create a central widget to hold the layout
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)

        # Set the central widget and window title
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Hex Map Visualization")

        
        
