import logging
import os
import io
from typing import List
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
    severity_distribution: dict


@router.post("", response_model=DetectionResponse)
async def detect_potholes(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    try:
        image_bytes = await file.read()

        raw_detections = detection.detect_potholes(image_bytes)

        if not raw_detections:
            return DetectionResponse(
                detections=[],
                total_potholes=0,
                total_cost=0.0,
                severity_distribution={"small": 0, "medium": 0, "large": 0},
            )

        results = []
        severity_dist = {"small": 0, "medium": 0, "large": 0}
        total_cost = 0.0

        for i, det in enumerate(raw_detections):
            det_area = area.calculate_area(det)
            severity = area.calculate_severity(det_area)

            est = estimation.estimate_repair(det_area, severity)

            results.append(
                DetectionResult(
                    bbox=det["bbox"],
                    area=round(det_area, 2),
                    severity=severity,
                    workers=est["workers"],
                    cost=est["cost"],
                    time=est["time"],
                    confidence=round(det["confidence"], 3),
                )
            )

            severity_dist[severity] += 1
            total_cost += est["cost"]

        logger.info(f"Detection complete: {len(results)} potholes, ${total_cost:.2f}")

        return DetectionResponse(
            detections=results,
            total_potholes=len(results),
            total_cost=round(total_cost, 2),
            severity_distribution=severity_dist,
        )

    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        raise HTTPException(500, f"Detection failed: {str(e)}")
