"""Time range utilities for MCP tools"""

from typing import Dict

# Supported time ranges and their minute equivalents
TIME_RANGE_MINUTES: Dict[str, int] = {
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "3h": 180,
    "24h": 1440
}


def parse_time_range(time_range: str) -> int:
    """
    Convert time range string to minutes
    
    Args:
        time_range: Time range string (e.g., "15m", "1h", "24h")
    
    Returns:
        Number of minutes
    
    Raises:
        ValueError: If time_range is not valid

    """
    if time_range not in TIME_RANGE_MINUTES:
        raise ValueError(
            f"Invalid time_range: '{time_range}'. "
            f"Valid options: {list(TIME_RANGE_MINUTES.keys())}"
        )
    return TIME_RANGE_MINUTES[time_range]

