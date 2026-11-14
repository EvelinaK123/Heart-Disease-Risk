"""Shared column definitions and input checks for the project scripts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


TARGET = "HeartDisease"
NUMERIC_FEATURES = ["Age", "RestingBP", "Cholesterol", "FastingBS", "MaxHR", "Oldpeak"]
CATEGORICAL_FEATURES = [
    "Sex",
    "ChestPainType",
    "RestingECG",
    "ExerciseAngina",
    "ST_Slope",
]
FEATURES = [
    "Age",
    "Sex",
    "ChestPainType",
    "RestingBP",
    "Cholesterol",
    "FastingBS",
    "RestingECG",
    "MaxHR",
    "ExerciseAngina",
    "Oldpeak",
    "ST_Slope",
]


def read_csv(path: str | Path) -> pd.DataFrame:
    """Read a CSV and give a friendly error if the file cannot be opened."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Could not find {path}. Copy heart.csv into the project's data folder "
            "or pass the correct path with --data."
        )
    return pd.read_csv(path)


def require_columns(frame: pd.DataFrame, required: list[str], context: str) -> None:
    """Raise a readable error listing required columns absent from a CSV."""
    missing = [name for name in required if name not in frame.columns]
    if missing:
        raise ValueError(
            f"{context} is missing required column(s): {', '.join(missing)}. "
            f"Columns found: {', '.join(map(str, frame.columns))}"
        )


def prepare_features(frame: pd.DataFrame, context: str = "Input CSV") -> pd.DataFrame:
    """Select the 11 model inputs in a stable order and parse numeric fields."""
    require_columns(frame, FEATURES, context)
    result = frame.loc[:, FEATURES].copy()
    for name in NUMERIC_FEATURES:
        try:
            result[name] = pd.to_numeric(result[name], errors="raise")
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Column {name!r} must contain numeric values. Check the input CSV."
            ) from error
    return result


def prepare_target(frame: pd.DataFrame) -> pd.Series:
    """Validate and return the binary dataset label."""
    require_columns(frame, [TARGET], "Training CSV")
    try:
        numeric_target = pd.to_numeric(frame[TARGET], errors="raise")
    except (TypeError, ValueError) as error:
        raise ValueError("HeartDisease must contain only the integer labels 0 and 1.") from error
    values = set(numeric_target.dropna().unique())
    if numeric_target.isna().any() or not values.issubset({0, 1}) or values != {0, 1}:
        raise ValueError(
            "HeartDisease must contain both dataset labels 0 and 1, with no missing labels."
        )
    return numeric_target.astype(int)

