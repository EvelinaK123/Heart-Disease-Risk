"""Compare two classifiers using training-only cross-validation, then evaluate once."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from common import (
    CATEGORICAL_FEATURES,
    FEATURES,
    NUMERIC_FEATURES,
    TARGET,
    prepare_features,
    prepare_target,
    read_csv,
)


RANDOM_STATE = 42
TEST_SIZE = 0.20
CV_FOLDS = 5


def make_pipeline(classifier) -> Pipeline:
    numeric = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("one_hot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessing = ColumnTransformer(
        transformers=[
            ("numeric", numeric, NUMERIC_FEATURES),
            ("categorical", categorical, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )
    return Pipeline(
        steps=[("preprocessor", preprocessing), ("classifier", classifier)]
    )


def evaluate(pipeline: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    predictions = pipeline.predict(X_test)
    matrix = confusion_matrix(y_test, predictions, labels=[0, 1])
    tn, fp, fn, tp = (int(value) for value in matrix.ravel())
    scores = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall_sensitivity": float(recall_score(y_test, predictions, zero_division=0)),
        "specificity": float(tn / (tn + fp)) if tn + fp else None,
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": None,
        "confusion_matrix": {"labels": [0, 1], "rows_actual_columns_predicted": matrix.tolist()},
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
        "true_positive": tp,
    }
    try:
        classes = list(pipeline.named_steps["classifier"].classes_)
        positive_index = classes.index(1)
        probability = pipeline.predict_proba(X_test)[:, positive_index]
        scores["roc_auc"] = float(roc_auc_score(y_test, probability))
    except (AttributeError, ValueError, IndexError):
        scores["roc_auc"] = None
    return scores


def report_markdown(
    selected_name: str,
    comparison: list[dict],
    metrics: dict,
    train_size: int,
    test_size: int,
) -> str:
    auc = "Not available" if metrics["roc_auc"] is None else f"{metrics['roc_auc']:.3f}"
    matrix = metrics["confusion_matrix"]["rows_actual_columns_predicted"]
    comparison_rows = "\n".join(
        f"| {row['model']} | {row['mean_balanced_accuracy']:.3f} | "
        f"{row['std_balanced_accuracy']:.3f} |"
        for row in comparison
    )
    return f"""# Model evaluation report

## Setup

- Train rows: {train_size:,}
- Test rows: {test_size:,} (20%, stratified by `HeartDisease`)
- Random seed: {RANDOM_STATE}
- Model selection: highest mean balanced accuracy in {CV_FOLDS}-fold stratified cross-validation on training data only.
- Selected model: **{selected_name}**

The test set was held out while comparing and selecting models. It was evaluated once after selection.

## Training-only model comparison

| Model | Mean training CV balanced accuracy | Standard deviation |
|---|---:|---:|
{comparison_rows}

## Final selected model on the held-out test set

| Metric | Score |
|---|---:|
| Accuracy | {metrics['accuracy']:.3f} |
| Balanced accuracy | {metrics['balanced_accuracy']:.3f} |
| Precision (class 1) | {metrics['precision']:.3f} |
| Recall / sensitivity (class 1) | {metrics['recall_sensitivity']:.3f} |
| Specificity (class 0) | {metrics['specificity']:.3f} |
| F1 (class 1) | {metrics['f1']:.3f} |
| ROC-AUC | {auc} |

Confusion matrix (rows are actual labels, columns are predicted labels; order is 0, 1):

| Actual \\ Predicted | 0 | 1 |
|---|---:|---:|
| 0 | {matrix[0][0]} | {matrix[0][1]} |
| 1 | {matrix[1][0]} | {matrix[1][1]} |

- False positive: the model predicts dataset label 1 for a row whose dataset label is 0.
- False negative: the model predicts dataset label 0 for a row whose dataset label is 1.

These are errors against this CSV's labels. Scores summarize this dataset split; they do not establish clinical usefulness or provide a medical diagnosis.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/heart.csv", help="Path to labeled heart.csv")
    parser.add_argument("--models-dir", default="models", help="Directory for the fitted pipeline")
    parser.add_argument("--reports-dir", default="reports", help="Directory for evaluation results")
    args = parser.parse_args()

    frame = read_csv(args.data)
    X = prepare_features(frame, "Training CSV")
    y = prepare_target(frame)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    models = {
        "Logistic Regression": LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            random_state=RANDOM_STATE,
            n_jobs=1,
        ),
    }
    cross_validation = StratifiedKFold(
        n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE
    )
    comparison = []
    fitted_candidates = {}
    for name, classifier in models.items():
        candidate = make_pipeline(classifier)
        cv = cross_validate(
            candidate,
            X_train,
            y_train,
            cv=cross_validation,
            scoring="balanced_accuracy",
            n_jobs=-1,
            error_score="raise",
        )
        mean_score = float(cv["test_score"].mean())
        std_score = float(cv["test_score"].std())
        comparison.append(
            {
                "model": name,
                "mean_balanced_accuracy": mean_score,
                "std_balanced_accuracy": std_score,
            }
        )
        fitted_candidates[name] = candidate

    selected = max(comparison, key=lambda row: row["mean_balanced_accuracy"])
    selected_name = selected["model"]
    final_pipeline = fitted_candidates[selected_name]
    final_pipeline.fit(X_train, y_train)
    metrics = evaluate(final_pipeline, X_test, y_test)

    models_dir = Path(args.models_dir)
    reports_dir = Path(args.reports_dir)
    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / "heart_disease_pipeline.joblib"
    joblib.dump(final_pipeline, model_path)

    evaluation = {
        "selected_model": selected_name,
        "selection_metric": "mean balanced accuracy in 5-fold cross-validation on training data",
        "random_state": RANDOM_STATE,
        "test_size_fraction": TEST_SIZE,
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "training_cv_comparison": comparison,
        "test_metrics": metrics,
        "model_file": str(model_path),
    }
    (reports_dir / "evaluation_results.json").write_text(
        json.dumps(evaluation, indent=2), encoding="utf-8"
    )
    (reports_dir / "evaluation_report.md").write_text(
        report_markdown(selected_name, comparison, metrics, len(X_train), len(X_test)),
        encoding="utf-8",
    )
    pd.DataFrame(comparison).to_csv(reports_dir / "model_comparison.csv", index=False)

    print(f"Selected by training-only cross-validation: {selected_name}")
    print(f"Saved fitted preprocessing + model pipeline to {model_path}")
    print(f"Saved evaluation report to {reports_dir / 'evaluation_report.md'}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

