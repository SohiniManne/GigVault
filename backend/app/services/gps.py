"""
GPS intelligence: haversine distance and implied speed between last two fixes.
Flags unrealistic jumps (spoofing / teleport claims).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlamb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlamb / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1 - a)))
    return r * c


def compute_gps_jump_signal(
    locations: List[Dict],
    speed_threshold_ms: float,
) -> Tuple[float, Optional[float]]:
    """
    Returns (gps_jump_binary_multiplier, implied_speed_m_s).
    gps_jump is 1 if last segment implies speed above threshold, else 0.
    """
    if len(locations) < 2:
        return 0.0, None
    a, b = locations[-2], locations[-1]
    try:
        lat1, lon1 = float(a["lat"]), float(a["lon"])
        lat2, lon2 = float(b["lat"]), float(b["lon"])
        t1, t2 = float(a.get("ts", 0)), float(b.get("ts", 0))
    except (KeyError, TypeError, ValueError):
        return 0.0, None
    dt = max(t2 - t1, 1e-3)
    dist = haversine_m(lat1, lon1, lat2, lon2)
    speed = dist / dt
    if speed > speed_threshold_ms:
        return 1.0, speed
    return 0.0, speed


def grid_key(lat: Optional[float], lon: Optional[float], decimals: int = 2) -> str:
    if lat is None or lon is None:
        return "unknown"
    return f"{round(lat, decimals)}:{round(lon, decimals)}"
