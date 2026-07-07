from PySide6.QtCore import Qt
from PySide6.QtGui import QPainterPath, QPen, QColor
from PySide6.QtWidgets import QGraphicsPathItem


class PdfPenItem(QGraphicsPathItem):
    def __init__(
        self,
        points=None,
        color=None,
        width=3,
        zoom=1.0,
        main_window=None,
        opacity=1.0,
        item_type="pen",
    ):
        super().__init__()

        self.points = points or []
        self.pen_color = color if color is not None else QColor(0, 0, 0)
        self.pen_width = width
        self.zoom = zoom
        self.main_window = main_window
        self.opacity = opacity
        self.item_type = item_type

        self.setFlags(
            QGraphicsPathItem.ItemIsSelectable
            | QGraphicsPathItem.ItemIsFocusable
        )

        self.setZValue(8)

        self.update_path()

    def update_path(self):
        path = QPainterPath()

        if self.points:
            first_point = self.points[0]
            path.moveTo(first_point[0] * self.zoom, first_point[1] * self.zoom)

            for x, y in self.points[1:]:
                path.lineTo(x * self.zoom, y * self.zoom)

        self.setPath(path)

        color = QColor(self.pen_color)
        color.setAlphaF(self.opacity)

        pen = QPen(color)
        pen.setWidthF(self.pen_width * self.zoom)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)

        self.setPen(pen)

    def add_point(self, x, y):
        self.points.append((x, y))
        self.update_path()