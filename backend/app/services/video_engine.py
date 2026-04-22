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

def process_video_pipeline(video_path: str, job_id: str, job_dir: str, skip_frames: int = 3) -> Dict[str, Any]:
    """
    Balanced high-accuracy video processing with Adaptive Frame Skipping.
    Prioritizes detection quality by intensifying processing during 'interest' events.
    """
    start_time = time.time()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file")

    # Get video properties
    input_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    
    # 1. Configuration
    target_w, target_h = 960, 540  # Improved Resolution
    output_fps = 15.0
    INITIAL_FULL_DENSITY_SEC = 3.0
    INTEREST_WINDOW_FRAMES = int(output_fps * 2) # Process 2 seconds densely after discovery
    BASE_SKIP = 3 # Moderate skip as requested
    
    unique_potholes = []
    processed_count = 0
    skipped_count = 0
    prev_gray = None
    sample_images = []
    
    # Paths
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    temp_base = os.path.join(backend_root, "temp", job_id)
    os.makedirs(temp_base, exist_ok=True)
    
    output_video_path = os.path.join(job_dir, "result.mp4")
    video_writer = None
    
    logger.info(f"STARTING ADAPTIVE VIDEO JOB {job_id} | Resolution: {target_w}x{target_h}")

    frame_idx = 0
    interest_frames_remaining = 0
    inference_times = []
    
    try:
        while True:
            # A. Timeout Check
            elapsed = time.time() - start_time
            if elapsed > MAX_PROCESSING_TIME:
                logger.warning(f"Timeout safety break at {elapsed:.1f}s. Finalizing partial results.")
                break

            ret, frame = cap.read()
            if not ret:
                break

            # B. Adaptive Skip Logic
            is_initial_buffer = (frame_idx / input_fps) < INITIAL_FULL_DENSITY_SEC
            in_interest_mode = interest_frames_remaining > 0
            
            # Decide if we skip this frame
            # Process if: initial buffer, in interest mode, or it's a skip interval
            should_process = is_initial_buffer or in_interest_mode or (frame_idx % BASE_SKIP == 0)
            
            if not should_process:
                frame_idx += 1
                skipped_count += 1
                continue

            # C. Resizing & Prep
            frame_resized = cv2.resize(frame, (target_w, target_h))
            curr_gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
            curr_gray_small = cv2.resize(curr_gray, (128, 128))

            # D. Scene Change / Motion Detection
            is_significant_motion = False
            if prev_gray is not None:
                similarity = compare_frames(prev_gray, curr_gray_small)
                if similarity < 0.85: # Significant change
                    is_significant_motion = True

            # E. Detection
            inf_start = time.time()
            # Use 960 imgsz for accuracy
            raw_detections = detection.detect_potholes_frame(frame_resized, imgsz=960)
            inference_times.append(time.time() - inf_start)
            
            detections_found = len(raw_detections) > 0
            
            # TRIGGER INTEREST MODE
            if detections_found or is_significant_motion:
                interest_frames_remaining = INTEREST_WINDOW_FRAMES
            elif in_interest_mode:
                interest_frames_remaining -= 1

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

                if not is_duplicate_pothole(pothole_data, unique_potholes, threshold=40.0): # Stricter threshold for 960p
                    unique_potholes.append(pothole_data)
                    frame_had_new_pothole = True
            
            # F. Annotation
            for det in raw_detections:
                det_area = area.calculate_area(det)
                det["severity"] = area.calculate_severity(det_area)
            
            annotated_frame = detection.draw_detections_frame(frame_resized, raw_detections)
            
            if frame_had_new_pothole and len(sample_images) < 5:
                sample_path = os.path.join(temp_base, f"sample_{len(sample_images) + 1}.jpg")
                cv2.imwrite(sample_path, annotated_frame)
                sample_images.append(sample_path)

            # G. Write to Video
            if video_writer is None:
                fourcc = cv2.VideoWriter_fourcc(*'avc1')
                video_writer = cv2.VideoWriter(output_video_path, fourcc, output_fps, (target_w, target_h))
                if not video_writer.isOpened():
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    video_writer = cv2.VideoWriter(output_video_path, fourcc, output_fps, (target_w, target_h))

            if video_writer and video_writer.isOpened():
                video_writer.write(annotated_frame)

            prev_gray = curr_gray_small
            processed_count += 1
            frame_idx += 1

    except Exception as e:
        logger.error(f"Error in processing loop: {e}")
    finally:
        cap.release()
        if video_writer:
            video_writer.release()

    # 8. Performance Logging
    total_time = time.time() - start_time
    avg_inf = sum(inference_times) / len(inference_times) if inference_times else 0
    logger.info(f"ADAPTIVE PERFORMANCE [{job_id}]:")
    logger.info(f" - Frames Processed: {processed_count} | Skipped: {skipped_count}")
    logger.info(f" - Coverage Time: {(frame_idx/input_fps):.1f}s of video")
    logger.info(f" - Avg Inference (960p): {avg_inf*1000:.1f}ms")
    logger.info(f" - Total Detections: {len(unique_potholes)}")
    
    # 9. Results Aggregation
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
    logger.info(f"JOB COMPLETED {job_id}")

    return {
        "detections": unique_potholes,
        "total_potholes": total_potholes,
        "total_cost": round(total_cost, 2),
        "severity_distribution": severity_distribution,
        "report_url": f"/output/{job_id}/{final_report_name}" if final_report_name else "",
        "video_url": f"/output/{job_id}/result.mp4" if os.path.exists(output_video_path) else "",
        "stats": {
            "processed_frames": processed_count,
            "skipped_frames": skipped_count,
            "processing_time": round(total_time, 2),
            "video_coverage_sec": round(frame_idx / input_fps, 1)
        }
    }
