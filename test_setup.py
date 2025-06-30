"""
Test script to verify the setup is working correctly
Run this before building the executable to ensure all dependencies are installed
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing Python setup for Heritage Report Generator...")
    print("-" * 50)
    
    # Test Python version
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("WARNING: Python 3.8 or higher is recommended")
    print()
    
    # Test required external modules
    external_modules = [
        ('pandas', 'Data processing'),
        ('reportlab', 'PDF generation'),
        ('pyinstaller', 'Executable building'),
        ('requests', 'Image downloading'),
        ('PIL', 'Image processing')
    ]
    
    all_good = True
    
    print("External dependencies:")
    for module_name, description in external_modules:
        try:
            __import__(module_name)
            print(f"✓ {module_name:<15} - {description:<25} [OK]")
        except ImportError:
            print(f"✗ {module_name:<15} - {description:<25} [MISSING]")
            all_good = False
    
    print("\nProject modules:")
    # Test project modules
    project_modules = [
        'main.py',
        'report_generator.py',
        'data_loader.py',
        'image_handler.py',
        'pdf_builder.py',
        'utils.py',
        'constants.py',
        'exceptions.py'
    ]
    
    for module_file in project_modules:
        if os.path.exists(module_file):
            print(f"✓ {module_file:<25} [EXISTS]")
        else:
            print(f"✗ {module_file:<25} [MISSING]")
            all_good = False
    
    print("-" * 50)
    
    if all_good:
        print("\n✓ All dependencies and modules are ready!")
        print("\nYou can now:")
        print("1. Run 'python build_exe.py' to create the executable")
        print("2. Test with 'python main.py your_csv_file.csv'")
    else:
        print("\n✗ Some dependencies or modules are missing!")
        print("\nFor external dependencies, run: pip install -r requirements.txt")
        print("For missing project modules, ensure all files are in the BuildFolder")
    
    return all_good

def test_sample_data():
    """Create a sample CSV for testing"""
    try:
        import pandas as pd
        from datetime import datetime
        
        print("\n\nCreating sample CSV file for testing...")
        
        # Sample data matching the expected format
        sample_data = {
            'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'Assessor\'s Name ': ['Test Assessor'],
            'Supervisor ': ['Test Supervisor'],
            'Organization': ['Test Organization'],
            'Date of Assessment': ['2024/12/15'],
            'Monument Reference ': ['TEST-001'],
            'Monument Name ': ['Test Heritage Site'],
            'Ownership ': ['Public'],
            'Governorate': ['Test Governorate'],
            'District': ['Test District'],
            'City-Village': ['Test City'],
            'Location': ['Test Location Description'],
            'Primary Display Photo Upload': ['https://drive.google.com/file/d/1234567890abcdef/view'],
            'Additional images and files ': ['https://drive.google.com/open?id=abc123, https://drive.google.com/file/d/xyz789/view'],
            'Observed structural conditions ': ['Moderate damage observed'],
            'Exterior walls condition': ['Partially damaged'],
            'Roof Conditions': ['Intact'],
            'Major Architectural Failure': ['None'],
            'Location of Major Damage': ['East wall'],
            'Evidence of Armed Conflict': ['Yes'],
            'Fire or Smoke Damage': ['No'],
            'Looting or Vandalism': ['No'],
            'Significant Cultural or Religous Symbol Damage ': ['Minor'],
            'Visible Damage to Sculptures, Catvings and Facade ': ['Yes'],
            'Damage to decorative elements ': ['Moderate'],
            'Conflict-Specific damage indicator ': ['Bullet holes'],
            'Water Infiltration and Weather Exposure ': ['Yes'],
            'Vegetation Overgrowth ': ['No'],
            'Secondary Hazards present ': ['Unstable structure'],
            'Satellite Imagery Observations': ['Visible from satellite'],
            'Eyewitness Report': ['Local residents reported damage'],
            'Testimonials': ['Community concerned about heritage loss'],
            'Potential Hazards to the public and site': ['Risk of collapse'],
            'Urgent Stabilization Required': ['Yes'],
            'Security measures needed': ['Perimeter fencing'],
            'Likelihood of continued damage': ['High'],
            'Historical or Cultural Significance': ['Important Ottoman-era building'],
            'Significance for local population': ['Central to community identity'],
            'Additional References': ['Historical records available']
        }
        
        df = pd.DataFrame(sample_data)
        df.to_csv('test_sample.csv', index=False, encoding='utf-8')
        
        print("✓ Sample CSV created: test_sample.csv")
        print("\nYou can test the program with:")
        print("python report_generator.py test_sample.csv")
        
    except Exception as e:
        print(f"Could not create sample CSV: {e}")

if __name__ == "__main__":
    if test_imports():
        test_sample_data()
    
    input("\nPress Enter to exit...")
