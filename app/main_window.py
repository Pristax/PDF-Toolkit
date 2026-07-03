import copy
import os
import tempfile
import fitz

from PySide6.QtGui import QIcon, QAction, QImage, QPixmap, QColor
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QToolBar,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QGraphicsPixmapItem,
    QColorDialog,
)

from app.pdf_editor_view import PdfEditorView
from app.pdf_text_item import PdfTextItem
from app.pdf_image_item import PdfImageItem


APP_NAME = "PDF Toolkit"
APP_VERSION = "v0.4"
APP_AUTHOR = "Jan Pristaš"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.resize(1200, 800)

        self.setAcceptDrops(True)

        self.pdf_document = None
        self.current_file_path = None
        self.current_page_index = 0
        self.zoom = 2.0

        # Temporary editable text objects.
        # They are stored here until Save / Save As writes them into the PDF.
        self.page_text_items = {}
        self.page_image_items = {}

        self.undo_stack = []
        self.max_undo_steps = 20
        self.is_restoring_undo = False

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
        self.rotate_pages_action.triggered.connect(self.rotate_pages)

        self.delete_pages_action = QAction("Delete Pages", self)
        self.delete_pages_action.triggered.connect(self.delete_pages)

        self.extract_pages_action = QAction("Extract Pages", self)
        self.extract_pages_action.triggered.connect(self.extract_pages)

        self.reorder_pages_action = QAction("Reorder Pages", self)
        self.reorder_pages_action.triggered.connect(self.reorder_pages)

        self.split_pages_action = QAction("Split PDF", self)
        self.split_pages_action.triggered.connect(self.split_pdf)

        self.merge_pages_action = QAction("Merge PDFs", self)
        self.merge_pages_action.triggered.connect(self.merge_pdfs)

        # Edit PDF actions
        self.add_text_action = QAction("Add Text", self)
        self.add_text_action.triggered.connect(self.add_text_item)

        self.add_image_action = QAction("Add Image", self)
        self.add_image_action.triggered.connect(self.add_image_item)

        self.pen_action = QAction("Pen", self)
        self.highlight_action = QAction("Highlight", self)
        self.signature_action = QAction("Signature", self)

        # Undo
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.undo_last_change)
        self.addAction(self.undo_action)

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

        # Help actions
        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.show_about_dialog)

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

        help_menu = menubar.addMenu("Help")
        help_menu.addAction(self.about_action)

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

        self.pdf_view = PdfEditorView(self)
        main_layout.addWidget(self.pdf_view)

        self.setCentralWidget(c_widget)

    def create_statusBar(self):
        self.statusBar().showMessage("Ready")


    def push_undo_state(self):
        if self.is_restoring_undo:
            return

        if not self.pdf_document:
            return

        try:
            self.save_current_page_text_items()

            state = {
                "pdf_bytes": self.pdf_document.tobytes(),
                "current_file_path": self.current_file_path,
                "current_page_index": self.current_page_index,
                "zoom": self.zoom,
                "page_text_items": copy.deepcopy(self.page_text_items),
                "page_image_items": copy.deepcopy(self.page_image_items),
            }

            self.undo_stack.append(state)

            if len(self.undo_stack) > self.max_undo_steps:
                self.undo_stack.pop(0)

            self.statusBar().showMessage("Undo state saved")

        except Exception as error:
            QMessageBox.warning(
                self,
                "Undo Error",
                f"Could not save undo state:\n{error}"
            )


    def undo_last_change(self):
        if not self.undo_stack:
            self.statusBar().showMessage("Nothing to undo")
            return

        try:
            self.is_restoring_undo = True

            state = self.undo_stack.pop()

            if self.pdf_document:
                self.pdf_document.close()

            self.pdf_document = fitz.open(
                stream=state["pdf_bytes"],
                filetype="pdf"
            )

            self.current_file_path = state["current_file_path"]
            self.current_page_index = state["current_page_index"]
            self.zoom = state["zoom"]
            self.page_text_items = copy.deepcopy(state["page_text_items"])
            self.page_image_items = copy.deepcopy(state.get("page_image_items", {}))

            if self.current_page_index >= len(self.pdf_document):
                self.current_page_index = max(0, len(self.pdf_document) - 1)

            self.render_page()
            self.statusBar().showMessage("Undo completed")

        except Exception as error:
            QMessageBox.critical(
                self,
                "Undo Error",
                f"Could not undo last change:\n{error}"
            )

        finally:
            self.is_restoring_undo = False

    # -------------------------
    # File handling
    # -------------------------

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            "",
            "PDF Files (*.pdf)"
        )

        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):
        try:
            if self.pdf_document:
                self.save_current_page_text_items()
                self.pdf_document.close()

            self.pdf_document = fitz.open(file_path)
            self.current_file_path = file_path
            self.current_page_index = 0
            self.page_text_items = {}
            self.page_image_items = {}

            self.render_page()
            self.statusBar().showMessage(f"Opened: {file_path}")

        except Exception as error:
            QMessageBox.critical(self, "Error", f"Could not open PDF:\n{error}")

    def close_pdf(self):
        if self.pdf_document:
            self.save_current_page_text_items()
            self.pdf_document.close()
            self.pdf_document = None

        self.current_file_path = None
        self.current_page_index = 0
        self.page_text_items = {}
        self.page_image_items = {}

        self.pdf_view.scene().clear()
        self.statusBar().showMessage("PDF closed")

    def save_pdf(self):
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF", "No PDF is currently open.")
            return

        if not self.current_file_path:
            self.save_pdf_as()
            return

        try:
            self.apply_text_items_to_pdf()

            try:
                self.pdf_document.saveIncr()
            except Exception:
                temp_dir = os.path.dirname(self.current_file_path)

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf",
                    dir=temp_dir
                ) as temp_file:
                    temp_path = temp_file.name

                self.pdf_document.save(temp_path)
                self.pdf_document.close()

                os.replace(temp_path, self.current_file_path)

                self.pdf_document = fitz.open(self.current_file_path)

            self.render_page()
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
            self.apply_text_items_to_pdf()
            self.pdf_document.save(file_path)
            self.current_file_path = file_path

            self.pdf_document.close()
            self.pdf_document = fitz.open(file_path)

            self.render_page()
            self.statusBar().showMessage(f"Saved As: {file_path}")

        except Exception as error:
            QMessageBox.critical(self, "Save As Error", f"Could not save PDF:\n{error}")

    # -------------------------
    # Rendering
    # -------------------------

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

        scene = self.pdf_view.scene()
        scene.clear()

        self.pdf_view.page_pixmap_item = QGraphicsPixmapItem(qt_pixmap)
        self.pdf_view.page_pixmap_item.setZValue(0)
        scene.addItem(self.pdf_view.page_pixmap_item)

        scene.setSceneRect(0, 0, qt_pixmap.width(), qt_pixmap.height())

        self.restore_text_items_for_current_page()

        page_count = len(self.pdf_document)
        self.statusBar().showMessage(
            f"Page {self.current_page_index + 1} / {page_count} | Zoom {int(self.zoom * 100)}%"
        )

    def next_page(self):
        if not self.pdf_document:
            return

        if self.current_page_index < len(self.pdf_document) - 1:
            self.save_current_page_text_items()
            self.current_page_index += 1
            self.render_page()

    def previous_page(self):
        if not self.pdf_document:
            return

        if self.current_page_index > 0:
            self.save_current_page_text_items()
            self.current_page_index -= 1
            self.render_page()

    def zoom_in(self):
        if not self.pdf_document:
            return

        self.save_current_page_text_items()
        self.zoom += 0.25
        self.render_page()

    def zoom_out(self):
        if not self.pdf_document:
            return

        if self.zoom > 0.5:
            self.save_current_page_text_items()
            self.zoom -= 0.25
            self.render_page()

    # -------------------------
    # Edit PDF - Add Text
    # -------------------------

    def add_text_item(self):
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF", "No PDF is currently open.")
            return

        text, ok = QInputDialog.getText(
            self,
            "Add Text",
            "Enter text:"
        )

        if not ok or not text.strip():
            return

        font_size, ok = QInputDialog.getInt(
            self,
            "Font Size",
            "Enter font size:",
            14,
            6,
            72
        )

        if not ok:
            return

        color = QColorDialog.getColor(
            QColor(0, 0, 0),
            self,
            "Select Text Color"
        )

        if not color.isValid():
            return

        self.push_undo_state()

        text_item = PdfTextItem(
            text,
            font_size,
            self.zoom,
            self,
            color
        )

        text_item.setPos(100, 100)

        self.pdf_view.scene().addItem(text_item)
        text_item.setSelected(True)

        self.statusBar().showMessage(
            "Text added. Drag it with mouse, double-click to edit, press Delete to remove."
        )

    def save_current_page_text_items(self):
        if not self.pdf_document:
            return

        scene = self.pdf_view.scene()
        text_items_for_page = []
        image_items_for_page = []

        for item in scene.items():
            if isinstance(item, PdfTextItem):
                text = item.toPlainText().strip()

                if not text:
                    continue

                position = item.scenePos()
                rect = item.boundingRect()

                text_color = item.text_color

                text_items_for_page.append(
                    {
                        "text": text,
                        "x": position.x() / self.zoom,
                        "y": position.y() / self.zoom,
                        "width": rect.width() / self.zoom,
                        "height": rect.height() / self.zoom,
                        "font_size": item.pdf_font_size,
                        "color": (
                            text_color.red(),
                            text_color.green(),
                            text_color.blue(),
                        ),
                    }
                )

            elif isinstance(item, PdfImageItem):
                position = item.scenePos()
                pixmap = item.pixmap()

                image_items_for_page.append(
                    {
                        "image_path": item.image_path,
                        "x": position.x() / self.zoom,
                        "y": position.y() / self.zoom,
                        "width": (pixmap.width() * item.scale()) / self.zoom,
                        "height": (pixmap.height() * item.scale()) / self.zoom,
                        "scale": item.scale(),
                    }
                )

        self.page_text_items[self.current_page_index] = text_items_for_page
        self.page_image_items[self.current_page_index] = image_items_for_page

    def restore_text_items_for_current_page(self):
        text_items_for_page = self.page_text_items.get(self.current_page_index, [])

        for item_data in text_items_for_page:
            color_data = item_data.get("color", (0, 0, 0))
            color = QColor(color_data[0], color_data[1], color_data[2])

            text_item = PdfTextItem(
                item_data["text"],
                item_data["font_size"],
                self.zoom,
                self,
                color
            )

            text_item.setPos(
                item_data["x"] * self.zoom,
                item_data["y"] * self.zoom
            )

            self.pdf_view.scene().addItem(text_item)

        image_items_for_page = self.page_image_items.get(self.current_page_index, [])

        for item_data in image_items_for_page:
            image_item = PdfImageItem(
                item_data["image_path"],
                self.zoom,
                self
            )

            image_item.setPos(
                item_data["x"] * self.zoom,
                item_data["y"] * self.zoom
            )

            image_item.setScale(item_data.get("scale", 1.0))

            self.pdf_view.scene().addItem(image_item)

    def apply_text_items_to_pdf(self):
        if not self.pdf_document:
            return

        self.save_current_page_text_items()

        for page_index, text_items in self.page_text_items.items():
            if page_index < 0 or page_index >= len(self.pdf_document):
                continue

            page = self.pdf_document[page_index]

            for item_data in text_items:
                text = item_data["text"].strip()

                if not text:
                    continue

                x = item_data["x"]
                y = item_data["y"]
                width = max(item_data["width"], 50)
                height = max(item_data["height"], item_data["font_size"] * 2)

                rect = fitz.Rect(
                    x,
                    y,
                    x + width,
                    y + height
                )

                color_data = item_data.get("color", (0, 0, 0))

                pdf_color = (
                    color_data[0] / 255,
                    color_data[1] / 255,
                    color_data[2] / 255,
                )

                page.insert_textbox(
                    rect,
                    text,
                    fontsize=item_data["font_size"],
                    color=pdf_color
                )

        for page_index, image_items in self.page_image_items.items():
            if page_index < 0 or page_index >= len(self.pdf_document):
                continue

            page = self.pdf_document[page_index]

            for item_data in image_items:
                image_path = item_data["image_path"]

                x = item_data["x"]
                y = item_data["y"]
                width = max(item_data["width"], 1)
                height = max(item_data["height"], 1)

                rect = fitz.Rect(
                    x,
                    y,
                    x + width,
                    y + height
                )

                page.insert_image(
                    rect,
                    filename=image_path
                )

        self.page_text_items = {}
        self.page_image_items = {}

    # -------------------------
    # Pages tools
    # -------------------------

    def parse_page_range(self, text):
        if not self.pdf_document:
            return []

        page_count = len(self.pdf_document)
        text = text.strip().lower()

        if text == "all":
            return list(range(page_count))

        pages = set()
        parts = text.split(",")

        for part in parts:
            part = part.strip()

            if not part:
                continue

            if "-" in part:
                start_text, end_text = part.split("-", 1)

                if not start_text.strip().isdigit() or not end_text.strip().isdigit():
                    raise ValueError("Invalid page range.")

                start = int(start_text.strip())
                end = int(end_text.strip())

                if start > end:
                    raise ValueError("Start page cannot be greater than end page.")

                for page_number in range(start, end + 1):
                    if page_number < 1 or page_number > page_count:
                        raise ValueError("Page number out of range.")

                    pages.add(page_number - 1)

            else:
                if not part.isdigit():
                    raise ValueError("Invalid page number.")

                page_number = int(part)

                if page_number < 1 or page_number > page_count:
                    raise ValueError("Page number out of range.")

                pages.add(page_number - 1)

        return sorted(pages)

    def rotate_pages(self):
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF", "No PDF is currently open.")
            return

        page_range, ok = QInputDialog.getText(
            self,
            "Rotate Pages",
            "Pages to rotate: example 1,3-5 or all"
        )

        if not ok or not page_range.strip():
            return

        rotation_options = ["90", "180", "270"]

        rotation_text, ok = QInputDialog.getItem(
            self,
            "Rotation",
            "Select rotation:",
            rotation_options,
            0,
            False
        )

        if not ok:
            return

        try:
            self.save_current_page_text_items()

            pages = self.parse_page_range(page_range)
            rotation = int(rotation_text)

            self.push_undo_state()

            for page_index in pages:
                page = self.pdf_document[page_index]
                new_rotation = (page.rotation + rotation) % 360
                page.set_rotation(new_rotation)

            self.render_page()
            self.statusBar().showMessage(f"Rotated {len(pages)} page(s) by {rotation} degrees")

        except Exception as error:
            QMessageBox.critical(self, "Rotate Error", f"Could not rotate pages:\n{error}")


    def delete_pages(self):
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF", "No PDF is currently open.")
            return

        if len(self.pdf_document) <= 1:
            QMessageBox.warning(self, "Delete Pages", "Cannot delete pages from a PDF with only one page.")
            return

        page_range, ok = QInputDialog.getText(
            self,
            "Delete Pages",
            "Pages to delete: example 1,3-5"
        )

        if not ok or not page_range.strip():
            return

        try:
            self.save_current_page_text_items()

            pages = self.parse_page_range(page_range)

            if len(pages) >= len(self.pdf_document):
                QMessageBox.warning(self, "Delete Pages", "Cannot delete all pages.")
                return

            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Delete {len(pages)} page(s)?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                return

            self.push_undo_state()

            for page_index in sorted(pages, reverse=True):
                self.pdf_document.delete_page(page_index)

            self.rebuild_text_items_after_delete(pages)
            self.rebuild_image_items_after_delete(pages)

            if self.current_page_index >= len(self.pdf_document):
                self.current_page_index = len(self.pdf_document) - 1

            self.render_page()
            self.statusBar().showMessage(f"Deleted {len(pages)} page(s)")

        except Exception as error:
            QMessageBox.critical(self, "Delete Error", f"Could not delete pages:\n{error}")


    def rebuild_text_items_after_delete(self, deleted_pages):
        deleted_pages = set(deleted_pages)
        new_page_text_items = {}

        for old_index, items in self.page_text_items.items():
            if old_index in deleted_pages:
                continue

            shift = sum(1 for deleted_index in deleted_pages if deleted_index < old_index)
            new_index = old_index - shift
            new_page_text_items[new_index] = items

        self.page_text_items = new_page_text_items

    def rebuild_image_items_after_delete(self, deleted_pages):
        deleted_pages = set(deleted_pages)
        new_page_image_items = {}

        for old_index, items in self.page_image_items.items():
            if old_index in deleted_pages:
                continue

            shift = sum(1 for deleted_index in deleted_pages if deleted_index < old_index)
            new_index = old_index - shift
            new_page_image_items[new_index] = items

        self.page_image_items = new_page_image_items

    def extract_pages(self):
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF", "No PDF is currently open.")
            return

        page_range, ok = QInputDialog.getText(
            self,
            "Extract Pages",
            "Pages to extract: example 1,3-5 or all"
        )

        if not ok or not page_range.strip():
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Extracted Pages As",
            "",
            "PDF Files (*.pdf)"
        )

        if not output_path:
            return

        if not output_path.lower().endswith(".pdf"):
            output_path += ".pdf"

        try:
            self.save_current_page_text_items()

            pages = self.parse_page_range(page_range)

            if not pages:
                QMessageBox.warning(self, "Extract Pages", "No pages selected.")
                return

            new_document = fitz.open()

            for page_index in pages:
                new_document.insert_pdf(
                    self.pdf_document,
                    from_page=page_index,
                    to_page=page_index
                )

            new_document.save(output_path)
            new_document.close()

            self.statusBar().showMessage(f"Extracted {len(pages)} page(s) to: {output_path}")

        except Exception as error:
            QMessageBox.critical(self, "Extract Error", f"Could not extract pages:\n{error}")


    def reorder_pages(self):
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF", "No PDF is currently open.")
            return

        page_count = len(self.pdf_document)

        order_text, ok = QInputDialog.getText(
            self,
            "Reorder Pages",
            f"Enter new page order.\n\n"
            f"Example for {page_count} pages: 3,1,2\n\n"
            f"You must use every page exactly once."
        )

        if not ok or not order_text.strip():
            return

        try:
            self.save_current_page_text_items()

            parts = order_text.split(",")
            new_order = []

            for part in parts:
                part = part.strip()

                if not part.isdigit():
                    raise ValueError("Only page numbers separated by commas are allowed.")

                page_number = int(part)

                if page_number < 1 or page_number > page_count:
                    raise ValueError(f"Page number {page_number} is out of range.")

                new_order.append(page_number - 1)

            if len(new_order) != page_count:
                raise ValueError(f"You must enter exactly {page_count} page numbers.")

            if len(set(new_order)) != page_count:
                raise ValueError("Each page can be used only once. Duplicate pages are not allowed.")

            reply = QMessageBox.question(
                self,
                "Confirm Reorder",
                "Reorder pages now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                return

            self.push_undo_state()

            self.pdf_document.select(new_order)

            reordered_text_items = {}

            for new_index, old_index in enumerate(new_order):
                if old_index in self.page_text_items:
                    reordered_text_items[new_index] = self.page_text_items[old_index]

            self.page_text_items = reordered_text_items

            reordered_image_items = {}

            for new_index, old_index in enumerate(new_order):
                if old_index in self.page_image_items:
                    reordered_image_items[new_index] = self.page_image_items[old_index]

            self.page_image_items = reordered_image_items


            self.current_page_index = 0
            self.render_page()

            self.statusBar().showMessage("Pages reordered successfully")

        except Exception as error:
            QMessageBox.critical(
                self,
                "Reorder Error",
                f"Could not reorder pages:\n{error}"
            )

    def merge_pdfs(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDFs to Merge - select at least 2 PDF files",
            "",
            "PDF Files (*.pdf)"
        )

        if not file_paths:
            return

        if len(file_paths) < 2:
            QMessageBox.warning(
                self,
                "Merge PDFs",
                "Please select at least 2 PDF files to merge.\n\n"
                "Tip: Hold Ctrl and click multiple PDF files."
            )
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged PDF As",
            "",
            "PDF Files (*.pdf)"
        )

        if not output_path:
            return

        if not output_path.lower().endswith(".pdf"):
            output_path += ".pdf"

        if output_path in file_paths:
            QMessageBox.warning(
                self,
                "Merge PDFs",
                "Do not save the merged PDF over one of the source files.\n"
                "Choose a new file name, for example merged.pdf."
            )
            return

        try:
            merged_document = fitz.open()

            for file_path in file_paths:
                source_document = fitz.open(file_path)
                merged_document.insert_pdf(source_document)
                source_document.close()

            merged_document.save(output_path)
            merged_document.close()

            self.statusBar().showMessage(
                f"Merged {len(file_paths)} PDF file(s) to: {output_path}"
            )

            reply = QMessageBox.question(
                self,
                "Open Merged PDF",
                "Merged PDF was created. Do you want to open it now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                self.load_pdf(output_path)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Merge Error",
                f"Could not merge PDFs:\n{error}"
            )

    def split_pdf(self):
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF", "No PDF is currently open.")
            return

        output_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder"
        )

        if not output_folder:
            return

        try:
            self.save_current_page_text_items()

            page_count = len(self.pdf_document)

            for page_index in range(page_count):
                new_document = fitz.open()

                new_document.insert_pdf(
                    self.pdf_document,
                    from_page=page_index,
                    to_page=page_index
                )

                output_path = f"{output_folder}/page_{page_index + 1}.pdf"

                new_document.save(output_path)
                new_document.close()

            self.statusBar().showMessage(f"Split PDF into {page_count} file(s)")

        except Exception as error:
            QMessageBox.critical(self, "Split Error", f"Could not split PDF:\n{error}")


    def add_image_item(self):
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF", "No PDF is currently open.")
            return

        image_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg)"
        )

        if not image_path:
            return

        self.push_undo_state()

        image_item = PdfImageItem(image_path, self.zoom, self)
        image_item.setPos(100, 100)

        self.pdf_view.scene().addItem(image_item)
        image_item.setSelected(True)

        self.statusBar().showMessage(
            "Image added. Drag it to move, use bottom-right handle to resize, press Delete to remove."
        )

    # -------------------------
    # Help
    # -------------------------

    def show_about_dialog(self):
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"""
            <h2>{APP_NAME}</h2>
            <p><b>Version: </b> {APP_VERSION}</p>
            <p><b>Created by: </b> {APP_AUTHOR}</p>
            <p>Desktop PDF editor and toolkit built with Python, PySide6 and PyMuPDF. </p>
            """
        )