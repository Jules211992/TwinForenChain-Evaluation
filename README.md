# TwinForenChain: Cyber-Forensic Attribution for IIoT Predictive Maintenance

Reproducibility repository for the paper:

TwinForenChain: Cyber-Forensic Attribution for IIoT Predictive Maintenance

## 1. Overview

TwinForenChain is a cyber-forensic attribution framework for Industrial Internet of Things predictive maintenance.

The objective is to move beyond integrity-only evidence preservation. TwinForenChain reconstructs the sensor-window, prediction, maintenance-decision, and attribution-report chain, then assigns an evidence-based cause to each audited decision.

The framework combines:

- Industrial IIoT sensing
- Edge evidence preparation
- IPFS off-chain evidence storage
- Hyperledger Fabric on-chain anchoring
- Predictive-maintenance decision records
- P7C evidence-routed forensic attribution

## 2. Main Contribution

TwinForenChain addresses the forensic attribution gap in IIoT predictive maintenance.

A suspicious or wrong maintenance decision may come from:

- real mechanical degradation
- replay attack
- signal smoothing attack
- data injection attack
- sensor fault
- model error

TwinForenChain does not only preserve evidence. It reconstructs the evidence chain and attributes the most likely cause.

## 3. Incident Classes

| Class | Cause | Type | Operational response |
|---|---|---|---|
| S0 | Normal operation | Benign | Continue monitoring |
| S1 | Real mechanical degradation | Non-malicious | Maintenance intervention |
| S2 | Replay attack | Malicious | Cyber-incident investigation |
| S3 | Signal smoothing attack | Malicious | Cyber-incident investigation |
| S4 | Data injection attack | Malicious | Cyber-incident investigation |
| S5 | Sensor fault | Non-malicious | Sensor inspection or replacement |
| S6 | Model error | Non-malicious | Model inspection and correction |

## 4. Repository Structure

| Folder | Description |
|---|---|
| data/final | Final P7C evaluation outputs |
| data/same_fold | Same-fold P7C, LR, and RF comparison results |
| scripts | Reproducibility scripts |
| figures | Main figures used in the paper |
| results | Summary result files |
| docs | Reproducibility notes |

## 5. Datasets

The evaluation uses three predictive-maintenance datasets:

| Dataset | Role | Chains |
|---|---|---:|
| NASA IMS | Bearing run-to-failure degradation | 3,500 |
| CWRU | Bearing fault signals | 3,500 |
| C-MAPSS | Turbofan PdM validation | 3,500 |
| Total | Controlled multi-dataset workload | 10,500 |

Each dataset contributes 500 evidence chains for each scenario S0-S6.

## 6. Experimental Testbed

TwinForenChain was evaluated on a private 14-VM deployment.

| Role | VMs | vCPUs | RAM | Storage |
|---|---:|---:|---:|---:|
| Fabric peers | 3 | 8 | 16 GB | 80 GB |
| RAFT orderers | 3 | 6 | 12 GB | 60 GB |
| IPFS nodes | 5 | 4 | 8 GB | 80 GB |
| Edge/attack injector | 1 | 8 | 16 GB | 80 GB |
| ML/attribution engine | 1 | 6 | 12 GB | 80 GB |
| Monitoring | 1 | 4 | 8 GB | 40 GB |
| Total | 14 | 80 | 160 GB | about 1 TB |

## 7. Main Results

| Metric | Value |
|---|---:|
| Controlled evidence chains | 10,500 |
| Evidence-chain completeness | 1.000 |
| IPFS hash recovery | 1.000 |
| Fabric verification | 1.000 |
| Final P7C CAA | 0.8579 |
| Final P7C AAA | 0.8873 |
| Final P7C FAR | 0.1421 |

## 8. Same-Fold Comparison

| Method | CAA | AAA | FAR |
|---|---:|---:|---:|
| LR supervised baseline | 0.7475 ± 0.0056 | 0.8309 ± 0.0075 | 0.2525 ± 0.0056 |
| Final P7C engine | 0.8579 ± 0.0087 | 0.8873 ± 0.0203 | 0.1421 ± 0.0087 |
| RF supervised upper bound | 0.8929 ± 0.0082 | 0.9349 ± 0.0056 | 0.1071 ± 0.0082 |

## 9. Reproduction

Install dependencies:

    pip install -r requirements.txt

Run final P7C reproduction:

    python scripts/reproduce_p7c_final_engine.py

Run PdM sensitivity reproduction:

    python scripts/reproduce_p7c_final_pdm_sensitivity.py

## 10. Expected Files

The repository should contain:

- data/final/p7c_final_fold_metrics.csv
- data/final/p7c_final_by_scenario.csv
- data/final/p7c_final_confusion_matrix.csv
- data/final/p7c_final_pdm_sensitivity_global.csv
- data/final/p7c_final_pdm_sensitivity_folds.csv
- data/same_fold/p7c_lr_rf_same_fold_metrics.csv
- figures/fig_p7c_global_comparison.pdf
- figures/fig_p7c_scenario_caa.pdf
- figures/fig_p7c_confusion_matrix.pdf
- figures/fig_p7c_pdm_sensitivity.pdf

## 11. Artifact Policy

This repository is prepared for scientific evaluation.

It includes clean CSV outputs, reproducibility scripts, figures, and documentation.

It excludes private credentials, Fabric private keys, deployment secrets, raw infrastructure logs, node_modules folders, crypto-config folders, and large vendor dependencies.

## 12. License

This project is released under the MIT License for research and evaluation purposes.

Datasets and external tools remain subject to their own licenses.
