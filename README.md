TwinForenChain: Evidence-Routed Forensic Attribution for IIoT Predictive Maintenance

Reproducibility repository for the paper:

TwinForenChain: Evidence-Routed Forensic Attribution for Industrial Internet of Things Predictive Maintenance

This repository provides the clean evaluation artifact used to reproduce the reported P7C attribution results, fold-level comparisons, sensitivity analysis, and main figures.

Overview

TwinForenChain is a cyber-forensic attribution framework for IIoT predictive maintenance. It reconstructs the sensor-window, prediction, and decision evidence chain, then assigns an evidence-based cause to audited maintenance decisions.

The framework evaluates seven incident classes:

S0 normal operation
S1 real mechanical degradation
S2 replay attack
S3 signal smoothing attack
S4 data injection attack
S5 sensor fault
S6 model error

Main Results

Final P7C engine:

CAA = 0.8579
AAA = 0.8873
FAR = 0.1421

Same-fold comparison:

P7C CAA mean = 0.8579
LR CAA mean = 0.7475
RF CAA mean = 0.8929

Evidence-chain layer:

Evidence-chain completeness = 1.000
IPFS hash recovery = 1.000
Fabric verification = 1.000

Repository Structure

data/final contains final P7C evaluation outputs.
data/same_fold contains same-fold P7C, LR, and RF comparison results.
scripts contains reproducibility scripts.
figures contains the main figures used in the article.
results contains summary files for quick verification.
docs contains reproducibility notes.
paper contains optional LaTeX tables or article material.

Reproduction

Install dependencies:

pip install -r requirements.txt

Run the final P7C reproduction script:

python scripts/reproduce_p7c_final_engine.py

Run the PdM sensitivity reproduction script:

python scripts/reproduce_p7c_final_pdm_sensitivity.py

Expected Files

data/final/p7c_final_fold_metrics.csv
data/final/p7c_final_by_scenario.csv
data/final/p7c_final_confusion_matrix.csv
data/final/p7c_final_pdm_sensitivity_global.csv
data/final/p7c_final_pdm_sensitivity_folds.csv
data/same_fold/p7c_lr_rf_same_fold_metrics.csv
figures/fig_p7c_global_comparison.pdf
figures/fig_p7c_scenario_caa.pdf
figures/fig_p7c_confusion_matrix.pdf
figures/fig_p7c_pdm_sensitivity.pdf

Artifact Policy

This repository is prepared for scientific evaluation. It excludes private credentials, deployment keys, raw infrastructure secrets, node_modules folders, and Fabric private key material.
