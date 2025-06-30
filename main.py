"""
Main entry point for Heritage Report Generator

This is the main script that should be compiled into an executable.
Supports both GUI and command-line interfaces.
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
VERSION = "2.1.0"
PROGRAM_NAME = "Heritage Site Assessment Report Generator"


def print_banner():
    """Print program banner"""
    print("=" * 60)
    print(f"{PROGRAM_NAME}")
    print(f"Version {VERSION}")
    print("=" * 60)
    print()


def run_gui_mode():
    """Launch GUI interface"""
    try:
        from gui_interface import run_gui
        print("Launching GUI interface...")
        run_gui()
        return True
    except ImportError as e:
        print(f"GUI not available: {e}")
        print("GUI dependencies may not be installed.")
        print("Falling back to command line mode...")
        return False
    except Exception as e:
        print(f"GUI error: {e}")
        print("Falling back to command line mode...")
        return False


def run_command_line_mode(args):
    """Run in command line mode"""

    # Setup logging
    setup_logging(args.log_file, args.log_level)
    logger = logging.getLogger(__name__)

    # Print banner for command line mode
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

        return True

    except ReportGeneratorError as e:
        logger.error(f"Report generation error: {e}")
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("  1. Internet connection is active")
        print("  2. Google Drive links are valid and accessible")
        print("  3. CSV file format is correct")
        return False

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        return False

    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"\n❌ Unexpected error: {e}")
        print("\nPlease report this error with the log file if available")
        return False

    finally:
        # Cleanup
        if generator:
            try:
                generator.cleanup()
            except:
                pass


def show_command_line_usage():
    """Show command line usage information"""
    print_banner()
    print("USAGE OPTIONS:")
    print()
    print("GUI Mode (Recommended):")
    print("  main.exe                    # Opens graphical interface")
    print("  main.exe --gui              # Force GUI mode")
    print()
    print("Command Line Mode:")
    print("  main.exe <csv_file>         # Generate report from CSV")
    print("  main.exe --no-gui <csv_file> # Force command line mode")
    print()
    print("Examples:")
    print("  main.exe heritage_data.csv")
    print("  main.exe data.csv --output my_report.pdf")
    print("  main.exe data.csv --export-images ./images/")
    print()
    print("For all options: main.exe --help")
    print()
    print("REQUIREMENTS:")
    print("  - Internet connection (for downloading images)")
    print("  - Logo files in same directory as CSV:")
    print("    • Biladi logo.jpg")
    print("    • CER Logo.jpg")


def main():
    """Main program entry point"""

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=PROGRAM_NAME,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Open GUI interface
  %(prog)s data.csv                 # Generate report from CSV
  %(prog)s --gui                    # Force GUI mode
  %(prog)s --no-gui data.csv        # Force command line mode
  %(prog)s data.csv -o report.pdf   # Specify output filename

Requirements:
  - Internet connection for downloading Google Drive images
  - Logo files (Biladi logo.jpg, CER Logo.jpg) in same folder as CSV
  - Google Drive images must be publicly accessible
        """
    )

    parser.add_argument(
        'csv_file',
        nargs='?',  # Make csv_file optional
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
        '--gui',
        action='store_true',
        help='Force GUI mode even with command line arguments'
    )

    parser.add_argument(
        '--no-gui',
        action='store_true',
        help='Force command line mode, show usage if no CSV provided'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Run basic functionality tests'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'{PROGRAM_NAME} {VERSION}'
    )

    args = parser.parse_args()

    # Handle test mode
    if args.test:
        try:
            from test_before_build import main as test_main
            test_main()
            return
        except ImportError:
            print("Test module not available")
            sys.exit(1)

    # Determine interface mode
    use_gui = False

    if args.gui:
        # Force GUI mode
        use_gui = True
    elif args.no_gui:
        # Force command line mode
        use_gui = False
    elif not args.csv_file:
        # No CSV file provided and not forced to command line - try GUI
        use_gui = True
    else:
        # CSV file provided - use command line by default
        use_gui = False

    # Launch appropriate interface
    if use_gui:
        # Try to launch GUI
        if run_gui_mode():
            return  # GUI ran successfully
        else:
            # GUI failed, fall back to command line
            if not args.csv_file:
                show_command_line_usage()
                input("\nPress Enter to exit...")
                sys.exit(1)
            # If we have a CSV file, continue to command line mode

    # Command line mode
    if not args.csv_file:
        show_command_line_usage()
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Run command line interface
    success = run_command_line_mode(args)

    # Wait for user input before closing (only in standalone mode)
    if not sys.stdin.isatty():
        # Running in a way where we shouldn't wait for input
        pass
    else:
        input("\nPress Enter to exit...")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)