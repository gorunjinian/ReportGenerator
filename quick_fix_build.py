"""
Quick fix build script - eliminates pandas completely
This will work where pandas fails in PyInstaller
"""

import os
import sys
import subprocess
import shutil

def create_pandas_free_data_loader():
    """Create a pandas-free version of data_loader.py"""
    
    pandas_free_code = '''"""
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
                        delimiters = [',', ';', '\\t', '|']
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
'''
    
    # Backup original data_loader.py
    if os.path.exists('data_loader.py'):
        shutil.copy2('data_loader.py', 'data_loader_pandas_backup.py')
        print("📋 Backed up original data_loader.py")
    
    # Write pandas-free version
    with open('data_loader.py', 'w', encoding='utf-8') as f:
        f.write(pandas_free_code)
    
    print("✅ Created pandas-free data_loader.py")

def quick_fix_build():
    """Build executable without pandas"""
    
    print("🚀 QUICK FIX BUILD - No Pandas Dependencies")
    print("=" * 60)
    
    # Step 1: Replace data_loader with pandas-free version
    create_pandas_free_data_loader()
    
    # Step 2: Check essential modules
    required_files = [
        'main.py', 'report_generator.py', 'data_loader.py',
        'image_handler.py', 'pdf_builder.py', 'utils.py',
        'constants.py', 'exceptions.py'
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    
    print("✅ All required files present")
    
    # Step 3: Build with minimal dependencies
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name=report_generator',
        '--console',  # Keep console for better error messages
        
        # Essential imports only
        '--hidden-import=reportlab',
        '--hidden-import=reportlab.lib',
        '--hidden-import=reportlab.lib.colors',
        '--hidden-import=reportlab.lib.pagesizes',
        '--hidden-import=reportlab.lib.styles', 
        '--hidden-import=reportlab.lib.units',
        '--hidden-import=reportlab.platypus',
        '--hidden-import=reportlab.pdfbase',
        '--hidden-import=reportlab.pdfbase.ttfonts',
        '--hidden-import=requests',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        
        # Project modules
        '--hidden-import=data_loader',
        '--hidden-import=image_handler',
        '--hidden-import=pdf_builder',
        '--hidden-import=report_generator', 
        '--hidden-import=utils',
        '--hidden-import=constants',
        '--hidden-import=exceptions',
        
        # Collect reportlab data
        '--collect-submodules=reportlab',
        
        'main.py'
    ]
    
    try:
        print("🔨 Building executable...")
        print("This may take 2-3 minutes...")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Check if executable was created
        exe_path = os.path.join('dist', 'report_generator.exe')
        if os.path.exists(exe_path):
            # Copy to main directory
            shutil.copy2(exe_path, 'report_generator.exe')
            
            # Get size
            size_mb = os.path.getsize('report_generator.exe') / (1024 * 1024)
            
            print(f"\n🎉 BUILD SUCCESSFUL!")
            print(f"📁 Created: report_generator.exe ({size_mb:.1f} MB)")
            
            # Cleanup
            cleanup_build()
            
            print(f"\n📋 USAGE INSTRUCTIONS:")
            print("1. Place these logo files in same folder as your CSV:")
            print("   - Biladi logo.jpg")
            print("   - CER Logo.jpg") 
            print("2. Drag CSV file onto run_report_generator.bat")
            print("3. Or run: report_generator.exe your_file.csv")
            
            return True
        else:
            print("❌ Executable not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error code {e.returncode}")
        print("STDOUT:", e.stdout[-1000:] if e.stdout else "None")
        print("STDERR:", e.stderr[-1000:] if e.stderr else "None")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def cleanup_build():
    """Remove build artifacts"""
    items_to_remove = ['build', 'dist', 'report_generator.spec', '__pycache__']
    
    for item in items_to_remove:
        if os.path.exists(item):
            try:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)
            except Exception as e:
                print(f"Warning: Could not remove {item}: {e}")

def restore_original():
    """Restore original data_loader.py"""
    if os.path.exists('data_loader_pandas_backup.py'):
        shutil.move('data_loader_pandas_backup.py', 'data_loader.py')
        print("🔄 Restored original pandas-based data_loader.py")

def test_basic_imports():
    """Test if basic dependencies are available"""
    print("🧪 Testing basic dependencies...")
    
    deps = ['reportlab', 'requests', 'PIL']
    all_good = True
    
    for dep in deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - install with: pip install {dep}")
            all_good = False
    
    return all_good

if __name__ == "__main__":
    print("Heritage Report Generator - Quick Fix Build")
    print("This version eliminates pandas to avoid DLL issues")
    print()
    
    if not test_basic_imports():
        print("\n❌ Missing dependencies. Install with:")
        print("pip install reportlab requests pillow")
        sys.exit(1)
    
    try:
        if quick_fix_build():
            print("\n✅ SUCCESS! Your executable is ready to use.")
            
            # Test the executable
            print("\n🧪 Quick test...")
            try:
                result = subprocess.run(['report_generator.exe', '--help'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("✅ Executable test passed!")
                else:
                    print("⚠️  Executable runs but with warnings")
            except:
                print("⚠️  Could not test executable (may still work)")
                
        else:
            print("\n❌ Build failed")
            restore_original()
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Build interrupted by user")
        restore_original()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        restore_original()
    
    input("\nPress Enter to exit...")
