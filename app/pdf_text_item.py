from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGraphicsTextItem


class PdfTextItem(QGraphicsTextItem):
    def __init__(self, text, font_size=14, zoom=1.0, main_window=None):
        super().__init__(text)

        self.pdf_font_size = font_size
        self.zoom = zoom
        self.main_window = main_window
        self.undo_saved_for_current_action = False

        font = QFont()
        font.setPointSize(max(1, int(font_size * zoom)))
        self.setFont(font)

        self.setDefaultTextColor(Qt.black)

        self.setFlags(
            QGraphicsTextItem.ItemIsMovable
            | QGraphicsTextItem.ItemIsSelectable
            | QGraphicsTextItem.ItemIsFocusable
        )

        self.setTextInteractionFlags(Qt.NoTextInteraction)

        self.setZValue(10)

    def mousePressEvent(self, event):
        self._push_undo_once()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.undo_saved_for_current_action = False
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        self._push_undo_once()

        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus(Qt.MouseFocusReason)

        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self.undo_saved_for_current_action = False
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clearFocus()
            self.setTextInteractionFlags(Qt.NoTextInteraction)
            return

        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Z:
            if self.main_window:
                self.main_window.undo_last_change()
            return

        self._push_undo_once()
        super().keyPressEvent(event)

    def _push_undo_once(self):
        if self.undo_saved_for_current_action:
            return

        if self.main_window:
            self.main_window.push_undo_state()

        self.undo_saved_for_current_action = True