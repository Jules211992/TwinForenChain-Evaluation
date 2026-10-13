# TwinForenChain Reproducibility Notes

This repository contains the clean reproducibility artifact for TwinForenChain.

The artifact supports verification of:

1. Final P7C fold-level attribution results
2. Scenario-level attribution results
3. Final P7C confusion matrix
4. PdM model-error sensitivity
5. Same-fold comparison between P7C, LR, and RF
6. Main paper figures

## Main Expected Results

| Metric | Value |
|---|---:|
| P7C CAA | 0.8579 |
| P7C AAA | 0.8873 |
| P7C FAR | 0.1421 |
| LR CAA mean | 0.7475 |
| RF CAA mean | 0.8929 |

## Reproduction

Install dependencies:

    pip install -r requirements.txt

Run:

    python scripts/reproduce_p7c_final_engine.py

    python scripts/reproduce_p7c_final_pdm_sensitivity.py

## Artifact Scope

This repository contains clean evaluation files only. It excludes private keys, credentials, Fabric crypto material, deployment secrets, raw logs, node_modules, and vendor folders.
