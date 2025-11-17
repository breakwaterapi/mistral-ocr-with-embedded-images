import sys
from pathlib import Path

from dotenv import load_dotenv

from src.image_enhancer import enhance_images_in_folder
from src.ocr import process_images

load_dotenv()


def enhance_images_cli():
    """CLI flow for enhancing images."""
    input_dir_str = input("Enter the input directory for images (default: samples): ") or "samples"
    output_dir_str = input("Enter the output directory for enhanced images (default: enhanced-images): ") or "enhanced-images"
    
    input_dir = Path(input_dir_str)
    output_dir = Path(output_dir_str)

    if not input_dir.is_dir():
        print(f"Error: Input directory not found at '{input_dir}'")
        return

    print(f"Enhancing images in '{input_dir}' and saving to '{output_dir}'...")
    enhance_images_in_folder(input_dir=input_dir, output_dir=output_dir)
    print("Image enhancement complete.")


def ocr_samples_cli():
    """CLI flow for running OCR on sample images."""
    print("Running OCR on sample images...")
    process_images(
        input_dir="samples",
        output_dir="output/individual_texts",
        combined_output_path="output/combined_text.txt",
        glob_patterns=["*.PNG", "*.png", "*.JPG", "*.JPEG", "*.jpg", "*.jpeg"],
        enhanced=False
    )
    print("OCR on samples complete.")


def ocr_enhanced_cli():
    """CLI flow for running OCR on enhanced images."""
    print("Running OCR on enhanced images...")
    process_images(
        input_dir="enhanced_images",
        output_dir="output/enhanced_ocr",
        combined_output_path="output/final_enhanced_ocr.txt",
        glob_patterns=["*_enhanced.PNG"],
        enhanced=True
    )
    print("OCR on enhanced images complete.")


def enhance_and_ocr_cli():
    """CLI flow for enhancing images and then running OCR."""
    input_dir_str = input("Enter the input directory for images (default: samples): ") or "samples"
    output_dir_str = input("Enter the output directory for enhanced images (default: enhanced-images): ") or "enhanced-images"

    input_dir = Path(input_dir_str)
    output_dir = Path(output_dir_str)

    if not input_dir.is_dir():
        print(f"Error: Input directory not found at '{input_dir}'")
        return

    # Step 1: Enhance images
    print(f"Step 1/2: Enhancing images in '{input_dir}' and saving to '{output_dir}'...")
    enhance_images_in_folder(input_dir=input_dir, output_dir=output_dir)
    print("Image enhancement complete.")

    # Step 2: OCR enhanced images
    print("Step 2/2: Performing OCR on enhanced images...")
    process_images(
        input_dir=output_dir_str,
        output_dir="output/enhanced_ocr",
        combined_output_path="output/final_enhanced_ocr.txt",
        glob_patterns=["*_enhanced.PNG"],
        enhanced=True
    )
    print("Enhance and OCR process complete.")


def main_menu():
    """Displays the main menu and handles user input."""
    while True:
        print("\n--- OCR & Image Enhancement Tool ---")
        print("1. Enhance Images")
        print("2. Run OCR on Samples")
        print("3. Run OCR on Enhanced Images")
        print("4. Enhance and OCR")
        print("5. Exit")
        
        choice = input("Please choose an option (1-5): ")
        
        if choice == '1':
            enhance_images_cli()
        elif choice == '2':
            ocr_samples_cli()
        elif choice == '3':
            ocr_enhanced_cli()
        elif choice == '4':
            enhance_and_ocr_cli()
        elif choice == '5':
            print("Exiting.")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


def main():
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
