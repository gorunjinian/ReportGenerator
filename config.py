"""
Configuration file for Heritage Site Assessment Report Generator

Modify these settings to customize the report generation.
This file is optional - if not present, default values will be used.
"""

# ==============================================================================
# DATE FORMATS
# ==============================================================================

# Format of dates in the CSV file
DATE_INPUT_FORMAT = '%Y/%m/%d'  # e.g., 2024/12/15

# Format of dates in the PDF report
DATE_OUTPUT_FORMAT = '%Y-%m-%d'  # e.g., 2024-12-15

# ==============================================================================
# LOGO SETTINGS
# ==============================================================================

# Logo dimensions in inches
LOGO_WIDTH = 2
LOGO_HEIGHT = 1

# Logo filenames (must be in same directory as CSV)
BILADI_LOGO_FILENAME = "Biladi logo.jpg"
CER_LOGO_FILENAME = "CER Logo.jpg"

# ==============================================================================
# IMAGE SETTINGS
# ==============================================================================

# Primary image dimensions (inches)
PRIMARY_IMAGE_MAX_WIDTH = 6
PRIMARY_IMAGE_MAX_HEIGHT = 4

# Additional images dimensions (inches)
ADDITIONAL_IMAGE_WIDTH = 3
ADDITIONAL_IMAGE_HEIGHT = 2

# Number of images per row in grid
IMAGES_PER_ROW = 2

# ==============================================================================
# DOWNLOAD SETTINGS
# ==============================================================================

# Timeout for image downloads (seconds)
DOWNLOAD_TIMEOUT = 30

# Download chunk size (bytes)
CHUNK_SIZE = 8192

# Maximum download retry attempts
MAX_RETRIES = 3

# ==============================================================================
# PAGE SETTINGS
# ==============================================================================

# Page size ('A4' or 'LETTER')
PAGE_SIZE = 'A4'

# Page margins in inches
TOP_MARGIN = 0.5
BOTTOM_MARGIN = 0.5
LEFT_MARGIN = 0.5
RIGHT_MARGIN = 0.5

# ==============================================================================
# TEXT SETTINGS
# ==============================================================================

# Report title
REPORT_TITLE = "Site Assessment Report"

# Font sizes
SECTION_TITLE_SIZE = 14
FIELD_LABEL_SIZE = 10
FIELD_VALUE_SIZE = 10

# Colors (hex format)
SECTION_TITLE_COLOR = '#1f4788'  # Dark blue
FIELD_LABEL_COLOR = '#333333'    # Dark gray
FIELD_VALUE_COLOR = '#000000'    # Black

# ==============================================================================
# FONT SETTINGS
# ==============================================================================

# Default fonts
DEFAULT_FONT = 'Helvetica'
BOLD_FONT = 'Helvetica-Bold'

# Arabic font support (if available)
# Place ARIALUNI.TTF in the same folder as the script
ARABIC_FONT_PATH = 'ARIALUNI.TTF'
ARABIC_FONT_NAME = 'ArialUnicode'

# ==============================================================================
# ADVANCED SETTINGS
# ==============================================================================

# Enable debug logging
DEBUG_MODE = False

# Save downloaded images after report generation
KEEP_DOWNLOADED_IMAGES = False

# Image quality (1-100, higher is better quality but larger file size)
IMAGE_QUALITY = 85

# Maximum PDF file size warning (MB)
MAX_PDF_SIZE_WARNING = 50

# ==============================================================================
# CUSTOM FIELD MAPPINGS
# ==============================================================================
# Uncomment and modify to customize field names or add new fields

# SECTION_FIELDS = {
#     "general_info": {
#         "Date of Assessment": "Date of Assessment",
#         "Assessor's Name": "Assessor's Name ",
#         # Add more fields as needed
#     }
# }

