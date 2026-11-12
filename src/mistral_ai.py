"""
Author: Mayank 'DerperDoing' Bagchi
Web: https://www.mayankbagchi.dev
Date: 29-09-2025
Version: 0.0.2
Description: Proper Mistral Document AI OCR processor implementation using the official API.
"""

import os
import base64
from pathlib import Path
from typing import Union

from dotenv import load_dotenv
load_dotenv()

from mistralai.client import Mistral

class MistralClient:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.ocr_model = os.getenv("MISTRAL_OCR_MODEL", "mistral-ocr-latest")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY environment variable is required")
        self.client = Mistral(api_key=self.api_key)

    def update_api_key(self, api_key: str):
        """Update the API key and recreate the client."""
        self.api_key = api_key
        self.client = Mistral(api_key=self.api_key)

    def _encode_image(self, image_path: str) -> str:
        """Encode image file to base64 data URL."""
        image_file = Path(image_path)
        if not image_file.is_file():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Determine MIME type based on file extension
        ext = image_file.suffix.lower()
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.avif': 'image/avif'
        }
        mime_type = mime_types.get(ext, 'image/jpeg')  # Default to JPEG

        encoded_image = base64.b64encode(image_file.read_bytes()).decode()
        return f"data:{mime_type};base64,{encoded_image}"

    def _encode_pdf(self, pdf_path: str) -> str:
        """Encode PDF file to base64 data URL."""
        pdf_file = Path(pdf_path)
        if not pdf_file.is_file():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        encoded_pdf = base64.b64encode(pdf_file.read_bytes()).decode()
        return f"data:application/pdf;base64,{encoded_pdf}"

    def ocr_image(self, image_path: str) -> str:
        """
        Perform OCR on an image using Mistral Document AI OCR processor.

        Args:
            image_path: Path to the image file

        Returns:
            Markdown string with extracted text and embedded images
        """
        try:
            base64_data_url = self._encode_image(image_path)

            ocr_response = self.client.ocr.process(
                model=self.ocr_model,
                document={
                    "type": "image_url",
                    "image_url": base64_data_url
                },
                include_image_base64=True
            )

            if not ocr_response or not ocr_response.pages:
                return ""

            return self._get_markdown_with_images(ocr_response)

        except Exception as e:
            raise Exception(f"Error performing OCR on image {image_path}: {e}")

    def ocr_pdf(self, pdf_path: str) -> str:
        """
        Perform OCR on a PDF using Mistral Document AI OCR processor.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Markdown string with extracted text and embedded images
        """
        try:
            # For PDFs, we'll upload the file and get a signed URL
            pdf_file = Path(pdf_path)
            if not pdf_file.is_file():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")

            uploaded_file = self.client.files.upload(
                file={
                    "file_name": pdf_file.name,
                    "content": pdf_file.read_bytes()
                },
                purpose="ocr"
            )

            signed_url = self.client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)

            ocr_response = self.client.ocr.process(
                model=self.ocr_model,
                document={
                    "type": "document_url",
                    "document_url": signed_url.url
                },
                include_image_base64=True
            )

            if not ocr_response or not ocr_response.pages:
                return ""

            return self._get_markdown_with_images(ocr_response)

        except Exception as e:
            raise Exception(f"Error performing OCR on PDF {pdf_path}: {e}")

    def test_connection(self) -> bool:
        """
        Test the API connection by making a simple API call.
        Returns True if connection is successful, False otherwise.
        """
        try:
            # Try to list available models as a simple connectivity test
            models = self.client.models.list()
            if models and len(models.data) > 0:
                print(f"API connection successful! Found {len(models.data)} available models")
                return True
            else:
                print("API connection failed: No models returned")
                return False
        except Exception as e:
            print(f"API connection failed: {e}")
            return False

    def _get_markdown_with_images(self, ocr_response) -> str:
        """Extract markdown content with embedded images from OCR response."""
        markdowns = []

        for page in ocr_response.pages:
            if not page.markdown:
                continue

            # Replace image placeholders with actual base64 data
            markdown_content = page.markdown
            if hasattr(page, 'images') and page.images:
                for img in page.images:
                    if img.id and img.image_base64:
                        # Replace the image reference with embedded base64
                        markdown_content = markdown_content.replace(
                            f"![{img.id}]({img.id})",
                            f"![{img.id}]({img.image_base64})"
                        )

            markdowns.append(markdown_content)

        return "\n\n".join(markdowns)