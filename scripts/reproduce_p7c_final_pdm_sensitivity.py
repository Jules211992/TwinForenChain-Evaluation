#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GroupKFold

BASE = Path.home() / "Desktop/twinforenchain-major-revision"
OUT = BASE / "outputs"
TABLES = BASE / "tables"
OUT.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)

RATES = [
    ("pdm000", "0.00"),
    ("pdm002", "0.02"),
    ("pdm004", "0.04"),
    ("pdm008", "0.08"),
]

SCENARIOS = ["S0", "S1", "S2", "S3", "S4", "S5", "S6"]
ATTACKS = {"S2", "S3", "S4"}

FEATURES_MAIN = [
    "C_model",
    "C_smooth",
    "C_inject",
    "C_sensor",
    "C_degradation",
    "std_ratio_to_context",
    "rms_ratio_to_context",
    "peak_ratio_to_context",
    "energy_ratio_to_context",
    "slope_gap_z",
    "context_degradation_score",
    "obs_degradation_score",
    "hist_distance_z",
    "context_distance_z",
]

FEATURES_CMODEL_GUARD = [
    "C_model",
    "C_smooth",
    "C_inject",
    "C_sensor",
    "C_degradation",
    "std_ratio_to_context",
    "rms_ratio_to_context",
    "peak_ratio_to_context",
    "energy_ratio_to_context",
    "slope_gap_z",
    "context_degradation_score",
    "obs_degradation_score",
]

def norm_s(x):
    x = str(x or "").strip()
    if x in SCENARIOS:
        return x
    for s in SCENARIOS:
        if x.startswith(s) or f"{s}_" in x:
            return s
    return x

