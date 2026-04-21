import os
import shutil
import uuid
import cv2
import logging
from typing import List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.services import detection, area, estimation
from app.services.video_engine import process_video_pipeline
from app.utils.cleanup import cleanup_job

logger = logging.getLogger(__name__)

router = APIRouter()

# Base directories (absolute paths)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"

class DetectionResult(BaseModel):
    bbox: List[float]
    area: float
    severity: str
    workers: int
    cost: float
    time: int
    confidence: float

@router.post("", response_model=None)
async def detect_potholes_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Unified endpoint for Image and Video detection with automated cleanup.
    """
    # 1. Initialization
    job_id = str(uuid.uuid4())
    filename = file.filename
    safe_filename = f"{job_id}_{filename}"
    
    upload_path = str(UPLOADS_DIR / safe_filename)
    job_output_dir = str(OUTPUT_DIR / job_id)
    
    # Auto-create folders
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(job_output_dir, exist_ok=True)
    
    logger.info(f"Job {job_id}: Processing {filename}")
    logger.info(f"Debug Paths - Upload: {upload_path}, Output: {job_output_dir}")

    # 2. Safe File Saving
    try:
        contents = await file.read()
        with open(upload_path, "wb") as f:
            f.write(contents)
        
        # Validation
        if not os.path.exists(upload_path):
            raise HTTPException(status_code=500, detail="File failed to save to disk")
            
    except Exception as e:
        logger.error(f"Job {job_id}: Save failed: {e}")
        raise HTTPException(status_code=500, detail=f"File save error: {str(e)}")

    # 3. File Type Detection
    ext = filename.lower()
    is_image = ext.endswith(('.jpg', '.jpeg', '.png'))
    is_video = ext.endswith(('.mp4', '.avi', '.mov', '.mkv'))

    if not is_image and not is_video:
        # Cleanup immediately if invalid type
        if os.path.exists(upload_path): os.remove(upload_path)
        shutil.rmtree(job_output_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail="Unsupported file type")

    try:
        if is_image:
            # --- IMAGE PROCESSING ---
            with open(upload_path, "rb") as f:
                image_bytes = f.read()

            raw_detections = detection.detect_potholes(image_bytes)
            
            results: List[DetectionResult] = []
            total_cost = 0.0
            severity_dist = {"small": 0, "medium": 0, "large": 0}

            for det in raw_detections:
                det_area = area.calculate_area(det)
                severity = area.calculate_severity(det_area)
                est = estimation.estimate_repair(det_area, severity)
                det["severity"] = severity

                results.append(
                    DetectionResult(
                        bbox=det["bbox"],
                        area=det_area,
                        severity=severity,
                        workers=est["workers"],
                        cost=est["cost"],
                        time=est["time"],
                        confidence=det["confidence"],
                    )
                )
                total_cost += est["cost"]
                severity_dist[severity.lower()] += 1

            # Save Annotated Image as result.jpg
            annotated_img = detection.draw_detections(image_bytes, raw_detections)
            result_path = os.path.join(job_output_dir, "result.jpg")
            cv2.imwrite(result_path, annotated_img)

            # Schedule Cleanup
            background_tasks.add_task(cleanup_job, upload_path, job_output_dir)

            return {
                "job_id": job_id,
                "detections": results,
                "total_potholes": len(results),
                "total_cost": round(total_cost, 2),
                "severity_distribution": severity_dist,
                "processed_url": f"/output/{job_id}/result.jpg",
                "original_url": f"/uploads/{safe_filename}"
            }

        else:
            # --- VIDEO PROCESSING ---
            results = process_video_pipeline(upload_path, job_id, job_output_dir)
            
            # Map video results to unified response keys
            results["job_id"] = job_id
            results["original_url"] = f"/uploads/{safe_filename}"
            if "video_url" in results:
                results["processed_url"] = results["video_url"]
            
            # Schedule Cleanup
            background_tasks.add_task(cleanup_job, upload_path, job_output_dir)
            
            return results

    except Exception as e:
        logger.error(f"Job {job_id}: Processing failed: {e}")
        # Cleanup on failure
        if os.path.exists(upload_path): os.remove(upload_path)
        shutil.rmtree(job_output_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        await file.close()

