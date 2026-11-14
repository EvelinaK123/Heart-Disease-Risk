# Model evaluation report

## Setup

- Train rows: 734
- Test rows: 184 (20%, stratified by `HeartDisease`)
- Random seed: 42
- Model selection: highest mean balanced accuracy in 5-fold stratified cross-validation on training data only.
- Selected model: **Random Forest**

The test set was held out while comparing and selecting models. It was evaluated once after selection.

## Training-only model comparison

| Model | Mean training CV balanced accuracy | Standard deviation |
|---|---:|---:|
| Logistic Regression | 0.847 | 0.044 |
| Random Forest | 0.850 | 0.041 |

## Final selected model on the held-out test set

| Metric | Score |
|---|---:|
| Accuracy | 0.908 |
| Balanced accuracy | 0.904 |
| Precision (class 1) | 0.897 |
| Recall / sensitivity (class 1) | 0.941 |
| Specificity (class 0) | 0.866 |
| F1 (class 1) | 0.919 |
| ROC-AUC | 0.932 |

Confusion matrix (rows are actual labels, columns are predicted labels; order is 0, 1):

| Actual \ Predicted | 0 | 1 |
|---|---:|---:|
| 0 | 71 | 11 |
| 1 | 6 | 96 |

- False positive: the model predicts dataset label 1 for a row whose dataset label is 0.
- False negative: the model predicts dataset label 0 for a row whose dataset label is 1.

These are errors against this CSV's labels. Scores summarize this dataset split; they do not establish clinical usefulness or provide a medical diagnosis.

