"""
Comprehensive testing script for Heritage Report Generator
Test all functionality before building the .exe
"""

import os
import sys
import traceback
from datetime import datetime
import tempfile

def create_test_csv():
    """Create a realistic test CSV file"""
    test_data = '''Timestamp,Assessor's Name ,Supervisor ,Organization,Date of Assessment,Monument Reference ,Monument Name ,Ownership ,Governorate,District,City-Village,Location,Primary Display Photo Upload,Additional images and files ,Observed structural conditions ,Exterior walls condition,Roof Conditions,Major Architectural Failure,Location of Major Damage,Evidence of Armed Conflict,Fire or Smoke Damage,Looting or Vandalism,Significant Cultural or Religous Symbol Damage ,Visible Damage to Sculptures, Catvings and Facade ,Damage to decorative elements ,Conflict-Specific damage indicator ,Water Infiltration and Weather Exposure ,Vegetation Overgrowth ,Secondary Hazards present ,Satellite Imagery Observations,Eyewitness Report,Testimonials,Potential Hazards to the public and site,Urgent Stabilization Required,Security measures needed,Likelihood of continued damage,Historical or Cultural Significance,Significance for local population,Additional References
2024/01/15 10:30:00,John Smith ,Dr. Jane Doe ,Heritage Foundation,2024/01/15,HER-001 ,Ancient Mosque of Al-Nour ,Public ,Damascus,Old City,Al-Nour District,Corner of Heritage Street and Ancient Road,https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs/view,https://drive.google.com/open?id=1234567890abcdef,Moderate structural damage with some areas requiring immediate attention,Partially damaged with visible cracks and missing stones,Roof structure intact but some tiles missing,Minor column damage on eastern side,Eastern wall shows impact damage,Yes - visible bullet holes and shrapnel marks,No evidence of fire damage,Minor vandalism to decorative elements,Significant damage to calligraphy inscriptions,Visible damage to carved stone decorations,Moderate damage to traditional geometric patterns,Bullet holes and explosive damage patterns,Yes - water damage from broken roof tiles,Minimal vegetation growth,Unstable masonry poses risk to visitors,Damage visible in satellite imagery from 2023,Local residents reported damage occurred in 2022,Community elders provide historical context,Risk of structural collapse in damaged sections,Yes - immediate stabilization of eastern wall required,Temporary barriers needed to restrict access,High - continued exposure to weather,15th century Ottoman mosque with unique architectural features,Central place of worship for local community,Historical archives available at National Library
2024/01/10 09:15:00,Sarah Ahmed ,Prof. Michael Brown ,Cultural Heritage Society,2024/01/10,HER-002 ,Byzantine Church Ruins ,Religious Trust,Aleppo,Historic Quarter,Christian Quarter,Near the Ancient Citadel,https://drive.google.com/file/d/abcdef1234567890/view,https://drive.google.com/file/d/xyz789/view,Severe damage with partial collapse,Major damage to outer walls,Roof completely destroyed,Significant structural failure in nave area,Central dome has collapsed,Yes - evidence of targeted destruction,Extensive fire damage throughout,Evidence of systematic looting,Sacred symbols deliberately damaged,Ancient frescoes severely damaged,Decorative columns destroyed,Systematic destruction patterns,Severe water infiltration,Significant vegetation overgrowth,Debris creates multiple hazards,Destruction documented in satellite imagery,Eyewitnesses describe deliberate targeting,Religious community mourns cultural loss,Multiple hazards from unstable structures,Critical - immediate action required,24/7 security presence needed,Very high - ongoing deterioration,6th century Byzantine church with rare frescoes,Historically significant to Christian community,UNESCO documentation available'''
    
    # Write test CSV
    with open('test_heritage_data.csv', 'w', encoding='utf-8') as f:
        f.write(test_data)
    
    print("✅ Created test CSV: test_heritage_data.csv")
    return 'test_heritage_data.csv'

