import os
import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from redis import Redis
from rq import Queue
from app.services.job_manager import job_manager
from app.services.worker_tasks import process_video_task, process_image_task

logger = logging.getLogger(__name__)

router = APIRouter()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"

# Redis queue setup
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = Redis.from_url(REDIS_URL)
queue = Queue('default', connection=redis_conn)

MAX_FILE_SIZE = 50 * 1024 * 1024 # Increased to 50MB since it's background processed

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """
    Async upload endpoint. Saves file and queues task.
    Returns job_id immediately.
    """
    job_id = str(uuid.uuid4())
    filename = file.filename
    safe_filename = f"{job_id}_{filename}"
    upload_path = str(UPLOADS_DIR / safe_filename)
    job_output_dir = str(OUTPUT_DIR / job_id)
    
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(job_output_dir, exist_ok=True)
    
    # 1. Validation
    ext = filename.lower()
    is_image = ext.endswith(('.jpg', '.jpeg', '.png'))
    is_video = ext.endswith(('.mp4', '.avi', '.mov', '.mkv'))
    
    if not is_image and not is_video:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    try:
        # 2. Save File (Fast IO)
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
             raise HTTPException(status_code=400, detail="File too large")
             
        with open(upload_path, "wb") as f:
            f.write(contents)
            
        # 3. Create Job in Redis
        job_manager.create_job(job_id)
        
        # 4. Queue Task
        if is_video:
            queue.enqueue(
                process_video_task, 
                args=(job_id, upload_path, job_output_dir),
                job_id=job_id,
                job_timeout='1h' # Allow up to 1 hour for video processing
            )
        else:
            queue.enqueue(
                process_image_task,
                args=(job_id, upload_path, job_output_dir, safe_filename),
                job_id=job_id,
                job_timeout='10m'
            )
            
        logger.info(f"Job {job_id} queued successfully for {filename}")
        
        return {
            "job_id": job_id,
            "status": "pending",
            "filename": filename
        }

    except Exception as e:
        logger.error(f"Upload failed for {filename}: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()
