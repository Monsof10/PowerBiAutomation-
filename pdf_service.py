"""
PDF Service Facade - Simple interface for PDF operations
"""
from pdf.splitter import PDFSplitter
from pdf.thumbnail_generator import ThumbnailGenerator
import config


def split_pdf(pdf_path, output_folder=None, prefix="page", generate_thumbnails=True):
    """
    Split PDF into pages and generate thumbnails
    
    Args:
        pdf_path: Path to PDF file
        output_folder: Output folder (optional)
        prefix: Filename prefix
        generate_thumbnails: Whether to create thumbnails
        
    Returns:
        tuple: (pdf_files, thumbnail_files)
    """
    if output_folder is None:
        output_folder = config.OUTPUT_FOLDER
    
    # Split PDF
    splitter = PDFSplitter(pdf_path, output_folder)
    pdf_files = splitter.split(prefix)
    
    # Generate thumbnails
    thumbnails = []
    if generate_thumbnails:
        try:
            generator = ThumbnailGenerator(config.PDF_THUMBNAIL_SIZE)
            thumbnails = generator.generate(pdf_files)
        except Exception as e:
            print(f"Could not generate thumbnails: {e}")
    
    return pdf_files, thumbnails


def get_pdf_info(pdf_path):
    """Get PDF metadata"""
    splitter = PDFSplitter(pdf_path, config.OUTPUT_FOLDER)
    return splitter.get_metadata()