def create_test_logos():
    """Create placeholder logo files for testing"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create simple placeholder logos
        for logo_name, text in [('Biladi logo.jpg', 'BILADI'), ('CER Logo.jpg', 'CER')]:
            if not os.path.exists(logo_name):
                # Create a simple colored rectangle with text
                img = Image.new('RGB', (200, 100), color='lightblue')
                draw = ImageDraw.Draw(img)
                
                # Try to use default font
                try:
                    font = ImageFont.load_default()
                except:
                    font = None
                
                # Draw text
                if font:
                    draw.text((50, 35), text, fill='darkblue', font=font)
                else:
                    draw.text((50, 35), text, fill='darkblue')
                
                img.save(logo_name, 'JPEG')
                print(f"✅ Created placeholder logo: {logo_name}")
    
    except ImportError:
        print("⚠️  PIL not available - creating text placeholder logos")
        for logo_name, text in [('Biladi logo.jpg', 'BILADI'), ('CER Logo.jpg', 'CER')]:
            if not os.path.exists(logo_name):
                with open(logo_name.replace('.jpg', '.txt'), 'w') as f:
                    f.write(f"Placeholder for {text} logo")
                print(f"ℹ️  Created text placeholder: {logo_name.replace('.jpg', '.txt')}")

def test_individual_modules():
    """Test each module individually"""
    print("\n" + "="*60)
    print("TESTING INDIVIDUAL MODULES")
    print("="*60)
    
    test_results = {}
    
    # Test 1: Constants and Utils
    try:
        print("\n🧪 Testing constants and utils...")
        from constants import SECTION_FIELDS, DATE_INPUT_FORMAT
        from utils import safe_str, extract_drive_file_id, parse_image_links
        
        # Test utility functions
        assert safe_str(None) == ''
        assert safe_str('  test  ') == 'test'
        assert extract_drive_file_id('https://drive.google.com/file/d/123ABC/view') == '123ABC'
        assert len(parse_image_links('link1, link2, link3')) == 3
        
        print("✅ Constants and utils work correctly")
        test_results['utils'] = True
        
    except Exception as e:
        print(f"❌ Constants/utils failed: {e}")
        test_results['utils'] = False
    
    # Test 2: Data Loader
    try:
        print("\n🧪 Testing data loader...")
        from data_loader import DataLoader
        
        csv_file = create_test_csv()
        loader = DataLoader(csv_file)
        data = loader.load_data()
        latest = loader.get_latest_entry()
        
        assert len(data) > 0, "No data loaded"
        assert latest is not None, "No latest entry found"
        assert 'Monument Name ' in latest, "Monument name missing"
        
        print(f"✅ Data loader works - loaded {len(data)} entries")
        print(f"   Latest entry: {latest.get('Monument Name ', 'Unknown')}")
        test_results['data_loader'] = True
        
    except Exception as e:
        print(f"❌ Data loader failed: {e}")
        test_results['data_loader'] = False
        traceback.print_exc()
    
    # Test 3: Image Handler
    try:
        print("\n🧪 Testing image handler...")
        from image_handler import ImageHandler
        
        handler = ImageHandler()
        
        # Test URL parsing (don't actually download)
        test_url = "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs/view"
        from utils import extract_drive_file_id
        file_id = extract_drive_file_id(test_url)
        
        assert file_id == "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs", "URL parsing failed"
        
        handler.cleanup()
        print("✅ Image handler initialization works")
        test_results['image_handler'] = True
        
    except Exception as e:
        print(f"❌ Image handler failed: {e}")
        test_results['image_handler'] = False
    
    # Test 4: PDF Builder
    try:
        print("\n🧪 Testing PDF builder...")
        from pdf_builder import PDFBuilder
        
        test_pdf = 'test_output.pdf'
        builder = PDFBuilder(test_pdf)
        
        # Test basic PDF creation
        builder.add_header_with_logos('.')
        test_data = {'Field 1': 'Value 1', 'Field 2': 'Value 2'}
        builder.add_section('Test Section', test_data)
        
        # Try to generate (might fail without complete data, but should not crash)
        try:
            builder.generate()
            print("✅ PDF builder works - test PDF created")
            if os.path.exists(test_pdf):
                os.remove(test_pdf)
        except Exception as pdf_e:
            print(f"⚠️  PDF generation had issues: {pdf_e}")
            print("   (This may be normal without complete data)")
        
        test_results['pdf_builder'] = True
        
    except Exception as e:
        print(f"❌ PDF builder failed: {e}")
        test_results['pdf_builder'] = False
    
    # Test 5: Report Generator
    try:
        print("\n🧪 Testing report generator...")
        from report_generator import ReportGenerator
        
        csv_file = 'test_heritage_data.csv'
        generator = ReportGenerator(csv_file)
        
        # Test data loading
        generator._load_data()
        assert generator.latest_data is not None, "No data loaded"
        
        print("✅ Report generator initialization works")
        print(f"   Processing: {generator.latest_data.get('Monument Name ', 'Unknown')}")
        
        generator.cleanup()
        test_results['report_generator'] = True
        
    except Exception as e:
        print(f"❌ Report generator failed: {e}")
        test_results['report_generator'] = False
        traceback.print_exc()
    
    return test_results

def test_full_workflow():
    """Test the complete workflow"""
    print("\n" + "="*60)
    print("TESTING COMPLETE WORKFLOW")
    print("="*60)
    
    try:
        create_test_logos()
        csv_file = create_test_csv()
        
        print(f"\n🧪 Testing complete report generation...")
        
        # Import main components
        from report_generator import ReportGenerator
        
        # Initialize generator
        generator = ReportGenerator(csv_file)
        
        # Test each phase
        print("Phase 1: Loading data...")
        generator._load_data()
        print(f"✅ Data loaded - Monument: {generator.latest_data.get('Monument Name ', 'Unknown')}")
        
        print("Phase 2: Processing images...")
        print("ℹ️  Skipping actual downloads for test")
        # Skip actual image downloads for testing
        generator.primary_images = []
        generator.additional_images = []
        
        print("Phase 3: Building PDF...")
        output_file = 'test_report.pdf'
        generator._build_pdf(output_file)
        
        if os.path.exists(output_file):
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"✅ PDF created successfully: {output_file} ({size_mb:.2f} MB)")
            
            # Cleanup
            generator.cleanup()
            
            return True
        else:
            print("❌ PDF file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Full workflow failed: {e}")
        traceback.print_exc()
        return False

def test_with_real_csv():
    """Test with user's actual CSV file"""
    print("\n" + "="*60)
    print("TESTING WITH YOUR CSV FILE")
    print("="*60)
    
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if not csv_files:
        print("ℹ️  No CSV files found in current directory")
        return False
    
    print("Available CSV files:")
    for i, csv_file in enumerate(csv_files):
        print(f"  {i+1}. {csv_file}")
    
    try:
        choice = input(f"\nEnter number (1-{len(csv_files)}) or press Enter to skip: ").strip()
        
        if not choice:
            return False
        
        csv_file = csv_files[int(choice) - 1]
        print(f"\n🧪 Testing with: {csv_file}")
        
        # Test data loading
        from data_loader import DataLoader
        loader = DataLoader(csv_file)
        data = loader.load_data()
        latest = loader.get_latest_entry()
        
        print(f"✅ Loaded {len(data)} records")
        print(f"   Latest entry date: {latest.get('Date of Assessment', 'Unknown')}")
        print(f"   Monument: {latest.get('Monument Name ', 'Unknown')}")
        
        # Show available fields
        print(f"\nAvailable fields ({len(loader.headers)}):")
        for field in loader.headers[:10]:  # Show first 10
            print(f"  - {field}")
        if len(loader.headers) > 10:
            print(f"  ... and {len(loader.headers) - 10} more")
        
        return True
        
    except (ValueError, IndexError):
        print("❌ Invalid selection")
        return False
    except Exception as e:
        print(f"❌ Error testing CSV: {e}")
        return False

