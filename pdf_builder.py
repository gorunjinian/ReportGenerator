"""
BALANCED PDF building module for Heritage Report Generator
Moderate logo sizing with compact header layout
"""

import os
import logging
from typing import List, Dict, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from constants import *
from utils import safe_str, format_date
from exceptions import PDFGenerationError

logger = logging.getLogger(__name__)


class PDFBuilder:
    """Balanced PDF generator with moderate logo sizing and compact layout"""

    def __init__(self, output_path: str):
        """Initialize PDF builder"""
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        self.story = []

    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Section title style
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=SECTION_TITLE_SIZE,
            textColor=colors.HexColor(SECTION_TITLE_COLOR),
            spaceAfter=6,
            spaceBefore=8,
            alignment=TA_LEFT
        ))

        # Field label style
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=FIELD_LABEL_SIZE,
            textColor=colors.HexColor(FIELD_LABEL_COLOR),
            fontName=BOLD_FONT,
            spaceAfter=2,
            alignment=TA_LEFT
        ))

        # Field value style
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=FIELD_VALUE_SIZE,
            textColor=colors.HexColor(FIELD_VALUE_COLOR),
            spaceAfter=3,
            alignment=TA_LEFT
        ))

        # Compact field style for two-column layout
        self.styles.add(ParagraphStyle(
            name='CompactField',
            parent=self.styles['Normal'],
            fontSize=FIELD_VALUE_SIZE - 1,
            textColor=colors.HexColor(FIELD_VALUE_COLOR),
            spaceAfter=2,
            leftIndent=0,
            alignment=TA_LEFT
        ))

    def _calculate_logo_dimensions(self, logo_path: str, is_biladi: bool = False) -> tuple:
        """
        Calculate logo dimensions with BALANCED sizing

        Args:
            logo_path: Path to logo file
            is_biladi: True if this is the Biladi logo (gets moderate size boost)

        Returns:
            tuple: (width, height) in ReportLab units
        """
        try:
            from PIL import Image as PILImage

            with PILImage.open(logo_path) as img:
                original_width, original_height = img.size

                if original_width <= 0 or original_height <= 0:
                    return (1.5*inch, 0.8*inch)

                # Calculate aspect ratio
                aspect_ratio = original_width / original_height

                if is_biladi:
                    # Biladi logo: Moderately larger (2.5x) for good visual balance
                    base_height = 0.6 * inch  # Smaller base
                    multiplier = 2.5  # Moderate multiplier instead of 10x
                    new_height = base_height * multiplier
                    new_width = new_height * aspect_ratio

                    # Reasonable constraints for Biladi
                    max_width_biladi = 3.5 * inch  # Reduced from 8.0
                    max_height_biladi = 1.8 * inch  # Reduced from 4.0

                    if new_width > max_width_biladi:
                        new_width = max_width_biladi
                        new_height = new_width / aspect_ratio
                    if new_height > max_height_biladi:
                        new_height = max_height_biladi
                        new_width = new_height * aspect_ratio

                else:
                    # CER logo: Keep good size
                    base_height = 0.85 * inch  # Slightly smaller than before
                    new_height = base_height
                    new_width = new_height * aspect_ratio

                    # Standard constraints for CER
                    max_width_cer = 2.5 * inch
                    max_height_cer = 1.0 * inch

                    if new_width > max_width_cer:
                        new_width = max_width_cer
                        new_height = new_width / aspect_ratio
                    if new_height > max_height_cer:
                        new_height = max_height_cer
                        new_width = new_height * aspect_ratio

                actual_area = (new_width * new_height) / (inch * inch)
                logo_type = "Biladi (2.5x)" if is_biladi else "CER (standard)"
                logger.debug(f"Logo {os.path.basename(logo_path)} [{logo_type}]: {original_width}x{original_height} -> {new_width/inch:.2f}x{new_height/inch:.2f} in (area: {actual_area:.2f} sq in)")
                return (new_width, new_height)

        except Exception as e:
            logger.warning(f"Could not calculate dimensions for {logo_path}: {e}")
            return (1.5*inch, 0.8*inch)

    def add_header_with_logos(self, csv_dir: str):
        """Add compact header with balanced logo sizing"""
        try:
            # Check for logo files
            biladi_logo_path = os.path.join(csv_dir, BILADI_LOGO_FILENAME)
            cer_logo_path = os.path.join(csv_dir, CER_LOGO_FILENAME)

            header_data = []

            # Try to load logos with balanced sizing
            if os.path.exists(biladi_logo_path) and os.path.exists(cer_logo_path):
                try:
                    # Calculate dimensions with balanced approach
                    biladi_width, biladi_height = self._calculate_logo_dimensions(biladi_logo_path, is_biladi=True)
                    cer_width, cer_height = self._calculate_logo_dimensions(cer_logo_path, is_biladi=False)

                    # Create logos with calculated dimensions
                    biladi_logo = Image(biladi_logo_path, width=biladi_width, height=biladi_height)
                    cer_logo = Image(cer_logo_path, width=cer_width, height=cer_height)

                    header_data = [[biladi_logo, '', cer_logo]]

                    # Log detailed sizing info
                    biladi_area = (biladi_width * biladi_height) / (inch * inch)
                    cer_area = (cer_width * cer_height) / (inch * inch)
                    size_multiplier = biladi_area / cer_area if cer_area > 0 else 0

                    logger.info(f"Balanced logo sizing:")
                    logger.info(f"  Biladi: {biladi_width/inch:.2f}×{biladi_height/inch:.2f} in (area: {biladi_area:.2f} sq in)")
                    logger.info(f"  CER:    {cer_width/inch:.2f}×{cer_height/inch:.2f} in (area: {cer_area:.2f} sq in)")
                    logger.info(f"  Biladi is {size_multiplier:.1f}x larger than CER")

                except Exception as logo_e:
                    logger.warning(f"Could not load logo images: {logo_e}")
                    # Fallback to text
                    header_data = [[
                        Paragraph("BILADI", self.styles['Normal']),
                        '',
                        Paragraph("CER", self.styles['Normal'])
                    ]]
            else:
                # Text placeholders
                header_data = [[
                    Paragraph("BILADI", self.styles['Normal']),
                    '',
                    Paragraph("CER", self.styles['Normal'])
                ]]
                logger.info("Using text placeholders for logos")
                if not os.path.exists(biladi_logo_path):
                    logger.warning(f"Biladi logo not found: {biladi_logo_path}")
                if not os.path.exists(cer_logo_path):
                    logger.warning(f"CER logo not found: {cer_logo_path}")

            # Create header table with balanced column widths
            if header_data:
                # Balanced column widths for moderate logo sizes
                biladi_col_width = 3.0 * inch  # Reduced from 4.5
                middle_col_width = 0.5 * inch  # Small spacer
                cer_col_width = 2.5 * inch     # Standard size

                header_table = Table(header_data, colWidths=[biladi_col_width, middle_col_width, cer_col_width])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),    # Reduced padding
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2), # Reduced padding
                ]))
                self.story.append(header_table)

            # MUCH smaller spacing after logos
            self.story.append(Spacer(1, 6))  # Reduced from 12

            # Add report title
            title = Paragraph(REPORT_TITLE, self.styles['Title'])
            self.story.append(title)

            # Smaller spacing after title
            self.story.append(Spacer(1, 10))  # Reduced from 18

        except Exception as e:
            logger.error(f"Error adding header: {e}")
            # Simple fallback
            title = Paragraph("Heritage Site Assessment Report", self.styles['Title'])
            self.story.append(title)
            self.story.append(Spacer(1, 10))

    def add_section(self, title: str, fields_dict: Dict[str, str]):
        """Add section with 2-column layout and section divider line"""
        try:
            # Add section title
            section_title = Paragraph(title, self.styles['SectionTitle'])
            self.story.append(section_title)
            self.story.append(Spacer(1, 6))

            # Filter populated fields
            populated_fields = []
            for label, value in fields_dict.items():
                if value is not None and str(value).strip():
                    clean_label = safe_str(label, 'Unknown Field')
                    clean_value = safe_str(value, '')
                    if clean_value:
                        populated_fields.append((clean_label, clean_value))

            if not populated_fields:
                no_data = Paragraph("(No data available)", self.styles['FieldValue'])
                self.story.append(no_data)
            else:
                # Create 2-column layout with safe table
                self._create_safe_two_column_layout(populated_fields)

            # Add section divider line
            self._add_section_divider()

            # Add spacing
            self.story.append(Spacer(1, 12))

        except Exception as e:
            logger.error(f"Error adding section '{title}': {e}")
            # Add error message
            error_para = Paragraph(f"Error loading section: {title}", self.styles['FieldValue'])
            self.story.append(error_para)

    def _add_section_divider(self):
        """Add a thin colored line to separate sections using a simpler approach"""
        try:
            # Create a thin line using a simple table approach
            line_data = [['']]  # Single empty cell

            # Calculate line width (full page width minus margins)
            line_width = 6.5 * inch

            # Create table with very small row height
            divider_table = Table(line_data, colWidths=[line_width], rowHeights=[2])  # 2 points high
            divider_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#59B4A6')),  # Your teal color
                ('LEFTPADDING', (0, 0), (0, 0), 0),
                ('RIGHTPADDING', (0, 0), (0, 0), 0),
                ('TOPPADDING', (0, 0), (0, 0), 0),
                ('BOTTOMPADDING', (0, 0), (0, 0), 0),
                ('GRID', (0, 0), (0, 0), 2, colors.HexColor('#59B4A6')),  # Ensures the line is visible
            ]))

            self.story.append(Spacer(1, 8))  # Small space before line
            self.story.append(divider_table)
            self.story.append(Spacer(1, 6))  # Small space after line

        except Exception as e:
            logger.error(f"Error adding section divider: {e}")
            # If divider fails, just add extra spacing
            self.story.append(Spacer(1, 6))

    def _create_safe_two_column_layout(self, fields: List[tuple]):
        """Create a safe two-column layout for field-value pairs"""
        if not fields:
            return

        try:
            # Calculate rows needed
            num_fields = len(fields)
            rows_needed = (num_fields + 1) // 2

            table_data = []
            for row in range(rows_needed):
                left_index = row
                right_index = row + rows_needed

                # Left column
                if left_index < num_fields:
                    label, value = fields[left_index]
                    left_cell = self._format_safe_field_cell(label, value)
                else:
                    left_cell = ""

                # Right column
                if right_index < num_fields:
                    label, value = fields[right_index]
                    right_cell = self._format_safe_field_cell(label, value)
                else:
                    right_cell = ""

                table_data.append([left_cell, right_cell])

            # Create table with FIXED, safe widths
            col_width = 3*inch  # Fixed width per column
            field_table = Table(table_data, colWidths=[col_width, col_width])
            field_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))

            self.story.append(field_table)

        except Exception as e:
            logger.error(f"Error creating two-column layout: {e}")
            # Fallback to simple list
            for label, value in fields:
                field_text = f"<b>{label}:</b> {value}"
                field_para = Paragraph(field_text, self.styles['FieldValue'])
                self.story.append(field_para)

    def _format_safe_field_cell(self, label: str, value: str):
        """Format a field label and value safely"""
        try:
            clean_label = safe_str(label, 'Field')
            clean_value = safe_str(value, '')

            # Limit value length to prevent layout issues
            if len(clean_value) > 80:
                clean_value = clean_value[:77] + "..."

            cell_content = f"<b>{clean_label}:</b><br/>{clean_value}"
            return Paragraph(cell_content, self.styles['CompactField'])
        except Exception as e:
            logger.error(f"Error formatting field cell: {e}")
            return Paragraph("(Error displaying field)", self.styles['CompactField'])

    def add_images_section(self, primary_images: List[str], additional_images: List[str]):
        """Add images section with actual images and section divider"""
        try:
            # Section title
            section_title = Paragraph("7. Documentation and Evidence", self.styles['SectionTitle'])
            self.story.append(section_title)
            self.story.append(Spacer(1, 6))

            # Filter valid images
            valid_primary = [img for img in (primary_images or []) if img and os.path.exists(str(img))]
            valid_additional = [img for img in (additional_images or []) if img and os.path.exists(str(img))]

            images_added = False

            # Add primary images
            if valid_primary:
                primary_label = Paragraph("<b>Primary Display Photos:</b>", self.styles['FieldLabel'])
                self.story.append(primary_label)
                self.story.append(Spacer(1, 3))

                self._add_safe_image_grid(valid_primary)
                images_added = True

            # Add additional images
            if valid_additional:
                if images_added:
                    self.story.append(Spacer(1, 6))
                additional_label = Paragraph("<b>Additional Images:</b>", self.styles['FieldLabel'])
                self.story.append(additional_label)
                self.story.append(Spacer(1, 3))

                self._add_safe_image_grid(valid_additional)
                images_added = True

            # Show total count
            if images_added:
                total_images = len(valid_primary) + len(valid_additional)
                total_text = f"<i>Total images: {total_images}</i>"
                total_para = Paragraph(total_text, self.styles['FieldValue'])
                self.story.append(total_para)
            else:
                no_images = Paragraph("(No images available)", self.styles['FieldValue'])
                self.story.append(no_images)

            # Add section divider line
            self._add_section_divider()

            # Add spacing
            self.story.append(Spacer(1, 12))

        except Exception as e:
            logger.error(f"Error adding images section: {e}")

    def _add_safe_image_grid(self, image_paths: List[str]):
        """Add images in a grid with VERY conservative sizing"""
        if not image_paths:
            return

        logger.info(f"Adding {len(image_paths)} images to safe grid")

        # VERY conservative image dimensions
        img_width = 1.8 * inch  # Small, safe width
        img_height = 1.3 * inch  # Small, safe height

        successful_images = 0

        # Process images in rows of 3
        for i in range(0, len(image_paths), 3):
            row_images = image_paths[i:i+3]
            image_row = []

            for img_path in row_images:
                try:
                    if img_path and os.path.exists(str(img_path)):
                        img = self._create_ultra_safe_image(img_path, img_width, img_height)
                        if img:
                            image_row.append(img)
                            successful_images += 1
                        else:
                            image_row.append("(Failed)")
                    else:
                        image_row.append("(Missing)")
                except Exception as e:
                    logger.error(f"Error processing image {img_path}: {e}")
                    image_row.append("(Error)")

            # Pad row
            while len(image_row) < 3:
                image_row.append('')

            # Create SIMPLE table for this row
            if image_row:
                try:
                    col_width = 2 * inch  # Fixed column width
                    img_table = Table([image_row], colWidths=[col_width] * 3)
                    img_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 1),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                        ('TOPPADDING', (0, 0), (-1, -1), 1),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ]))

                    self.story.append(img_table)
                    self.story.append(Spacer(1, 3))

                except Exception as e:
                    logger.error(f"Error creating image table: {e}")

        logger.info(f"Successfully added {successful_images}/{len(image_paths)} images to grid")

    def _create_ultra_safe_image(self, img_path: str, max_width: float, max_height: float):
        """Create image with ultra-safe, fixed dimensions"""
        try:
            if not img_path or not os.path.exists(str(img_path)):
                return None

            # Get original dimensions with PIL
            try:
                from PIL import Image as PILImage
                with PILImage.open(str(img_path)) as pil_img:
                    orig_width, orig_height = pil_img.size

                if orig_width <= 0 or orig_height <= 0:
                    return None

            except Exception:
                return None

            # Create ReportLab image
            img = Image(str(img_path))

            # Calculate aspect ratio
            aspect_ratio = orig_height / orig_width

            # Use FIXED dimensions - always the same size
            if aspect_ratio > 1.0:  # Taller than wide
                new_height = max_height
                new_width = new_height / aspect_ratio
                if new_width > max_width:
                    new_width = max_width
                    new_height = new_width * aspect_ratio
            else:  # Wider than tall
                new_width = max_width
                new_height = new_width * aspect_ratio
                if new_height > max_height:
                    new_height = max_height
                    new_width = new_height / aspect_ratio

            # Ensure minimum reasonable size
            min_size = 0.3 * inch
            new_width = max(min_size, min(new_width, max_width))
            new_height = max(min_size, min(new_height, max_height))

            # Set FIXED dimensions
            img.drawWidth = new_width
            img.drawHeight = new_height

            return img

        except Exception as e:
            logger.error(f"Error creating ultra-safe image for {img_path}: {e}")
            return None

    def generate(self) -> bool:
        """Generate the PDF document with balanced features"""
        try:
            if not self.story:
                self.story.append(Paragraph("No content available", self.styles['Normal']))

            logger.info(f"Generating balanced PDF with moderate logo sizing")

            # Use standard margins
            doc = SimpleDocTemplate(
                self.output_path,
                pagesize=A4,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch,
                leftMargin=0.75*inch,
                rightMargin=0.75*inch
            )

            # Build PDF
            doc.build(self.story)

            # Verify
            if os.path.exists(self.output_path):
                file_size = os.path.getsize(self.output_path)
                logger.info(f"Balanced PDF generated: {self.output_path} ({file_size} bytes)")
                return True
            else:
                logger.error("PDF file was not created")
                return False

        except Exception as e:
            logger.error(f"Error generating balanced PDF: {e}")
            raise PDFGenerationError(f"Failed to generate PDF: {str(e)}")