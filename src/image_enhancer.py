"""
Image Enhancement Script for Phone Screenshots
Optimizes white screen screenshots with black text for better OCR results
"""

from pathlib import Path
from typing import List, Tuple

try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    print("PIL (Pillow) not available. Please install it: pip install Pillow")
    PIL_AVAILABLE = False

def enhance_phone_screenshot(image_path: Path, output_path: Path) -> bool:
    """
    Enhance a phone screenshot for better OCR results.

    Args:
        image_path: Path to original screenshot
        output_path: Path to save enhanced image

    Returns:
        True if enhancement was successful
    """
    if not PIL_AVAILABLE:
        print("PIL not available. Cannot enhance images.")
        return False

    try:
        # Open the image
        img = Image.open(image_path)

        # Convert to RGB if not already
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Store original size
        original_width, original_height = img.size
        print(f"  Original size: {original_width}x{original_height}")

        # 1. Increase contrast significantly (white background, black text)
        contrast_enhancer = ImageEnhance.Contrast(img)
        enhanced_img = contrast_enhancer.enhance(3.0)  # 3x contrast boost

        # 2. Sharpen the text
        enhanced_img = enhanced_img.filter(ImageFilter.SHARPEN)

        # 3. Additional sharpening for better text clarity
        enhanced_img = enhanced_img.filter(ImageFilter.SHARPEN)

        # 4. Enhance brightness slightly if needed
        brightness_enhancer = ImageEnhance.Brightness(enhanced_img)
        enhanced_img = brightness_enhancer.enhance(1.1)  # Slight brightness increase

        # Save enhanced image
        enhanced_img.save(output_path, 'PNG', quality=95)

        # Show enhancement info
        enhanced_width, enhanced_height = enhanced_img.size
        print(f"  Enhanced size: {enhanced_width}x{enhanced_height}")
        print(f"  Saved to: {output_path}")

        return True

    except Exception as e:
        print(f"  Error enhancing {image_path}: {e}")
        return False

def enhance_images_in_folder(input_dir: Path, output_dir: Path = Path("./enhanced-images")) -> List[Tuple[Path, Path]]:
    """
    Enhance all images in a folder and save PNG outputs with _enhanced suffix.

    Args:
        input_dir: Directory containing images
        output_dir: Where to write enhanced PNGs

    Returns:
        List of tuples (original_path, enhanced_path)
    """
    supported_exts = {".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"}
    output_dir.mkdir(parents=True, exist_ok=True)

    enhanced_files: List[Tuple[Path, Path]] = []

    for img_path in sorted(input_dir.iterdir()):
        if not img_path.is_file() or img_path.suffix not in supported_exts:
            continue
        # Always output PNG with _enhanced suffix
        enhanced_path = output_dir / f"{img_path.stem}_enhanced.PNG"
        if enhance_phone_screenshot(img_path, enhanced_path):
            enhanced_files.append((img_path, enhanced_path))
            print(f"  Enhanced: {img_path.name} -> {enhanced_path.name}")
        else:
            print(f"  Failed to enhance: {img_path.name}")

    print(f"\nEnhancement completed! {len(enhanced_files)} file(s) written to {output_dir}")
    return enhanced_files