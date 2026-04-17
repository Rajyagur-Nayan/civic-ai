import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Realistic labor and material costs
COST_PER_M2 = 100.0

# Tiered requirements based on severity
REQUIREMENTS = {
    "small": {"workers": 1, "time": 2},
    "medium": {"workers": 2, "time": 4},
    "large": {"workers": 4, "time": 8}
}

def estimate_repair(area: float, severity: str) -> Dict[str, Any]:
    """
    Estimate resources needed for repair.
    Cost = area * 100
    Labor/Time based on severity tier.
    """
    # Flat cost calculation
    estimated_cost = area * COST_PER_M2

    # Get tiered requirements
    req = REQUIREMENTS.get(severity, REQUIREMENTS["medium"])
    
    result = {
        "workers": req["workers"],
        "cost": round(estimated_cost, 2),
        "time": req["time"],
    }

    logger.info(f"Estimation ({severity}): Cost=${estimated_cost:.2f}, Workers={req['workers']}, Time={req['time']}h")
    return result
