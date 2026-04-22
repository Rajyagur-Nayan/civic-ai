import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
import io

logger = logging.getLogger(__name__)

# --- LAZY MODEL LOADING ---
model = None

def get_model():
    """
    Lazy load the YOLO model only when needed.
    Prevents startup crashes on Render.
    """
    global model
    if model is None:
        try:
            from ultralytics import YOLO
            
            # Use absolute path resolution for reliable loading
            # Root directory is 'backend' during execution on Render
            base_path = Path(__file__).resolve().parent.parent
            model_path = base_path / "models" / "yolov8" / "best.pt"
            
            if not model_path.exists():
                logger.error(f"CRITICAL: Model file not found at {model_path}")
                # Fallback to default for safety
                model = YOLO("yolov8n.pt")
                logger.warning("Fell back to yolov8n.pt because best.pt was missing")
            else:
                model = YOLO(str(model_path))
                logger.info("YOLO model loaded successfully")
        except Exception as e:
            logger.error(f"MODEL LOAD ERROR: {str(e)}")
            raise RuntimeError(f"YOLO model failed to load: {e}")
    return model

def bytes_to_cv2(image_bytes: bytes) -> np.ndarray:
    """Convert bytes to OpenCV BGR image"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image format")
    return img

def detect_potholes_frame(
    img_cv2: np.ndarray, 
    imgsz: int = 960, 
    augment: bool = False
) -> List[Dict[str, Any]]:
    """
    Core detection logic that works directly on a cv2 frame (numpy array).
    """
    try:
        # Lazy load the model
        model = get_model()
        
        # PIL for YOLO inference (preferred by Ultralytics)
        img_pil = Image.fromarray(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB))
        
        # Run inference with optimized parameters
        results = model.predict(
            source=img_pil, 
            conf=0.25,      # Lower threshold for more detections
            iou=0.45,       # Adjusted NMS IoU
            imgsz=imgsz,    # Parameterized resolution
            augment=augment, # Parameterized TTA
            device="cpu",   # Force CPU for Render stability
            verbose=False
        )
        
        detections = []
        if not results:
            return []

        result = results[0]
        boxes = result.boxes
        
        for box in boxes:
            xyxy = box.xyxy[0].cpu().numpy().tolist()
            conf = float(box.conf[0].cpu().numpy())
            x1, y1, x2, y2 = [int(v) for v in xyxy]
            
            w = x2 - x1
            h = y2 - y1

            if w <= 0 or h <= 0: continue

            detections.append({
                "bbox": [round(float(x), 2) for x in xyxy],
                "width": float(w),
                "height": float(h),
                "confidence": round(conf, 3)
            })

        return detections

    except Exception as e:
        logger.error(f"Frame detection error: {e}")
        raise RuntimeError(f"ML Processing Failed: {e}")

def detect_potholes(
    image_bytes: bytes, 
    imgsz: int = 960, 
    augment: bool = False
) -> List[Dict[str, Any]]:
    """
    Legacy wrapper for image bytes.
    """
    if not image_bytes:
        return []

    try:
        img_cv2 = bytes_to_cv2(image_bytes)
        return detect_potholes_frame(img_cv2, imgsz, augment)
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise RuntimeError(f"ML Processing Failed: {e}")

def draw_detections_frame(img: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
    """
    Draw bounding boxes on a cv2 frame directly.
    """
    # Create a copy to avoid modifying the original frame if needed, 
    # but for performance in video engine we might want to modify in-place.
    # Here we return a new one or modified one.
    for det in detections:
        x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
        conf = det["confidence"]
        severity = det.get("severity", "unknown").capitalize()
        
        color = (0, 0, 255) # Default Red
        if severity == "Small": color = (0, 255, 0)      # Green
        elif severity == "Medium": color = (0, 255, 255) # Yellow
        
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
        
        label = f"Pothole | {conf:.2f} | {severity}"
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        
        cv2.rectangle(img, (x1, y1 - 30), (x1 + w, y1), color, -1)
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
    return img

def draw_detections(image_bytes: bytes, detections: List[Dict[str, Any]]) -> np.ndarray:
    """
    Legacy wrapper for image bytes.
    """
    img = bytes_to_cv2(image_bytes)
    return draw_detections_frame(img, detections)

def reset_model():
    """Reset the singleton instance"""
    global model
    model = None
    logger.info("Model cleared from memory")
