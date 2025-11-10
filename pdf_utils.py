# pdf_utils.py
from PyPDF2 import PdfReader, PdfWriter

def remove_pages(input_path: str, output_path: str, pages_to_remove: list):
    """
    Remove pages (0-based indices) from input PDF and write to output_path.
    pages_to_remove: e.g., [0,2] removes first and third page.
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()
    total = len(reader.pages)
    remove_set = set(pages_to_remove)
    for i in range(total):
        if i in remove_set:
            continue
        writer.add_page(reader.pages[i])
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path

def extract_pages(input_path: str, output_path: str, pages_to_keep: list):
    """
    Keep only the pages listed (0-based).
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()
    total = len(reader.pages)
    for i in pages_to_keep:
        if 0 <= i < total:
            writer.add_page(reader.pages[i])
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path

def rotate_page(input_path: str, output_path: str, page_index: int, rotation: int):
    """
    Rotate a specific page by rotation degrees (90/180/270).
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()
    total = len(reader.pages)
    for i in range(total):
        p = reader.pages[i]
        if i == page_index:
            p.rotate(rotation)
        writer.add_page(p)
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path
