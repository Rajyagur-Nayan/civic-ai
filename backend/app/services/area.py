import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

PIXEL_TO_METER_RATIO = 0.01


def calculate_area(detection: Dict[str, Any]) -> float:
    width_px = detection["width"]
    height_px = detection["height"]

    width_m = width_px * PIXEL_TO_METER_RATIO
    height_m = height_px * PIXEL_TO_METER_RATIO

    area = width_m * height_m

    logger.info(f"Calculated area: {area:.2f} sq meters")
    return area


def calculate_severity(area: float) -> str:
    if area < 0.5:
        return "small"
    elif area < 2.0:
        return "medium"
    else:
        return "large"
