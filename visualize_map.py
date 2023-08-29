from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QGraphicsPixmapItem
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPen, QPainterPath, QPixmap, QColor
import math
import sys
import gameobjects
from map_logic import Hex


class HexMapVisualization(QGraphicsView):
    def __init__(self, hex_map, edge_map):
        super().__init__()
        self.hex_map = hex_map
        self.edge_map = edge_map
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.draw_map()

    def draw_map(self):

        size = 80

        for hex_field,game_objects in self.hex_map.hex_map.items():
            self.draw_hex_terrain(hex_field, size)

        for edge,game_objects in self.edge_map.edge_map.items():
            #check if the game object is a river and a terrain
            for game_object in game_objects:
                if isinstance(game_object, gameobjects.Terrain) and game_object.terrain_type == "river":
                    self.draw_edge_terrain(edge, size)
                    self.add_graphic_to_edge(edge, size, "river.png")

    def draw_edge_terrain(self, edge, size):

       source_hex = edge.spawn_hex
       corners = source_hex.get_cornerpixel_coordinates(size)
       
       edge_path = QPainterPath()
       edge_path.moveTo(*corners[edge.spawn_direction])  # todo: look at this suspicious behavior
       edge_path.lineTo(*corners[(edge.spawn_direction + 1)%6])
       
       pen = QPen(QColor("#0000FF"))
       pen.setWidth(10)
       
       #self.scene.addPath(edge_path, pen=pen)

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

        self.scene.addPath(hex_path, pen=pen)

        for game_object in self.hex_map.get_hex_object_list(hex):
            if isinstance(game_object, gameobjects.Terrain):
                self.add_graphic_to_hex(hex, size, game_object.texture)

        # Add coordinate labels
        hex_x_coordinates, hex_y_coordinates = hex.get_pixel_coordinates(size)

        label = QGraphicsTextItem(f"({hex.q_axis}, {hex.r_axis})")
        label.setPos(hex_x_coordinates - label.boundingRect().width() / 2,
                     hex_y_coordinates - label.boundingRect().height()/2)
        self.scene.addItem(label)

    def add_graphic_to_hex(self, hex_field, size, asset="missing.png"):

        x_axis, y_axis = hex_field.get_pixel_coordinates(size)

        # Create a scaled QPixmap object

        scale_factor = 2.33
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

        scale_factor = 1.2
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



class HexMapApp(QMainWindow):

    def __init__(self, hex_map, edge_map):
        super().__init__()
        self.visualization = HexMapVisualization(hex_map, edge_map)
        self.setCentralWidget(self.visualization)
        self.setWindowTitle("Hex Map Visualization")
