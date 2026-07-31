from pathlib import Path

import easyocr
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

from utils.logger import logger

# Initialize OCR once
reader = easyocr.Reader(["en"], gpu=False, verbose=False)


def preprocess_image(image_path: Path) -> np.ndarray:
    """
    Improve image quality before OCR.
    """

    img = Image.open(image_path).convert("L")

    img = ImageEnhance.Contrast(img).enhance(2.5)
    img = ImageEnhance.Sharpness(img).enhance(2.0)

    img = img.filter(ImageFilter.MedianFilter(size=3))

    return np.array(img)


def extract_text_from_image(file_path: Path) -> str:
    """
    Extract text using EasyOCR.
    """

    try:
        img = preprocess_image(file_path)

        results = reader.readtext(
            img,
            detail=0,
            paragraph=True
        )

        text = "\n".join(results)

        logger.info(f"OCR Extracted Text:\n{text}")

        return text

    except Exception as e:
        logger.error(f"OCR Error: {e}")
        return ""