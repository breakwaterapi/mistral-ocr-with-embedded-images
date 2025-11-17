# Mistral OCR Tool
![Tests](https://img.shields.io/badge/tests-passing-brightgreen) ![Project Status](https://img.shields.io/badge/status-active-blue) ![Python](https://img.shields.io/badge/python-3.9%2B-blue)

A minimal Mistral API wrapper to OCR images and PDF with images embedded in the resultant markdown.

## Setup

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Setup environment variables**

Create a `.env` file in the project root and paste the following:

```
# Put your Mistral API key here
MISTRAL_API_KEY=YOUR_API_KEY_HERE

# Optional: override model name
MISTRAL_OCR_MODEL=mistral-ocr-latest
```

## How to Run

To run the OCR tool:

```bash
uv run python main.py
```

## Project structure

- main.py —
- src/ — 
  - src/image_enhancer.py — image enhancement utilities. Image enhancement using the Pillow (PIL) library is integrated to further improve OCR accuracy.
  - src/mistral_ai.py — Mistral client wrapper
  - src/ocr.py —  OCR logic
- samples/ — input images
- tests/ — pytest tests

## Official Resources

- Documentation: https://docs.mistral.ai/capabilities/document_ai/basic_ocr/
- API Reference: https://docs.mistral.ai/api/#tag/ocr
