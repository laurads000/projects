"""Train a RandomForest on data/gestures.csv and save models/gesture_model.pkl."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "gestures.csv"
MODEL_PATH = ROOT / "models" / "gesture_model.pkl"


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit(
            f"No data at {DATA_PATH}. Run scripts/data_collection.py first."
        )

    df = pd.read_csv(DATA_PATH)
    if len(df) < 10:
        raise SystemExit(
            f"Only {len(df)} samples in {DATA_PATH}. Collect more data first."
        )

    print("Samples per class:")
    print(df["label"].value_counts())
    print()

    X = df.drop(columns=["label"]).values
    y = df["label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print("Classification report:")
    print(classification_report(y_test, y_pred))
    print("Confusion matrix (rows=true, cols=predicted):")
    print("Classes order:", clf.classes_)
    print(confusion_matrix(y_test, y_pred, labels=clf.classes_))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
