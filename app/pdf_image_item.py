from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPixmap, QPen
from PySide6.QtWidgets import QGraphicsPixmapItem


class PdfImageItem(QGraphicsPixmapItem):
    RESIZE_MARGIN = 18

    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"

    def __init__(self, image_path, zoom=1.0, main_window=None):
        pixmap = QPixmap(image_path)
        super().__init__(pixmap)

        self.image_path = image_path
        self.zoom = zoom
        self.main_window = main_window

        self.undo_saved_for_current_action = False

        self.resizing = False
        self.resize_corner = None
        self.resize_start_scene_pos = None
        self.start_scale = 1.0
        self.start_pos = None

        self.setFlags(
            QGraphicsPixmapItem.ItemIsMovable
            | QGraphicsPixmapItem.ItemIsSelectable
            | QGraphicsPixmapItem.ItemIsFocusable
        )

        self.setAcceptHoverEvents(True)
        self.setTransformationMode(Qt.SmoothTransformation)
        self.setZValue(9)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        if self.isSelected():
            painter.setPen(QPen(Qt.black, 1, Qt.DashLine))
            painter.drawRect(super().boundingRect())

    def get_corner_at_position(self, position):
        rect = super().boundingRect()
        margin = self.RESIZE_MARGIN

        top_left = QRectF(
            rect.left(),
            rect.top(),
            margin,
            margin
        )

        top_right = QRectF(
            rect.right() - margin,
            rect.top(),
            margin,
            margin
        )

        bottom_left = QRectF(
            rect.left(),
            rect.bottom() - margin,
            margin,
            margin
        )

        bottom_right = QRectF(
            rect.right() - margin,
            rect.bottom() - margin,
            margin,
            margin
        )

        if top_left.contains(position):
            return self.TOP_LEFT

        if top_right.contains(position):
            return self.TOP_RIGHT

        if bottom_left.contains(position):
            return self.BOTTOM_LEFT

        if bottom_right.contains(position):
            return self.BOTTOM_RIGHT

        return None

    def hoverMoveEvent(self, event):
        corner = self.get_corner_at_position(event.pos())

        if corner in (self.TOP_LEFT, self.BOTTOM_RIGHT):
            self.setCursor(Qt.SizeFDiagCursor)

        elif corner in (self.TOP_RIGHT, self.BOTTOM_LEFT):
            self.setCursor(Qt.SizeBDiagCursor)

        else:
            self.setCursor(Qt.OpenHandCursor)

        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        self.unsetCursor()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        self._push_undo_once()

        corner = self.get_corner_at_position(event.pos())

        if corner:
            self.resizing = True
            self.resize_corner = corner
            self.resize_start_scene_pos = event.scenePos()
            self.start_scale = self.scale()
            self.start_pos = self.pos()

            event.accept()
            return

        self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            self.resize_from_corner(event.scenePos())
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.resize_corner = None
        self.resize_start_scene_pos = None
        self.start_scale = self.scale()
        self.start_pos = self.pos()
        self.undo_saved_for_current_action = False
        self.unsetCursor()

        super().mouseReleaseEvent(event)

    def resize_from_corner(self, current_scene_pos):
        if not self.resize_start_scene_pos:
            return

        rect = super().boundingRect()
        original_width = max(1, rect.width())
        original_height = max(1, rect.height())

        delta = current_scene_pos - self.resize_start_scene_pos

        if self.resize_corner == self.BOTTOM_RIGHT:
            scale_change = max(
                delta.x() / original_width,
                delta.y() / original_height
            )

            new_scale = max(0.05, self.start_scale + scale_change)
            self.setScale(new_scale)

        elif self.resize_corner == self.TOP_LEFT:
            scale_change = max(
                -delta.x() / original_width,
                -delta.y() / original_height
            )

            new_scale = max(0.05, self.start_scale + scale_change)
            old_scene_bottom_right = self.mapToScene(rect.bottomRight())

            self.setScale(new_scale)

            new_scene_bottom_right = self.mapToScene(rect.bottomRight())
            movement = old_scene_bottom_right - new_scene_bottom_right
            self.setPos(self.pos() + movement)

        elif self.resize_corner == self.TOP_RIGHT:
            scale_change = max(
                delta.x() / original_width,
                -delta.y() / original_height
            )

            new_scale = max(0.05, self.start_scale + scale_change)
            old_scene_bottom_left = self.mapToScene(rect.bottomLeft())

            self.setScale(new_scale)

            new_scene_bottom_left = self.mapToScene(rect.bottomLeft())
            movement = old_scene_bottom_left - new_scene_bottom_left
            self.setPos(self.pos() + movement)

        elif self.resize_corner == self.BOTTOM_LEFT:
            scale_change = max(
                -delta.x() / original_width,
                delta.y() / original_height
            )

            new_scale = max(0.05, self.start_scale + scale_change)
            old_scene_top_right = self.mapToScene(rect.topRight())

            self.setScale(new_scale)

            new_scene_top_right = self.mapToScene(rect.topRight())
            movement = old_scene_top_right - new_scene_top_right
            self.setPos(self.pos() + movement)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            self._push_undo_once()

            delta = event.angleDelta().y()

            if delta > 0:
                self.setScale(self.scale() * 1.1)
            else:
                self.setScale(max(0.05, self.scale() / 1.1))

            event.accept()
            return

        super().wheelEvent(event)

    def _push_undo_once(self):
        if self.undo_saved_for_current_action:
            return

        if self.main_window:
            self.main_window.push_undo_state()

        self.undo_saved_for_current_action = True