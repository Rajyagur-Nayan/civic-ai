import logging
import os
import io
from typing import List, Dict, Any
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_annotated_image(
    image_bytes: bytes,
    detections: List[Dict[str, Any]],
    output_filename: str = "annotated.jpg",
) -> str:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()

    severity_colors = {
        "small": (0, 255, 0),
        "medium": (255, 255, 0),
        "large": (255, 0, 0),
    }

    for i, det in enumerate(detections):
        bbox = det["bbox"]
        x1, y1, x2, y2 = bbox
        severity = det.get("severity", "small")

        color = severity_colors.get(severity, (255, 0, 0))

        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

        label = f"#{i + 1} {severity}"
        draw.text((x1, y1 - 20), label, fill=color, font=font)

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    image.save(output_path)

    logger.info(f"Saved annotated image to {output_path}")
    return output_path
    
def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return np.array(image)
