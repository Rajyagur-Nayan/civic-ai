import os
import shutil
import logging
import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from app.services.video_engine import process_video_pipeline
from app.utils.cleanup import cleanup_job

logger = logging.getLogger(__name__)

router = APIRouter()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"

@router.post("", response_model=None)
async def detect_video_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Endpoint specifically for Video detection with automated cleanup.
    """
    job_id = str(uuid.uuid4())
    filename = file.filename
    safe_filename = f"{job_id}_{filename}"
    
    upload_path = str(UPLOADS_DIR / safe_filename)
    job_output_dir = str(OUTPUT_DIR / job_id)
    
    # Auto-create folders
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(job_output_dir, exist_ok=True)
    
    logger.info(f"Video Job {job_id}: Processing {filename}")

    if not filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        shutil.rmtree(job_output_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail="Invalid video format")

    try:
        # 1. Safe Save
        contents = await file.read()
        with open(upload_path, "wb") as f:
            f.write(contents)
            
        # 2. Validation
        if not os.path.exists(upload_path):
            raise HTTPException(status_code=500, detail="File failed to save")
        
        # 3. Process Video
        results = process_video_pipeline(upload_path, job_id, job_output_dir, skip_frames=10)
        
        # Add metadata and schedule cleanup
        results["job_id"] = job_id
        background_tasks.add_task(cleanup_job, upload_path, job_output_dir)
        
        logger.info(f"Video Job {job_id} success")
        return results

    except Exception as e:
        logger.error(f"Video Job {job_id} failed: {e}")
        if os.path.exists(upload_path): os.remove(upload_path)
        shutil.rmtree(job_output_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")
    finally:
        await file.close()

