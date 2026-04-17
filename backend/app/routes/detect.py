import logging
from typing import List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

from app.services import detection, area, estimation

logger = logging.getLogger(__name__)

router = APIRouter()

class DetectionResult(BaseModel):
    bbox: List[float]
    area: float
    severity: str
    workers: int
    cost: float
    time: int
    confidence: float

class DetectionResponse(BaseModel):
    detections: List[DetectionResult]
    total_potholes: int
    total_cost: float

@router.post("", response_model=DetectionResponse)
async def detect_potholes_endpoint(file: UploadFile = File(...)):
    """
    Enhanced detection endpoint with accuracy filtering and resource estimation.
    """
    logger.info(f"Accuracy Upgrade: Detection request for {file.filename}")

    try:
        # Read Bytes
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty image file")

        # 1. Run Core Detection (with confidence, aspect ratio, and brightness filters)
        raw_detections = detection.detect_potholes(image_bytes)

        # 2. Process results with improved estimations
        results: List[DetectionResult] = []
        total_cost = 0.0

        for det in raw_detections:
            try:
                # Calculate metrics using updated services
                det_area = area.calculate_area(det)
                severity = area.calculate_severity(det_area)
                est = estimation.estimate_repair(det_area, severity)

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

            except Exception as e:
                logger.error(f"Error enriching detection: {e}")
                continue

        logger.info(f"Pipeline Success: Found {len(results)} valid potholes. Total Cost: ${total_cost:.2f}")
        
        return DetectionResponse(
            detections=results,
            total_potholes=len(results),
            total_cost=round(total_cost, 2)
        )

    except Exception as e:
        logger.error(f"Critical pipeline error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Pothole detection pipeline failed. Check backend logs for details."
        )
    finally:
        await file.close()
