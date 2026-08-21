"""Interactive training-data collector.

Hold a pose and press the matching key each frame you want saved.
Move your hand slightly between samples (angle, distance, position).

Controls:
  1  -> infinite_void
  2  -> domain_expansion_2   (rename in KEY_LABELS as needed)
  0  -> none (required negative class)
  q  -> quit

Always collect plenty of "none" — resting, pointing, talking with hands, etc.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import cv2
import mediapipe as mp

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gesture_recognizer.hand_wrapper import hands_from_result
from gesture_recognizer.normalize import TWO_HAND_DIM, normalize_two_hands

OUTPUT_CSV = ROOT / "data" / "gestures.csv"

KEY_LABELS = {
    ord("1"): "infinite_void",
    ord("2"): "domain_expansion_2",
    ord("0"): "none",
}


def ensure_csv_header() -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    if not OUTPUT_CSV.exists():
        with OUTPUT_CSV.open("w", newline="") as f:
            writer = csv.writer(f)
            header = ["label"] + [f"f{i}" for i in range(TWO_HAND_DIM)]
            writer.writerow(header)


def append_sample(label: str, features) -> None:
    with OUTPUT_CSV.open("a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([label] + features.tolist())


def main() -> None:
    ensure_csv_header()

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    counts = {label: 0 for label in KEY_LABELS.values()}

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    ) as hands:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            active_label = None
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

            if result.multi_hand_landmarks:
                for hand_lms in result.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, hand_lms, mp_hands.HAND_CONNECTIONS
                    )

                hand_objs = hands_from_result(
                    [h.landmark for h in result.multi_hand_landmarks],
                    result.multi_handedness,
                )

                if key in KEY_LABELS:
                    active_label = KEY_LABELS[key]
                    features = normalize_two_hands(hand_objs)
                    append_sample(active_label, features)
                    counts[active_label] += 1

            y = 30
            for label, count in counts.items():
                cv2.putText(
                    frame,
                    f"{label}: {count}",
                    (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
                y += 25
            if active_label:
                cv2.putText(
                    frame,
                    f"SAVED: {active_label}",
                    (10, y + 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow("Data Collection - press label keys, q to quit", frame)

    cap.release()
    cv2.destroyAllWindows()
    print("Final counts:", counts)
    print(f"Saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
