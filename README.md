# Heart Disease Classification

A small, local machine-learning project that learns to predict the `HeartDisease` **dataset label** in the supplied CSV. It predicts label `1` when that label is present and `0` when it is absent. It is a learning project, not a medical diagnosis or medical advice.

The supplied file has 11 predictor fields matching the Triage page: `Age`, `Sex`, `ChestPainType`, `RestingBP`, `Cholesterol`, `FastingBS`, `RestingECG`, `MaxHR`, `ExerciseAngina`, `Oldpeak`, and `ST_Slope`. The CSV does not contain `ca` (number of major vessels) or `thal` (perfusion category), so this project does not invent, estimate, or require them.

## Project files

- `data/heart.csv` — local copy of the supplied labeled data. It is ignored by Git and must be copied into place on each computer.
- `data/sample_input_fictional.csv` — three invented example rows for the prediction command; these are not real people or records from the dataset.
- `src/common.py` — the one shared definition of predictor columns, plus CSV and target checks used by the other scripts.
- `src/eda.py` — checks the CSV and writes the inspection report.
- `src/train.py` — creates a stratified split, compares models on training data only, evaluates the selected model once on the held-out test set, and saves the fitted pipeline and reports.
- `src/predict.py` — loads that saved pipeline, predicts from an unlabeled CSV, and writes a results CSV.
- `requirements.txt` — the Python packages used by the scripts.
- `reports/eda_report.md` — the inspection findings for the supplied CSV.
- `reports/evaluation_report.md` — created by the training command after you run it.
- `reports/evaluation_results.json` and `reports/model_comparison.csv` — machine-readable evaluation output created by training.
- `models/heart_disease_pipeline.joblib` — created locally by training; ignored by Git.
- `.gitignore` — keeps the private dataset, fitted model, virtual environment, and prediction outputs out of commits.

## Windows PowerShell setup and training

Install Python 3.12 for your Windows account in its default location, plus Git. Then open PowerShell and run these commands from the folder where you want the project:

```powershell
git clone https://github.com/EvelinaK123/Heart-Disease-Risk.git
Set-Location .\Heart-Disease-Risk
$python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $python)) { throw "Install Python 3.12 for your account, then retry." }
& $python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item "$HOME\Downloads\heart.csv" .\data\heart.csv
```

The next command inspects the CSV and writes `reports/eda_report.md`:

```powershell
..venv\Scripts\python.exe .\src\eda.py --data .\data\heart.csv
```

Train and evaluate the models:

```powershell
..venv\Scripts\python.exe .\src\train.py --data .\data\heart.csv
```

This writes the fitted preprocessing-and-model pipeline to `models\heart_disease_pipeline.joblib` and evaluation outputs to `reports\`. The training command uses a fixed random seed so the split and model setup are reproducible with the listed package versions.

## macOS / Linux setup and training

Install Python 3.12 and Git. In Terminal, run:

```bash
git clone https://github.com/EvelinaK123/Heart-Disease-Risk.git
cd Heart-Disease-Risk
python3.12 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
cp ~/Downloads/heart.csv ./data/heart.csv
./.venv/bin/python ./src/eda.py --data ./data/heart.csv
./.venv/bin/python ./src/train.py --data ./data/heart.csv
```

## Make predictions

The prediction input needs the 11 predictor columns and does not need a `HeartDisease` column. Category values should be text labels from the CSV: `Sex` is `F` or `M`; `ChestPainType` is `ASY`, `ATA`, `NAP`, or `TA`; `RestingECG` is `LVH`, `Normal`, or `ST`; `ExerciseAngina` is `N` or `Y`; `ST_Slope` is `Down`, `Flat`, or `Up`. The model uses these actual labels rather than numeric codes from another page. Unseen categories are handled by the saved preprocessing pipeline without crashing, though this project's data cannot teach it what those categories mean.

Windows PowerShell:

```powershell
..venv\Scripts\python.exe .\src\predict.py --input .\data\sample_input_fictional.csv --output .\predictions\sample_predictions.csv
```

macOS / Linux:

```bash
./.venv/bin/python ./src/predict.py --input ./data/sample_input_fictional.csv --output ./predictions/sample_predictions.csv
```

The results CSV contains the input predictors, `PredictedHeartDisease` (the predicted dataset class), and `ScoreForHeartDisease1` when the chosen model provides a probability score. The score is a model output for class 1, not a clinical risk estimate.

## What training does

1. It reserves 20% of the rows as a test set with stratification. Stratification keeps the class proportions roughly similar in the training and test parts. A fixed random seed makes the split repeatable.
2. It compares Logistic Regression and Random Forest with five-fold stratified cross-validation using only the training portion. Each fold fits its own preprocessing on that fold's training rows. The model with higher mean balanced accuracy is selected; ties follow the order shown in `src/train.py`.
3. It fits the selected complete pipeline on the whole training portion, then evaluates it once on the held-out test set. That test set is not used to choose or tune the model.
4. It saves the **whole pipeline** (preprocessing plus classifier). Prediction loads that same pipeline, so it applies the learned imputers, scaling, and category encoding in the same way as during training.

Numeric fields are imputed with the training median if values are genuinely missing and standardized for Logistic Regression. Text category fields are imputed with the training most-frequent category if needed and one-hot encoded. The encoder ignores an unseen category rather than breaking. Since imputer and encoder fitting happen inside the pipeline, their learned values come from training data only.

## How to read the evaluation

`reports/evaluation_report.md` includes:

- **Accuracy:** share of all test rows with the right dataset label.
- **Balanced accuracy:** average recall across labels 0 and 1; useful when class counts differ.
- **Precision:** among rows predicted as label 1, how many have dataset label 1.
- **Recall / sensitivity:** among rows whose dataset label is 1, how many are predicted 1.
- **Specificity:** among rows whose dataset label is 0, how many are predicted 0.
- **F1:** a combined summary of precision and recall for label 1.
- **ROC-AUC:** how well the model score ranks label 1 above label 0 over possible thresholds, when the selected model provides a usable score.
- **Confusion matrix:** rows are actual labels and columns are predicted labels. A false positive means predicting label 1 for a row with actual dataset label 0. A false negative means predicting label 0 for a row with actual dataset label 1.

These scores measure agreement with labels in this CSV and its held-out split. A high score does not prove clinical usefulness, and model output is not a medical diagnosis.

## Data inspection and cleaning decision

Run `src/eda.py` to regenerate the inspection report. It checks column names, data types, missing values, exact duplicate rows, target balance, category values, numeric ranges, and basic suspicious values. The supplied CSV has 918 rows, no missing values, no exact duplicate rows, 410 label-0 rows and 508 label-1 rows. It has 172 zero `Cholesterol` values and one zero `RestingBP` value.

Those zeros are preserved exactly as recorded: this project does not treat them as missing, replace them, or remove those rows. The pipeline's imputer applies only to actual missing values; zero is passed as a numeric value. This is an explicit project data-handling decision, not a claim that zero is clinically meaningful.

## Privacy and version control

The supplied `data/heart.csv`, fitted model, and prediction outputs are ignored by Git. Keep the dataset and generated model on your local machine. The fictional sample input and aggregate reports contain no copied example records.

