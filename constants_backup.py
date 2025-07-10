"""
Constants and configuration for Heritage Report Generator
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch

# Try to load custom config
try:
    from config import *
except ImportError:
    # Default configuration values
    
    # Date formats
    DATE_INPUT_FORMAT = '%Y/%m/%d'
    DATE_OUTPUT_FORMAT = '%Y-%m-%d'
    
    # Logo settings (inches)
    LOGO_WIDTH = 2
    LOGO_HEIGHT = 1
    
    # Image settings (inches)
    PRIMARY_IMAGE_MAX_WIDTH = 6
    PRIMARY_IMAGE_MAX_HEIGHT = 4
    ADDITIONAL_IMAGE_WIDTH = 3
    ADDITIONAL_IMAGE_HEIGHT = 2
    IMAGES_PER_ROW = 2
    
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
    REPORT_TITLE = "Site Assessment Report"
    SECTION_TITLE_SIZE = 14
    FIELD_LABEL_SIZE = 10
    FIELD_VALUE_SIZE = 10
    
    # Font settings
    DEFAULT_FONT = 'Helvetica'
    BOLD_FONT = 'Helvetica-Bold'
    ARABIC_FONT_PATH = 'ARIALUNI.TTF'
    ARABIC_FONT_NAME = 'ArialUnicode'

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
BILADI_LOGO_FILENAME = "Biladi logo.jpg"
CER_LOGO_FILENAME = "CER Logo.jpg"