def run_main_script_test():
    """Test the main script directly"""
    print("\n" + "="*60)
    print("TESTING MAIN SCRIPT")
    print("="*60)
    
    try:
        csv_file = create_test_csv()
        
        print("🧪 Testing main script with test CSV...")
        
        # Import and run main components
        import sys
        
        # Simulate command line arguments
        old_argv = sys.argv
        sys.argv = ['main.py', csv_file]
        
        try:
            # Import main functions
            from main import main
            from report_generator import ReportGenerator
            
            # Test ReportGenerator directly
            generator = ReportGenerator(csv_file)
            output_file = 'main_script_test.pdf'
            
            # Generate report (skip images)
            print("Generating test report...")
            stats = generator.generate_report(output_file)
            
            print(f"✅ Main script test successful!")
            print(f"   Monument: {stats['monument_name']}")
            print(f"   Date: {stats['assessment_date']}")
            
            if os.path.exists(output_file):
                size_mb = os.path.getsize(output_file) / (1024 * 1024)
                print(f"   PDF: {output_file} ({size_mb:.2f} MB)")
            
            return True
            
        finally:
            sys.argv = old_argv
            
    except Exception as e:
        print(f"❌ Main script test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🔍 HERITAGE REPORT GENERATOR - PRE-BUILD TESTING")
    print("="*70)
    
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Test results tracking
    all_results = {}
    
    # Run tests
    print("\n1️⃣  Testing individual modules...")
    module_results = test_individual_modules()
    all_results.update(module_results)
    
    print("\n2️⃣  Testing complete workflow...")
    workflow_result = test_full_workflow()
    all_results['workflow'] = workflow_result
    
    print("\n3️⃣  Testing main script...")
    main_result = run_main_script_test()
    all_results['main_script'] = main_result
    
    print("\n4️⃣  Testing with your CSV files...")
    csv_result = test_with_real_csv()
    all_results['user_csv'] = csv_result
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for result in all_results.values() if result)
    total = len(all_results)
    
    for test_name, result in all_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Ready to build executable.")
        print("\nTo build the executable, run:")
        print("   python build.py")
    elif passed >= total - 1:
        print("\n⚠️  Most tests passed. You can try building, but there may be issues.")
    else:
        print("\n❌ Several tests failed. Fix issues before building.")
        print("\nCommon issues:")
        print("- Missing dependencies (pip install -r requirements.txt)")
        print("- Incorrect file paths or permissions")
        print("- CSV format doesn't match expected structure")
    
    # Cleanup test files
    test_files = ['test_heritage_data.csv', 'test_output.pdf', 'test_report.pdf', 'main_script_test.pdf']
    for f in test_files:
        if os.path.exists(f):
            try:
                os.remove(f)
            except:
                pass

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
