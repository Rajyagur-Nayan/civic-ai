import cv2
import os
import time
import logging
import shutil
import numpy as np
from typing import List, Dict, Any, Tuple
from skimage.metrics import structural_similarity as ssim
from app.services import detection, area, estimation
from app.services.pdf_service import generate_pothole_report

logger = logging.getLogger(__name__)

# Constants
SCALE_FACTOR = 0.0005
COST_PER_M2 = 100
# Smarter limits: Strict for Render (100s timeout), generous for Local
IS_RENDER = os.getenv("RENDER", "false").lower() == "true"
MAX_PROCESSING_TIME = 85 if IS_RENDER else 600 
MAX_TOTAL_FRAMES = 150 if IS_RENDER else 5000  # 5000 frames is ~2.7 mins at 30fps without skipping
SIMILARITY_THRESHOLD = 0.95

def compare_frames(gray1: np.ndarray, gray2: np.ndarray) -> float:
    """Compare two pre-processed frames for similarity using SSIM"""
    try:
        score, _ = ssim(gray1, gray2, full=True)
        return score
    except Exception as e:
        logger.error(f"Error comparing frames: {e}")
        return 0.0

def get_centroid(bbox: List[float]) -> Tuple[float, float]:
    """Calculate centroid of a bounding box [x1, y1, x2, y2]"""
    x1, y1, x2, y2 = bbox
    return (x1 + x2) / 2, (y1 + y2) / 2

def is_duplicate_pothole(new_det: Dict[str, Any], unique_potholes: List[Dict[str, Any]], threshold: float = 50.0) -> bool:
    """Check if a detection is a duplicate of an already tracked pothole using centroid distance"""
    new_centroid = get_centroid(new_det["bbox"])
    
    for existing in unique_potholes:
        existing_centroid = get_centroid(existing["bbox"])
        distance = np.sqrt((new_centroid[0] - existing_centroid[0])**2 + (new_centroid[1] - existing_centroid[1])**2)
        
        if distance < threshold:
            return True
    return False

