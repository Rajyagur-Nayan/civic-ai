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
MAX_PROCESSING_TIME = 90  # Seconds (Render timeout is ~100s)
MAX_TOTAL_FRAMES = 100    # Hard limit on processed frames
SIMILARITY_THRESHOLD = 0.90 # Lowered to skip more similar frames

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

def process_video_pipeline(video_path: str, job_id: str, job_dir: str, skip_frames: int = 30) -> Dict[str, Any]:
    """
    Optimized pipeline for video pothole detection (Render compatible).
    Processes every 'skip_frames' to reduce CPU load and prevent timeouts.
    """
    start_time = time.time()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file")

    unique_potholes = []
    processed_count = 0
    prev_gray = None
    sample_images = []
    
    # Setup paths
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    temp_base = os.path.join(backend_root, "temp", job_id)
    frame_dir = os.path.join(temp_base, "frames")
    
    os.makedirs(temp_base, exist_ok=True)
    os.makedirs(frame_dir, exist_ok=True)
    
    total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    
    logger.info(f"STARTING VIDEO JOB {job_id}: Total Frames: {total_video_frames}, FPS: {fps}")

    frame_idx = 0
    while True:
        # Check for timeout safety (Render limit)
        elapsed = time.time() - start_time
        if elapsed > MAX_PROCESSING_TIME:
            logger.warning(f"Job {job_id} approaching timeout ({elapsed:.1f}s). Breaking early.")
            break

        if processed_count >= MAX_TOTAL_FRAMES:
            logger.warning(f"Reached MAX_TOTAL_FRAMES limit ({MAX_TOTAL_FRAMES}). Stopping.")
            break

        ret, frame = cap.read()
        if not ret:
            break

        # SKIP FRAMES AGGRESSIVELY
        if frame_idx % skip_frames != 0:
            frame_idx += 1
            continue

        # RESIZE FRAME FOR SPEED
        # Standardize to 640 width for detection
        h, w = frame.shape[:2]
        new_w = 640
        new_h = int(h * (new_w / w))
        frame_resized = cv2.resize(frame, (new_w, new_h))

        # SIMILARITY CHECK
        curr_gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        curr_gray_small = cv2.resize(curr_gray, (128, 128)) # Smaller for faster SSIM

        if prev_gray is not None:
            similarity = compare_frames(prev_gray, curr_gray_small)
            if similarity > SIMILARITY_THRESHOLD:
                frame_idx += 1
                continue

        # DETECTION
        _, buffer = cv2.imencode('.jpg', frame_resized)
        img_bytes = buffer.tobytes()
        
        # Use imgsz=640 for faster inference on CPU
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
        
        # ANNOTATION
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
        
        if processed_count % 5 == 0:
            logger.info(f"Job {job_id}: Processed {processed_count} frames... ({elapsed:.1f}s elapsed)")

    cap.release()

    # Video Generation (result.mp4)
    output_video_path = os.path.join(job_dir, "result.mp4")
    frames = sorted([f for f in os.listdir(frame_dir) if f.endswith(".jpg")])
    
    if frames:
        first_frame = cv2.imread(os.path.join(frame_dir, frames[0]))
        if first_frame is not None:
            h, w, _ = first_frame.shape
            try:
                fourcc = cv2.VideoWriter_fourcc(*'avc1')
                video_writer = cv2.VideoWriter(output_video_path, fourcc, 5.0, (w, h)) # Lower FPS for processed video
                
                if not video_writer.isOpened():
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    video_writer = cv2.VideoWriter(output_video_path, fourcc, 5.0, (w, h))
                
                for f_name in frames:
                    img = cv2.imread(os.path.join(frame_dir, f_name))
                    if img is not None:
                        video_writer.write(img)
                video_writer.release()
            except Exception as e:
                logger.error(f"Video writing error: {e}")
    
    total_potholes = len(unique_potholes)
    total_cost = sum(p["cost"] for p in unique_potholes)
    severity_distribution = {"small": 0, "medium": 0, "large": 0}
    for p in unique_potholes:
        severity_distribution[p["severity"]] += 1

    # Report
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
        logger.error(f"Report generation error: {e}")
        final_report_name = ""

    shutil.rmtree(temp_base, ignore_errors=True)
    
    logger.info(f"JOB COMPLETED {job_id}: {total_potholes} potholes found in {time.time()-start_time:.1f}s")

    return {
        "detections": unique_potholes,
        "total_potholes": total_potholes,
        "total_cost": round(total_cost, 2),
        "severity_distribution": severity_distribution,
        "report_url": f"/output/{job_id}/{final_report_name}" if final_report_name else "",
        "video_url": f"/output/{job_id}/result.mp4"
    }
