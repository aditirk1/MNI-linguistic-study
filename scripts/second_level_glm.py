"""
Second-Level GLM — NEBULA101 Multimodal Analysis
Tests unique variance of nlang and entropy in neural outcomes.

Model: Neural_outcome ~ nlang_z + entropy_z + age_z + edu_z + sex_binary + TIV_z

Run after:
  1) CONN outputs FC values per subject
  2) TBSS outputs FA skeleton values per subject
  3) Alice localizer outputs individual language maps

This script handles the statistical modeling and figure generation.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
import statsmodels.api as sm
import json

# ============================================================
# CONFIGURATION
# ============================================================
root = Path(r"C:\Users\Aditi\ds005613")
design = pd.read_csv(root / "subset_50_design_matrix.csv")

# TIV will be added after CAT12/VBM segmentation
# For now, placeholder (set to 0 or fill after structural processing)
if "TIV_z" not in design.columns:
    design["TIV_z"] = 0.0  # placeholder — update after CAT12

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def run_glm(outcome_values, design_df, outcome_name="outcome"):
    """
    Run GLM: outcome ~ nlang_z + entropy_z + age_z + edu_z + sex_binary + TIV_z
    Returns summary dict with coefficients, p-values, partial R-squared.
    """
    df = design_df.copy()
    df["outcome"] = outcome_values

    predictors = ["nlang_z", "entropy_z", "age_z", "edu_z", "sex_binary", "TIV_z"]
    X = sm.add_constant(df[predictors])
    y = df["outcome"]

    model = sm.OLS(y, X, missing="drop").fit()

    results = {
        "outcome": outcome_name,
        "n": int(model.nobs),
        "r_squared": model.rsquared,
        "adj_r_squared": model.rsquared_adj,
        "f_stat": model.fvalue,
        "f_pvalue": model.f_pvalue,
        "coefficients": {},
    }

    for pred in predictors:
        results["coefficients"][pred] = {
            "beta": model.params[pred],
            "se": model.bse[pred],
            "t": model.tvalues[pred],
            "p": model.pvalues[pred],
            "ci_low": model.conf_int().loc[pred, 0],
            "ci_high": model.conf_int().loc[pred, 1],
        }

    # Partial R-squared for nlang and entropy (unique variance)
    for key_pred in ["nlang_z", "entropy_z"]:
        reduced_preds = [p for p in predictors if p != key_pred]
        X_reduced = sm.add_constant(df[reduced_preds])
        model_reduced = sm.OLS(y, X_reduced, missing="drop").fit()
        partial_r2 = (model_reduced.ssr - model.ssr) / model_reduced.ssr
        results["coefficients"][key_pred]["partial_r2"] = partial_r2

    return results, model


def print_results(results):
    """Pretty-print GLM results."""
    print(f"\n{'='*60}")
    print(f"Outcome: {results['outcome']}")
    print(f"N={results['n']}  R²={results['r_squared']:.4f}  "
          f"adj.R²={results['adj_r_squared']:.4f}  "
          f"F={results['f_stat']:.3f}  p={results['f_pvalue']:.4e}")
    print(f"{'='*60}")
    print(f"{'Predictor':<14} {'Beta':>8} {'SE':>8} {'t':>8} {'p':>10} {'partial_R²':>10}")
    print("-" * 60)
    for pred, vals in results["coefficients"].items():
        pr2 = vals.get("partial_r2", "")
        pr2_str = f"{pr2:.4f}" if pr2 != "" else ""
        sig = "*" if vals["p"] < 0.05 else ""
        print(f"{pred:<14} {vals['beta']:>8.4f} {vals['se']:>8.4f} "
              f"{vals['t']:>8.3f} {vals['p']:>10.4e} {pr2_str:>10} {sig}")
    print()


# ============================================================
# ANALYSIS 1: Resting-State FC (from CONN output)
# ============================================================
# After CONN finishes, export ROI-to-ROI FC matrix per subject.
# Load mean FC within language network as outcome variable.

fc_results_file = root / "derivatives" / "conn_restfc" / "fc_language_network_values.csv"

if fc_results_file.exists():
    fc_data = pd.read_csv(fc_results_file)
    merged = design.merge(fc_data, on="participant_id")
    results_fc, model_fc = run_glm(merged["fc_language_network"], merged, "Language_Network_FC")
    print_results(results_fc)
else:
    print("[PENDING] FC values not yet available. Run CONN first.")
    print(f"  Expected: {fc_results_file}")

# ============================================================
# ANALYSIS 2: DWI FA in perisylvian tracts (from TBSS output)
# ============================================================
# After TBSS finishes, extract mean FA in language-relevant tracts
# (arcuate fasciculus, SLF, ILF) per subject.

fa_results_file = root / "derivatives" / "dwi_fsl" / "fa_perisylvian_values.csv"

if fa_results_file.exists():
    fa_data = pd.read_csv(fa_results_file)
    merged = design.merge(fa_data, on="participant_id")
    results_fa, model_fa = run_glm(merged["fa_perisylvian"], merged, "Perisylvian_FA")
    print_results(results_fa)
else:
    print("[PENDING] FA values not yet available. Run TBSS first.")
    print(f"  Expected: {fa_results_file}")

# ============================================================
# SUMMARY TABLE FOR PAPER/PPT
# ============================================================
print("\n" + "=" * 60)
print("SUMMARY: Key hypotheses")
print("=" * 60)
print("H1: nlang -> Language Network FC (unique variance over entropy)")
print("H2: entropy -> Perisylvian FA (unique variance over nlang)")
print("H3: Dissociable neural substrates per predictor")
print()
print("Model: outcome ~ nlang_z + entropy_z + age_z + edu_z + sex_binary + TIV_z")
print(f"Sample: n={len(design)} (stratified by nlang tertiles)")
print(f"nlang range: {design['nlang'].min()}-{design['nlang'].max()}")
print(f"entropy range: {design['entropy_curr_tot_exp'].min():.2f}-{design['entropy_curr_tot_exp'].max():.2f}")
print(f"nlang-entropy correlation: r={design['nlang_z'].corr(design['entropy_z']):.3f}")
