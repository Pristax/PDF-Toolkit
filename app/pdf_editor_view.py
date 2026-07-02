from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene

from app.pdf_text_item import PdfTextItem


class PdfEditorView(QGraphicsView):
    def __init__(self, main_window=None):
        super().__init__()

        self.main_window = main_window
        self.setScene(QGraphicsScene(self))
        self.page_pixmap_item = None

        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)

        self.setDragMode(QGraphicsView.RubberBandDrag)

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

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Z:
            if self.main_window:
                self.main_window.undo_last_change()
            return

        if event.key() == Qt.Key_Delete:
            selected_items = self.scene().selectedItems()

            text_items = [
                item for item in selected_items
                if isinstance(item, PdfTextItem)
            ]

            if text_items:
                if self.main_window:
                    self.main_window.push_undo_state()

                for item in text_items:
                    self.scene().removeItem(item)

                if self.main_window:
                    self.main_window.statusBar().showMessage("Selected text removed")

                return

        super().keyPressEvent(event)