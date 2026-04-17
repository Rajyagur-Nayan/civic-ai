import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Real-world scale factor (m2 per pixel) 
# Configure this based on camera calibration
SCALE_FACTOR = 0.0005 

def calculate_area(detection: Dict[str, Any]) -> float:
    """
    Calculate area in square meters from bounding box dimensions.
    Uses pixel area scaled by a calibration factor.
    """
    try:
        width_px = detection.get("width", 0)
        height_px = detection.get("height", 0)

        if width_px <= 0 or height_px <= 0:
            return 0.1

        # Calculate pixel area
        pixel_area = width_px * height_px
        
        # Scale to real-world area
        real_area = pixel_area * SCALE_FACTOR
        
        # Clamp values: Smallest repairable pothole is 0.1m2, largest is 5m2
        clamped_area = max(0.1, min(5.0, real_area))

        logger.info(f"Area Calculation: {pixel_area} px -> {real_area:.3f} m2 (Clamped to {clamped_area:.2f} m2)")
        return round(clamped_area, 2)

    except Exception as e:
        logger.error(f"Error calculating area: {e}")
        return 0.1


def calculate_severity(area: float) -> str:
    """
    Classify severity based on damage area (in m2)
    - Small: < 0.5 m²
    - Medium: 0.5 – 2 m²
    - Large: > 2 m²
    """
    if area < 0.5:
        return "small"
    elif area <= 2.0:
        return "medium"
    else:
        return "large"
