"""
Test OCR on Enhanced Images
Tests if image enhancement improves OCR results for phone screenshots
"""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from src.mistral_ai import MistralClient
from src.ocr import _ocr_image_plain

load_dotenv()


def test_enhanced_images() -> None:
    """
    Test OCR on enhanced images to see if enhancement improved results
    """
    try:
        client = MistralClient()
        print("Testing API connection for enhanced OCR...")
        if not client.test_connection():
            print("Cannot proceed with enhanced OCR due to API connection failure")
            return
    except Exception as e:
        print(f"Error initializing Mistral AI client: {e}")
        return

    # Path to enhanced images
    enhanced_dir = Path("./enhanced_images")

    if not enhanced_dir.exists():
        print(f"Enhanced images directory not found: {enhanced_dir}")
        return

    # Find all enhanced PNG files
    enhanced_files = list(enhanced_dir.glob("*_enhanced.PNG"))

    if not enhanced_files:
        print("No enhanced PNG files found")
        return

    print(f"\nTesting OCR on {len(enhanced_files)} enhanced images...")
    print("=" * 60)

    # Create output directory for enhanced OCR results
    enhanced_output_dir = Path("./output/enhanced_ocr")
    enhanced_output_dir.mkdir(parents=True, exist_ok=True)

    improved_count = 0
    total_chars_before = 0
    total_chars_after = 0

    for enhanced_file in enhanced_files:
        # Get original filename
        original_name = enhanced_file.stem.replace('_enhanced', '')

        print(f"\nTesting enhanced: {original_name}")

        # Get path to original file for comparison
        original_file = Path(f"./sample_files/{original_name}.PNG")

        if not original_file.exists():
            print(f"  Original file not found: {original_file}")
            continue

        # Read original OCR result for comparison
        original_ocr_file = Path(f"./output/individual_texts/{original_name}.txt")
        original_content = ""
        if original_ocr_file.exists():
            original_content = original_ocr_file.read_text(encoding="utf-8").strip()
            total_chars_before += len(original_content)

        # Test OCR on enhanced image
        try:
            enhanced_text = _ocr_image_plain(client, enhanced_file)
            total_chars_after += len(enhanced_text.strip())

            # Save enhanced OCR result
            enhanced_ocr_path = enhanced_output_dir / f"{original_name}_enhanced.txt"
            enhanced_ocr_path.write_text(enhanced_text.strip(), encoding="utf-8")

            # Compare results
            original_chars = len(original_content)
            enhanced_chars = len(enhanced_text.strip())

            if enhanced_chars > original_chars * 1.5:  # 50% improvement threshold
                improved_count += 1
                print(f"  IMPROVED: {original_chars} -> {enhanced_chars} chars (+{enhanced_chars-original_chars})")
                print(f"     Sample: '{enhanced_text.strip()[:100]}...'")
            elif enhanced_chars > original_chars:
                print(f"  SLIGHTLY BETTER: {original_chars} -> {enhanced_chars} chars")
            else:
                print(f"  SIMILAR: {original_chars} -> {enhanced_chars} chars")

        except Exception as e:
            error_msg = f"Error OCRing enhanced {original_name}: {e}"
            print(f"  {error_msg}")

            # Save error to file
            enhanced_ocr_path = enhanced_output_dir / f"{original_name}_enhanced.txt"
            enhanced_ocr_path.write_text(error_msg, encoding="utf-8")

    print("\nEnhancement Results Summary:")
    print(f"   - Images tested: {len(enhanced_files)}")
    print(f"   - Improved (>50% more text): {improved_count}")
    print(f"   - Total characters before: {total_chars_before}")
    print(f"   - Total characters after: {total_chars_after}")
    print(f"   - Overall improvement: {(total_chars_after-total_chars_before)/max(total_chars_before, 1)*100:.1f}%")

    if improved_count > 0:
        print("\nSuccess! Enhanced images show improved OCR results!")
        print(f"Enhanced OCR results saved in: {enhanced_output_dir}")
        print("Original OCR results in: ./output/individual_texts/")
    else:
        print("\nEnhancement did not significantly improve OCR results.")
        print("   This might indicate the images have inherent content issues.")
    print("\nRecommendations:")
    print("   - Try different enhancement parameters (more/less contrast)")
    print("   - Consider manual review of original images")
    print("   - Some images might need different preprocessing approaches")


def test_ocr_on_sample_jpg() -> None:
    """
    Test OCR on a sample JPG image.
    """
    try:
        client = MistralClient()
        print("Testing API connection for JPG OCR...")
        if not client.test_connection():
            print("Cannot proceed with JPG OCR due to API connection failure")
            return
    except Exception as e:
        print(f"Error initializing Mistral AI client: {e}")
        return

    image_path = Path("samples/sample.jpg")
    if not image_path.exists():
        print(f"Sample JPG not found at {image_path}")
        return

    print(f"Testing OCR on {image_path}...")
    try:
        text = _ocr_image_plain(client, image_path)
        assert text.strip() != ""
        print("Successfully extracted text from JPG.")
    except Exception as e:
        print(f"Error during JPG OCR test: {e}")
        assert False, f"JPG OCR test failed with exception: {e}"


if __name__ == "__main__":
    test_enhanced_images()
    test_ocr_on_sample_jpg()