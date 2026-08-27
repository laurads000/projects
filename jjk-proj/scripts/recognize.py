"""Real-time gesture recognition using models/gesture_model.pkl."""

from __future__ import annotations

import sys
import urllib.request
from collections import deque
from pathlib import Path

import cv2
import joblib
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gesture_recognizer.hand_wrapper import hands_from_result
from gesture_recognizer.normalize import normalize_two_hands

CLF_PATH = ROOT / "models" / "gesture_model.pkl"
LANDMARKER_PATH = ROOT / "hand_landmarker.task"
LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
CONFIDENCE_THRESHOLD = 0.85
SMOOTHING_WINDOW = 10
CONFIRM_FRACTION = 1.0

DISPLAY_NAMES = {
    "infinite_void": "Infinite void (Gojo)",
    "malevolent_shrine": "Malevolent shrine (Sukuna)",
    "none": "none",
}


def ensure_model() -> None:
    if LANDMARKER_PATH.exists():
        return
    print(f"Downloading hand model to {LANDMARKER_PATH}...")
    urllib.request.urlretrieve(LANDMARKER_URL, LANDMARKER_PATH)


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
    if not CLF_PATH.exists():
        raise SystemExit(
            f"No classifier at {CLF_PATH}. Run scripts/train.py first."
        )

    ensure_model()
    clf = joblib.load(CLF_PATH)

    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(LANDMARKER_PATH)),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.7,
    )
    detector = vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(1)
    recent: deque[str] = deque(maxlen=SMOOTHING_WINDOW)
    confirmed_gesture = None
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

            current_label = "none"
            current_conf = 0.0

            if result.hand_landmarks:
                draw_landmarks(frame, result.hand_landmarks)
                hand_objs = hands_from_result(
                    result.hand_landmarks,
                    result.handedness,
                )
                features = normalize_two_hands(hand_objs).reshape(1, -1)

                probs = clf.predict_proba(features)[0]
                best_idx = int(probs.argmax())
                current_conf = float(probs[best_idx])
                predicted = clf.classes_[best_idx]

                if current_conf >= CONFIDENCE_THRESHOLD:
                    current_label = predicted

            recent.append(current_label)

            if len(recent) == SMOOTHING_WINDOW:
                most_common = max(set(recent), key=recent.count)
                agreement = recent.count(most_common) / SMOOTHING_WINDOW
                if most_common != "none" and agreement >= CONFIRM_FRACTION:
                    if confirmed_gesture != most_common:
                        confirmed_gesture = most_common
                        on_gesture_confirmed(confirmed_gesture)
                else:
                    confirmed_gesture = None

            display = DISPLAY_NAMES.get(current_label, current_label)
            cv2.putText(
                frame,
                f"Frame: {display} ({current_conf:.2f})",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2,
            )
            if confirmed_gesture:
                confirmed_display = DISPLAY_NAMES.get(
                    confirmed_gesture, confirmed_gesture
                )
                cv2.putText(
                    frame,
                    f"CONFIRMED: {confirmed_display}",
                    (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 0, 255),
                    3,
                )

            cv2.imshow("Gesture Recognition", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.close()


def on_gesture_confirmed(label: str) -> None:
    display = DISPLAY_NAMES.get(label, label)
    print(f">>> Gesture confirmed: {display}")


if __name__ == "__main__":
    main()
