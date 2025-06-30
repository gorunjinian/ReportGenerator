"""
Main report generator class for Heritage Report Generator
"""

import os
import logging
from typing import Dict, Any, Optional

from data_loader import DataLoader
from image_handler import ImageHandler
from pdf_builder import PDFBuilder
from constants import *
from utils import safe_str, format_date
from exceptions import ReportGeneratorError

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Main class for generating heritage assessment reports"""
    
    def __init__(self, csv_path: str):
        """
        Initialize report generator
        
        Args:
            csv_path: Path to CSV file
        """
        self.csv_path = csv_path
        self.csv_dir = os.path.dirname(csv_path)
        
        # Initialize components
        self.data_loader = DataLoader(csv_path)
        self.image_handler = ImageHandler()
        self.pdf_builder = None
        
        # Data storage
        self.latest_data = None
        self.primary_images = []
        self.additional_images = []
        
    def generate_report(self, output_path: str) -> Dict[str, Any]:
        """
        Generate the complete report
        
        Args:
            output_path: Path for output PDF
            
        Returns:
            Dict[str, Any]: Report generation statistics
            
        Raises:
            ReportGeneratorError: If report generation fails
        """
        try:
            logger.info("Starting report generation")
            
            # Load and process data
            self._load_data()
            
            # Download images
            self._download_images()
            
            # Build PDF
            self._build_pdf(output_path)
            
            # Get statistics
            stats = self._get_statistics()
            
            logger.info("Report generation completed successfully")
            return stats
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise ReportGeneratorError(f"Failed to generate report: {str(e)}")
    
    def _load_data(self):
        """Load and validate CSV data"""
        logger.info("Loading CSV data")
        
        # Load data
        self.data_loader.load_data()
        
        # Get latest entry
        self.latest_data = self.data_loader.get_latest_entry()
        
        # Log some basic info
        date_value = self.latest_data.get('Date of Assessment', 'Unknown')
        logger.info(f"Processing assessment from: {date_value}")
    
    def _download_images(self):
        """Download images from Google Drive links"""
        logger.info("Downloading images")
        
        # Get image links
        primary_links = self.latest_data.get(PRIMARY_IMAGE_FIELD, '')
        additional_links = self.latest_data.get(ADDITIONAL_IMAGES_FIELD, '')
        
        # Download primary images
        if primary_links:
            self.primary_images = self.image_handler.process_image_links(
                primary_links, 
                "primary"
            )
        
        # Download additional images
        if additional_links:
            self.additional_images = self.image_handler.process_image_links(
                additional_links, 
                "additional"
            )
        
        # Log download results
        total_images = len(self.primary_images) + len(self.additional_images)
        logger.info(f"Downloaded {total_images} images total")
    
    def _build_pdf(self, output_path: str):
        """Build the PDF report"""
        logger.info("Building PDF report")
        
        # Initialize PDF builder
        self.pdf_builder = PDFBuilder(output_path)
        
        # Add header with logos
        self.pdf_builder.add_header_with_logos(self.csv_dir)
        
        # Add sections
        self._add_all_sections()
        
        # Generate PDF
        self.pdf_builder.generate()
    
    def _add_all_sections(self):
        """Add all sections to the PDF"""
        # Section 1: General Information
        self._add_section(
            "1. General Information",
            SECTION_FIELDS['general_info']
        )
        
        # Section 2: Location Information
        self._add_section(
            "2. Location Information",
            SECTION_FIELDS['location_info']
        )
        
        # Section 3: Preliminary Conditions
        self._add_section(
            "3. Preliminary Conditions",
            SECTION_FIELDS['preliminary_conditions']
        )
        
        # Section 4: Evidence of Conflict or Damage
        self._add_section(
            "4. Evidence of Conflict or Damage",
            SECTION_FIELDS['conflict_evidence']
        )
        
        # Section 5: Visible Damage
        self._add_section(
            "5. Visible Damage",
            SECTION_FIELDS['visible_damage']
        )
        
        # Section 6: Environmental Concerns
        self._add_section(
            "6. Environmental Concerns",
            SECTION_FIELDS['environmental_concerns']
        )
        
        # Section 7: Documentation and Evidence (with images)
        self._add_documentation_section()
        
        # Section 8: Risk Assessment
        self._add_section(
            "8. Risk Assessment",
            SECTION_FIELDS['risk_assessment']
        )
        
        # Section 9: Historical or Cultural Significance
        self._add_section(
            "9. Historical or Cultural Significance",
            SECTION_FIELDS['significance']
        )
    
    def _add_section(self, title: str, field_mappings: Dict[str, str]):
        """Add a standard section to the PDF"""
        section_data = {}
        
        for display_name, csv_field in field_mappings.items():
            value = self.latest_data.get(csv_field, '')
            
            # Special handling for date field
            if csv_field == 'Date of Assessment' and value:
                value = format_date(value, DATE_INPUT_FORMAT, DATE_OUTPUT_FORMAT)
            
            section_data[display_name] = safe_str(value)
        
        self.pdf_builder.add_section(title, section_data)
    
    def _add_documentation_section(self):
        """Add documentation section with text and images"""
        # First add text documentation
        section_data = {}
        for display_name, csv_field in SECTION_FIELDS['documentation'].items():
            value = self.latest_data.get(csv_field, '')
            section_data[display_name] = safe_str(value)
        
        if any(section_data.values()):
            self.pdf_builder.add_section("7. Documentation and Evidence", section_data)
        
        # Then add images
        self.pdf_builder.add_images_section(self.primary_images, self.additional_images)
    
    def _get_statistics(self) -> Dict[str, Any]:
        """Get report generation statistics"""
        image_stats = self.image_handler.get_download_stats()
        
        stats = {
            'csv_file': os.path.basename(self.csv_path),
            'assessment_date': self.latest_data.get('Date of Assessment', 'Unknown'),
            'monument_name': self.latest_data.get('Monument Name ', 'Unknown'),
            'primary_images': len(self.primary_images),
            'additional_images': len(self.additional_images),
            'total_images': image_stats['total_downloaded'],
            'total_image_size_mb': image_stats['total_size_mb']
        }
        
        return stats
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'image_handler'):
            self.image_handler.cleanup()
    
    def export_images(self, output_dir: str) -> bool:
        """
        Export downloaded images to a directory
        
        Args:
            output_dir: Directory to export images to
            
        Returns:
            bool: True if successful
        """
        try:
            monument_name = safe_str(
                self.latest_data.get('Monument Name ', 'unknown'), 
                'unknown'
            ).replace(' ', '_')
            
            self.image_handler.copy_to_output_dir(output_dir, monument_name)
            return True
            
        except Exception as e:
            logger.error(f"Error exporting images: {e}")
            return False
