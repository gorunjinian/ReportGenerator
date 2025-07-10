"""
Utility functions for Heritage Report Generator
Enhanced with comprehensive null safety and multiple image support
"""

import os
import re
from datetime import datetime
import logging
from typing import Optional, List, Tuple

from constants import GOOGLE_DRIVE_PATTERNS, ALTERNATIVE_DATE_FORMATS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_logging(log_file: Optional[str] = None, log_level: str = 'INFO'):
    """
    Setup logging configuration

    Args:
        log_file: Optional path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    if log_file:
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format
        )


def validate_csv_path(csv_path: str) -> bool:
    """
    Validate if CSV file exists and is readable

    Args:
        csv_path: Path to CSV file

    Returns:
        bool: True if valid, False otherwise
    """
    if not csv_path:
        logger.error("CSV path is empty or None")
        return False

    csv_path = str(csv_path)  # Ensure it's a string

    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        return False

    if not os.path.isfile(csv_path):
        logger.error(f"Path is not a file: {csv_path}")
        return False

    if not csv_path.lower().endswith('.csv'):
        logger.warning(f"File does not have .csv extension: {csv_path}")

    return True


def generate_output_filename(csv_path: str, suffix: str = "Report") -> str:
    """
    Generate output filename with timestamp

    Args:
        csv_path: Path to input CSV file
        suffix: Suffix to add to filename

    Returns:
        str: Output filename path
    """
    if not csv_path:
        csv_path = "unknown.csv"

    csv_path = str(csv_path)
    csv_dir = os.path.dirname(csv_path)
    csv_name = os.path.splitext(os.path.basename(csv_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_filename = f"{csv_name}_{suffix}_{timestamp}.pdf"
    output_path = os.path.join(csv_dir, output_filename)

    return output_path


def extract_drive_file_id(url: str) -> Optional[str]:
    """
    Extract file ID from various Google Drive URL formats with null safety

    Args:
        url: Google Drive URL

    Returns:
        Optional[str]: File ID if found, None otherwise
    """
    if not url or url in [None, 'null', 'NULL', '']:
        return None

    url = safe_str(url).strip()
    if not url:
        return None

    for pattern in GOOGLE_DRIVE_PATTERNS:
        try:
            match = re.search(pattern, url)
            if match:
                file_id = match.group(1)
                logger.debug(f"Extracted file ID: {file_id} from URL: {url}")
                return file_id
        except Exception as e:
            logger.warning(f"Error matching pattern {pattern} against {url}: {e}")
            continue

    logger.warning(f"Could not extract file ID from URL: {url}")
    return None


def parse_image_links(links_str: str) -> List[str]:
    """
    Parse semicolon/comma-separated image links with enhanced null safety and multiple format support

    Args:
        links_str: String containing semicolon/comma/newline-separated links

    Returns:
        List[str]: List of cleaned links
    """
    if not links_str or links_str in [None, 'null', 'NULL', '']:
        return []

    try:
        links_str = safe_str(links_str)
        if not links_str:
            return []

        # Split by multiple possible delimiters
        # Handle semicolons (primary from Google Forms), commas, and newlines
        import re
        # Split by semicolon (most common), comma, or newline, then filter out empty strings
        raw_links = re.split(r'[;,\n\r]+', links_str)

        links = []
        for link in raw_links:
            clean_link = safe_str(link).strip()
            # Remove any surrounding quotes or whitespace
            clean_link = clean_link.strip('"\'')

            if clean_link and clean_link.lower() not in ['null', 'none', '']:
                # Validate that it looks like a URL or Google Drive ID
                if ('drive.google.com' in clean_link or
                    clean_link.startswith(('http://', 'https://')) or
                    re.match(r'^[a-zA-Z0-9_-]{25,}$', clean_link)):  # Direct Google Drive ID
                    links.append(clean_link)
                else:
                    logger.debug(f"Skipping invalid link format: {clean_link}")

        logger.info(f"Parsed {len(links)} valid image links from input string")
        return links
    except Exception as e:
        logger.error(f"Error parsing image links: {e}")
        return []


def safe_str(value: any, default: str = '') -> str:
    """
    Safely convert value to string with comprehensive null handling

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        str: Converted string
    """
    try:
        # Handle None explicitly
        if value is None:
            return default

        # Handle pandas NaN/null values
        if hasattr(value, 'isna') and value.isna():
            return default

        # Handle string representations of null
        if isinstance(value, str):
            if value.lower().strip() in ['null', 'none', 'nan', '']:
                return default

        # Handle numeric null representations
        if str(value).lower().strip() in ['null', 'none', 'nan', '']:
            return default

        # Convert to string and strip whitespace
        result = str(value).strip()

        # Final check for empty result
        if not result:
            return default

        return result

    except Exception as e:
        logger.warning(f"Error converting value to string: {value} -> {e}")
        return default


def format_date(date_value: any, input_format: str, output_format: str) -> str:
    """
    Format date value with multiple format fallbacks and null safety

    Args:
        date_value: Date value to format
        input_format: Primary input date format
        output_format: Output date format

    Returns:
        str: Formatted date string
    """
    try:
        # Handle null values
        if date_value is None or date_value in ['null', 'NULL', 'None', '']:
            return ''

        if hasattr(date_value, 'strftime'):
            # Already a datetime object
            return date_value.strftime(output_format)
        elif isinstance(date_value, (str, int, float)):
            date_str = safe_str(date_value).strip()

            if not date_str:
                return ''

            # Try multiple date formats
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
            return safe_str(date_value)

    except Exception as e:
        logger.warning(f"Could not format date {date_value}: {e}")
        return safe_str(date_value)


def create_temp_filename(prefix: str, extension: str, temp_dir: str) -> str:
    """
    Create a unique temporary filename

    Args:
        prefix: Filename prefix
        extension: File extension (without dot)
        temp_dir: Temporary directory path

    Returns:
        str: Full path to temporary file
    """
    prefix = safe_str(prefix, 'temp')
    extension = safe_str(extension, 'tmp').lstrip('.')

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{prefix}_{timestamp}.{extension}"
    return os.path.join(temp_dir, filename)


def clean_filename(filename: str) -> str:
    """
    Clean filename by removing invalid characters

    Args:
        filename: Original filename

    Returns:
        str: Cleaned filename
    """
    filename = safe_str(filename, 'unknown')

    # Remove invalid characters for Windows/Unix filenames
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')

    # Ensure we have a valid filename
    if not filename:
        filename = 'unknown'

    return filename


def get_file_size_mb(filepath: str) -> float:
    """
    Get file size in megabytes

    Args:
        filepath: Path to file

    Returns:
        float: File size in MB
    """
    try:
        if not filepath or not os.path.exists(str(filepath)):
            return 0.0
        size_bytes = os.path.getsize(str(filepath))
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0.0


def ensure_directory_exists(directory: str) -> bool:
    """
    Ensure directory exists, create if not

    Args:
        directory: Directory path

    Returns:
        bool: True if directory exists or was created
    """
    try:
        if not directory:
            return False
        os.makedirs(str(directory), exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Could not create directory {directory}: {e}")
        return False


def is_valid_image_url(url: str) -> bool:
    """
    Check if URL appears to be a valid image URL

    Args:
        url: URL to check

    Returns:
        bool: True if URL appears valid
    """
    if not url:
        return False

    url = safe_str(url).strip()
    if not url or url.lower() in ['null', 'none', '']:
        return False

    # Check for Google Drive patterns
    if 'drive.google.com' in url:
        return extract_drive_file_id(url) is not None

    # Check for common image URLs
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    url_lower = url.lower()

    return (url.startswith(('http://', 'https://')) and
            any(ext in url_lower for ext in image_extensions))


def sanitize_field_value(value: any, max_length: int = 1000) -> str:
    """
    Sanitize field value for safe PDF generation

    Args:
        value: Value to sanitize
        max_length: Maximum allowed length

    Returns:
        str: Sanitized string value
    """
    clean_value = safe_str(value)

    if len(clean_value) > max_length:
        clean_value = clean_value[:max_length-3] + "..."

    # Remove any characters that might cause PDF issues
    clean_value = re.sub(r'[^\w\s\-.,;:!?()\[\]{}]', '', clean_value)

    return clean_value