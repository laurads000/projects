"""Vector helpers for hand Points."""

from __future__ import annotations

import math

import numpy as np


def add(a, b):
    return (a.x + b.x, a.y + b.y, a.z + b.z)


def sub(a, b):
    return (a.x - b.x, a.y - b.y, a.z - b.z)


def angle(a, b, c) -> float:
    """Angle at b between points a-b-c, in radians."""
    ba = np.array(sub(a, b), dtype=np.float64)
    bc = np.array(sub(c, b), dtype=np.float64)
    denom = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denom < 1e-9:
        return 0.0
    cos_angle = float(np.dot(ba, bc) / denom)
    cos_angle = max(-1.0, min(1.0, cos_angle))
    return float(math.acos(cos_angle))
