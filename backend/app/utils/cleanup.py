import os
import shutil
import asyncio
import logging

logger = logging.getLogger(__name__)

async def cleanup_job(upload_path: str, output_dir: str, delay: int = 600):
    """
    Deletes the specified files and directories after a delay.
    
    Args:
        upload_path: Path to the original uploaded file
        output_dir: Path to the job's output directory
        delay: Delay in seconds (default 10 minutes)
    """
    logger.info(f"Cleanup scheduled in {delay}s for: {upload_path} and {output_dir}")
    
    await asyncio.sleep(delay)
    
    # 1. Cleanup original upload
    if os.path.exists(upload_path):
        try:
            os.remove(upload_path)
            logger.info(f"Cleanup: Deleted original upload {upload_path}")
        except Exception as e:
            logger.warning(f"Cleanup: Failed to delete upload {upload_path}: {e}")
            
    # 2. Cleanup output folder
    if os.path.exists(output_dir):
        try:
            shutil.rmtree(output_dir, ignore_errors=True)
            logger.info(f"Cleanup: Deleted output directory {output_dir}")
        except Exception as e:
            logger.warning(f"Cleanup: Failed to delete output directory {output_dir}: {e}")
