# PDF Toolkit
A modern, open-source PDF toolkit built with Python and PySide6.
The goal of this project is to provide a fast, lightweight, and user-friendly alternative to bulky PDF software.

##Status: 🚧 Work in Progress

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
Download the "PDF-Toolkit"
Create a virtual environment:
```bash
python -m venv .venv

Activate it.
Windows:
```bash
.venv\Scripts\activate

Linux/macOS:
source .venv/bin/activate

Install dependencies:
```bash
pip install -r requirements.txt

Run the application:
```bash
python main.py