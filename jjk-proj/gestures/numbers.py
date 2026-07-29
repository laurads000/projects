"""Count raised fingers from MediaPipe hand landmarks.

Normalized landmark coords: (0, 0) is the top-left of the image,
x increases right, y increases down. Values are in [0, 1].
"""
#logic: count fingers up if tip.y < pip.y
# ** thumb: 
from __future__ import annotations

import math
import time
from typing import Optional, Sequence

# MediaPipe hand landmark indices
_THUMB_CMC = 1  # base of thumb
_THUMB_MCP = 2  # next thumb joint
_THUMB_IP = 3
_THUMB_TIP = 4
_INDEX_MCP = 5  # index knuckle
_FINGER_TIPS = (8, 12, 16, 20)  # index, middle, ring, pinky
_FINGER_PIPS = (6, 10, 14, 18)

# Thumb is "up" only if all pass:
# 1) abduction angle at CMC (CMC→MCP vs CMC→index knuckle)
# 2) extension: tip farther from CMC than MCP is (MCP vs CMC length)
# 3) tip.y < IP.y (same tip-above-joint idea as other fingers; IP ≈ PIP)
_THUMB_ABDUCTION_DEG = 30.0


def _angle_deg(a, b, c) -> float:
    """Angle ABC in degrees (vertex at b)."""
    ba_x, ba_y = a.x - b.x, a.y - b.y
    bc_x, bc_y = c.x - b.x, c.y - b.y
    norm_ba = math.hypot(ba_x, ba_y)
    norm_bc = math.hypot(bc_x, bc_y)
    if norm_ba == 0 or norm_bc == 0:
        return 0.0
    cos = (ba_x * bc_x + ba_y * bc_y) / (norm_ba * norm_bc)
    cos = max(-1.0, min(1.0, cos))
    return math.degrees(math.acos(cos))


def _dist(a, b) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def _thumb_is_up(landmarks: Sequence) -> bool:
    cmc = landmarks[_THUMB_CMC]
    mcp = landmarks[_THUMB_MCP]
    ip = landmarks[_THUMB_IP]
    tip = landmarks[_THUMB_TIP]
    index_mcp = landmarks[_INDEX_MCP]

    # 1) Angle at CMC between next thumb joint and index knuckle.
    abduction = _angle_deg(mcp, cmc, index_mcp)
    if abduction < _THUMB_ABDUCTION_DEG:
        return False

    # 2) MCP vs CMC: thumb extended if tip is beyond MCP from the CMC base.
    if _dist(cmc, tip) <= _dist(cmc, mcp):
        return False

    # 3) Tip above IP (thumb's PIP equivalent); y grows downward.
    if tip.y >= ip.y:
        return False

    return True


def count_fingers_up(
    landmarks: Sequence,
    handedness: Optional[str] = None,
) -> int:
    """Return how many fingers are extended (0–5) for one hand."""
    _ = handedness  # kept for call-site compatibility; thumb no longer uses it
    tips_up = 0

    if _thumb_is_up(landmarks):
        tips_up += 1

    # Other fingers: tip above PIP in image coords (y grows downward).
    for tip_idx, pip_idx in zip(_FINGER_TIPS, _FINGER_PIPS):
        if landmarks[tip_idx].y < landmarks[pip_idx].y:
            tips_up += 1

    return tips_up


def count_all_fingers_up(
    hand_landmarks_list: Sequence,
    handedness_list: Optional[Sequence] = None,
) -> int:
    """Sum raised fingers across all detected hands."""
    total = 0
    for i, landmarks in enumerate(hand_landmarks_list):
        label = None
        if handedness_list is not None and i < len(handedness_list):
            categories = handedness_list[i]
            if categories:
                label = categories[0].category_name
        total += count_fingers_up(landmarks, label)
    return total


class FingerHoldTracker:
    """Emit a finger count once it has been held steady for ``hold_seconds``."""

    def __init__(self, hold_seconds: float = 3.0) -> None:
        self.hold_seconds = hold_seconds
        self._current: Optional[int] = None
        self._since: Optional[float] = None
        self._reported: Optional[int] = None

    def update(self, count: Optional[int]) -> Optional[int]:
        """Feed the latest count (or ``None`` if no hand).

        Returns the count the first time the hold duration is met; otherwise
        ``None``. Changing the count (or losing the hand) resets the timer.
        """
        now = time.monotonic()

        if count is None:
            self._current = None
            self._since = None
            return None

        if count != self._current:
            self._current = count
            self._since = now
            self._reported = None
            return None

        if self._since is None:
            self._since = now
            return None

        if (
            now - self._since >= self.hold_seconds
            and self._reported != count
        ):
            self._reported = count
            return count

        return None

    def hold_progress(self) -> float:
        """Fraction of the hold completed for the current count (0–1)."""
        if self._current is None or self._since is None:
            return 0.0
        elapsed = time.monotonic() - self._since
        return min(1.0, elapsed / self.hold_seconds)
