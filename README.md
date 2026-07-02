# PDF Toolkit
A modern, open-source PDF toolkit built with Python and PySide6.
The goal of this project is to provide a fast, lightweight, and user-friendly alternative to bulky PDF software.

## Status: 🚧 Work in Progress

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
