import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_PATH = Path(__file__).resolve().parent / "hand_landmarker.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)

# checking if the model is already downloaded
def ensure_model() -> None:
    if MODEL_PATH.exists():
        return
    print(f"Downloading hand model to {MODEL_PATH}...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

# drawing the hand landmarks
def draw_hand_landmarks(frame, hand_landmarks_list) -> None:
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

# actual shenanigans
def main() -> None:
    ensure_model()

    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.7,
    )
    detector = vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(1)
    frame_timestamp_ms = 0

    try:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = detector.detect_for_video(mp_image, frame_timestamp_ms)
            frame_timestamp_ms += 33

            if result.hand_landmarks:
                draw_hand_landmarks(frame, result.hand_landmarks)

            cv2.imshow("Hand demo", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.close()


if __name__ == "__main__":
    main()
