from pathlib import Path
import pytesseract
import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_path

TESSERACT_CONFIG = "--oem 3 --psm 6"


def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Preprocess an image to improve OCR accuracy.

    The image is converted to grayscale and binarized using
    Otsu's thresholding method.
    """
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return gray


def extract_text_from_image(image: Image.Image) -> str:
    """
    Extract text from a single image using Tesseract OCR.

    The image is preprocessed before text extraction to
    improve recognition accuracy.
    """
    processed = preprocess_image(image)
    return pytesseract.image_to_string(processed, lang="eng", config=TESSERACT_CONFIG)


def extract_text_from_pdf(path: str) -> str:
    """
    Extract text from a PDF file by converting each page to an image
    and applying OCR.

    Each page is rendered at 300 DPI to enhance OCR quality.
    """
    pages = convert_from_path(path, dpi=300)
    text = ""

    for page in pages:
        text += extract_text_from_image(page)

    return text


def extract_text(path: str) -> str:
    """
    Unified OCR entry point.
    Auto-detects PDF or image.
    """
    ext = Path(path).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(path)

    image = Image.open(path)
    return extract_text_from_image(image)
