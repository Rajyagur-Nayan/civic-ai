import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
import cv2
from ultralytics import YOLO
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Singleton model instance
_model: Optional[YOLO] = None

def get_model_path() -> Path:
    """Get absolute path to best.pt"""
    # Path relative to this file: services/detection.py -> app/models/yolov8/best.pt
    base_path = Path(__file__).resolve().parent.parent
    model_path = base_path / "models" / "yolov8" / "best.pt"
    return model_path

def get_model() -> YOLO:
    """Load custom YOLOv8 model (singleton pattern)"""
    global _model
    if _model is None:
        try:
            model_path = get_model_path()
            logger.info(f"Loading custom YOLO model from: {model_path}")
            
            if not model_path.exists():
                logger.error(f"Model file not found at {model_path}")
                # Fallback to default if best.pt is missing (for safety)
                _model = YOLO("yolov8n.pt")
                logger.warning("Fell back to yolov8n.pt because best.pt was missing")
            else:
                _model = YOLO(str(model_path))
                logger.info("Custom model (best.pt) loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    return _model

def bytes_to_cv2(image_bytes: bytes) -> np.ndarray:
    """Convert bytes to OpenCV BGR image"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image format")
    return img

def detect_potholes(image_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Advanced detection pipeline with strict filtering.
    1. Confidence >= 0.4 
    2. Aspect Ratio (skip if too flat or too narrow)
    3. Brightness (skip if ROI is too bright - likely not a hole)
    """
    if not image_bytes:
        return []

    try:
        model = get_model()
        
        # Convert bytes to OpenCV image for filtering
        img_cv2 = bytes_to_cv2(image_bytes)
        img_gray = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2GRAY)
        
        # PIL for YOLO inference (preferred by Ultralytics)
        img_pil = Image.fromarray(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB))
        
        # Run inference with higher confidence threshold
        results = model.predict(source=img_pil, conf=0.4, verbose=False)
        
        detections = []
        if not results:
            return []

        result = results[0]
        boxes = result.boxes
        height_orig, width_orig = img_cv2.shape[:2]

        for box in boxes:
            # 1. Basic properties
            xyxy = box.xyxy[0].cpu().numpy().tolist()
            conf = float(box.conf[0].cpu().numpy())
            x1, y1, x2, y2 = [int(v) for v in xyxy]
            
            w = x2 - x1
            h = y2 - y1

            # 2. Aspect Ratio Filter (Reject flat/narrow shapes)
            if w <= 0 or h <= 0: continue
            aspect_ratio = w / h
            if aspect_ratio > 3 or aspect_ratio < 0.33: # 0.33 is 1/3
                logger.info(f"Skipping detection: Aspect Ratio {aspect_ratio:.2f} too extreme")
                continue

            # 3. Brightness Filter (Potholes are usually dark/shadowed)
            # Clip ROI to image boundaries
            rx1, ry1 = max(0, x1), max(0, y1)
            rx2, ry2 = min(width_orig, x2), min(height_orig, y2)
            roi = img_gray[ry1:ry2, rx1:rx2]
            
            if roi.size > 0:
                mean_brightness = np.mean(roi)
                if mean_brightness > 140:
                    logger.info(f"Skipping detection: Mean brightness {mean_brightness:.1f} too high")
                    continue

            # 4. Valid detection confirmed
            detections.append({
                "bbox": [round(float(x), 2) for x in xyxy],
                "width": float(w),
                "height": float(h),
                "confidence": round(conf, 3)
            })

        logger.info(f"Accuracy pipeline: {len(boxes)} raw -> {len(detections)} filtered")
        return detections

    except Exception as e:
        logger.error(f"Detection error: {e}")
        return []

def draw_detections(image_bytes: bytes, detections: List[Dict[str, Any]]) -> np.ndarray:
    """
    Draw bounding boxes with enriched labels.
    Expected det format: {bbox, confidence, severity (optional)}
    """
    img = bytes_to_cv2(image_bytes)
    
    for det in detections:
        x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
        conf = det["confidence"]
        severity = det.get("severity", "unknown").capitalize()
        
        # Color based on severity
        color = (0, 0, 255) # Default Red
        if severity == "Small": color = (0, 255, 0)      # Green
        elif severity == "Medium": color = (0, 255, 255) # Yellow
        
        # Bbox
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
        
        # Label: Pothole | 0.82 | Medium
        label = f"Pothole | {conf:.2f} | {severity}"
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        
        # Label background
        cv2.rectangle(img, (x1, y1 - 30), (x1 + w, y1), color, -1)
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
    return img

def reset_model():
    """Reset the singleton instance"""
    global _model
    _model = None
    logger.info("Model cleared from memory")
