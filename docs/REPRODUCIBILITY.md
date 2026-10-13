TwinForenChain Reproducibility Notes

This artifact supports reproduction of the evaluation reported in the TwinForenChain paper.

Evaluation Components

1. Final P7C fold-level attribution metrics
2. Scenario-level attribution results
3. Final P7C confusion matrix
4. PdM error-rate sensitivity
5. Same-fold comparison between P7C, LR, and RF
6. Main figures used in the article

Key Result Files

data/final/p7c_final_fold_metrics.csv
data/final/p7c_final_by_scenario.csv
data/final/p7c_final_confusion_matrix.csv
data/final/p7c_final_pdm_sensitivity_global.csv
data/final/p7c_final_pdm_sensitivity_folds.csv
data/same_fold/p7c_lr_rf_same_fold_metrics.csv

Expected Main Results

P7C CAA = 0.8579
P7C AAA = 0.8873
P7C FAR = 0.1421

Same-Fold Comparison

P7C CAA mean = 0.8579
LR CAA mean = 0.7475
RF CAA mean = 0.8929

Interpretation

P7C substantially improves over the LR supervised baseline and remains close to the RF supervised upper bound while preserving audit-oriented interpretability.
