from PIL import Image
import os

# Import your OCR functions
from ocr import extract_text_from_image, extract_text_from_pdf


def test_image_ocr():
    image_path = "sample.png"  # replace with your image file

    if not os.path.exists(image_path):
        print("❌ Image file not found:", image_path)
        return

    image = Image.open(image_path)
    text = extract_text_from_image(image)

    print("===== IMAGE OCR OUTPUT =====")
    print(text)


def test_pdf_ocr():
    pdf_path = "sample.pdf"  # replace with your PDF file

    if not os.path.exists(pdf_path):
        print("❌ PDF file not found:", pdf_path)
        return

    text = extract_text_from_pdf(pdf_path)

    print("===== PDF OCR OUTPUT =====")
    print(text)


if __name__ == "__main__":
    test_image_ocr()
    test_pdf_ocr()
