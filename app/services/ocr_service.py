import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io

from app.core.aws import s3
from app.models.file import File, FileType
from app.core.config import settings


async def run_ocr(file: File) -> str:
    """
    Runs OCR on a File DB object.
    Supports PDF and Image files.
    """

    # 1️⃣ Download file bytes from S3
    response = s3.get_object(
        Bucket=settings.AWS_S3_BUCKET,
        Key=file.s3_key,
    )

    file_bytes: bytes = response["Body"].read()

    extracted_text = ""

    # 2️⃣ Handle PDF
    if file.file_type == FileType.pdf:
        images = convert_from_bytes(file_bytes)

        for image in images:
            extracted_text += pytesseract.image_to_string(image)
            extracted_text += "\n"

    # 3️⃣ Handle Image
    elif file.file_type == FileType.image:
        image = Image.open(io.BytesIO(file_bytes))
        extracted_text = pytesseract.image_to_string(image)

    else:
        raise ValueError(f"Unsupported file type: {file.file_type}")

    return extracted_text.strip()
