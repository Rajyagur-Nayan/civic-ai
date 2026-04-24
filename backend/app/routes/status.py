from fastapi import APIRouter, HTTPException
from app.services.job_manager import job_manager

router = APIRouter()

@router.get("/{job_id}")
async def get_job_status(job_id: str):
    """
    Check the current status of a job.
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "error": job.get("error")
    }
