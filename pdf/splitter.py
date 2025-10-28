"""
PDF Splitter - Single responsibility: Split PDF into pages
"""
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from utils.logger import get_logger

logger = get_logger(__name__)


class PDFSplitter:
    """Split PDF files into individual pages"""
    
    def __init__(self, pdf_path, output_folder):
        """
        Initialize splitter
        
        Args:
            pdf_path: Path to PDF file
            output_folder: Folder for output files
        """
        self.pdf_path = Path(pdf_path)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    def get_page_count(self):
        """Get number of pages in PDF"""
        reader = PdfReader(str(self.pdf_path))
        return len(reader.pages)
    
    def split(self, prefix="page"):
        """
        Split PDF into individual pages
        
        Args:
            prefix: Filename prefix for output files
            
        Returns:
            list: Paths to created PDF files
        """
        logger.info(f"Splitting PDF: {self.pdf_path}")
        
        reader = PdfReader(str(self.pdf_path))
        output_files = []
        
        for page_num, page in enumerate(reader.pages, 1):
            writer = PdfWriter()
            writer.add_page(page)
            
            output_file = self.output_folder / f"{prefix}_{page_num}.pdf"
            
            with open(output_file, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_file)
            logger.debug(f"Created: {output_file.name}")
        
        logger.info(f"Split into {len(output_files)} pages")
        return output_files
    
    def get_metadata(self):
        """Get PDF metadata"""
        reader = PdfReader(str(self.pdf_path))
        
        metadata = {
            'filename': self.pdf_path.name,
            'pages': len(reader.pages),
            'size_mb': self.pdf_path.stat().st_size / (1024 * 1024)
        }
        
        if reader.metadata:
            metadata['title'] = reader.metadata.get('/Title', 'N/A')
            metadata['author'] = reader.metadata.get('/Author', 'N/A')
        
        return metadata

