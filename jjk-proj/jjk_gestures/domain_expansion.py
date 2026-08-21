"""JJK domain-expansion gesture detection."""

# GESTURE GUIDE:
# infinite void: Gojo
# malevolent shrine: Sukuna
from __future__ import annotations

import math
from typing import Sequence

from gesture_recognizer.hand_wrapper import Hand

# How close index/middle PIPs must be in normalized image coords.
_PIP_ALIGN_TOL = 0.04
# Middle must be at least this much farther (larger z) than index tip.
_Z_FARTHER_MARGIN = 0.00


def _xy_dist(a, b) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def is_infinite_void(hand: Hand) -> bool:
    """True if index/middle PIPs align and middle tip is farther than index."""
    assert hand.index.pip is not None and hand.middle.pip is not None

    # 1) PIP of index (2nd) and middle (3rd) lined up within tolerance.
    if _xy_dist(hand.index.pip, hand.middle.pip) > _PIP_ALIGN_TOL:
        return False

    # 2) Middle tip farther from camera than index tip (larger z).
    if hand.middle.tip.z < hand.index.tip.z + _Z_FARTHER_MARGIN:
        return False

    return True


def any_hand_infinite_void(hands: Sequence[Hand]) -> bool:
    return any(is_infinite_void(hand) for hand in hands)
