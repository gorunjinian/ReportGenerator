"""
Module testing script for Heritage Report Generator
Use this to test individual modules
"""

import sys
import os


def test_data_loader():
    """Test the data loader module"""
    print("\n" + "="*60)
    print("Testing DataLoader Module")
    print("="*60)
    
    try:
        from data_loader import DataLoader
        
        # Get test CSV file
        csv_file = input("Enter path to test CSV file: ").strip()
        if not os.path.exists(csv_file):
            print("File not found!")
            return
        
        # Test loading
        loader = DataLoader(csv_file)
        loader.load_data()
        
        # Get column info
        info = loader.get_column_info()
        print(f"\nCSV Information:")
        print(f"- Total rows: {info['total_rows']}")
        print(f"- Total columns: {info['total_columns']}")
        
        # Get latest entry
        latest = loader.get_latest_entry()
        print(f"\nLatest entry date: {latest.get('Date of Assessment', 'Unknown')}")
        print(f"Monument: {latest.get('Monument Name ', 'Unknown')}")
        
        print("\n✓ DataLoader test passed!")
        
    except Exception as e:
        print(f"\n✗ DataLoader test failed: {e}")
        import traceback
        traceback.print_exc()


def test_image_handler():
    """Test the image handler module"""
    print("\n" + "="*60)
    print("Testing ImageHandler Module")
    print("="*60)
    
    try:
        from image_handler import ImageHandler
        
        # Get test URL
        test_url = input("Enter Google Drive image URL: ").strip()
        if not test_url:
            print("No URL provided!")
            return
        
        # Test downloading
        handler = ImageHandler()
        
        print("\nDownloading image...")
        result = handler.download_drive_image(test_url, "test_image")
        
        if result:
            print(f"✓ Image downloaded successfully: {result}")
            stats = handler.get_download_stats()
            print(f"  Size: {stats['total_size_mb']} MB")
        else:
            print("✗ Failed to download image")
        
        # Cleanup
        handler.cleanup()
        
    except Exception as e:
        print(f"\n✗ ImageHandler test failed: {e}")
        import traceback
        traceback.print_exc()


def test_pdf_builder():
    """Test the PDF builder module"""
    print("\n" + "="*60)
    print("Testing PDFBuilder Module")
    print("="*60)
    
    try:
        from pdf_builder import PDFBuilder
        
        # Create test PDF
        output_path = "test_report.pdf"
        
        builder = PDFBuilder(output_path)
        
        # Add header
        builder.add_header_with_logos(".")
        
        # Add test sections
        test_data = {
            "Field 1": "Test Value 1",
            "Field 2": "Test Value 2",
            "Field 3": "Test Value 3"
        }
        
        builder.add_section("Test Section 1", test_data)
        builder.add_section("Test Section 2", test_data)
        
        # Generate PDF
        if builder.generate():
            print(f"\n✓ Test PDF created: {output_path}")
        else:
            print("\n✗ Failed to create PDF")
        
    except Exception as e:
        print(f"\n✗ PDFBuilder test failed: {e}")
        import traceback
        traceback.print_exc()


def test_utils():
    """Test utility functions"""
    print("\n" + "="*60)
    print("Testing Utils Module")
    print("="*60)
    
    try:
        from utils import extract_drive_file_id, parse_image_links, safe_str
        
        # Test URL extraction
        test_urls = [
            "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs/view",
            "https://drive.google.com/open?id=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs",
            "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs"
        ]
        
        print("\nTesting Google Drive URL extraction:")
        for url in test_urls:
            file_id = extract_drive_file_id(url)
            print(f"  {url[:50]}... → {file_id}")
        
        # Test link parsing
        links_str = "link1.com, link2.com, link3.com"
        parsed = parse_image_links(links_str)
        print(f"\nParsed links: {parsed}")
        
        # Test safe string
        print(f"\nSafe string tests:")
        print(f"  None → '{safe_str(None)}'")
        print(f"  '  test  ' → '{safe_str('  test  ')}'")
        
        print("\n✓ Utils test passed!")
        
    except Exception as e:
        print(f"\n✗ Utils test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main test menu"""
    print("Heritage Report Generator - Module Testing")
    print("=" * 60)
    
    while True:
        print("\nSelect module to test:")
        print("1. DataLoader (CSV reading)")
        print("2. ImageHandler (Image downloading)")
        print("3. PDFBuilder (PDF generation)")
        print("4. Utils (Utility functions)")
        print("5. Run all tests")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-5): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            test_data_loader()
        elif choice == '2':
            test_image_handler()
        elif choice == '3':
            test_pdf_builder()
        elif choice == '4':
            test_utils()
        elif choice == '5':
            test_utils()
            test_data_loader()
            test_image_handler()
            test_pdf_builder()
        else:
            print("Invalid choice!")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
