# Data inspection and EDA report

Source file: `data/heart.csv` (the user's supplied CSV)

## File overview

- Rows: 918
- Columns: 12
- Column names: `Age`, `Sex`, `ChestPainType`, `RestingBP`, `Cholesterol`, `FastingBS`, `RestingECG`, `MaxHR`, `ExerciseAngina`, `Oldpeak`, `ST_Slope`, `HeartDisease`
- Required predictors: 11 matching fields from the Triage page.
- `ca` and `thal` are not in this CSV and are not used or required.

## Data types and missing values

The CSV's six numeric predictor columns and the target load as numeric values; the five category columns load as text. The inspection found no missing values.

| Column | Loaded data type | Missing values | Distinct non-missing values |
|---|---:|---:|---:|
| `Age` | integer | 0 | 50 |
| `Sex` | text | 0 | 2 |
| `ChestPainType` | text | 0 | 4 |
| `RestingBP` | integer | 0 | 67 |
| `Cholesterol` | integer | 0 | 222 |
| `FastingBS` | integer | 0 | 2 |
| `RestingECG` | text | 0 | 3 |
| `MaxHR` | integer | 0 | 119 |
| `ExerciseAngina` | text | 0 | 2 |
| `Oldpeak` | decimal | 0 | 53 |
| `ST_Slope` | text | 0 | 3 |
| `HeartDisease` | integer | 0 | 2 |

## Duplicate rows

Exact duplicate rows beyond the first copy: **0**. No rows are removed by inspection or training.

## Target balance

`HeartDisease` is the dataset label: 1 means the dataset label is present; 0 means it is absent. This project predicts this dataset label.

| Dataset label | Rows | Share |
|---:|---:|---:|
| 0 | 410 | 44.7% |
| 1 | 508 | 55.3% |

## Category values

- `Sex`: `F` 193, `M` 725
- `ChestPainType`: `ASY` 496, `ATA` 173, `NAP` 203, `TA` 46
- `RestingECG`: `LVH` 188, `Normal` 552, `ST` 178
- `ExerciseAngina`: `N` 547, `Y` 371
- `ST_Slope`: `Down` 63, `Flat` 460, `Up` 395
- `FastingBS`: `0` 704, `1` 214

## Numeric ranges and suspicious values

| Column | Minimum | Median | Maximum | Zero values |
|---|---:|---:|---:|---:|
| `Age` | 28 | 54 | 77 | 0 |
| `RestingBP` | 0 | 130 | 200 | 1 |
| `Cholesterol` | 0 | 223 | 603 | 172 |
| `FastingBS` | 0 | 0 | 1 | 704 |
| `MaxHR` | 60 | 138 | 202 | 0 |
| `Oldpeak` | -2.6 | 0.6 | 6.2 | 368 |

- Zero values in `Cholesterol`: **172**.
- Zero values in `RestingBP`: **1**. This row also has `Cholesterol` 0; it is retained.
- No negative `Age`, `Cholesterol`, or `MaxHR` values were found.
- `FastingBS` contains only 0 and 1; `HeartDisease` contains only labels 0 and 1.

These checks are data-quality flags, not clinical thresholds.

## Cleaning decision

The 172 zero values in `Cholesterol` and the one zero in `RestingBP` are reported as recorded. They are not changed to missing values, imputed, or used to remove rows. Exact duplicate rows are also retained. During model fitting, the preprocessing pipeline uses median or most-frequent imputation only if a true missing value is present; zero remains an ordinary numeric input.

## Scope note

This project uses the 11 available matching predictor fields: `Age`, `Sex`, `ChestPainType`, `RestingBP`, `Cholesterol`, `FastingBS`, `RestingECG`, `MaxHR`, `ExerciseAngina`, `Oldpeak`, and `ST_Slope`. It does not invent, estimate, or require `ca` or `thal`.

