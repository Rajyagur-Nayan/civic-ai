import redis
import json
import os
import logging
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = redis.from_url(REDIS_URL)

class JobManager:
    """
    Manages job status and result persistence in Redis.
    Structure: job:{job_id} -> hash map with status, results, error.
    """
    
    @staticmethod
    def create_job(job_id: str):
        """Initialize a new job in Redis"""
        try:
            redis_conn.hset(f"job:{job_id}", mapping={
                "status": "pending",
                "result": "",
                "error": ""
            })
            # Set expiry to 24 hours to keep Redis clean
            redis_conn.expire(f"job:{job_id}", 86400)
            logger.info(f"Job {job_id} initialized in Redis")
        except Exception as e:
            logger.error(f"Failed to create job {job_id} in Redis: {e}")

    @staticmethod
    def update_status(job_id: str, status: str, error: Optional[str] = None):
        """Update the status of a job"""
        try:
            mapping = {"status": status}
            if error:
                mapping["error"] = error
            redis_conn.hset(f"job:{job_id}", mapping=mapping)
            logger.info(f"Job {job_id} status updated to: {status}")
        except Exception as e:
            logger.error(f"Failed to update job {job_id} status: {e}")

    @staticmethod
    def set_result(job_id: str, result: Dict[str, Any]):
        """Store the final result and mark as completed"""
        try:
            redis_conn.hset(f"job:{job_id}", mapping={
                "status": "completed",
                "result": json.dumps(result)
            })
            logger.info(f"Job {job_id} completed and results stored")
        except Exception as e:
            logger.error(f"Failed to store result for job {job_id}: {e}")
            JobManager.update_status(job_id, "failed", str(e))

    @staticmethod
    def get_job(job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve job status and result"""
        try:
            job_data = redis_conn.hgetall(f"job:{job_id}")
            if not job_data:
                return None
            
            # Convert bytes to strings
            decoded_job = {k.decode(): v.decode() for k, v in job_data.items()}
            
            # Parse JSON result if it exists
            if decoded_job.get("result"):
                decoded_job["result"] = json.loads(decoded_job["result"])
            else:
                decoded_job["result"] = None
                
            return decoded_job
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None

job_manager = JobManager()
