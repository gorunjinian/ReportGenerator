"""
PDF building module for Heritage Report Generator
Enhanced with two-column layout for better space utilization
"""

import os
import logging
from typing import List, Dict, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
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
    """Handles PDF generation with two-column layout"""

    def __init__(self, output_path: str):
        """
        Initialize PDF builder

        Args:
            output_path: Path for output PDF
        """
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        self.story = []

    def setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        # Try to register font with better Unicode support
        arabic_font = DEFAULT_FONT
        try:
            if os.path.exists(ARABIC_FONT_PATH):
                pdfmetrics.registerFont(TTFont(ARABIC_FONT_NAME, ARABIC_FONT_PATH))
                arabic_font = ARABIC_FONT_NAME
                logger.info(f"Registered font: {ARABIC_FONT_NAME}")
        except Exception as e:
            logger.warning(f"Could not register Arabic font: {e}")

        # Section title style
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=SECTION_TITLE_SIZE,
            textColor=colors.HexColor(SECTION_TITLE_COLOR),
            spaceAfter=12,
            spaceBefore=12,
            alignment=TA_LEFT
        ))

        # Field label style (for two-column layout)
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=FIELD_LABEL_SIZE,
            textColor=colors.HexColor(FIELD_LABEL_COLOR),
            fontName=BOLD_FONT,
            spaceAfter=2,
            alignment=TA_LEFT
        ))

        # Field value style (for two-column layout)
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=FIELD_VALUE_SIZE,
            textColor=colors.HexColor(FIELD_VALUE_COLOR),
            spaceAfter=6,
            fontName=arabic_font,
            alignment=TA_LEFT
        ))

        # Compact field style for two-column layout
        self.styles.add(ParagraphStyle(
            name='CompactField',
            parent=self.styles['Normal'],
            fontSize=FIELD_VALUE_SIZE - 1,
            textColor=colors.HexColor(FIELD_VALUE_COLOR),
            spaceAfter=4,
            fontName=arabic_font,
            leftIndent=0,
            alignment=TA_LEFT
        ))

    def add_header_with_logos(self, csv_dir: str):
        """Add header with logos to the report"""
        header_data = []

        # Check for logo files
        biladi_logo_path = os.path.join(csv_dir, BILADI_LOGO_FILENAME)
        cer_logo_path = os.path.join(csv_dir, CER_LOGO_FILENAME)

        try:
            if os.path.exists(biladi_logo_path) and os.path.exists(cer_logo_path):
                biladi_logo = Image(
                    biladi_logo_path,
                    width=LOGO_WIDTH*inch,
                    height=LOGO_HEIGHT*inch
                )
                cer_logo = Image(
                    cer_logo_path,
                    width=LOGO_WIDTH*inch,
                    height=LOGO_HEIGHT*inch
                )
                header_data = [[biladi_logo, '', cer_logo]]
                logger.info("Added logos to header")
            else:
                # Text placeholders if logos not found
                header_data = [[
                    Paragraph("BILADI", self.styles['Title']),
                    '',
                    Paragraph("CER", self.styles['Title'])
                ]]
                logger.warning("Logo files not found, using text placeholders")

        except Exception as e:
            logger.error(f"Error adding logos: {e}")
            header_data = [[
                Paragraph("BILADI", self.styles['Title']),
                '',
                Paragraph("CER", self.styles['Title'])
            ]]

        # Create header table
        header_table = Table(header_data, colWidths=[2.5*inch, 2*inch, 2.5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        self.story.append(header_table)
        self.story.append(Spacer(1, 0.3*inch))

        # Add report title
        title = Paragraph(REPORT_TITLE, self.styles['Title'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.2*inch))

    def add_section(self, title: str, fields_dict: Dict[str, str]):
        """
        Add a section with title and field-value pairs in two-column layout

        Args:
            title: Section title
            fields_dict: Dictionary of field labels and values
        """
        # Add section title (full width)
        self.story.append(Paragraph(title, self.styles['SectionTitle']))
        self.story.append(Spacer(1, 0.1*inch))

        # Filter out empty fields
        populated_fields = [(label, value) for label, value in fields_dict.items()
                           if value and str(value).strip()]

        if not populated_fields:
            self.story.append(Paragraph("(No data available)", self.styles['FieldValue']))
        else:
            # Create two-column layout
            self._create_two_column_layout(populated_fields)

        # Add blue divider line
        self._add_section_divider()

        # Add spacing after divider
        self.story.append(Spacer(1, 0.15*inch))

    def _add_section_divider(self):
        """Add a thin blue horizontal divider line"""
        # Create a thin blue line spanning the page width
        divider = HRFlowable(
            width="100%",
            thickness=1,
            lineCap='round',
            color=colors.HexColor(SECTION_TITLE_COLOR),  # Same blue as section titles
            spaceBefore=0.1*inch,
            spaceAfter=0.05*inch,
            hAlign='CENTER',
            vAlign='BOTTOM'
        )
        self.story.append(divider)

    def _create_two_column_layout(self, fields: List[tuple]):
        """Create a two-column layout for field-value pairs"""

        # Calculate how many rows we need
        num_fields = len(fields)
        rows_needed = (num_fields + 1) // 2  # Round up division

        table_data = []

        for row in range(rows_needed):
            left_index = row
            right_index = row + rows_needed

            # Left column
            if left_index < num_fields:
                label, value = fields[left_index]
                left_cell = self._format_field_cell(label, value)
            else:
                left_cell = ""

            # Right column
            if right_index < num_fields:
                label, value = fields[right_index]
                right_cell = self._format_field_cell(label, value)
            else:
                right_cell = ""

            table_data.append([left_cell, right_cell])

        # Create table with appropriate column widths
        available_width = 7.5 * inch  # Page width minus margins
        col_width = available_width / 2

        field_table = Table(table_data, colWidths=[col_width, col_width])
        field_table.setStyle(TableStyle([
            # Basic table styling
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),

            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),

            # Optional: Add subtle borders for debugging (remove in production)
            # ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))

        self.story.append(field_table)

    def _format_field_cell(self, label: str, value: str) -> str:
        """Format a field label and value for display in table cell"""

        # Clean and truncate if necessary
        clean_value = safe_str(value)
        if len(clean_value) > 100:  # Truncate very long values
            clean_value = clean_value[:97] + "..."

        # Create formatted cell content with label and value
        cell_content = f"<b>{label}:</b><br/>{clean_value}"

        return Paragraph(cell_content, self.styles['CompactField'])

    def add_images_section(self, primary_images: List[str], additional_images: List[str]):
        """
        Add images section to the report

        Args:
            primary_images: List of primary image paths
            additional_images: List of additional image paths
        """
        # Add section title
        self.story.append(Paragraph("7. Documentation and Evidence", self.styles['SectionTitle']))
        self.story.append(Spacer(1, 0.1*inch))

        # Add primary images
        if primary_images:
            self.story.append(Paragraph("<b>Primary Display Photo:</b>", self.styles['FieldLabel']))
            for img_path in primary_images[:1]:  # Show only first primary image
                self._add_image(
                    img_path,
                    PRIMARY_IMAGE_MAX_WIDTH*inch,
                    PRIMARY_IMAGE_MAX_HEIGHT*inch
                )

        # Add additional images
        if additional_images:
            self.story.append(Paragraph("<b>Additional Images:</b>", self.styles['FieldLabel']))
            self._add_image_grid(
                additional_images,
                ADDITIONAL_IMAGE_WIDTH*inch,
                ADDITIONAL_IMAGE_HEIGHT*inch
            )

        if not primary_images and not additional_images:
            self.story.append(Paragraph("(No images available)", self.styles['FieldValue']))

        # Add blue divider line
        self._add_section_divider()

        # Add spacing after divider
        self.story.append(Spacer(1, 0.15*inch))

    def add_documentation_section_with_text(self, text_fields: Dict[str, str]):
        """Add text documentation fields in two-column layout"""

        # Filter populated text fields
        populated_fields = [(label, value) for label, value in text_fields.items()
                           if value and str(value).strip()]

        if populated_fields:
            self.story.append(Paragraph("7. Documentation and Evidence", self.styles['SectionTitle']))
            self.story.append(Spacer(1, 0.1*inch))
            self._create_two_column_layout(populated_fields)

            # Add blue divider line
            self._add_section_divider()

            # Add spacing after divider
            self.story.append(Spacer(1, 0.15*inch))

    def _add_image(self, img_path: str, max_width: float, max_height: float):
        """Add single image to the story"""
        try:
            if not os.path.exists(img_path):
                logger.warning(f"Image file not found: {img_path}")
                return

            img = Image(img_path)

            # Calculate aspect ratio and resize
            img_width, img_height = img.drawWidth, img.drawHeight
            aspect = img_height / float(img_width)

            # Fit within max dimensions
            if img_width > max_width:
                img_width = max_width
                img_height = img_width * aspect

            if img_height > max_height:
                img_height = max_height
                img_width = img_height / aspect

            img.drawWidth = img_width
            img.drawHeight = img_height

            # Add image with spacing
            self.story.append(Spacer(1, 0.1*inch))
            self.story.append(img)
            self.story.append(Spacer(1, 0.1*inch))

        except Exception as e:
            logger.error(f"Error adding image {img_path}: {e}")
            self.story.append(Paragraph("(Error loading image)", self.styles['FieldValue']))

    def _add_image_grid(self, image_paths: List[str], width: float, height: float):
        """Add images in a grid layout"""
        for i in range(0, len(image_paths), IMAGES_PER_ROW):
            row_images = image_paths[i:i+IMAGES_PER_ROW]
            image_row = []

            for img_path in row_images:
                try:
                    if os.path.exists(img_path):
                        img = Image(img_path, width=width, height=height)
                        image_row.append(img)
                except Exception as e:
                    logger.error(f"Error adding grid image {img_path}: {e}")

            if image_row:
                # Pad row if needed
                while len(image_row) < IMAGES_PER_ROW:
                    image_row.append('')

                # Create table for row
                img_table = Table([image_row], colWidths=[3.5*inch] * IMAGES_PER_ROW)
                img_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ]))

                self.story.append(img_table)
                self.story.append(Spacer(1, 0.1*inch))

    def generate(self) -> bool:
        """
        Generate the PDF document

        Returns:
            bool: True if successful
        """
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                self.output_path,
                pagesize=PAGE_SIZE,
                topMargin=TOP_MARGIN,
                bottomMargin=BOTTOM_MARGIN,
                leftMargin=LEFT_MARGIN,
                rightMargin=RIGHT_MARGIN
            )

            # Build PDF
            doc.build(self.story)
            logger.info(f"PDF generated successfully: {self.output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise PDFGenerationError(f"Failed to generate PDF: {str(e)}")