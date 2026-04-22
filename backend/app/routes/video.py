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

# 100MB limit for better video support
MAX_FILE_SIZE = 100 * 1024 * 1024 

@router.post("", response_model=None)
async def detect_video_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Endpoint for Video detection optimized for Render.
    Includes file size limits and robust error handling to prevent connection resets.
    """
    job_id = str(uuid.uuid4())
    print(f"REQUEST RECEIVED: Video detection for {file.filename}")
    
    # 1. Validation
    if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HTTPException(status_code=400, detail="Invalid video format. Supported: .mp4, .avi, .mov, .mkv")

    # 2. File Size Limit Check
    # Note: Using seek to check size without reading entire file into memory immediately
    try:
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File too large: {file_size} bytes")
            raise HTTPException(
                status_code=400, 
                detail=f"Video file too large ({file_size/(1024*1024):.1f}MB). Maximum allowed is 20MB."
            )
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        logger.error(f"Size validation error: {e}")

    filename = file.filename
    safe_filename = f"{job_id}_{filename}"
    upload_path = str(UPLOADS_DIR / safe_filename)
    job_output_dir = str(OUTPUT_DIR / job_id)
    
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(job_output_dir, exist_ok=True)
    
    try:
        # 3. Safe Save
        logger.info(f"Saving video to {upload_path}...")
        contents = await file.read()
        with open(upload_path, "wb") as f:
            f.write(contents)
            
        if not os.path.exists(upload_path):
            raise RuntimeError("File failed to save to disk")
        
        # 4. Process Video with higher density (skip 2 instead of 5 for thoroughness)
        logger.info(f"Processing video {job_id}...")
        results = process_video_pipeline(upload_path, job_id, job_output_dir, skip_frames=2)
        
        # 5. Finalize Result
        results["job_id"] = job_id
        results["original_url"] = f"/uploads/{safe_filename}"
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_job, upload_path, job_output_dir)
        
        logger.info(f"PROCESSING COMPLETED: Job {job_id}")
        return results

    except Exception as e:
        logger.error(f"ERROR processing video job {job_id}: {str(e)}")
        # Cleanup on failure
        if os.path.exists(upload_path): os.remove(upload_path)
        shutil.rmtree(job_output_dir, ignore_errors=True)
        
        # Always return a proper JSON error response
        return {
            "error": "Video processing failed or timed out",
            "detail": str(e),
            "job_id": job_id
        }
    finally:
        await file.close()
