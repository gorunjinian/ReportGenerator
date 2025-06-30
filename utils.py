"""
Utility functions for Heritage Report Generator
"""

import os
import re
from datetime import datetime
import logging
from typing import Optional, List, Tuple

from constants import GOOGLE_DRIVE_PATTERNS

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
    csv_dir = os.path.dirname(csv_path)
    csv_name = os.path.splitext(os.path.basename(csv_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    output_filename = f"{csv_name}_{suffix}_{timestamp}.pdf"
    output_path = os.path.join(csv_dir, output_filename)
    
    return output_path


def extract_drive_file_id(url: str) -> Optional[str]:
    """
    Extract file ID from various Google Drive URL formats
    
    Args:
        url: Google Drive URL
        
    Returns:
        Optional[str]: File ID if found, None otherwise
    """
    if not url:
        return None
    
    url = str(url).strip()
    
    for pattern in GOOGLE_DRIVE_PATTERNS:
        match = re.search(pattern, url)
        if match:
            file_id = match.group(1)
            logger.debug(f"Extracted file ID: {file_id} from URL: {url}")
            return file_id
    
    logger.warning(f"Could not extract file ID from URL: {url}")
    return None


def parse_image_links(links_str: str) -> List[str]:
    """
    Parse comma-separated image links
    
    Args:
        links_str: String containing comma-separated links
        
    Returns:
        List[str]: List of cleaned links
    """
    if not links_str:
        return []
    
    links = [link.strip() for link in str(links_str).split(',') if link.strip()]
    return links


def safe_str(value: any, default: str = '') -> str:
    """
    Safely convert value to string
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        str: Converted string
    """
    try:
        if value is None or (hasattr(value, 'isna') and value.isna()):
            return default
        return str(value).strip()
    except Exception:
        return default


def format_date(date_value: any, input_format: str, output_format: str) -> str:
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
    # Remove invalid characters for Windows/Unix filenames
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
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
        size_bytes = os.path.getsize(filepath)
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
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Could not create directory {directory}: {e}")
        return False
