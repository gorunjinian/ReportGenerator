"""
CSV data loader without pandas dependency
This version uses Python's built-in csv module instead of pandas
"""

import csv
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from exceptions import CSVLoadError, DataValidationError
from constants import DATE_INPUT_FORMAT
from utils import safe_str

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles CSV data loading without pandas dependency"""
    
    def __init__(self, csv_path: str):
        """Initialize data loader"""
        self.csv_path = csv_path
        self.data = []
        self.headers = []
        self.latest_entry = None
        
    def load_data(self) -> List[Dict[str, str]]:
        """Load CSV data using built-in csv module"""
        try:
            logger.info(f"Loading CSV file: {self.csv_path}")
            
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(self.csv_path, 'r', encoding=encoding, newline='') as csvfile:
                        # Auto-detect delimiter
                        sample = csvfile.read(1024)
                        csvfile.seek(0)
                        
                        # Try common delimiters
                        delimiters = [',', ';', '\t', '|']
                        best_delimiter = ','
                        max_columns = 0
                        
                        for delim in delimiters:
                            csvfile.seek(0)
                            reader = csv.reader(csvfile, delimiter=delim)
                            first_row = next(reader, [])
                            if len(first_row) > max_columns:
                                max_columns = len(first_row)
                                best_delimiter = delim
                        
                        # Read with best delimiter
                        csvfile.seek(0)
                        reader = csv.DictReader(csvfile, delimiter=best_delimiter)
                        self.headers = reader.fieldnames or []
                        self.data = [row for row in reader]
                        
                        logger.info(f"Loaded with {encoding} encoding, {best_delimiter} delimiter")
                        break
                        
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    logger.warning(f"Failed with {encoding}: {e}")
                    continue
            else:
                raise CSVLoadError("Could not load CSV with any supported encoding")
            
            if not self.data:
                raise CSVLoadError("CSV file is empty")
            
            logger.info(f"Loaded {len(self.data)} records, {len(self.headers)} columns")
            return self.data
            
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise CSVLoadError(f"Failed to load CSV: {str(e)}")
    
    def get_latest_entry(self) -> Dict[str, Any]:
        """Get latest entry by Date of Assessment"""
        if not self.data:
            self.load_data()
        
        try:
            date_column = 'Date of Assessment'
            
            if date_column not in self.headers:
                logger.warning(f"Date column not found, using last row")
                self.latest_entry = self.data[-1]
                return self.latest_entry
            
            # Find latest date
            latest_date = None
            latest_entry = None
            
            for row in self.data:
                date_str = row.get(date_column, '').strip()
                if not date_str:
                    continue
                
                # Try to parse date
                date_obj = None
                date_formats = [
                    DATE_INPUT_FORMAT,  # From constants
                    '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y',
                    '%Y-%m-%d', '%m-%d-%Y', '%d-%m-%Y'
                ]
                
                for fmt in date_formats:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if date_obj and (latest_date is None or date_obj > latest_date):
                    latest_date = date_obj
                    latest_entry = row
            
            if latest_entry:
                self.latest_entry = latest_entry
                logger.info(f"Selected entry from: {latest_date}")
            else:
                logger.warning("No valid dates found, using last row")
                self.latest_entry = self.data[-1]
            
            return self.latest_entry
            
        except Exception as e:
            logger.error(f"Error getting latest entry: {e}")
            raise DataValidationError(f"Failed to get latest entry: {str(e)}")
    
    def validate_required_fields(self, required_fields: List[str]) -> bool:
        """Check if required fields exist"""
        if not self.headers:
            return False
        
        missing = [f for f in required_fields if f not in self.headers]
        if missing:
            logger.warning(f"Missing fields: {missing}")
            return False
        return True
    
    def get_field_value(self, field_name: str, default: str = '') -> str:
        """Get field value from latest entry"""
        if self.latest_entry is None:
            self.get_latest_entry()
        
        value = self.latest_entry.get(field_name, default)
        return safe_str(value, default)
    
    def get_column_info(self) -> Dict[str, Any]:
        """Get CSV information"""
        if not self.data:
            self.load_data()
        
        return {
            'total_columns': len(self.headers),
            'total_rows': len(self.data),
            'columns': list(self.headers)
        }
    
    def export_latest_entry(self, output_path: str) -> bool:
        """Export latest entry to CSV"""
        try:
            if self.latest_entry is None:
                self.get_latest_entry()
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.headers)
                writer.writeheader()
                writer.writerow(self.latest_entry)
            
            logger.info(f"Exported to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            return False
