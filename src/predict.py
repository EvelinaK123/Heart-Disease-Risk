"""Use a saved pipeline to predict dataset labels for an unlabeled CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib

from common import prepare_features, read_csv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV with the 11 predictor columns")
    parser.add_argument(
        "--model",
        default="models/heart_disease_pipeline.joblib",
        help="Path to the pipeline created by src/train.py",
    )
    parser.add_argument("--output", required=True, help="Where to write prediction results CSV")
    args = parser.parse_args()

    model_path = Path(args.model)
    if not model_path.is_file():
        raise FileNotFoundError(
            f"Could not find fitted pipeline {model_path}. Run src/train.py first."
        )
    source = read_csv(args.input)
    features = prepare_features(source, "Prediction CSV")
    pipeline = joblib.load(model_path)
    predicted = pipeline.predict(features)

    results = features.copy()
    results["PredictedHeartDisease"] = predicted.astype(int)
    try:
        classes = list(pipeline.named_steps["classifier"].classes_)
        positive_index = classes.index(1)
        results["ScoreForHeartDisease1"] = pipeline.predict_proba(features)[:, positive_index]
    except (AttributeError, ValueError, IndexError):
        pass

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output, index=False)
    print(f"Wrote {len(results)} prediction(s) to {output}")


if __name__ == "__main__":
    main()

