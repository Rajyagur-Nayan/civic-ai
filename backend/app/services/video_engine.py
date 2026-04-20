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
MAX_FRAMES = 5000  # Increased for full extraction
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

def process_video_pipeline(video_path: str, job_id: str, job_dir: str, skip_frames: int = 10) -> Dict[str, Any]:
    """
    Main pipeline for video pothole detection (re-designed for job isolation).
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file")

    unique_potholes = []
    processed_count = 0
    prev_gray = None
    sample_images = []
    
    # Setup paths relative to backend root and job_id
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    temp_base = os.path.join(backend_root, "temp", job_id)
    frame_dir = os.path.join(temp_base, "frames")
    
    os.makedirs(temp_base, exist_ok=True)
    if os.path.exists(frame_dir):
        shutil.rmtree(frame_dir)
    os.makedirs(frame_dir, exist_ok=True)
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_idx = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if processed_count >= MAX_FRAMES:
            logger.warning(f"Reached MAX_FRAMES limit ({MAX_FRAMES}). Stopping extraction.")
            break

        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        curr_gray_resized = cv2.resize(curr_gray, (256, 256))

        if prev_gray is not None:
            similarity = compare_frames(prev_gray, curr_gray_resized)
            if similarity > SIMILARITY_THRESHOLD:
                frame_idx += 1
                continue

        _, buffer = cv2.imencode('.jpg', frame)
        img_bytes = buffer.tobytes()
        
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

        prev_gray = curr_gray_resized
        processed_count += 1
        frame_idx += 1

    cap.release()

    # Video Generation (result.mp4)
    output_video_path = os.path.join(job_dir, "result.mp4")
    frames = sorted([f for f in os.listdir(frame_dir) if f.endswith(".jpg")])
    if frames:
        first_frame = cv2.imread(os.path.join(frame_dir, frames[0]))
        h, w, _ = first_frame.shape
        # Use 'avc1' for H.264 (web standard). Fallback to 'mp4v' if necessary.
        try:
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (w, h))
            
            # Check if video_writer opened successfully. If not, try fallback.
            if not video_writer.isOpened():
                logger.warning("avc1 codec failed, falling back to mp4v")
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (w, h))
        except Exception as e:
            logger.error(f"Error initializing VideoWriter with avc1: {e}")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (w, h))

        if video_writer.isOpened():
            for f_name in frames:
                img = cv2.imread(os.path.join(frame_dir, f_name))
                video_writer.write(img)
            video_writer.release()
            logger.info(f"Video saved successfully to {output_video_path}")
        else:
            logger.error(f"Could not open VideoWriter for {output_video_path}")

    total_potholes = len(unique_potholes)
    total_cost = sum(p["cost"] for p in unique_potholes)
    severity_distribution = {"small": 0, "medium": 0, "large": 0}
    for p in unique_potholes:
        severity_distribution[p["severity"]] += 1

    # PDF Report (saved in job_id folder as well)
    # The pdf_service might need an update, but we'll use job_dir for now if possible
    report_path = generate_pothole_report(
        total_potholes=total_potholes,
        total_cost=total_cost,
        severity_distribution=severity_distribution,
        detections=unique_potholes,
        sample_images=sample_images
    )
    # Move report to job_dir if it was generated elsewhere
    final_report_name = f"report_{job_id}.pdf"
    final_report_path = os.path.join(job_dir, final_report_name)
    if report_path and os.path.exists(report_path):
        shutil.move(report_path, final_report_path)

    # Final cleanup of temp frames
    shutil.rmtree(temp_base, ignore_errors=True)

    return {
        "detections": unique_potholes,
        "total_potholes": total_potholes,
        "total_cost": round(total_cost, 2),
        "severity_distribution": severity_distribution,
        "report_url": f"/output/{job_id}/{final_report_name}",
        "video_url": f"/output/{job_id}/result.mp4"
    }

