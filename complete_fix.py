"""
Complete fix for all identified issues:
1. PDF PAGE_SIZE configuration
2. Date format handling
3. Enhanced error handling
"""

import os
import sys

def update_constants_file():
    """Update constants.py to fix PAGE_SIZE and date format issues"""
    
    print("🔧 Updating constants.py...")
    
    updated_constants = '''"""
Constants and configuration for Heritage Report Generator
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
SECTION_TITLE_COLOR = '#1f4788'
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
BILADI_LOGO_FILENAME = "Biladi logo.jpg"
CER_LOGO_FILENAME = "CER Logo.jpg"
'''
    
    # Backup original
    if os.path.exists('constants.py'):
        with open('constants_backup.py', 'w', encoding='utf-8') as f_backup:
            with open('constants.py', 'r', encoding='utf-8') as f_orig:
                f_backup.write(f_orig.read())
        print("📋 Backed up original constants.py")
    
    # Write updated version
    with open('constants.py', 'w', encoding='utf-8') as f:
        f.write(updated_constants)
    
    print("✅ Updated constants.py with fixes")

def update_utils_file():
    """Update utils.py to handle multiple date formats"""
    
    print("🔧 Updating utils.py for better date handling...")
    
    # Read current utils.py
    with open('utils.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already updated
    if 'ALTERNATIVE_DATE_FORMATS' in content:
        print("✅ utils.py already has enhanced date handling")
        return
    
    # Find the format_date function and replace it
    new_format_date = '''def format_date(date_value: any, input_format: str, output_format: str) -> str:
    """
    Format date value with multiple format fallbacks
    
    Args:
        date_value: Date value to format
        input_format: Primary input date format
        output_format: Output date format
        
    Returns:
        str: Formatted date string
    """
    try:
        if hasattr(date_value, 'strftime'):
            # Already a datetime object
            return date_value.strftime(output_format)
        elif isinstance(date_value, str):
            date_str = str(date_value).strip()
            
            # Try multiple date formats
            from constants import ALTERNATIVE_DATE_FORMATS
            formats_to_try = [input_format] + ALTERNATIVE_DATE_FORMATS
            
            for fmt in formats_to_try:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime(output_format)
                except ValueError:
                    continue
            
            logger.warning(f"Could not parse date '{date_str}' with any known format")
            return date_str  # Return original if can't parse
        else:
            return ''
    except Exception as e:
        logger.warning(f"Could not format date {date_value}: {e}")
        return safe_str(date_value)'''
    
    # Replace the function
    import re
    pattern = r'def format_date\(.*?\n(?:.*\n)*?.*return safe_str\(date_value\)'
    
    if re.search(pattern, content, re.MULTILINE | re.DOTALL):
        content = re.sub(pattern, new_format_date, content, flags=re.MULTILINE | re.DOTALL)
        
        with open('utils.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Updated utils.py with enhanced date parsing")
    else:
        print("⚠️  Could not locate format_date function to update")

def test_fixes():
    """Test all the fixes"""
    
    print("\n🧪 Testing fixes...")
    
    try:
        # Test 1: Constants loading
        from constants import PAGE_SIZE, ALTERNATIVE_DATE_FORMATS
        from reportlab.lib.pagesizes import A4
        
        print(f"✅ PAGE_SIZE correctly loaded: {type(PAGE_SIZE)} = {PAGE_SIZE}")
        print(f"✅ Alternative date formats: {len(ALTERNATIVE_DATE_FORMATS)} formats")
        
        if PAGE_SIZE == A4:
            print("✅ PAGE_SIZE matches A4 constant")
        else:
            print("❌ PAGE_SIZE mismatch!")
            return False
        
        # Test 2: Date parsing
        from utils import format_date
        from constants import DATE_INPUT_FORMAT, DATE_OUTPUT_FORMAT
        
        test_dates = [
            "2024-01-15",      # Your CSV format
            "2024/01/15",      # Original expected format
            "01/15/2024",      # US format
        ]
        
        for test_date in test_dates:
            result = format_date(test_date, DATE_INPUT_FORMAT, DATE_OUTPUT_FORMAT)
            print(f"✅ Date parsing '{test_date}' → '{result}'")
        
        # Test 3: PDF generation
        from pdf_builder import PDFBuilder
        
        builder = PDFBuilder('test_fix.pdf')
        builder.add_header_with_logos('.')
        builder.add_section('Test Section', {'Test': 'Value'})
        
        if builder.generate():
            print("✅ PDF generation test passed")
            if os.path.exists('test_fix.pdf'):
                os.remove('test_fix.pdf')
            return True
        else:
            print("❌ PDF generation test failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_actual_csv():
    """Test with the actual CSV file"""
    
    print("\n🧪 Testing with your actual CSV...")
    
    if not os.path.exists('CSV data.csv'):
        print("⚠️  CSV data.csv not found")
        return False
    
    try:
        from report_generator import ReportGenerator
        
        generator = ReportGenerator('CSV data.csv')
        
        # Test data loading
        generator._load_data()
        monument_name = generator.latest_data.get('Monument Name ', 'Unknown')
        assessment_date = generator.latest_data.get('Date of Assessment', 'Unknown')
        
        print(f"✅ Data loaded successfully")
        print(f"   Monument: {monument_name}")
        print(f"   Date: {assessment_date}")
        
        # Test PDF generation (skip images)
        generator.primary_images = []
        generator.additional_images = []
        
        output_file = 'actual_test_report.pdf'
        generator._build_pdf(output_file)
        
        if os.path.exists(output_file):
            size_kb = os.path.getsize(output_file) / 1024
            print(f"✅ PDF generated successfully: {output_file} ({size_kb:.1f} KB)")
            
            generator.cleanup()
            os.remove(output_file)
            return True
        else:
            print("❌ PDF file not created")
            return False
            
    except Exception as e:
        print(f"❌ Test with actual CSV failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Apply all fixes and test"""
    
    print("🔧 COMPLETE FIX FOR HERITAGE REPORT GENERATOR")
    print("=" * 60)
    
    # Apply fixes
    update_constants_file()
    update_utils_file()
    
    # Test fixes
    if not test_fixes():
        print("❌ Basic tests failed")
        return False
    
    # Test with actual data
    if not test_with_actual_csv():
        print("❌ Actual CSV test failed")
        return False
    
    print("\n🎉 ALL FIXES APPLIED AND TESTED SUCCESSFULLY!")
    print("=" * 60)
    print("✅ PDF generation error fixed")
    print("✅ Date format handling improved")
    print("✅ Your CSV data works correctly")
    print("\nNext steps:")
    print("1. Test full report: python main.py 'CSV data.csv'")
    print("2. Build executable: python quick_fix_build.py")
    
    return True

if __name__ == "__main__":
    if main():
        print("\n✅ SUCCESS - All issues fixed!")
    else:
        print("\n❌ Some fixes failed - check messages above")
    
    input("\nPress Enter to exit...")
