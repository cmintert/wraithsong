from PySide6.QtCore import Qt, QSize, QObject, Signal
from PySide6.QtGui import QPen, QPainterPath, QPixmap, QColor, QFont
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsPixmapItem,
    QGraphicsPathItem,
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QMainWindow,
)

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
        q_axis, r_axis = self.hex.get_axial_coordinates()

        self.emitter.hex_hovered.emit(
            q_axis, r_axis
        )  # Emit the signal to the parent widget

        pen = QPen(QColor(PEN_COLOR_HOVER))
        pen.setWidth(5)

        self.setPen(pen)
        self.setZValue(10)

    def hoverLeaveEvent(self, event):
        pen = QPen(QColor(PEN_COLOR_DEFAULT))  # Original color
        pen.setWidth(5)
        self.setPen(pen)
        self.setZValue(0)


class HexMapVisualization(QGraphicsView):
    def __init__(self, hex_map, edge_map, graph, parent_app=None):
        super().__init__()
        self.parent_app = parent_app
        self.hex_map = hex_map
        self.edge_map = edge_map
        self.graph = graph
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.draw_map()

    @staticmethod
    def interpolate_color(min_color, max_color, factor):
        """
        Interpolate between two QColor objects based on a factor.

        :param min_color: Starting QColor
        :param max_color: Ending QColor
        :param factor: Value between 0 and 1 to interpolate colors
        :return: Interpolated QColor
        """
        red = min_color.red() + factor * (max_color.red() - min_color.red())
        green = min_color.green() + factor * (max_color.green() - min_color.green())
        blue = min_color.blue() + factor * (max_color.blue() - min_color.blue())
        return QColor(red, green, blue)

    def get_color_for_distance(self, distance, min_distance=0, max_distance=4):
        """
        Get a color based on the distance value using a gradient from green to red.

        :param distance: Distance value
        :param min_distance: Minimum expected distance (corresponds to green)
        :param max_distance: Maximum expected distance (corresponds to red)
        :return: QColor for the specified distance
        """
        # Normalize distance to a factor between 0 and 1

        factor = (distance - min_distance) / (max_distance - min_distance)
        factor = max(0, min(1, factor))  # Ensure factor is in [0, 1] range

        # Determine the gradient segment and adjust the factor for the segment
        if factor < 0.5:
            start_color = QColor("#78a26c")
            end_color = QColor("#ffca51")
            factor = factor * 2  # Adjust factor for this segment
        else:
            start_color = QColor("#ffca51")
            end_color = QColor("#832800")
            factor = (factor - 0.5) * 2  # Adjust factor for this segment

        return self.interpolate_color(start_color, end_color, factor)

    def draw_map(self):
        hex_size = 80

        for hex_field, game_objects in self.hex_map.hex_map.items():
            self.draw_hex_terrain(hex_field, hex_size)

        for edge, game_objects in self.edge_map.edge_map.items():
            # check if the game object is a river and a terrain
            for game_object in game_objects:
                if (
                    isinstance(game_object, gameobjects.Terrain)
                    and game_object.terrain_type == "river"
                ):
                    self.add_graphic_to_edge(edge, hex_size, "river.png")
                elif (
                    isinstance(game_object, gameobjects.Structure)
                    and game_object.terrain_type == "road"
                ):
                    self.add_graphic_to_edge(edge, hex_size, "road.png")

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
        hoverable_hex.emitter.hex_hovered.connect(self.show_move_distances)
        hoverable_hex.setPen(pen)

        self.scene.addItem(hoverable_hex)

        for game_object in self.hex_map.get_hex_object_list(hex):
            if isinstance(game_object, gameobjects.Terrain):
                self.add_graphic_to_hex(hex, size, game_object.texture)
                self.add_coordinate_labels(hex, size)

    def add_coordinate_labels(self, hex, size):
        hex_x_coordinates, hex_y_coordinates = hex.get_pixel_coordinates(size)

        label = QGraphicsTextItem(f"{hex.q_axis}, {hex.r_axis}")
        label.setFont(QFont("Vinque Rg", 15))
        label.setOpacity(0.6)

        label.setPos(
            hex_x_coordinates - label.boundingRect().width() / 2,
            hex_y_coordinates - label.boundingRect().height() / 2,
        )

        self.scene.addItem(label)

    def show_move_distances(self, q=0, r=0, move_cost_limit=6):
        hex_size = 80

        distances = self.graph.djikstra(
            Hex.hex_obj_from_string(f"{q},{r}"), move_cost_limit
        )

        # Remove all distance labels from the scene
        for item in self.scene.items():
            if getattr(item, "is_distance_label", False):
                self.scene.removeItem(item)

        # Iterate over the Hex Fields and add the distance labels
        for hex_field in self.hex_map.hex_map.keys():
            if not distances[hex_field] > move_cost_limit:
                hex_x_coordinates, hex_y_coordinates = hex_field.get_pixel_coordinates(
                    hex_size
                )

                label_distances = QGraphicsTextItem(f"{distances[hex_field]}")
                label_distances.setFont(QFont("Vinque Rg", 15))
                label_distances.setPos(
                    hex_x_coordinates - label_distances.boundingRect().width() / 2,
                    hex_y_coordinates - label_distances.boundingRect().height() + 60,
                )
                label_distances.setOpacity(1)

                color = self.get_color_for_distance(distances[hex_field])
                label_distances.setDefaultTextColor("#130f06")

                # Draw a small circle below the label
                circle_path = QPainterPath()
                circle_path.addEllipse(label_distances.boundingRect().center(), 13, 13)
                circle_item = QGraphicsPathItem(circle_path)
                circle_item.setBrush(QColor(color))
                circle_item.setOpacity(0.6)
                circle_item.setPen(Qt.NoPen)
                circle_item.setPos(label_distances.pos())

                # Flag items as distance labels
                circle_item.is_distance_label = True
                label_distances.is_distance_label = True

                self.scene.addItem(circle_item)
                self.scene.addItem(label_distances)

    def add_graphic_to_hex(self, hex_field, size, asset="missing.png"):
        x_axis, y_axis = hex_field.get_pixel_coordinates(size)

        # Create a scaled QPixmap object

        scale_factor = 2.33
        pixmap = QPixmap(f"assets/{asset}")
        scale_pixmap = pixmap.scaled(
            QSize(size * scale_factor, size * scale_factor),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

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
        rotation_matrix = (-60, 0, 60, -60, 0, 60)

        source_hex = edge.spawn_hex
        edge_center_coordinates = source_hex.get_edgecenter_pixel_coordinates(size)

        x_axis, y_axis = (
            edge_center_coordinates[edge.spawn_direction][0],
            edge_center_coordinates[edge.spawn_direction][1],
        )

        scale_factor = (
            1.2  # This is the scale factor for the texture to fit the hex edge
        )

        pixmap = QPixmap(f"assets/{asset}")
        scale_pixmap = pixmap.scaled(
            QSize(size * scale_factor, size * scale_factor),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        pixmap_item = QGraphicsPixmapItem(scale_pixmap)
        pixmap_item.setOffset(
            -pixmap_item.boundingRect().width() / 2,
            -pixmap_item.boundingRect().height() / 2,
        )

        graphic_x_center = x_axis
        graphic_y_center = y_axis

        pixmap_item.setRotation(rotation_matrix[edge.spawn_direction])
        pixmap_item.setPos(graphic_x_center, graphic_y_center)

        # Draw the edge texture on screen

        self.scene.addItem(pixmap_item)

    def update_info_label(self, q, r):
        self.parent_app.hex_info_label.setText(f"Hex Coordinates: {q},{r}")


class HexMapApp(QMainWindow):
    def __init__(self, hex_map, edge_map, graph):
        super().__init__()
        self.map_area_widget = HexMapVisualization(hex_map, edge_map, graph, self)
        self.map_area_widget.setStyleSheet("background-color: darkgray;")

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
        self.layout.addWidget(self.map_area_widget)
        self.layout.addWidget(self.hex_info_widget)

        # Create a central widget to hold the layout
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)

        # Set the central widget and window title
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Hex Map Visualization")
