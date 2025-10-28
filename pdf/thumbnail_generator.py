"""
Thumbnail Generator - Single responsibility: Create PDF thumbnails
"""
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
from utils.logger import get_logger

logger = get_logger(__name__)


class ThumbnailGenerator:
    """Generate thumbnail images from PDF files"""
    
    def __init__(self, size=(200, 280), dpi=150):
        """
        Initialize generator
        
        Args:
            size: Thumbnail size (width, height)
            dpi: Resolution for PDF rendering
        """
        self.size = size
        self.dpi = dpi
    
    def generate(self, pdf_files):
        """
        Generate thumbnails for PDF files
        
        Args:
            pdf_files: List of PDF file paths
            
        Returns:
            list: Paths to created thumbnail images
        """
        logger.info(f"Generating {len(pdf_files)} thumbnails...")
        
        thumbnails = []
        
        for pdf_path in pdf_files:
            try:
                thumbnail_path = self._create_thumbnail(Path(pdf_path))
                thumbnails.append(thumbnail_path)
            except Exception as e:
                logger.warning(f"Failed to create thumbnail for {pdf_path}: {e}")
        
        logger.info(f"Generated {len(thumbnails)} thumbnails")
        return thumbnails
    
    def _create_thumbnail(self, pdf_path):
        """Create thumbnail for single PDF"""
        images = convert_from_path(str(pdf_path), dpi=self.dpi)
        
        if not images:
            raise ValueError("No images generated from PDF")
        
        image = images[0]
        image.thumbnail(self.size, Image.Resampling.LANCZOS)
        
        thumbnail_path = pdf_path.with_suffix('.png')
        image.save(thumbnail_path, 'PNG')
        
        return thumbnail_path

