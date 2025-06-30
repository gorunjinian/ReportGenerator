"""
Main entry point for Heritage Report Generator

This is the main script that should be compiled into an executable.
"""

import sys
import os
import argparse
import logging
from datetime import datetime

from report_generator import ReportGenerator
from utils import validate_csv_path, generate_output_filename, setup_logging
from exceptions import ReportGeneratorError

# Version information
VERSION = "2.0.0"
PROGRAM_NAME = "Heritage Site Assessment Report Generator"


def print_banner():
    """Print program banner"""
    print("=" * 60)
    print(f"{PROGRAM_NAME}")
    print(f"Version {VERSION}")
    print("=" * 60)
    print()


def main():
    """Main program entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=PROGRAM_NAME,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'csv_file',
        nargs='?',
        help='Path to CSV file containing assessment data'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output PDF filename (default: auto-generated with timestamp)'
    )
    
    parser.add_argument(
        '-l', '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        help='Save logs to file'
    )
    
    parser.add_argument(
        '--export-images',
        help='Export downloaded images to specified directory'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'{PROGRAM_NAME} {VERSION}'
    )
    
    args = parser.parse_args()
    
    # If no CSV file provided, show usage
    if not args.csv_file:
        print_banner()
        print("Usage: Drag and drop a CSV file onto the program")
        print("   or: main.exe <csv_file> [options]")
        print()
        print("For more options: main.exe --help")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Setup logging
    setup_logging(args.log_file, args.log_level)
    logger = logging.getLogger(__name__)
    
    # Print banner
    print_banner()
    
    # Validate CSV file
    csv_path = args.csv_file
    if not validate_csv_path(csv_path):
        print(f"Error: Invalid CSV file: {csv_path}")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Generate output filename if not provided
    output_path = args.output or generate_output_filename(csv_path)
    
    # Initialize report generator
    generator = None
    
    try:
        print(f"Processing: {os.path.basename(csv_path)}")
        print("\nPhase 1: Loading data...")
        
        # Create report generator
        generator = ReportGenerator(csv_path)
        
        print("Phase 2: Downloading images from Google Drive...")
        print("(This may take a while depending on internet speed)\n")
        
        # Generate report
        stats = generator.generate_report(output_path)
        
        # Export images if requested
        if args.export_images:
            print(f"\nExporting images to: {args.export_images}")
            generator.export_images(args.export_images)
        
        # Print results
        print("\n" + "=" * 60)
        print("✓ REPORT GENERATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Output file: {output_path}")
        print(f"File size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
        print()
        print("Report Details:")
        print(f"  - Monument: {stats['monument_name']}")
        print(f"  - Assessment Date: {stats['assessment_date']}")
        print(f"  - Images Downloaded: {stats['total_images']}")
        print(f"  - Image Data Size: {stats['total_image_size_mb']} MB")
        print("=" * 60)
        
    except ReportGeneratorError as e:
        logger.error(f"Report generation error: {e}")
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("  1. Internet connection is active")
        print("  2. Google Drive links are valid and accessible")
        print("  3. CSV file format is correct")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"\n❌ Unexpected error: {e}")
        print("\nPlease report this error with the log file if available")
        
    finally:
        # Cleanup
        if generator:
            try:
                generator.cleanup()
            except:
                pass
        
        # Wait for user input before closing
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
