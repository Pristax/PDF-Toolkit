# PDF Toolkit
A modern, open-source PDF toolkit built with Python and PySide6.
The goal of this project is to provide a fast, lightweight, and user-friendly alternative to bulky PDF software.

## Status: 🚧 Work in Progress

<img width="1919" height="1153" alt="image" src="https://github.com/user-attachments/assets/de3c18f3-c17b-47af-8255-1399ce234482" />


# Features (Planned)

## PDF Management
- Open PDF files
- Save edited PDFs
- Merge multiple PDFs
- Split PDF documents
- Rotate pages
- Delete pages
- Extract selected pages
- Reorder pages

## Editing
- Add text
- Add images
- Draw with a pen
- Highlight text
- Insert shapes
- Add signatures

## OCR
Convert scanned PDFs into searchable documents
Extract text from images

## Export
- PDF → Images
- Images → PDF

## Security
- Password protection
- Remove passwords (with permission)
- Remove metadata

## Changelog

### v0.5

Version 0.5 adds image editing support and improves text customization.

#### Added

- Added **Add Image** tool
- Support for adding `.png`, `.jpg` and `.jpeg` images to PDF pages
- Added movable image objects
- Added image resizing directly on the PDF page
- Added resize support from all image corners
- Added invisible resize zones instead of visible resize handles
- Added `Ctrl + mouse wheel` image resizing
- Added image deletion using the `Delete` key
- Added `Ctrl+Z` undo support for image actions
- Added text color selection for **Add Text**
- Text color is preserved when changing pages or zoom level
- Text color is saved into the final PDF

#### Improved

- Improved image resize behavior
- Removed the visible black resize square from image objects
- Improved image object selection and movement
- Improved Add Text workflow with color selection
- Improved undo handling for edit objects
- Improved saving of inserted text and images into PDF files

#### Refactor

- Added separate image object class:
  - `app/pdf_image_item.py`
- Extended editor object handling for both text and images
- Extended save/restore logic for editable page objects

### v0.4

Version 0.4 improves the PDF editing system and project structure.

#### Added

- Added editable text objects
- Added movable text objects on PDF pages
- Added double-click text editing
- Added text deletion using the `Delete` key
- Added `Ctrl+Z` undo support
- Added drag & drop PDF opening directly inside the PDF viewer
- Added separate editor view for PDF rendering and object editing
- Added separate text item class for editable PDF text objects

#### Improved

- Reworked the PDF viewer from `QLabel` / `QScrollArea` to `QGraphicsView` / `QGraphicsScene`
- Improved Add Text workflow
- Text can now be moved directly by dragging the text object
- Improved Save and Save As handling for inserted text
- Improved drag & drop behavior after switching to `QGraphicsView`
- Improved code organization by splitting the project into multiple files

#### Refactor

- Moved main window logic to `app/main_window.py`
- Added `app/pdf_editor_view.py`
- Added `app/pdf_text_item.py`
- Simplified `main.py` to only start the application

### v0.3

- Added Extract Pages
- Added Merge PDFs
- Added Split PDF
- Added Reorder Pages

### v0.2

- Added page range parser
- Added Rotate Pages
- Added Delete Pages

### v0.1

- Initial PySide6 app window
- Added menu bar and toolbar
- Added PDF opening
- Added drag & drop PDF opening
- Added PDF rendering
- Added page navigation
- Added zoom in / zoom out
- Added Save and Save As
- Added Close PDF
- Added status bar

# Technologies
- Python 3.11+
- PySide6
- PyMuPDF
- pypdf
- Pillow

# Installation

### 1. Download the project

Clone the repository:

```bash
git clone https://github.com/Pristax/PDF-Toolkit.git
cd PDF-Toolkit
```

Or download the project as a ZIP file from GitHub and extract it.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows:

```bash
.venv\Scripts\activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python main.py
```
