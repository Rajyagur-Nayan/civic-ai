import logging
import os
from typing import List, Dict, Any, Optional
import numpy as np
from ultralytics import YOLO

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "yolov8", "best.pt")

_model: Optional[YOLO] = None


def get_model() -> YOLO:
    global _model
    if _model is None:
        if os.path.exists(MODEL_PATH):
            logger.info(f"Loading custom model from {MODEL_PATH}")
            _model = YOLO(MODEL_PATH)
        else:
            logger.info("Loading default YOLOv8n model")
            _model = YOLO("yolov8n.pt")
    return _model


def detect_potholes(image_bytes: bytes) -> List[Dict[str, Any]]:
    model = get_model()

    results = model.predict(image_bytes, conf=0.25, iou=0.45, verbose=False)

    detections = []
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                xyxy = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())

                x1, y1, x2, y2 = xyxy
                width = float(x2 - x1)
                height = float(y2 - y1)

                detections.append(
                    {
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "confidence": conf,
                        "width": width,
                        "height": height,
                    }
                )

    logger.info(f"Detected {len(detections)} potholes")
    return detections