def process_video_pipeline(video_path: str, job_id: str, job_dir: str, skip_frames: int = 5) -> Dict[str, Any]:
    """
    Stabilized video processing for Render. 
    Uses mp4v codec and aggressive optimizations to prevent crashes.
    """
    start_time = time.time()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file")

    unique_potholes = []
    processed_count = 0
    prev_gray = None
    sample_images = []
    
    # Paths
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    temp_base = os.path.join(backend_root, "temp", job_id)
    frame_dir = os.path.join(temp_base, "frames")
    
    os.makedirs(temp_base, exist_ok=True)
    os.makedirs(frame_dir, exist_ok=True)
    
    # Target dimensions
    target_w, target_h = 640, 360
    
    logger.info(f"STARTING STABILIZED VIDEO JOB {job_id}")

    frame_idx = 0
    while True:
        # 1. Timeout Check
        elapsed = time.time() - start_time
        if elapsed > MAX_PROCESSING_TIME:
            logger.warning(f"Timeout safety break at {elapsed:.1f}s. Returning partial results.")
            break

        if processed_count >= MAX_TOTAL_FRAMES:
            break

        ret, frame = cap.read()
        if not ret:
            break

        # 2. Frame Skipping (User requested 5)
        if frame_idx % skip_frames != 0:
            frame_idx += 1
            continue

        # 3. Resizing (User requested 640x360)
        frame_resized = cv2.resize(frame, (target_w, target_h))

        # 4. Similarity Check
        curr_gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        curr_gray_small = cv2.resize(curr_gray, (128, 128))

        if prev_gray is not None:
            similarity = compare_frames(prev_gray, curr_gray_small)
            if similarity > SIMILARITY_THRESHOLD:
                frame_idx += 1
                continue

        # 5. Detection
        _, buffer = cv2.imencode('.jpg', frame_resized)
        img_bytes = buffer.tobytes()
        
        # CPU optimized inference
        raw_detections = detection.detect_potholes(img_bytes, imgsz=640, augment=False)
        
        frame_had_new_pothole = False
        for det in raw_detections:
            det_area = area.calculate_area(det)
            pothole_data = {
                "bbox": det["bbox"],
                "area": det_area,
                "severity": area.calculate_severity(det_area),
                "cost": estimation.estimate_repair(det_area, area.calculate_severity(det_area))["cost"],
                "confidence": det["confidence"]
            }

            if not is_duplicate_pothole(pothole_data, unique_potholes):
                unique_potholes.append(pothole_data)
                frame_had_new_pothole = True
        
        # 6. Annotation and Save
        for det in raw_detections:
            det_area = area.calculate_area(det)
            det["severity"] = area.calculate_severity(det_area)
            
        annotated_frame = detection.draw_detections(img_bytes, raw_detections)
        frame_name = f"frame_{processed_count + 1:05d}.jpg"
        frame_path = os.path.join(frame_dir, frame_name)
        cv2.imwrite(frame_path, annotated_frame)

        if frame_had_new_pothole and len(sample_images) < 5:
            sample_path = os.path.join(temp_base, f"sample_{processed_count + 1}.jpg")
            cv2.imwrite(sample_path, annotated_frame)
            sample_images.append(sample_path)

        prev_gray = curr_gray_small
        processed_count += 1
        frame_idx += 1

    cap.release()

    # 7. Video Generation (Using 'mp4v' for Linux compatibility)
    output_video_path = os.path.join(job_dir, "result.mp4")
    frames = sorted([f for f in os.listdir(frame_dir) if f.endswith(".jpg")])
    
    if frames:
        try:
            # Use avc1 (H.264) for universal browser compatibility
            # Fallback chain: avc1 -> mp4v
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            video_writer = cv2.VideoWriter(output_video_path, fourcc, 15.0, (target_w, target_h))
            
            if not video_writer.isOpened():
                logger.warning("avc1 codec failed, falling back to mp4v")
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(output_video_path, fourcc, 15.0, (target_w, target_h))

            if not video_writer.isOpened():
                raise RuntimeError("VideoWriter failed to initialize with available codecs")
            
            for f_name in frames:
                img = cv2.imread(os.path.join(frame_dir, f_name))
                if img is not None:
                    video_writer.write(img)
            video_writer.release()
            logger.info(f"Video saved successfully to {output_video_path}")
        except Exception as e:
            logger.error(f"FATAL: VideoWriter error: {e}")
            # Ensure partial results are still returned even if video generation fails
    
    # 8. Results Aggregation
    total_potholes = len(unique_potholes)
    total_cost = sum(p["cost"] for p in unique_potholes)
    severity_distribution = {"small": 0, "medium": 0, "large": 0}
    for p in unique_potholes:
        severity_distribution[p["severity"]] += 1

    # Report
    final_report_name = ""
    try:
        report_path = generate_pothole_report(
            total_potholes=total_potholes,
            total_cost=total_cost,
            severity_distribution=severity_distribution,
            detections=unique_potholes,
            sample_images=sample_images
        )
        final_report_name = f"report_{job_id}.pdf"
        final_report_path = os.path.join(job_dir, final_report_name)
        if report_path and os.path.exists(report_path):
            shutil.move(report_path, final_report_path)
    except Exception as e:
        logger.error(f"Partial Failure: Report generation failed: {e}")

    shutil.rmtree(temp_base, ignore_errors=True)
    logger.info(f"JOB DONE {job_id}: {total_potholes} potholes.")

    return {
        "detections": unique_potholes,
        "total_potholes": total_potholes,
        "total_cost": round(total_cost, 2),
        "severity_distribution": severity_distribution,
        "report_url": f"/output/{job_id}/{final_report_name}" if final_report_name else "",
        "video_url": f"/output/{job_id}/result.mp4" if os.path.exists(output_video_path) else ""
    }
