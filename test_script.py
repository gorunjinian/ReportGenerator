"""
Test script to verify logo sizing and aspect ratio handling
Run this to check if your .png logos will display correctly
"""

import os
from PIL import Image as PILImage
from reportlab.lib.units import inch


def test_logo_dimensions():
    """Test logo dimension calculations with area-based sizing"""
    print("🧪 LOGO SIZING TEST - Area-Based Approach")
    print("=" * 50)

    # Constants from your config
    BILADI_LOGO_FILENAME = "Biladi logo.png"
    CER_LOGO_FILENAME = "CER Logo.png"

    target_area = 2.0  # square inches - same as in fixed code
    max_width = 3.0  # inches
    max_height = 1.2  # inches
    min_width = 1.0  # inches
    min_height = 0.6  # inches

    results = {}

    for logo_name in [BILADI_LOGO_FILENAME, CER_LOGO_FILENAME]:
        print(f"\n📊 Testing: {logo_name}")

        if not os.path.exists(logo_name):
            print(f"   ❌ File not found: {logo_name}")
            continue

        try:
            # Load and analyze the image
            with PILImage.open(logo_name) as img:
                original_width, original_height = img.size
                aspect_ratio = original_width / original_height

                print(f"   📐 Original size: {original_width} x {original_height} pixels")
                print(f"   📏 Aspect ratio: {aspect_ratio:.3f} ({'wide' if aspect_ratio > 1 else 'tall'})")

                # Calculate new dimensions using area-based approach (same logic as fixed code)
                import math

                # Calculate dimensions based on target area
                new_height_inches = math.sqrt(target_area / aspect_ratio)
                new_width_inches = new_height_inches * aspect_ratio

                # Apply constraints
                if new_width_inches > max_width or new_height_inches > max_height:
                    width_scale = max_width / new_width_inches if new_width_inches > max_width else 1.0
                    height_scale = max_height / new_height_inches if new_height_inches > max_height else 1.0
                    scale = min(width_scale, height_scale)
                    new_width_inches *= scale
                    new_height_inches *= scale

                if new_width_inches < min_width or new_height_inches < min_height:
                    width_scale = min_width / new_width_inches if new_width_inches < min_width else 1.0
                    height_scale = min_height / new_height_inches if new_height_inches < min_height else 1.0
                    scale = max(width_scale, height_scale)
                    new_width_inches *= scale
                    new_height_inches *= scale

                actual_area = new_width_inches * new_height_inches

                print(f"   📝 PDF size: {new_width_inches:.2f} x {new_height_inches:.2f} inches")
                print(f"   📐 Actual area: {actual_area:.2f} square inches")
                print(f"   ✅ Aspect ratio preserved: {(new_width_inches / new_height_inches):.3f}")

                results[logo_name] = {
                    'width': new_width_inches,
                    'height': new_height_inches,
                    'area': actual_area,
                    'aspect_ratio': aspect_ratio
                }

        except Exception as e:
            print(f"   ❌ Error reading {logo_name}: {e}")

    # Compare the results
    if len(results) == 2:
        biladi_name = BILADI_LOGO_FILENAME
        cer_name = CER_LOGO_FILENAME

        print(f"\n💡 COMPARISON:")
        if biladi_name in results and cer_name in results:
            biladi = results[biladi_name]
            cer = results[cer_name]

            area_diff = abs(biladi['area'] - cer['area'])
            area_diff_percent = (area_diff / max(biladi['area'], cer['area'])) * 100

            print(f"Area difference: {area_diff:.3f} sq in ({area_diff_percent:.1f}%)")

            if area_diff_percent < 15:
                print("✅ Logos will have similar visual weight!")
            elif area_diff_percent < 30:
                print("⚠️  Logos will have some size difference but should be acceptable")
            else:
                print("❌ Logos may still appear quite different in size")

            print(f"\nFinal sizes:")
            print(f"  Biladi: {biladi['width']:.2f} × {biladi['height']:.2f} inches")
            print(f"  CER:    {cer['width']:.2f} × {cer['height']:.2f} inches")

    print(f"\n💡 SUMMARY:")
    print("The new area-based approach ensures:")
    print("- Both logos maintain their original aspect ratios")
    print("- Both logos have similar total area (visual weight)")
    print("- Neither logo will appear dramatically smaller than the other")


def create_test_pdf():
    """Create a test PDF with just the logos to verify sizing"""
    print(f"\n🔧 Creating test PDF...")

    try:
        # Import the fixed PDF builder
        import sys
        sys.path.append('.')  # Make sure we can import from current directory

        from pdf_builder import PDFBuilder

        # Create test PDF
        builder = PDFBuilder('logo_test.pdf')
        builder.add_header_with_logos('.')  # Look for logos in current directory

        # Add some dummy content
        builder.add_section('Test Section', {'Test Field': 'This is a test to verify logo sizing'})

        if builder.generate():
            print("✅ Test PDF created: logo_test.pdf")
            print("   Open this file to check if logos look correct")
            return True
        else:
            print("❌ Failed to create test PDF")
            return False

    except Exception as e:
        print(f"❌ Error creating test PDF: {e}")
        return False


def main():
    """Run all tests"""
    print("Heritage Report Generator - Logo Sizing Test")
    print("This will verify your .png logos will display correctly\n")

    # Test 1: Analyze logo dimensions
    test_logo_dimensions()

    # Test 2: Create test PDF
    if create_test_pdf():
        print(f"\n🎉 SUCCESS!")
        print("Your logos should now display correctly with proper aspect ratios.")
        print("\nNext steps:")
        print("1. Check logo_test.pdf to verify the sizing looks good")
        print("2. Replace your pdf_builder.py with the fixed version")
        print("3. Test your full report generation")
    else:
        print(f"\n⚠️  Test PDF creation failed")
        print("Make sure you have:")
        print("- Both .png logo files in the current directory")
        print("- The updated pdf_builder.py file")
        print("- All required dependencies installed")


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")