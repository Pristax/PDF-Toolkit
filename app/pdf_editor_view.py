from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene

from app.pdf_text_item import PdfTextItem
from app.pdf_image_item import PdfImageItem
from app.pdf_pen_item import PdfPenItem


class PdfEditorView(QGraphicsView):
    def __init__(self, main_window=None):
        super().__init__()

        self.main_window = main_window
        self.setScene(QGraphicsScene(self))
        self.page_pixmap_item = None

        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)

        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.current_pen_item = None
        self.is_drawing = False

    def dragEnterEvent(self, event):
        if self._event_has_pdf(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if self._event_has_pdf(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        for url in event.mimeData().urls():
            file_path = url.toLocalFile()

            if file_path.lower().endswith(".pdf"):
                if self.main_window:
                    self.main_window.load_pdf(file_path)

                event.acceptProposedAction()
                return

        event.ignore()

    def _event_has_pdf(self, event):
        if not event.mimeData().hasUrls():
            return False

        for url in event.mimeData().urls():
            file_path = url.toLocalFile()

            if file_path.lower().endswith(".pdf"):
                return True

        return False

    def mousePressEvent(self, event):
        if (
            self.main_window
            and self.main_window.current_tool in ("pen", "highlight")
            and event.button() == Qt.LeftButton
            and self.main_window.pdf_document
        ):
            self.main_window.push_undo_state()

            scene_pos = self.mapToScene(event.pos())

            pdf_x = scene_pos.x() / self.main_window.zoom
            pdf_y = scene_pos.y() / self.main_window.zoom

            if self.main_window.current_tool == "highlight":
                color = self.main_window.highlight_color
                width = self.main_window.highlight_width
                opacity = self.main_window.highlight_opacity
                item_type = "highlight"
            else:
                color = self.main_window.pen_color
                width = self.main_window.pen_width
                opacity = 1.0
                item_type = "pen"

            self.current_pen_item = PdfPenItem(
                points=[(pdf_x, pdf_y)],
                color=color,
                width=width,
                zoom=self.main_window.zoom,
                main_window=self.main_window,
                opacity=opacity,
                item_type=item_type,
            )

            self.scene().addItem(self.current_pen_item)

            self.is_drawing = True
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_drawing and self.current_pen_item and self.main_window:
            scene_pos = self.mapToScene(event.pos())

            pdf_x = scene_pos.x() / self.main_window.zoom
            pdf_y = scene_pos.y() / self.main_window.zoom

            self.current_pen_item.add_point(pdf_x, pdf_y)

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.is_drawing:
            self.is_drawing = False
            self.current_pen_item = None

            if self.main_window:
                if self.main_window.current_tool == "highlight":
                    message = "Highlight added. Press Delete to remove selected highlight or Ctrl+Z to undo."
                else:
                    message = "Pen stroke added. Press Delete to remove selected stroke or Ctrl+Z to undo."

                self.main_window.statusBar().showMessage(message)

            event.accept()
            return

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Z:
            if self.main_window:
                self.main_window.undo_last_change()
            return

        if event.key() == Qt.Key_Escape:
            if self.main_window:
                self.main_window.current_tool = None
                self.main_window.statusBar().showMessage("Pen tool disabled")
            return

        if event.key() == Qt.Key_Delete:
            selected_items = self.scene().selectedItems()

            editable_items = [
                item for item in selected_items
                if isinstance(item, (PdfTextItem, PdfImageItem, PdfPenItem))
            ]

            if editable_items:
                if self.main_window:
                    self.main_window.push_undo_state()

                for item in editable_items:
                    self.scene().removeItem(item)

                if self.main_window:
                    self.main_window.statusBar().showMessage("Selected item removed")

                return

        super().keyPressEvent(event)