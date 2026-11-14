"""Create a markdown data inspection report from the supplied training CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from common import (
    CATEGORICAL_FEATURES,
    FEATURES,
    NUMERIC_FEATURES,
    TARGET,
    read_csv,
    require_columns,
)


def count_outside(series: pd.Series, low: float, high: float) -> int:
    values = pd.to_numeric(series, errors="coerce")
    return int(((values < low) | (values > high)).sum())


def build_report(frame: pd.DataFrame, source: str) -> str:
    require_columns(frame, FEATURES + [TARGET], "Training CSV")
    lines = [
        "# Data inspection and EDA report",
        "",
        f"Source file: `{source}`",
        "",
        "## File overview",
        "",
        f"- Rows: {len(frame):,}",
        f"- Columns: {len(frame.columns)}",
        f"- Column names: {', '.join(f'`{column}`' for column in frame.columns)}",
        "- Required predictors: 11 matching fields from the Triage page.",
        "- `ca` and `thal` are not in this CSV and are not used or required.",
        "",
        "## Data types and missing values",
        "",
        "| Column | Loaded data type | Missing values | Distinct non-missing values |",
        "|---|---:|---:|---:|",
    ]
    for column in frame.columns:
        lines.append(
            f"| `{column}` | `{frame[column].dtype}` | "
            f"{int(frame[column].isna().sum())} | {int(frame[column].nunique(dropna=True))} |"
        )

    lines += [
        "",
        "## Duplicate rows",
        "",
        f"Exact duplicate rows beyond the first copy: **{int(frame.duplicated().sum())}**.",
        "No rows are removed by the inspection or training scripts.",
        "",
        "## Target balance",
        "",
        f"`{TARGET}` is the dataset label: 1 means the dataset label is present; "
        "0 means it is absent. This is a prediction of the dataset label.",
        "",
        "| Dataset label | Rows | Share |",
        "|---:|---:|---:|",
    ]
    target_counts = frame[TARGET].value_counts(dropna=False).sort_index()
    for value, count in target_counts.items():
        share = count / len(frame) * 100 if len(frame) else 0
        lines.append(f"| {value} | {count:,} | {share:.1f}% |")

    lines += ["", "## Category values", ""]
    for column in CATEGORICAL_FEATURES + ["FastingBS"]:
        if column not in frame.columns:
            continue
        counts = frame[column].value_counts(dropna=False).sort_index(key=lambda s: s.astype(str))
        rendered = ", ".join(f"`{value}`: {count:,}" for value, count in counts.items())
        lines.append(f"- `{column}`: {rendered}")

    lines += [
        "",
        "## Numeric ranges and suspicious values",
        "",
        "| Column | Minimum | Median | Maximum | Zero values |",
        "|---|---:|---:|---:|---:|",
    ]
    for column in NUMERIC_FEATURES:
        numeric = pd.to_numeric(frame[column], errors="coerce")
        lines.append(
            f"| `{column}` | {numeric.min():g} | {numeric.median():g} | "
            f"{numeric.max():g} | {int((numeric == 0).sum())} |"
        )

    bad_fasting = int((~pd.to_numeric(frame["FastingBS"], errors="coerce").isin([0, 1])).sum())
    bad_target = int((~pd.to_numeric(frame[TARGET], errors="coerce").isin([0, 1])).sum())
    checks = [
        f"- `Cholesterol == 0`: **{int((pd.to_numeric(frame['Cholesterol'], errors='coerce') == 0).sum())}** rows.",
        f"- `Cholesterol` outside the broad software sanity range 0–1000: **{count_outside(frame['Cholesterol'], 0, 1000)}** rows (zero values are reported separately above).",
        f"- `RestingBP == 0`: **{int((pd.to_numeric(frame['RestingBP'], errors='coerce') == 0).sum())}** rows.",
        f"- `RestingBP <= 0`: **{int((pd.to_numeric(frame['RestingBP'], errors='coerce') <= 0).sum())}** rows.",
        f"- `RestingBP` above the broad software sanity limit of 300: **{int((pd.to_numeric(frame['RestingBP'], errors='coerce') > 300).sum())}** rows.",
        f"- `Age` outside the broad software sanity range 0–120: **{count_outside(frame['Age'], 0, 120)}** rows.",
        f"- `MaxHR` outside the broad software sanity range 0–300: **{count_outside(frame['MaxHR'], 0, 300)}** rows.",
        f"- `Oldpeak` outside the broad software sanity range -10–20: **{count_outside(frame['Oldpeak'], -10, 20)}** rows.",
        f"- `FastingBS` outside the dataset's 0/1 values: **{bad_fasting}** rows.",
        f"- `HeartDisease` outside the dataset's 0/1 labels: **{bad_target}** rows.",
    ]
    lines += [
        "",
        *checks,
        "",
        "The broad range checks are simple data-quality flags, not clinical thresholds.",
        "",
        "## Cleaning decision",
        "",
        "The 172 zero values in `Cholesterol` and the one zero in `RestingBP` are "
        "reported as recorded. They are not changed to missing values, imputed, or "
        "used to remove rows. Exact duplicate rows are also retained. The model pipeline "
        "uses median/most-frequent imputation only if a true missing value is present; "
        "zero is an ordinary numeric input to that pipeline.",
        "",
        "## Scope note",
        "",
        "This project uses the 11 available matching predictor fields: "
        "`Age`, `Sex`, `ChestPainType`, `RestingBP`, `Cholesterol`, `FastingBS`, "
        "`RestingECG`, `MaxHR`, `ExerciseAngina`, `Oldpeak`, and `ST_Slope`. "
        "It does not invent, estimate, or require `ca` or `thal`.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/heart.csv", help="Path to heart.csv")
    parser.add_argument(
        "--output", default="reports/eda_report.md", help="Where to write the markdown report"
    )
    args = parser.parse_args()

    frame = read_csv(args.data)
    report = build_report(frame, Path(args.data).as_posix())
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(f"EDA report saved to {output}")


if __name__ == "__main__":
    main()

