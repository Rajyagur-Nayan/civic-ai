import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

COST_PER_SQM = {"small": 150.0, "medium": 120.0, "large": 100.0}

WORKERS = {"small": 1, "medium": 2, "large": 4}

TIME_HOURS = {"small": 2, "medium": 4, "large": 8}


def estimate_repair(area: float, severity: str) -> Dict[str, Any]:
    cost_per_sqm = COST_PER_SQM.get(severity, 100.0)
    estimated_cost = area * cost_per_sqm

    workers_needed = WORKERS.get(severity, 2)
    repair_time = TIME_HOURS.get(severity, 4)

    result = {
        "workers": workers_needed,
        "cost": round(estimated_cost, 2),
        "time": repair_time,
    }

    logger.info(f"Estimation: {result}")
    return result
