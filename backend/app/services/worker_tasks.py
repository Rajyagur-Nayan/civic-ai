import logging
import os
import shutil
from app.services.video_engine import process_video_pipeline
from app.services.job_manager import job_manager
from app.services import detection, area, estimation
import cv2

logger = logging.getLogger(__name__)

def process_video_task(job_id: str, video_path: str, output_dir: str):
    """
    Background task for video processing.
    """
    job_manager.update_status(job_id, "processing")
    try:
        logger.info(f"Worker: Starting video processing for job {job_id}")
        results = process_video_pipeline(video_path, job_id, output_dir)
        
        # Add metadata
        results["job_id"] = job_id
        
        job_manager.set_result(job_id, results)
        logger.info(f"Worker: Video processing completed for job {job_id}")
    except Exception as e:
        logger.error(f"Worker: Video processing failed for job {job_id}: {e}")
        job_manager.update_status(job_id, "failed", str(e))

def process_image_task(job_id: str, image_path: str, output_dir: str, safe_filename: str):
    """
    Background task for image processing.
    """
    job_manager.update_status(job_id, "processing")
    try:
        logger.info(f"Worker: Starting image processing for job {job_id}")
        
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        raw_detections = detection.detect_potholes(image_bytes)
        
        results_list = []
        total_cost = 0.0
        severity_dist = {"small": 0, "medium": 0, "large": 0}

        for det in raw_detections:
            det_area = area.calculate_area(det)
            severity = area.calculate_severity(det_area)
            est = estimation.estimate_repair(det_area, severity)
            det["severity"] = severity

            results_list.append({
                "bbox": det["bbox"],
                "area": det_area,
                "severity": severity,
                "workers": est["workers"],
                "cost": est["cost"],
                "time": est["time"],
                "confidence": det["confidence"],
            })
            total_cost += est["cost"]
            severity_dist[severity.lower()] += 1

        # Save Annotated Image
        annotated_img = detection.draw_detections(image_bytes, raw_detections)
        result_path = os.path.join(output_dir, "result.jpg")
        cv2.imwrite(result_path, annotated_img)

        final_results = {
            "job_id": job_id,
            "detections": results_list,
            "total_potholes": len(results_list),
            "total_cost": round(total_cost, 2),
            "severity_distribution": severity_dist,
            "processed_url": f"/output/{job_id}/result.jpg",
            "original_url": f"/uploads/{safe_filename}"
        }
        
        job_manager.set_result(job_id, final_results)
        logger.info(f"Worker: Image processing completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Worker: Image processing failed for job {job_id}: {e}")
        job_manager.update_status(job_id, "failed", str(e))