def safe_numeric(df, cols):
    for c in cols:
        if c not in df.columns:
            df[c] = 0.0
        df[c] = pd.to_numeric(df[c], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return df

def group_id(df):
    required = ["source_window_id", "context_window_id", "history_window_id"]
    if all(c in df.columns for c in required):
        return (
            df["source_window_id"].astype(str)
            + "__" + df["context_window_id"].astype(str)
            + "__" + df["history_window_id"].astype(str)
        )
    return df["evidence_chain_id"].astype(str)

def write_csv(path, rows):
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def fit_cmodel_guard(train_df):
    sub = train_df[(train_df["C_hist"] == 0) & (train_df["C_model"] == 1)].copy()
    X = sub[FEATURES_CMODEL_GUARD].values
    y = (sub["truth"] == "S6").astype(int).values

    clf = DecisionTreeClassifier(
        criterion="entropy",
        max_depth=3,
        min_samples_leaf=60,
        class_weight="balanced",
        random_state=20260828,
    )
    clf.fit(X, y)
    return clf

def fit_main_tree(train_df):
    sub = train_df[train_df["C_hist"] == 0].copy()
    X = sub[FEATURES_MAIN].values
    y = sub["truth"].values

    clf = DecisionTreeClassifier(
        criterion="entropy",
        max_depth=5,
        min_samples_leaf=80,
        class_weight="balanced",
        random_state=20260828,
    )
    clf.fit(X, y)
    return clf

def predict_final_p7c(test_df, guard, main):
    preds = []
    sources = []

    for _, row in test_df.iterrows():
        if int(row["C_hist"]) == 1:
            preds.append("S2")
            sources.append("deterministic_C_hist")
            continue

        if int(row["C_model"]) == 1:
            xg = row[FEATURES_CMODEL_GUARD].values.reshape(1, -1)
            if int(guard.predict(xg)[0]) == 1:
                preds.append("S6")
                sources.append("conditional_model_consistency")
                continue

        xm = row[FEATURES_MAIN].values.reshape(1, -1)
        preds.append(main.predict(xm)[0])
        sources.append("hierarchical_non_replay_rule")

    return preds, sources

def metrics(df, pred_col):
    total = len(df)
    correct = int((df["truth"] == df[pred_col]).sum())
    caa = correct / total
    far = 1 - caa

    attack_df = df[df["truth"].isin(ATTACKS)]
    aaa = float((attack_df["truth"] == attack_df[pred_col]).mean())

    return correct, caa, aaa, far

def run_rate(tag, rate):
    campaign = OUT / f"s0_s6_leakage_free_campaign_v3_pdm_noise_{tag}.csv"
    if not campaign.exists():
        raise FileNotFoundError(campaign)

    df = pd.read_csv(campaign)
    df["truth"] = df["scenario_truth"].apply(norm_s)

    all_num = ["C_hist"] + sorted(set(FEATURES_MAIN + FEATURES_CMODEL_GUARD))
    df = safe_numeric(df, all_num)

    df["P7C_final_pred"] = ""
    df["P7C_final_source"] = ""

    groups = group_id(df)
    gkf = GroupKFold(n_splits=5)

    fold_rows = []

    for fold, (train_idx, test_idx) in enumerate(gkf.split(df, df["truth"], groups), start=1):
        train_df = df.iloc[train_idx].copy()
        test_df = df.iloc[test_idx].copy()

        guard = fit_cmodel_guard(train_df)
        main = fit_main_tree(train_df)

        preds, sources = predict_final_p7c(test_df, guard, main)

        df.loc[df.index[test_idx], "P7C_final_pred"] = preds
        df.loc[df.index[test_idx], "P7C_final_source"] = sources

        tmp = test_df.copy()
        tmp["P7C_final_pred"] = preds
        correct, caa, aaa, far = metrics(tmp, "P7C_final_pred")
        fold_rows.append({
            "rate_tag": tag,
            "pdm_error_rate": rate,
            "fold": fold,
            "total": len(tmp),
            "correct": correct,
            "CAA": f"{caa:.4f}",
            "AAA_S2_S4": f"{aaa:.4f}",
            "FAR": f"{far:.4f}",
        })

    correct, caa, aaa, far = metrics(df, "P7C_final_pred")
    global_row = {
        "rate_tag": tag,
        "pdm_error_rate": rate,
        "method": "P7C_final_evidence_routed_hierarchical",
        "total": len(df),
        "correct": correct,
        "CAA": f"{caa:.4f}",
        "AAA_S2_S4": f"{aaa:.4f}",
        "FAR": f"{far:.4f}",
    }

    scenario_rows = []
    for s in SCENARIOS:
        sub = df[df["truth"] == s]
        correct_s = int((sub["truth"] == sub["P7C_final_pred"]).sum())
        scenario_rows.append({
            "rate_tag": tag,
            "pdm_error_rate": rate,
            "scenario": s,
            "total": len(sub),
            "correct": correct_s,
            "CAA": f"{correct_s/len(sub):.4f}",
        })

    source_counts = Counter(df["P7C_final_source"].tolist())
    source_rows = [
        {
            "rate_tag": tag,
            "pdm_error_rate": rate,
            "decision_source": k,
            "count": v,
            "share": f"{v/len(df):.4f}",
        }
        for k, v in source_counts.items()
    ]

    df.to_csv(OUT / f"p7c_final_pdm_sensitivity_predictions_{tag}.csv", index=False)

    return global_row, fold_rows, scenario_rows, source_rows

def main():
    print("===== FINAL P7C PDM SENSITIVITY =====")

    globals_all = []
    folds_all = []
    scenarios_all = []
    sources_all = []

    for tag, rate in RATES:
        print("RUN", tag, rate)
        g, f, s, src = run_rate(tag, rate)
        globals_all.append(g)
        folds_all.extend(f)
        scenarios_all.extend(s)
        sources_all.extend(src)

    write_csv(OUT / "p7c_final_pdm_sensitivity_global.csv", globals_all)
    write_csv(OUT / "p7c_final_pdm_sensitivity_folds.csv", folds_all)
    write_csv(OUT / "p7c_final_pdm_sensitivity_by_scenario.csv", scenarios_all)
    write_csv(OUT / "p7c_final_pdm_sensitivity_sources.csv", sources_all)

    tex = TABLES / "table_p7c_final_pdm_sensitivity.tex"
    with open(tex, "w", encoding="utf-8") as f:
        f.write("\\begin{table}[t]\n")
        f.write("\\centering\n")
        f.write("\\caption{Sensitivity of the final evidence-routed hierarchical P7C engine to ordinary PdM error.}\n")
        f.write("\\label{tab:p7c_final_pdm_sensitivity}\n")
        f.write("\\begin{tabular}{rrrr}\n")
        f.write("\\hline\n")
        f.write("PdM error & CAA & AAA & FAR \\\\\n")
        f.write("\\hline\n")
        for r in globals_all:
            f.write(
                f"{float(r['pdm_error_rate'])*100:.0f}\\% & "
                f"{r['CAA']} & {r['AAA_S2_S4']} & {r['FAR']} \\\\\n"
            )
        f.write("\\hline\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")

    print("\n===== FINAL P7C GLOBAL SENSITIVITY =====")
    for r in globals_all:
        print(r)

    print("\n===== FINAL P7C S1/S5/S6 SENSITIVITY =====")
    for r in scenarios_all:
        if r["scenario"] in ["S1", "S5", "S6"]:
            print(r)

    print("\n===== FINAL P7C DECISION SOURCES =====")
    for r in sources_all:
        print(r)

    print("\n===== OUTPUT FILES =====")
    for p in [
        OUT / "p7c_final_pdm_sensitivity_global.csv",
        OUT / "p7c_final_pdm_sensitivity_folds.csv",
        OUT / "p7c_final_pdm_sensitivity_by_scenario.csv",
        OUT / "p7c_final_pdm_sensitivity_sources.csv",
        tex,
    ]:
        print(p)

if __name__ == "__main__":
    main()
