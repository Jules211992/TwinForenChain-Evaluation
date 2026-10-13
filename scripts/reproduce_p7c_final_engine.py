#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd

from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import GroupKFold

BASE = Path.home() / "Desktop/twinforenchain-major-revision"
OUT = BASE / "outputs"
TABLES = BASE / "tables"
LOGS = BASE / "logs"
OUT.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

OOF = OUT / "ratio_robustness_true_prevalence_predictions_oof.csv"

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

COMPARE = [
    ("Article_P7C_flat_scoring", "P7C_pred_primary"),
    ("LR_supervised_baseline", "LR_pred_primary"),
    ("RF_upper_bound", "RF_pred_primary"),
]

def norm_s(x):
    x = str(x or "").strip()
    if x in SCENARIOS:
        return x
    for s in SCENARIOS:
        if x.startswith(s) or f"{s}_" in x:
            return s
    return x

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

def safe_numeric(df, cols):
    for c in cols:
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

def fit_cmodel_guard(train_df):
    # Règle interne : parmi les cas C_model=1 et non replay,
    # déterminer si l'incohérence modèle est la cause primaire S6.
    sub = train_df[
        (train_df["C_hist"] == 0)
        & (train_df["C_model"] == 1)
    ].copy()

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
    # Moteur hiérarchique principal non-replay.
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

def predict(df, guard, main):
    preds = []
    sources = []

    for _, row in df.iterrows():
        if int(row["C_hist"]) == 1:
            preds.append("S2")
            sources.append("deterministic_C_hist")
            continue

        if int(row["C_model"]) == 1:
            xg = row[FEATURES_CMODEL_GUARD].values.reshape(1, -1)
            guard_pred = int(guard.predict(xg)[0])
            if guard_pred == 1:
                preds.append("S6")
                sources.append("conditional_C_model_guard")
                continue

        xm = row[FEATURES_MAIN].values.reshape(1, -1)
        preds.append(main.predict(xm)[0])
        sources.append("hierarchical_non_replay_rule")

    return preds, sources

def metrics(df, pred_col, method):
    total = len(df)
    correct = int((df["truth"] == df[pred_col]).sum())
    caa = correct / total
    far = 1 - caa

    attack_df = df[df["truth"].isin(ATTACKS)]
    aaa = float((attack_df["truth"] == attack_df[pred_col]).mean())

    return {
        "method": method,
        "total": total,
        "correct": correct,
        "CAA": f"{caa:.4f}",
        "AAA_S2_S4": f"{aaa:.4f}",
        "FAR": f"{far:.4f}",
    }

def by_scenario(df, pred_col, method):
    rows = []
    for s in SCENARIOS:
        sub = df[df["truth"] == s]
        total = len(sub)
        correct = int((sub["truth"] == sub[pred_col]).sum())
        rows.append({
            "method": method,
            "scenario": s,
            "total": total,
            "correct": correct,
            "CAA": f"{correct/total:.4f}",
        })
    return rows

def confusion(df, pred_col, method):
    rows = []
    for truth in SCENARIOS:
        sub = df[df["truth"] == truth]
        c = Counter(sub[pred_col].tolist())
        row = {"method": method, "truth": truth}
        for p in SCENARIOS:
            row[p] = c.get(p, 0)
        row["total"] = len(sub)
        rows.append(row)
    return rows

