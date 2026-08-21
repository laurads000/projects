"""MediaPipe hand landmark wrappers: Point, Finger, Hand."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Sequence

# MediaPipe hand landmark indices
WRIST = 0
THUMB_CMC, THUMB_MCP, THUMB_IP, THUMB_TIP = 1, 2, 3, 4
INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP = 5, 6, 7, 8
MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP = 9, 10, 11, 12
RING_MCP, RING_PIP, RING_DIP, RING_TIP = 13, 14, 15, 16
PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP = 17, 18, 19, 20


@dataclass(frozen=True)
class Point:
    """Normalized landmark: (0, 0) is top-left; x→right, y→down; smaller z = closer."""

    x: float
    y: float
    z: float = 0.0

    @classmethod
    def from_landmark(cls, lm) -> Point:
        return cls(x=lm.x, y=lm.y, z=getattr(lm, "z", 0.0) or 0.0)


@dataclass(frozen=True)
class Finger:
    """One finger's joint coordinates from MediaPipe."""

    name: str
    mcp: Point
    tip: Point
    pip: Optional[Point] = None  # IP for thumb
    dip: Optional[Point] = None  # not present on thumb
    cmc: Optional[Point] = None  # thumb base only


@dataclass(frozen=True)
class Hand:
    """One hand: wrist + five fingers."""

    wrist: Point
    thumb: Finger
    index: Finger
    middle: Finger
    ring: Finger
    pinky: Finger
    handedness: Optional[str] = None

    @property
    def fingers(self) -> tuple[Finger, Finger, Finger, Finger, Finger]:
        return (self.thumb, self.index, self.middle, self.ring, self.pinky)

    @classmethod
    def from_landmarks(
        cls,
        landmarks: Sequence,
        handedness: Optional[str] = None,
    ) -> Hand:
        def p(i: int) -> Point:
            return Point.from_landmark(landmarks[i])

        thumb = Finger(
            name="thumb",
            cmc=p(THUMB_CMC),
            mcp=p(THUMB_MCP),
            pip=p(THUMB_IP),  # IP stands in for PIP
            tip=p(THUMB_TIP),
        )
        index = Finger(
            name="index",
            mcp=p(INDEX_MCP),
            pip=p(INDEX_PIP),
            dip=p(INDEX_DIP),
            tip=p(INDEX_TIP),
        )
        middle = Finger(
            name="middle",
            mcp=p(MIDDLE_MCP),
            pip=p(MIDDLE_PIP),
            dip=p(MIDDLE_DIP),
            tip=p(MIDDLE_TIP),
        )
        ring = Finger(
            name="ring",
            mcp=p(RING_MCP),
            pip=p(RING_PIP),
            dip=p(RING_DIP),
            tip=p(RING_TIP),
        )
        pinky = Finger(
            name="pinky",
            mcp=p(PINKY_MCP),
            pip=p(PINKY_PIP),
            dip=p(PINKY_DIP),
            tip=p(PINKY_TIP),
        )
        return cls(
            wrist=p(WRIST),
            thumb=thumb,
            index=index,
            middle=middle,
            ring=ring,
            pinky=pinky,
            handedness=handedness,
        )


def _handedness_label(entry: Any) -> Optional[str]:
    """Support Tasks API (category_name) and legacy Hands (.classification[].label)."""
    if entry is None:
        return None
    if isinstance(entry, str):
        return entry

    # Legacy mp.solutions.hands: ClassificationList
    classification = getattr(entry, "classification", None)
    if classification:
        return classification[0].label

    # Tasks HandLandmarker: sequence of Category
    try:
        first = entry[0]
    except (TypeError, IndexError, KeyError):
        return None

    if hasattr(first, "category_name"):
        return first.category_name
    if hasattr(first, "label"):
        return first.label
    return None


def hands_from_result(hand_landmarks_list, handedness_list=None) -> list[Hand]:
    """Build Hand objects from MediaPipe landmark + handedness fields."""
    hands: list[Hand] = []
    for i, landmarks in enumerate(hand_landmarks_list):
        label = None
        if handedness_list is not None and i < len(handedness_list):
            label = _handedness_label(handedness_list[i])
        hands.append(Hand.from_landmarks(landmarks, label))
    return hands
