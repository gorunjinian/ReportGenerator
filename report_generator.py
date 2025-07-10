"""
Main report generator class for Heritage Report Generator
Enhanced with comprehensive multiple image support and detailed logging
"""

import os
import logging
from typing import Dict, Any, Optional

from data_loader import DataLoader
from image_handler import ImageHandler
from pdf_builder import PDFBuilder
from constants import *
from utils import safe_str, format_date, is_valid_image_url, parse_image_links
from exceptions import ReportGeneratorError

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Main class for generating heritage assessment reports with enhanced multiple image support"""

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
        Generate the complete report with enhanced error handling

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

            # Download images (only if valid links exist)
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

        if not self.latest_data:
            raise ReportGeneratorError("No data found in CSV file")

        # Log some basic info
        date_value = self.latest_data.get('Date of Assessment', 'Unknown')
        monument_name = self.latest_data.get('Monument Name ', 'Unknown')
        logger.info(f"Processing assessment from: {date_value} for monument: {monument_name}")

    def _download_images(self):
        """Download images from Google Drive links with enhanced null safety and detailed logging"""
        logger.info("Processing image links")

        # Get image links with null safety
        primary_links = self.latest_data.get(PRIMARY_IMAGE_FIELD, None)
        additional_links = self.latest_data.get(ADDITIONAL_IMAGES_FIELD, None)

        # Log what we found
        logger.info(f"Primary image field: {repr(primary_links[:100] if primary_links else None)}...")
        logger.info(f"Additional images field: {repr(additional_links[:100] if additional_links else None)}...")

        # Initialize empty lists
        self.primary_images = []
        self.additional_images = []

        # Parse and count links first
        from utils import parse_image_links
        primary_parsed = parse_image_links(safe_str(primary_links)) if primary_links else []
        additional_parsed = parse_image_links(safe_str(additional_links)) if additional_links else []

        total_links = len(primary_parsed) + len(additional_parsed)
        logger.info(f"Found {len(primary_parsed)} primary + {len(additional_parsed)} additional = {total_links} total image links")

        # Process primary images only if we have valid links
        if primary_parsed:
            logger.info(f"Processing {len(primary_parsed)} primary images...")
            try:
                self.primary_images = self.image_handler.process_image_links(
                    safe_str(primary_links),
                    "primary"
                )
                logger.info(f"Successfully downloaded {len(self.primary_images)}/{len(primary_parsed)} primary images")
            except Exception as e:
                logger.error(f"Error processing primary images: {e}")
                self.primary_images = []
        else:
            logger.info("No primary image links found")

        # Process additional images only if we have valid links
        if additional_parsed:
            logger.info(f"Processing {len(additional_parsed)} additional images...")
            try:
                self.additional_images = self.image_handler.process_image_links(
                    safe_str(additional_links),
                    "additional"
                )
                logger.info(f"Successfully downloaded {len(self.additional_images)}/{len(additional_parsed)} additional images")
            except Exception as e:
                logger.error(f"Error processing additional images: {e}")
                self.additional_images = []
        else:
            logger.info("No additional image links found")

        # Log final results with layout information
        total_downloaded = len(self.primary_images) + len(self.additional_images)
        rows_needed = (total_downloaded + 2) // 3 if total_downloaded > 0 else 0
        logger.info(f"Image processing complete: {total_downloaded}/{total_links} images downloaded")
        logger.info(f"PDF layout: {total_downloaded} images will use {rows_needed} rows (3 per row)")

        if total_downloaded != total_links:
            failed_count = total_links - total_downloaded
            logger.warning(f"{failed_count} images failed to download - check internet connection and link permissions")

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
        success = self.pdf_builder.generate()
        if not success:
            raise ReportGeneratorError("PDF generation failed")

    def _add_all_sections(self):
        """Add all sections to the PDF with enhanced error handling"""
        try:
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

        except Exception as e:
            logger.error(f"Error adding sections to PDF: {e}")
            raise ReportGeneratorError(f"Failed to add sections: {str(e)}")

    def _add_section(self, title: str, field_mappings: Dict[str, str]):
        """Add a standard section to the PDF with null safety"""
        try:
            section_data = {}

            for display_name, csv_field in field_mappings.items():
                value = self.latest_data.get(csv_field, None)

                # Special handling for date field
                if csv_field == 'Date of Assessment' and value:
                    try:
                        value = format_date(value, DATE_INPUT_FORMAT, DATE_OUTPUT_FORMAT)
                    except Exception as e:
                        logger.warning(f"Error formatting date: {e}")
                        value = safe_str(value)

                # Clean and store the value
                clean_value = safe_str(value)
                if clean_value:  # Only add non-empty values
                    section_data[display_name] = clean_value

            # Add section to PDF
            self.pdf_builder.add_section(title, section_data)

        except Exception as e:
            logger.error(f"Error adding section '{title}': {e}")
            # Add error placeholder
            self.pdf_builder.add_section(title, {"Error": f"Could not load section data: {str(e)}"})

    def _add_documentation_section(self):
        """Add documentation section with text and images"""
        try:
            # First add text documentation
            section_data = {}
            for display_name, csv_field in SECTION_FIELDS['documentation'].items():
                value = self.latest_data.get(csv_field, None)
                clean_value = safe_str(value)
                if clean_value:
                    section_data[display_name] = clean_value

            # Add text documentation if we have any
            if section_data:
                self.pdf_builder.add_section("7. Documentation and Evidence", section_data)

            # Then add images (this will handle the case where no images exist)
            self.pdf_builder.add_images_section(self.primary_images, self.additional_images)

        except Exception as e:
            logger.error(f"Error adding documentation section: {e}")
            # Add error placeholder
            self.pdf_builder.add_section(
                "7. Documentation and Evidence",
                {"Error": f"Could not load documentation: {str(e)}"}
            )

    def _get_statistics(self) -> Dict[str, Any]:
        """Get report generation statistics"""
        try:
            image_stats = self.image_handler.get_download_stats()

            stats = {
                'csv_file': os.path.basename(self.csv_path),
                'assessment_date': safe_str(self.latest_data.get('Date of Assessment', 'Unknown')),
                'monument_name': safe_str(self.latest_data.get('Monument Name ', 'Unknown')),
                'primary_images': len(self.primary_images),
                'additional_images': len(self.additional_images),
                'total_images': image_stats.get('total_downloaded', 0),
                'total_image_size_mb': image_stats.get('total_size_mb', 0.0)
            }

            return stats

        except Exception as e:
            logger.error(f"Error generating statistics: {e}")
            return {
                'csv_file': 'Unknown',
                'assessment_date': 'Unknown',
                'monument_name': 'Unknown',
                'primary_images': 0,
                'additional_images': 0,
                'total_images': 0,
                'total_image_size_mb': 0.0
            }

    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'image_handler'):
                self.image_handler.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

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