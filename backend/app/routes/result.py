from fastapi import APIRouter, HTTPException
from app.services.job_manager import job_manager

router = APIRouter()

@router.get("/{job_id}")
async def get_job_result(job_id: str):
    """
    Retrieve the results of a completed job.
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["status"] != "completed":
        return {
            "job_id": job_id,
            "status": job["status"],
            "message": "Results not ready yet"
        }
    
    return {
        "job_id": job_id,
        "status": "completed",
        "result": job["result"]
    }
