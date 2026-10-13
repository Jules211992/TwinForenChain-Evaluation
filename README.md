TwinForenChain

TwinForenChain is a reproducibility artifact for an evidence-routed forensic attribution framework for IIoT predictive maintenance.

The repository contains clean scripts, evaluation outputs, and figures used to verify the final P7C attribution results.

Main results

P7C CAA = 0.8579
P7C AAA = 0.8873
P7C FAR = 0.1421

Same-fold comparison

P7C CAA mean = 0.8579
LR CAA mean = 0.7475
RF CAA mean = 0.8929

Repository content

scripts contains reproducibility scripts.
data contains clean CSV evaluation outputs.
figures contains the main result figures.

Reproduction

python scripts/reproduce_p7c_final_engine.py

python scripts/export_same_fold_p7c_lr_rf_stats.py

This repository does not include private credentials, deployment keys, raw infrastructure logs, or internal vendor folders.
