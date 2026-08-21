"""Real-time gesture recognition using models/gesture_model.pkl."""

from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

import cv2
import joblib
import mediapipe as mp

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gesture_recognizer.hand_wrapper import hands_from_result
from gesture_recognizer.normalize import normalize_two_hands

MODEL_PATH = ROOT / "models" / "gesture_model.pkl"
CONFIDENCE_THRESHOLD = 0.85
SMOOTHING_WINDOW = 10
CONFIRM_FRACTION = 1.0


def main() -> None:
    if not MODEL_PATH.exists():
        raise SystemExit(
            f"No model at {MODEL_PATH}. Run scripts/train.py first."
        )

    clf = joblib.load(MODEL_PATH)

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    recent: deque[str] = deque(maxlen=SMOOTHING_WINDOW)
    confirmed_gesture = None

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

            current_label = "none"
            current_conf = 0.0

            if result.multi_hand_landmarks:
                for hand_lms in result.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, hand_lms, mp_hands.HAND_CONNECTIONS
                    )

                hand_objs = hands_from_result(
                    [h.landmark for h in result.multi_hand_landmarks],
                    result.multi_handedness,
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

            cv2.putText(
                frame,
                f"Frame: {current_label} ({current_conf:.2f})",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2,
            )
            if confirmed_gesture:
                cv2.putText(
                    frame,
                    f"CONFIRMED: {confirmed_gesture}",
                    (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 0, 255),
                    3,
                )

            cv2.imshow("Gesture Recognition", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


def on_gesture_confirmed(label: str) -> None:
    print(f">>> Gesture confirmed: {label}")


if __name__ == "__main__":
    main()
