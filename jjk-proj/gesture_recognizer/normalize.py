"""Converts Hand objects into normalized, scale-invariant feature vectors."""

from __future__ import annotations

import numpy as np

from gesture_recognizer.hand_wrapper import Hand, Point

LANDMARK_ORDER = [
    "wrist",
    "thumb.cmc", "thumb.mcp", "thumb.pip", "thumb.tip",
    "index.mcp", "index.pip", "index.dip", "index.tip",
    "middle.mcp", "middle.pip", "middle.dip", "middle.tip",
    "ring.mcp", "ring.pip", "ring.dip", "ring.tip",
    "pinky.mcp", "pinky.pip", "pinky.dip", "pinky.tip",
]

NUM_LANDMARKS = len(LANDMARK_ORDER)  # 21
SINGLE_HAND_DIM = NUM_LANDMARKS * 3  # 63 (NUM_LANDMARKS x 3 coords: (x, y, z))
TWO_HAND_DIM = SINGLE_HAND_DIM * 2   # 126 (SINGLE_HAND_DIM x 2 hands)


def _get_point(hand: Hand, dotted_name: str) -> Point:
    if dotted_name == "wrist":
        return hand.wrist
    finger_name, joint_name = dotted_name.split(".")
    finger = getattr(hand, finger_name)
    point = getattr(finger, joint_name)
    if point is None:
        raise ValueError(f"{dotted_name} is None on this hand (missing joint).")
    return point


def hand_to_array(hand: Hand) -> np.ndarray:
    """Convert Hand to raw (21, 3) array of (x, y, z)."""
    coords = [
        (p.x, p.y, p.z)
        for p in (_get_point(hand, name) for name in LANDMARK_ORDER)
    ]
    return np.array(coords, dtype=np.float32)

# Normalize a single hand
# 1. Subtract the wrist position from every point --> wrist becomes the origin, translation-invariant
# 2. Divide every coordinate by the largest distance from the wrist to any other landmark 
#   --> makes dist from camera irrelevant, scale invariant
def normalize_hand(hand: Hand) -> np.ndarray:   # returns (63,) feature vector
    # 1. Translation invariant
    coords = hand_to_array(hand)
    wrist = coords[0].copy()
    coords -= wrist 

    # 2. Scale invariant
    distances = np.linalg.norm(coords, axis=1)  # distance of each point from wrist
    max_dist = distances.max()
    if max_dist > 1e-6:                     # tolerance 
        coords /= max_dist

    return coords.flatten()

# Normalize two hands
# 1. Combine up to two Hands into one fixed-length (126,) vector.
# 2. Order: [left, right] regardless of the order MediaPipe detected them
# 3. A missing hand is zero-filled
def normalize_two_hands(
    hands: list[Hand],
    left_first: bool = True,
) -> np.ndarray:

    # default 0 for all indices
    left = np.zeros(SINGLE_HAND_DIM, dtype=np.float32)
    right = np.zeros(SINGLE_HAND_DIM, dtype=np.float32)

    for hand in hands:
        vec = normalize_hand(hand)
        if hand.handedness == "Left":
            left = vec
        elif hand.handedness == "Right":
            right = vec
        else:
            if not left.any():
                left = vec
            else:
                right = vec

    return (
        np.concatenate([left, right])
        if left_first
        else np.concatenate([right, left])
    )
