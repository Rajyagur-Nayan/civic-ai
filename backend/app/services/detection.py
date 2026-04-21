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

# --- GLOBAL MODEL INITIALIZATION (Loads ONLY ONCE when module is imported) ---
try:
    # Use absolute path resolution for reliable loading
    base_path = Path(__file__).resolve().parent.parent
    model_path = base_path / "models" / "yolov8" / "best.pt"
    
    if not model_path.exists():
        logger.error(f"CRITICAL: Model file not found at {model_path}")
        # Fallback to default for safety so the app doesn't crash entirely if not strictly required
        model = YOLO("yolov8n.pt")
        logger.warning("Fell back to yolov8n.pt because best.pt was missing")
    else:
        # Standard Ultralytics YOLO loading
        model = YOLO(str(model_path))
        logger.info("YOLO model loaded successfully")
except Exception as e:
    logger.error(f"FAILURE: YOLO model could not be initialized: {e}")
    # Re-raise to ensure the app fails to start if model loading is corrupted
    raise RuntimeError(f"YOLO model initialization failed: {e}")

def bytes_to_cv2(image_bytes: bytes) -> np.ndarray:
    """Convert bytes to OpenCV BGR image"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image format")
    return img

def detect_potholes(
    image_bytes: bytes, 
    imgsz: int = 1280, 
    augment: bool = True
) -> List[Dict[str, Any]]:
    """
    Advanced detection pipeline with accuracy upgrades.
    """
    if not image_bytes:
        return []

    try:
        logger.info("Inference started...")
        
        # Convert bytes to OpenCV image
        img_cv2 = bytes_to_cv2(image_bytes)
        
        # PIL for YOLO inference (preferred by Ultralytics)
        img_pil = Image.fromarray(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB))
        
        # Run inference with optimized parameters
        # Use the global 'model' loaded at the module level
        results = model.predict(
            source=img_pil, 
            conf=0.25,      # Lower threshold for more detections
            iou=0.45,       # Adjusted NMS IoU
            imgsz=imgsz,    # Parameterized resolution
            augment=augment, # Parameterized TTA
            verbose=False
        )
        
        detections = []
        if not results:
            logger.info("Inference results count: 0")
            return []

        result = results[0]
        boxes = result.boxes
        
        for box in boxes:
            # 1. Basic properties
            xyxy = box.xyxy[0].cpu().numpy().tolist()
            conf = float(box.conf[0].cpu().numpy())
            x1, y1, x2, y2 = [int(v) for v in xyxy]
            
            w = x2 - x1
            h = y2 - y1

            # 2. Basic sanity checks (Removed aggressive filters to avoid empty results)
            if w <= 0 or h <= 0: continue

            # 3. Valid detection confirmed
            detections.append({
                "bbox": [round(float(x), 2) for x in xyxy],
                "width": float(w),
                "height": float(h),
                "confidence": round(conf, 3)
            })

        logger.info(f"Inference results count: {len(detections)}")
        return detections

    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise RuntimeError(f"ML Processing Failed: {e}")

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
