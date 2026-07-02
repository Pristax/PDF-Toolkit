import sys
import fitz

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction, QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QToolBar,
    QLabel,
    QScrollArea,
    QFileDialog,
    QMessageBox,
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Toolkit")
        self.resize(1200, 800)

        self.setAcceptDrops(True)

        self.pdf_document = None
        self.current_file_path = None
        self.current_page_index = 0
        self.zoom = 2.0

        self.create_actions()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_central_widget()
        self.create_statusBar()

    def create_actions(self):
        # File actions
        self.open_action = QAction(QIcon("assets/icons/open.png"), "Open PDF", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_pdf)

        self.save_action = QAction(QIcon("assets/icons/save.png"), "Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_pdf)

        self.save_as_action = QAction("Save As", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self.save_pdf_as)

        self.close_action = QAction(QIcon("assets/icons/close.png"), "Close PDF", self)
        self.close_action.triggered.connect(self.close_pdf)

        self.exit_action = QAction(QIcon("assets/icons/exit.png"), "Exit", self)
        self.exit_action.setShortcut("Alt+F4")
        self.exit_action.triggered.connect(self.close)

        # Pages actions
        self.rotate_pages_action = QAction("Rotate Pages", self)
        self.delete_pages_action = QAction("Delete Pages", self)
        self.extract_pages_action = QAction("Extract Pages", self)
        self.reorder_pages_action = QAction("Reorder Pages", self)
        self.split_pages_action = QAction("Split PDF", self)
        self.merge_pages_action = QAction("Merge PDFs", self)

        # Annotate actions
        self.add_text_action = QAction("Add Text", self)
        self.add_image_action = QAction("Add Image", self)
        self.pen_action = QAction("Pen", self)
        self.highlight_action = QAction("Highlight", self)
        self.signature_action = QAction("Signature", self)

        # Convert actions
        self.pdf_to_images_action = QAction("PDF to Images", self)
        self.images_to_pdf_action = QAction("Images to PDF", self)
        self.ocr_action = QAction("OCR", self)
        self.searchable_pdf_action = QAction("Make Searchable PDF", self)

        # Security actions
        self.add_password_action = QAction("Add Password", self)
        self.remove_password_action = QAction("Remove Password", self)
        self.remove_metadata_action = QAction("Remove Metadata", self)

        # View actions
        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.setShortcut("Ctrl++")
        self.zoom_in_action.triggered.connect(self.zoom_in)

        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.setShortcut("Ctrl+-")
        self.zoom_out_action.triggered.connect(self.zoom_out)

        self.fit_width_action = QAction("Fit Width", self)
        self.fit_page_action = QAction("Fit Page", self)

        self.previous_page_action = QAction("Previous Page", self)
        self.previous_page_action.setShortcut("Left")
        self.previous_page_action.triggered.connect(self.previous_page)

        self.next_page_action = QAction("Next Page", self)
        self.next_page_action.setShortcut("Right")
        self.next_page_action.triggered.connect(self.next_page)

    def create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.close_action)
        file_menu.addAction(self.exit_action)

        pages_menu = menubar.addMenu("Pages")
        pages_menu.addAction(self.merge_pages_action)
        pages_menu.addAction(self.split_pages_action)
        pages_menu.addSeparator()
        pages_menu.addAction(self.extract_pages_action)
        pages_menu.addAction(self.delete_pages_action)
        pages_menu.addAction(self.rotate_pages_action)
        pages_menu.addAction(self.reorder_pages_action)

        edit_pdf_menu = menubar.addMenu("Edit PDF")
        edit_pdf_menu.addAction(self.add_text_action)
        edit_pdf_menu.addAction(self.add_image_action)
        edit_pdf_menu.addAction(self.highlight_action)
        edit_pdf_menu.addAction(self.pen_action)
        edit_pdf_menu.addAction(self.signature_action)

        convert_menu = menubar.addMenu("Convert")
        convert_menu.addAction(self.pdf_to_images_action)
        convert_menu.addAction(self.images_to_pdf_action)
        convert_menu.addSeparator()
        convert_menu.addAction(self.ocr_action)
        convert_menu.addAction(self.searchable_pdf_action)

        security_menu = menubar.addMenu("Security")
        security_menu.addAction(self.add_password_action)
        security_menu.addAction(self.remove_password_action)
        security_menu.addSeparator()
        security_menu.addAction(self.remove_metadata_action)

        view_menu = menubar.addMenu("View")
        view_menu.addAction(self.zoom_in_action)
        view_menu.addAction(self.zoom_out_action)
        view_menu.addSeparator()
        view_menu.addAction(self.fit_width_action)
        view_menu.addAction(self.fit_page_action)
        view_menu.addSeparator()
        view_menu.addAction(self.previous_page_action)
        view_menu.addAction(self.next_page_action)

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.save_as_action)
        toolbar.addSeparator()

        toolbar.addAction(self.merge_pages_action)
        toolbar.addAction(self.split_pages_action)
        toolbar.addSeparator()

        toolbar.addAction(self.rotate_pages_action)
        toolbar.addAction(self.delete_pages_action)
        toolbar.addSeparator()

        toolbar.addAction(self.add_text_action)
        toolbar.addAction(self.highlight_action)
        toolbar.addAction(self.pen_action)
        toolbar.addSeparator()

        toolbar.addAction(self.previous_page_action)
        toolbar.addAction(self.next_page_action)
        toolbar.addSeparator()

        toolbar.addAction(self.zoom_in_action)
        toolbar.addAction(self.zoom_out_action)

    def create_central_widget(self):
        c_widget = QWidget()
        main_layout = QVBoxLayout(c_widget)

        self.pdf_label = QLabel("Open a PDF file")
        self.pdf_label.setAlignment(Qt.AlignCenter)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.pdf_label)

        main_layout.addWidget(self.scroll_area)

        self.setCentralWidget(c_widget)

    def create_statusBar(self):
        self.statusBar().showMessage("Ready")

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            "",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):
        try:
            if self.pdf_document:
                self.pdf_document.close()

            self.pdf_document = fitz.open(file_path)
            self.current_file_path = file_path
            self.current_page_index = 0

            self.render_page()
            self.statusBar().showMessage(f"Opened: {file_path}")

        except Exception as error:
            QMessageBox.critical(self, "Error", f"Could not open PDF:\n{error}")

    def close_pdf(self):
        if self.pdf_document:
            self.pdf_document.close()
            self.pdf_document = None

        self.current_page_index = 0
        self.pdf_label.setText("Open a PDF file")
        self.pdf_label.setPixmap(QPixmap())
        self.statusBar().showMessage("PDF closed")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()

                if file_path.lower().endswith(".pdf"):
                    event.acceptProposedAction()
                    return

        event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()

                if file_path.lower().endswith(".pdf"):
                    self.load_pdf(file_path)
                    event.acceptProposedAction()
                    return

        event.ignore()

    def render_page(self):
        if not self.pdf_document:
            return

        page = self.pdf_document[self.current_page_index]

        matrix = fitz.Matrix(self.zoom, self.zoom)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)

        image = QImage(
            pixmap.samples,
            pixmap.width,
            pixmap.height,
            pixmap.stride,
            QImage.Format_RGB888
        )

        qt_pixmap = QPixmap.fromImage(image.copy())

        self.pdf_label.setPixmap(qt_pixmap)
        self.pdf_label.adjustSize()

        page_count = len(self.pdf_document)
        self.statusBar().showMessage(
            f"Page {self.current_page_index + 1} / {page_count} | Zoom {int(self.zoom * 100)}%"
        )

    def next_page(self):
        if not self.pdf_document:
            return

        if self.current_page_index < len(self.pdf_document) - 1:
            self.current_page_index += 1
            self.render_page()

    def previous_page(self):
        if not self.pdf_document:
            return

        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.render_page()

    def zoom_in(self):
        if not self.pdf_document:
            return

        self.zoom += 0.25
        self.render_page()

    def zoom_out(self):
        if not self.pdf_document:
            return

        if self.zoom > 0.5:
            self.zoom -= 0.25
            self.render_page()

    def save_pdf(self):
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF", "No PDF is currently open.")
            return

        if not self.current_file_path:
            self.save_pdf_as()
            return

        try:
            self.pdf_document.saveIncr()
            self.statusBar().showMessage(f"Saved: {self.current_file_path}")

        except Exception as error:
            QMessageBox.critical(self, "Save Error", f"Could not save PDF:\n{error}")


    def save_pdf_as(self):
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF", "No PDF is currently open.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF As",
            "",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".pdf"):
            file_path += ".pdf"

        try:
            self.pdf_document.save(file_path)
            self.current_file_path = file_path

            self.pdf_document.close()
            self.pdf_document = fitz.open(file_path)

            self.render_page()
            self.statusBar().showMessage(f"Saved As: {file_path}")

        except Exception as error:
            QMessageBox.critical(self, "Save As Error", f"Could not save PDF:\n{error}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())