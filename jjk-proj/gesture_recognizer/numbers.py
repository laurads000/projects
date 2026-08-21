"""Count raised fingers using Hand / Finger wrappers."""

from __future__ import annotations

import math
import time
from typing import Optional, Sequence

from gesture_recognizer.hand_wrapper import Hand, hands_from_result

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


def _thumb_is_up(hand: Hand) -> bool:
    thumb = hand.thumb
    assert thumb.cmc is not None and thumb.pip is not None
    cmc, mcp, ip, tip = thumb.cmc, thumb.mcp, thumb.pip, thumb.tip
    index_mcp = hand.index.mcp

    # 1) Angle at CMC between next thumb joint and index knuckle.
    if _angle_deg(mcp, cmc, index_mcp) < _THUMB_ABDUCTION_DEG:
        return False

    # 2) MCP vs CMC: tip beyond MCP from CMC base.
    if _dist(cmc, tip) <= _dist(cmc, mcp):
        return False

    # 3) Tip above IP (y grows downward).
    if tip.y >= ip.y:
        return False

    return True


def count_fingers_up(hand: Hand) -> int:
    """Return how many fingers are extended (0–5) for one hand."""
    tips_up = 0

    if _thumb_is_up(hand):
        tips_up += 1

    for finger in (hand.index, hand.middle, hand.ring, hand.pinky):
        if finger.pip is not None and finger.tip.y < finger.pip.y:
            tips_up += 1

    return tips_up


def count_all_fingers_up(hands: Sequence[Hand]) -> int:
    """Sum raised fingers across all detected hands."""
    return sum(count_fingers_up(hand) for hand in hands)


def count_all_fingers_up_from_landmarks(
    hand_landmarks_list: Sequence,
    handedness_list: Optional[Sequence] = None,
) -> int:
    """Convenience: MediaPipe landmark lists → finger count."""
    return count_all_fingers_up(hands_from_result(hand_landmarks_list, handedness_list))


class FingerHoldTracker:
    """Emit a value once it has been held steady for ``hold_seconds``."""

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
