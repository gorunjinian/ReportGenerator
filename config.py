"""
Configuration file for Heritage Report Generator
Updated with 3-per-row image layout
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch

# Default configuration values
DATE_INPUT_FORMAT = '%Y/%m/%d'
DATE_OUTPUT_FORMAT = '%Y-%m-%d'

# Alternative date formats to try
ALTERNATIVE_DATE_FORMATS = [
    '%Y-%m-%d',      # 2024-01-15 (common Google Forms format)
    '%Y/%m/%d',      # 2024/01/15
    '%m/%d/%Y',      # 01/15/2024
    '%d/%m/%Y',      # 15/01/2024
    '%Y-%m-%d %H:%M:%S',  # 2024-01-15 10:30:00
    '%m/%d/%Y %H:%M:%S',  # 01/15/2024 10:30:00
]

# Logo settings (inches)
LOGO_WIDTH = 2
LOGO_HEIGHT = 1

# Image settings (inches) - Updated for 3 images per row
PRIMARY_IMAGE_MAX_WIDTH = 6
PRIMARY_IMAGE_MAX_HEIGHT = 4
ADDITIONAL_IMAGE_WIDTH = 2.4  # Reduced for 3-per-row layout
ADDITIONAL_IMAGE_HEIGHT = 1.8
IMAGES_PER_ROW = 3  # Changed from 2 to 3 as requested

# Download settings
DOWNLOAD_TIMEOUT = 30  # seconds
CHUNK_SIZE = 8192  # bytes
MAX_RETRIES = 3

# Page settings
PAGE_SIZE = A4
TOP_MARGIN = 0.5 * inch
BOTTOM_MARGIN = 0.5 * inch
LEFT_MARGIN = 0.5 * inch
RIGHT_MARGIN = 0.5 * inch

# Colors
SECTION_TITLE_COLOR = '#ff5c28'
FIELD_LABEL_COLOR = '#333333'
FIELD_VALUE_COLOR = '#000000'

# Text settings
REPORT_TITLE = "Heritage Site Assessment Report"
SECTION_TITLE_SIZE = 14
FIELD_LABEL_SIZE = 10
FIELD_VALUE_SIZE = 10

# Font settings
DEFAULT_FONT = 'Helvetica'
BOLD_FONT = 'Helvetica-Bold'
ARABIC_FONT_PATH = 'ARIALUNI.TTF'
ARABIC_FONT_NAME = 'ArialUnicode'

# Try to load custom config and override defaults
try:
    from config import *
    # Ensure PAGE_SIZE is properly converted if it's a string
    if isinstance(PAGE_SIZE, str):
        if PAGE_SIZE.upper() == 'A4':
            PAGE_SIZE = A4
        elif PAGE_SIZE.upper() == 'LETTER':
            PAGE_SIZE = letter
        else:
            PAGE_SIZE = A4  # fallback

    # Ensure margins are proper units
    if isinstance(TOP_MARGIN, (int, float)):
        TOP_MARGIN = TOP_MARGIN * inch
    if isinstance(BOTTOM_MARGIN, (int, float)):
        BOTTOM_MARGIN = BOTTOM_MARGIN * inch
    if isinstance(LEFT_MARGIN, (int, float)):
        LEFT_MARGIN = LEFT_MARGIN * inch
    if isinstance(RIGHT_MARGIN, (int, float)):
        RIGHT_MARGIN = RIGHT_MARGIN * inch

except ImportError:
    pass  # Use defaults

# Google Drive patterns
GOOGLE_DRIVE_PATTERNS = [
    r'/file/d/([a-zA-Z0-9-_]+)',  # /file/d/FILE_ID/view
    r'id=([a-zA-Z0-9-_]+)',        # ?id=FILE_ID
    r'/([a-zA-Z0-9-_]{33,})',     # Long ID in path
    r'^([a-zA-Z0-9-_]+)$'         # Just the ID
]

# Field mappings for sections
SECTION_FIELDS = {
    "general_info": {
        "Date of Assessment": "Date of Assessment",
        "Assessor's Name": "Assessor's Name ",
        "Supervisor": "Supervisor ",
        "Organization": "Organization",
        "Monument Reference": "Monument Reference ",
        "Monument Name": "Monument Name ",
        "Ownership": "Ownership "
    },
    "location_info": {
        "Governorate": "Governorate",
        "District": "District",
        "City/Village": "City-Village",
        "Location": "Location"
    },
    "preliminary_conditions": {
        "Observed Structural Conditions": "Observed structural conditions ",
        "Exterior Walls Condition": "Exterior walls condition",
        "Roof Conditions": "Roof Conditions",
        "Major Architectural Failure": "Major Architectural Failure",
        "Location of Major Damage": "Location of Major Damage"
    },
    "conflict_evidence": {
        "Evidence of Armed Conflict": "Evidence of Armed Conflict",
        "Fire or Smoke Damage": "Fire or Smoke Damage",
        "Looting or Vandalism": "Looting or Vandalism",
        "Conflict-Specific Damage Indicator": "Conflict-Specific damage indicator "
    },
    "visible_damage": {
        "Significant Cultural/Religious Symbol Damage": "Significant Cultural or Religous Symbol Damage ",
        "Visible Damage to Sculptures/Carvings": "Visible Damage to Sculptures, Catvings and Facade ",
        "Damage to Decorative Elements": "Damage to decorative elements "
    },
    "environmental_concerns": {
        "Water Infiltration and Weather Exposure": "Water Infiltration and Weather Exposure ",
        "Vegetation Overgrowth": "Vegetation Overgrowth ",
        "Secondary Hazards Present": "Secondary Hazards present "
    },
    "documentation": {
        "Satellite Imagery Observations": "Satellite Imagery Observations",
        "Eyewitness Report": "Eyewitness Report",
        "Testimonials": "Testimonials"
    },
    "risk_assessment": {
        "Potential Hazards to Public and Site": "Potential Hazards to the public and site",
        "Urgent Stabilization Required": "Urgent Stabilization Required",
        "Security Measures Needed": "Security measures needed",
        "Likelihood of Continued Damage": "Likelihood of continued damage"
    },
    "significance": {
        "Historical or Cultural Significance": "Historical or Cultural Significance",
        "Significance for Local Population": "Significance for local population",
        "Additional References": "Additional References"
    }
}

# Image field names
PRIMARY_IMAGE_FIELD = "Primary Display Photo Upload"
ADDITIONAL_IMAGES_FIELD = "Additional images and files "

# Logo filenames
BILADI_LOGO_FILENAME = "Biladi logo.png"
CER_LOGO_FILENAME = "CER Logo.png"