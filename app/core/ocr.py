from pathlib import Path
import pytesseract
import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_path, convert_from_bytes
from typing import Union
import logging

logger = logging.getLogger(__name__)

TESSERACT_CONFIG = "--oem 3 --psm 6"


def preprocess_image(image: Image.Image) -> np.ndarray:
    """Preprocess an image to improve OCR accuracy.

    The image is converted to RGB (if needed), then to grayscale and
    binarized using Otsu's thresholding method.
    """
    if image.mode != "RGB":
        image = image.convert("RGB")

    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return gray


def extract_text_from_image(image: Image.Image) -> str:
    """Extract text from a single image using Tesseract OCR."""
    processed = preprocess_image(image)
    return pytesseract.image_to_string(processed, lang="eng", config=TESSERACT_CONFIG)


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes by rendering pages and running OCR."""
    pages = convert_from_bytes(pdf_bytes, dpi=300)
    text = ""
    for page in pages:
        text += extract_text_from_image(page)
    return text


def extract_text_from_pdf_path(path: str) -> str:
    """Extract text from a PDF file path by rendering pages and running OCR.

    Note: requires Poppler installed for `convert_from_path`.
    """
    try:
        pages = convert_from_path(path, dpi=300)
    except Exception as e:
        logger.exception("Failed to convert PDF path to images: %s", path)
        raise

    text = ""
    for page in pages:
        text += extract_text_from_image(page)
    return text


def extract_text(source: Union[str, bytes]) -> str:
    """Unified OCR entry point.

    Accepts a file path string or PDF bytes. For non-PDF file paths, treats
    the path as an image file and runs OCR on it.
    """
    if isinstance(source, (bytes, bytearray)):
        return extract_text_from_pdf_bytes(bytes(source))

    path = str(source)
    ext = Path(path).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf_path(path)

    try:
        image = Image.open(path)
    except Exception:
        logger.exception("Failed to open image: %s", path)
        raise

    return extract_text_from_image(image)
