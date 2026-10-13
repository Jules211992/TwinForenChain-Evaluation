TwinForenChain Evaluation Artifact

This repository contains the clean evaluation artifact for TwinForenChain.

TwinForenChain is a cyber-forensic attribution framework for IIoT predictive maintenance. It reconstructs the sensor-window, prediction, and decision evidence chain, then assigns an evidence-based cause to audited maintenance decisions.

Main results

P7C CAA = 0.8579
P7C AAA = 0.8873
P7C FAR = 0.1421

Repository structure

scripts contains reproducibility scripts.
data contains clean CSV evaluation outputs.
figures contains the main result figures.
paper contains the LaTeX source when available.

Reproduction

python scripts/reproduce_p7c_final_engine.py

python scripts/reproduce_p7c_final_pdm_sensitivity.py

This repository does not include private credentials, deployment keys, raw infrastructure logs, or internal vendor folders.
