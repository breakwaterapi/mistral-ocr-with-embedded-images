"""
Consolidated OCR Processing Module
"""

import os
import re
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from src.mistral_ai import MistralClient

load_dotenv()


def _ocr_image_plain(client: MistralClient, image_path: Path) -> str:
    """
    Call the existing mistral_client.ocr_image but strip any embedded images
    and return plain text only. The current client returns markdown with
    embedded images; we will remove markdown image tags.
    """
    markdown = client.ocr_image(str(image_path))

    # Remove markdown image tags: ![alt](src)
    # Also collapse excessive blank lines to single blank lines.
    # Remove image lines entirely or inline occurrences
    no_images = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", markdown)

    # Convert headers and formatting to plain text by stripping leading #'s and spaces
    def strip_md_format(line: str) -> str:
        # Strip heading markers
        line = re.sub(r"^\s{0,3}#{1,6}\s*", "", line)
        # Replace horizontal rules with blank
        if re.match(r"^\s*([-*_]\s*){3,}\s*$", line):
            return ""
        # Strip emphasis markers but keep content
        line = line.replace("**", "").replace("__", "").replace("*", "").replace("_", "")
        # Inline code/backticks
        line = line.replace("`", "")
        return line

    lines = [strip_md_format(l) for l in no_images.splitlines()]
    # Remove trailing spaces
    lines = [l.rstrip() for l in lines]
    # Collapse 3+ blank lines to 1
    collapsed = []
    blank_streak = 0
    for l in lines:
        if l.strip() == "":
            blank_streak += 1
            if blank_streak <= 1:
                collapsed.append("")
        else:
            blank_streak = 0
            collapsed.append(l)
    return "\n".join(collapsed).strip() + "\n"


def _combine_text_files(text_dir: Path, enhanced: bool) -> str:
    """
    Read all text files from the directory and combine them into one document.
    """
    if not text_dir.exists():
        return "No text files directory found"

    text_files = sorted(text_dir.glob("*.txt"))

    if not text_files:
        return "No text files found to combine"

    print(f"Found {len(text_files)} text files to combine")

    if enhanced:
        results = []
        for i, text_file in enumerate(text_files, start=1):
            try:
                content = text_file.read_text(encoding="utf-8").strip()
                if content:
                    results.append({
                        'filename': text_file.stem.replace('_enhanced', ''),
                        'content': content,
                        'characters': len(content),
                        'order': i
                    })
            except Exception as e:
                print(f"  Error reading {text_file}: {e}")
        return _create_enhanced_report(results)
    else:
        combined_parts = []
        for i, text_file in enumerate(text_files, start=1):
            try:
                content = text_file.read_text(encoding="utf-8").strip()
                if content:
                    filename = text_file.stem
                    header = f"\n{'='*50}\nFILE: {filename}\n{'='*50}\n"
                    combined_parts.append(header + content)
                    print(f"  [{i}/{len(text_files)}] Added: {filename}")
            except Exception as e:
                print(f"  Error reading {text_file}: {e}")
        
        if not combined_parts:
            return "No content found in any text files"

        final_content = "\n\n" + "\n\n".join(combined_parts) + "\n\n"
        summary_header = f"""# COMBINED OCR RESULTS
Generated from {len(text_files)} individual text files
Processing Date: {Path.cwd()}
Total Files Combined: {len(combined_parts)}

{'='*80}

"""
        return summary_header + final_content


def _create_enhanced_report(results: List[dict]) -> str:
    """
    Create a properly organized document from OCR results for enhanced images.
    """
    sorted_results = sorted(results, key=lambda x: x['order'])
    sections = []
    header = f"""# COMPLETE ENHANCED OCR DOCUMENT
Generated from {len(sorted_results)} enhanced images
Processing Date: {Path.cwd()}
Total Characters Extracted: {sum(r['characters'] for r in sorted_results)}

{'='*80}

## DOCUMENT CONTENTS

"""
    sections.append(header)

    for i, result in enumerate(sorted_results, start=1):
        filename = result['filename']
        content = result['content']
        char_count = result['characters']
        section_header = f"""
{'='*60}
SECTION {i}: {filename.upper()}
{'='*60}
Characters: {char_count}
{'-'*60}

"""
        sections.append(section_header + content + "\n")

    footer = f"""\n
{'='*80}
END OF DOCUMENT
{'='*80}
Total Sections: {len(sorted_results)}
Total Characters: {sum(r['characters'] for r in sorted_results)}
Enhanced OCR Processing: Complete
"""
    sections.append(footer)
    return "".join(sections)


def process_images(input_dir: str, output_dir: str, combined_output_path: str, glob_patterns: List[str], enhanced: bool) -> None:
    """
    Process all images in a directory, perform OCR, and create a combined text file.
    """
    try:
        client = MistralClient()
        print("Testing API connection...")
        if not client.test_connection():
            print("Cannot proceed with OCR due to API connection failure")
            return
    except Exception as e:
        print(f"Error initializing Mistral AI client: {e}")
        return

    image_paths = []
    for pattern in glob_patterns:
        image_paths.extend(sorted(Path(input_dir).glob(pattern)))
    
    # Deduplicate
    seen = set()
    unique_image_paths = []
    for f in image_paths:
        if f.resolve() not in seen:
            unique_image_paths.append(f)
            seen.add(f.resolve())

    if not unique_image_paths:
        print(f"No images found in {input_dir} matching patterns: {glob_patterns}")
        return

    print(f"Found {len(unique_image_paths)} images. Starting OCR...")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    successful_ocr = 0

    for idx, img in enumerate(unique_image_paths, start=1):
        print(f"[{idx}/{len(unique_image_paths)}] OCR: {img}")
        img_name = img.stem
        out_path = output_path / f"{img_name}.txt"

        try:
            text = _ocr_image_plain(client, img)
            if text.strip():
                out_path.write_text(text.strip(), encoding="utf-8")
                successful_ocr += 1
                print(f"  Saved: {out_path}")
            else:
                print(f"  No text extracted: {img}")
        except Exception as e:
            error_msg = f"Error OCRing {img}: {e}"
            print(f"  {error_msg}")
            out_path.write_text(error_msg, encoding="utf-8")

    print(f"\nOCR completed. Successfully processed {successful_ocr}/{len(unique_image_paths)} images")

    print("\nCombining all text files...")
    combined_text = _combine_text_files(output_path, enhanced)

    combined_path = Path(combined_output_path)
    combined_path.parent.mkdir(parents=True, exist_ok=True)
    combined_path.write_text(combined_text, encoding="utf-8")

    print(f"Combined text saved to: {combined_path}")
    print(f"Individual text files in: {output_path}")