def main():
    print("===== P7C CONDITIONAL C_MODEL GUARD =====")
    print("Input:", OOF)

    df = pd.read_csv(OOF)
    df["truth"] = df["scenario_truth"].apply(norm_s)

    all_num = ["C_hist"] + sorted(set(FEATURES_MAIN + FEATURES_CMODEL_GUARD))
    df = safe_numeric(df, all_num)

    for _, col in COMPARE:
        df[col + "_norm"] = df[col].apply(norm_s)

    groups = group_id(df)
    gkf = GroupKFold(n_splits=5)

    df["P7C_conditional_cmodel_pred"] = ""
    df["P7C_conditional_cmodel_source"] = ""

    fold_rows = []
    guard_rules = []
    main_rules = []

    for fold, (train_idx, test_idx) in enumerate(gkf.split(df, df["truth"], groups), start=1):
        train_df = df.iloc[train_idx].copy()
        test_df = df.iloc[test_idx].copy()

        guard = fit_cmodel_guard(train_df)
        main = fit_main_tree(train_df)

        preds, sources = predict(test_df, guard, main)
        df.loc[df.index[test_idx], "P7C_conditional_cmodel_pred"] = preds
        df.loc[df.index[test_idx], "P7C_conditional_cmodel_source"] = sources

        tmp = test_df.copy()
        tmp["P7C_conditional_cmodel_pred"] = preds
        fold_rows.append(metrics(tmp, "P7C_conditional_cmodel_pred", f"P7C_conditional_cmodel_fold_{fold}"))

        guard_rules.append(
            f"\n===== FOLD {fold} C_MODEL GUARD =====\n"
            + export_text(guard, feature_names=FEATURES_CMODEL_GUARD)
        )
        main_rules.append(
            f"\n===== FOLD {fold} MAIN RULES =====\n"
            + export_text(main, feature_names=FEATURES_MAIN)
        )

    global_rows = []
    for method, col in COMPARE:
        global_rows.append(metrics(df, col + "_norm", method))
    global_rows.append(metrics(df, "P7C_conditional_cmodel_pred", "P7C_evidence_routed_hierarchical_conditional_Cmodel"))

    scen_rows = []
    for method, col in COMPARE:
        scen_rows.extend(by_scenario(df, col + "_norm", method))
    scen_rows.extend(by_scenario(df, "P7C_conditional_cmodel_pred", "P7C_evidence_routed_hierarchical_conditional_Cmodel"))

    conf_rows = []
    for method, col in COMPARE:
        conf_rows.extend(confusion(df, col + "_norm", method))
    conf_rows.extend(confusion(df, "P7C_conditional_cmodel_pred", "P7C_evidence_routed_hierarchical_conditional_Cmodel"))

    lookup = {(r["method"], r["scenario"]): float(r["CAA"]) for r in scen_rows}
    gain_rows = []
    for s in SCENARIOS:
        old = lookup[("Article_P7C_flat_scoring", s)]
        new = lookup[("P7C_evidence_routed_hierarchical_conditional_Cmodel", s)]
        rf = lookup[("RF_upper_bound", s)]
        gain_rows.append({
            "scenario": s,
            "article_P7C_CAA": f"{old:.4f}",
            "conditional_hierarchical_P7C_CAA": f"{new:.4f}",
            "gain_vs_article_P7C": f"{new-old:.4f}",
            "RF_upper_bound_CAA": f"{rf:.4f}",
        })

    source_counts = Counter(df["P7C_conditional_cmodel_source"].tolist())
    source_rows = [{"decision_source": k, "count": v, "share": f"{v/len(df):.4f}"} for k, v in source_counts.items()]

    write_csv(OUT / "p7c_conditional_cmodel_global_comparison.csv", global_rows)
    write_csv(OUT / "p7c_conditional_cmodel_fold_metrics.csv", fold_rows)
    write_csv(OUT / "p7c_conditional_cmodel_by_scenario.csv", scen_rows)
    write_csv(OUT / "p7c_conditional_cmodel_confusion_matrix.csv", conf_rows)
    write_csv(OUT / "p7c_conditional_cmodel_gain_vs_article.csv", gain_rows)
    write_csv(OUT / "p7c_conditional_cmodel_decision_sources.csv", source_rows)
    df.to_csv(OUT / "p7c_conditional_cmodel_oof_predictions.csv", index=False)

    (LOGS / "p7c_conditional_cmodel_guard_rules_by_fold.txt").write_text("\n".join(guard_rules), encoding="utf-8")
    (LOGS / "p7c_conditional_cmodel_main_rules_by_fold.txt").write_text("\n".join(main_rules), encoding="utf-8")

    final_guard = fit_cmodel_guard(df)
    final_main = fit_main_tree(df)
    (LOGS / "p7c_conditional_cmodel_final_guard_rules.txt").write_text(
        export_text(final_guard, feature_names=FEATURES_CMODEL_GUARD),
        encoding="utf-8",
    )
    (LOGS / "p7c_conditional_cmodel_final_main_rules.txt").write_text(
        export_text(final_main, feature_names=FEATURES_MAIN),
        encoding="utf-8",
    )

    print("\n===== GLOBAL COMPARISON =====")
    for r in global_rows:
        print(r)

    print("\n===== FOLD METRICS =====")
    for r in fold_rows:
        print(r)

    print("\n===== SCENARIO GAINS =====")
    for r in gain_rows:
        print(r)

    print("\n===== DECISION SOURCES =====")
    for r in source_rows:
        print(r)

    print("\n===== CONFUSION CONDITIONAL P7C ONLY =====")
    for r in conf_rows:
        if r["method"] == "P7C_evidence_routed_hierarchical_conditional_Cmodel":
            print(r)

    print("\n===== OUTPUT FILES =====")
    for p in [
        OUT / "p7c_conditional_cmodel_global_comparison.csv",
        OUT / "p7c_conditional_cmodel_fold_metrics.csv",
        OUT / "p7c_conditional_cmodel_by_scenario.csv",
        OUT / "p7c_conditional_cmodel_confusion_matrix.csv",
        OUT / "p7c_conditional_cmodel_gain_vs_article.csv",
        OUT / "p7c_conditional_cmodel_decision_sources.csv",
        OUT / "p7c_conditional_cmodel_oof_predictions.csv",
        LOGS / "p7c_conditional_cmodel_guard_rules_by_fold.txt",
        LOGS / "p7c_conditional_cmodel_main_rules_by_fold.txt",
        LOGS / "p7c_conditional_cmodel_final_guard_rules.txt",
        LOGS / "p7c_conditional_cmodel_final_main_rules.txt",
    ]:
        print(p)

if __name__ == "__main__":
    main()
