"""
PDF Handler Module
Handles PDF splitting and processing
"""
import logging
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image
import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PDFHandler:
    """Handles PDF splitting and thumbnail generation"""
    
    def __init__(self, pdf_path, output_folder=None):
        """
        Initialize PDF Handler
        
        Args:
            pdf_path: Path to the PDF file to process
            output_folder: Folder where split PDFs will be saved
        """
        self.pdf_path = Path(pdf_path)
        self.output_folder = Path(output_folder) if output_folder else config.OUTPUT_FOLDER
        self.output_folder.mkdir(exist_ok=True)
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        self.split_pdfs = []
        self.thumbnails = []
    
    def get_page_count(self):
        """Get the number of pages in the PDF"""
        try:
            reader = PdfReader(str(self.pdf_path))
            return len(reader.pages)
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            raise
    
    def split_pdf(self, prefix=None):
        """
        Split PDF into individual pages
        
        Args:
            prefix: Prefix for output filenames
            
        Returns:
            List of paths to split PDF files
        """
        if prefix is None:
            prefix = config.PDF_PREFIX
        
        logger.info(f"Splitting PDF: {self.pdf_path}")
        
        try:
            reader = PdfReader(str(self.pdf_path))
            total_pages = len(reader.pages)
            
            logger.info(f"PDF has {total_pages} pages")
            
            self.split_pdfs = []
            
            for page_num in range(total_pages):
                # Create a writer for this page
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])
                
                # Generate output filename
                output_filename = f"{prefix}_{page_num + 1}.pdf"
                output_path = self.output_folder / output_filename
                
                # Write the page to a new PDF
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                self.split_pdfs.append(output_path)
                logger.info(f"Created: {output_filename}")
            
            logger.info(f"Successfully split PDF into {total_pages} pages")
            return self.split_pdfs
            
        except Exception as e:
            logger.error(f"Error splitting PDF: {e}")
            raise
    
    def generate_thumbnails(self, dpi=150):
        """
        Generate thumbnail images for each split PDF
        
        Args:
            dpi: DPI for rendering thumbnails
            
        Returns:
            List of paths to thumbnail images
        """
        logger.info("Generating thumbnails...")
        
        self.thumbnails = []
        
        try:
            for pdf_path in self.split_pdfs:
                # Convert PDF page to image
                images = convert_from_path(str(pdf_path), dpi=dpi)
                
                if images:
                    image = images[0]  # First (and only) page
                    
                    # Resize to thumbnail size
                    image.thumbnail(config.PDF_THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                    
                    # Save thumbnail
                    thumbnail_path = pdf_path.with_suffix('.png')
                    image.save(thumbnail_path, 'PNG')
                    
                    self.thumbnails.append(thumbnail_path)
                    logger.debug(f"Created thumbnail: {thumbnail_path.name}")
            
            logger.info(f"Generated {len(self.thumbnails)} thumbnails")
            return self.thumbnails
            
        except Exception as e:
            logger.error(f"Error generating thumbnails: {e}")
            logger.warning("Continuing without thumbnails...")
            return []
    
    def get_pdf_info(self):
        """
        Get information about the PDF
        
        Returns:
            Dictionary with PDF information
        """
        try:
            reader = PdfReader(str(self.pdf_path))
            
            info = {
                'filename': self.pdf_path.name,
                'path': str(self.pdf_path),
                'pages': len(reader.pages),
                'size_mb': self.pdf_path.stat().st_size / (1024 * 1024)
            }
            
            # Try to get metadata
            if reader.metadata:
                info['title'] = reader.metadata.get('/Title', 'N/A')
                info['author'] = reader.metadata.get('/Author', 'N/A')
                info['creation_date'] = reader.metadata.get('/CreationDate', 'N/A')
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting PDF info: {e}")
            return {'error': str(e)}
    
    def cleanup_split_pdfs(self):
        """Delete all split PDF files"""
        logger.info("Cleaning up split PDFs...")
        
        for pdf_path in self.split_pdfs:
            try:
                if pdf_path.exists():
                    pdf_path.unlink()
                    logger.debug(f"Deleted: {pdf_path.name}")
            except Exception as e:
                logger.warning(f"Could not delete {pdf_path}: {e}")
        
        self.split_pdfs = []
    
    def cleanup_thumbnails(self):
        """Delete all thumbnail images"""
        logger.info("Cleaning up thumbnails...")
        
        for thumb_path in self.thumbnails:
            try:
                if thumb_path.exists():
                    thumb_path.unlink()
                    logger.debug(f"Deleted: {thumb_path.name}")
            except Exception as e:
                logger.warning(f"Could not delete {thumb_path}: {e}")
        
        self.thumbnails = []
    
    def cleanup_all(self):
        """Delete all generated files"""
        self.cleanup_split_pdfs()
        self.cleanup_thumbnails()


def split_pdf_file(pdf_path, output_folder=None, generate_thumbs=True):
    """
    Convenience function to split a PDF file
    
    Args:
        pdf_path: Path to PDF file
        output_folder: Output folder for split PDFs
        generate_thumbs: Whether to generate thumbnails
        
    Returns:
        Tuple of (split_pdf_paths, thumbnail_paths)
    """
    handler = PDFHandler(pdf_path, output_folder)
    split_pdfs = handler.split_pdf()
    
    thumbnails = []
    if generate_thumbs:
        try:
            thumbnails = handler.generate_thumbnails()
        except Exception as e:
            logger.warning(f"Could not generate thumbnails: {e}")
    
    return split_pdfs, thumbnails


if __name__ == "__main__":
    # Test the PDF handler
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_handler.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    try:
        handler = PDFHandler(pdf_file)
        info = handler.get_pdf_info()
        print(f"PDF Info: {info}")
        
        split_pdfs = handler.split_pdf()
        print(f"Split into {len(split_pdfs)} files")
        
        thumbnails = handler.generate_thumbnails()
        print(f"Generated {len(thumbnails)} thumbnails")
        
        print("\nSplit PDFs:")
        for pdf in split_pdfs:
            print(f"  - {pdf}")
        
    except Exception as e:
        print(f"Error: {e}")

