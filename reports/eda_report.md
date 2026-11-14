# Data inspection and EDA report

Source file: `data/heart.csv`

## File overview

- Rows: 918
- Columns: 12
- Column names: `Age`, `Sex`, `ChestPainType`, `RestingBP`, `Cholesterol`, `FastingBS`, `RestingECG`, `MaxHR`, `ExerciseAngina`, `Oldpeak`, `ST_Slope`, `HeartDisease`
- Required predictors: 11 matching fields from the Triage page.
- `ca` and `thal` are not in this CSV and are not used or required.

## Data types and missing values

| Column | Loaded data type | Missing values | Distinct non-missing values |
|---|---:|---:|---:|
| `Age` | `int64` | 0 | 50 |
| `Sex` | `object` | 0 | 2 |
| `ChestPainType` | `object` | 0 | 4 |
| `RestingBP` | `int64` | 0 | 67 |
| `Cholesterol` | `int64` | 0 | 222 |
| `FastingBS` | `int64` | 0 | 2 |
| `RestingECG` | `object` | 0 | 3 |
| `MaxHR` | `int64` | 0 | 119 |
| `ExerciseAngina` | `object` | 0 | 2 |
| `Oldpeak` | `float64` | 0 | 53 |
| `ST_Slope` | `object` | 0 | 3 |
| `HeartDisease` | `int64` | 0 | 2 |

## Duplicate rows

Exact duplicate rows beyond the first copy: **0**.
No rows are removed by the inspection or training scripts.

## Target balance

`HeartDisease` is the dataset label: 1 means the dataset label is present; 0 means it is absent. This is a prediction of the dataset label.

| Dataset label | Rows | Share |
|---:|---:|---:|
| 0 | 410 | 44.7% |
| 1 | 508 | 55.3% |

## Category values

- `Sex`: `F`: 193, `M`: 725
- `ChestPainType`: `ASY`: 496, `ATA`: 173, `NAP`: 203, `TA`: 46
- `RestingECG`: `LVH`: 188, `Normal`: 552, `ST`: 178
- `ExerciseAngina`: `N`: 547, `Y`: 371
- `ST_Slope`: `Down`: 63, `Flat`: 460, `Up`: 395
- `FastingBS`: `0`: 704, `1`: 214

## Numeric ranges and suspicious values

| Column | Minimum | Median | Maximum | Zero values |
|---|---:|---:|---:|---:|
| `Age` | 28 | 54 | 77 | 0 |
| `RestingBP` | 0 | 130 | 200 | 1 |
| `Cholesterol` | 0 | 223 | 603 | 172 |
| `FastingBS` | 0 | 0 | 1 | 704 |
| `MaxHR` | 60 | 138 | 202 | 0 |
| `Oldpeak` | -2.6 | 0.6 | 6.2 | 368 |

- `Cholesterol == 0`: **172** rows.
- `Cholesterol` outside the broad software sanity range 0–1000: **0** rows (zero values are reported separately above).
- `RestingBP == 0`: **1** rows.
- `RestingBP <= 0`: **1** rows.
- `RestingBP` above the broad software sanity limit of 300: **0** rows.
- `Age` outside the broad software sanity range 0–120: **0** rows.
- `MaxHR` outside the broad software sanity range 0–300: **0** rows.
- `Oldpeak` outside the broad software sanity range -10–20: **0** rows.
- `FastingBS` outside the dataset's 0/1 values: **0** rows.
- `HeartDisease` outside the dataset's 0/1 labels: **0** rows.

The broad range checks are simple data-quality flags, not clinical thresholds.

## Cleaning decision

The 172 zero values in `Cholesterol` and the one zero in `RestingBP` are reported as recorded. They are not changed to missing values, imputed, or used to remove rows. Exact duplicate rows are also retained. The model pipeline uses median/most-frequent imputation only if a true missing value is present; zero is an ordinary numeric input to that pipeline.

## Scope note

This project uses the 11 available matching predictor fields: `Age`, `Sex`, `ChestPainType`, `RestingBP`, `Cholesterol`, `FastingBS`, `RestingECG`, `MaxHR`, `ExerciseAngina`, `Oldpeak`, and `ST_Slope`. It does not invent, estimate, or require `ca` or `thal`.

