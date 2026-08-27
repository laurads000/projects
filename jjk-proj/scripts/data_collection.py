"""Interactive training-data collector (HandLandmarker Tasks API).

Hold a pose and press the matching key each frame you want saved.
Move your hand slightly between samples (angle, distance, position).

The KEY you press is how you tell the program which gesture you're teaching.
You do the Infinite Void hand sign → hold/press 1. Sukuna's seal → press 2.
Ordinary hands (not a domain seal) → press 0 ("none").

Controls:
  1  -> infinite_void       (Gojo)
  2  -> malevolent_shrine   (Sukuna)
  0  -> none                (not a special gesture — required!)
  q  -> quit
"""

from __future__ import annotations

import csv
import sys
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gesture_recognizer.hand_wrapper import hands_from_result
from gesture_recognizer.normalize import TWO_HAND_DIM, normalize_two_hands

OUTPUT_CSV = ROOT / "data" / "gestures.csv"
MODEL_PATH = ROOT / "hand_landmarker.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)

# Keyboard → class name stored in gestures.csv / learned by the model
KEY_LABELS = {
    ord("1"): "infinite_void",
    ord("2"): "malevolent_shrine",
    ord("0"): "none",
}

DISPLAY_NAMES = {
    "infinite_void": "Infinite void (Gojo)",
    "malevolent_shrine": "Malevolent shrine (Sukuna)",
    "none": "none (not a seal)",
}


def ensure_model() -> None:
    if MODEL_PATH.exists():
        return
    print(f"Downloading hand model to {MODEL_PATH}...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)


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


def draw_landmarks(frame, hand_landmarks_list) -> None:
    height, width, _ = frame.shape
    for landmarks in hand_landmarks_list:
        points = [(int(lm.x * width), int(lm.y * height)) for lm in landmarks]
        for connection in vision.HandLandmarksConnections.HAND_CONNECTIONS:
            cv2.line(
                frame,
                points[connection.start],
                points[connection.end],
                (0, 255, 0),
                2,
            )
        for point in points:
            cv2.circle(frame, point, 3, (0, 0, 255), -1)


def main() -> None:
    ensure_model()
    ensure_csv_header()

    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.7,
    )
    detector = vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(1)
    counts = {label: 0 for label in KEY_LABELS.values()}
    frame_timestamp_ms = 0

    try:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = detector.detect_for_video(mp_image, frame_timestamp_ms)
            frame_timestamp_ms += 33

            active_label = None
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

            if result.hand_landmarks:
                draw_landmarks(frame, result.hand_landmarks)
                hand_objs = hands_from_result(
                    result.hand_landmarks,
                    result.handedness,
                )

                if key in KEY_LABELS:
                    active_label = KEY_LABELS[key]
                    features = normalize_two_hands(hand_objs)
                    append_sample(active_label, features)
                    counts[active_label] += 1

            y = 30
            for label, count in counts.items():
                title = DISPLAY_NAMES.get(label, label)
                cv2.putText(
                    frame,
                    f"{title}: {count}",
                    (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )
                y += 25
            cv2.putText(
                frame,
                "1=Gojo void  2=Sukuna shrine  0=none  q=quit",
                (10, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
            )
            if active_label:
                cv2.putText(
                    frame,
                    f"SAVED: {DISPLAY_NAMES.get(active_label, active_label)}",
                    (10, y + 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow("Data Collection - press label keys, q to quit", frame)
    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.close()

    print("Final counts:", counts)
    print(f"Saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
