"""
FC analysis using CONN-preprocessed (realign+unwarp) BOLD files.

Improvements over the raw-BOLD Colab run:
  - Input is motion-corrected usub-*.nii (not raw BOLD)
  - Mean framewise displacement (FD) computed from rp_*.txt
  - FD included as nuisance covariate in the GLM

Outputs to derivatives/fc_conn_preprocessed/:
  fc_outcomes_conn.csv        per-subject FC + mean_fd
  fc_glm_results_conn.csv     GLM table
  group_fc_matrix_conn.png    heatmap
  connectome_conn.png         glass brain
  fc_scatter_conn.png         scatter plots
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats as sp_stats
import warnings
warnings.filterwarnings("ignore")

base = Path(r"C:\Users\Aditi\ds005613")
out = base / "derivatives" / "fc_conn_preprocessed"
out.mkdir(parents=True, exist_ok=True)

roi_coords = [
    (-51, 22, 10),   (-56, -14, 4),  (-46, -62, 28),
    (-4, 4, 52),     (51, 22, 10),   (56, -14, 4),
]
roi_labels = ["IFG_L", "STG_L", "AngG_L", "SMA_L", "IFG_R", "STG_R"]

# ── Identify the 32 subjects with usub + rp files ─────────────────────
subs_file = base / "subset_50_participants.txt"
all_subs = [s.strip() for s in subs_file.read_text().splitlines() if s.strip()]

valid_subs = []
for s in all_subs:
    fdir = base / s / "ses-01" / "func"
    usub = list(fdir.glob("usub-*task-rest*bold.nii"))
    rp = list(fdir.glob("rp_*task-rest*bold.txt"))
    if usub and rp:
        valid_subs.append((s, usub[0], rp[0]))

print(f"Subjects with CONN-preprocessed data: {len(valid_subs)}")

# ── Step 1: Compute mean FD from rp_*.txt ─────────────────────────────
HEAD_RADIUS_MM = 50.0

def compute_mean_fd(rp_path):
    """Mean framewise displacement (Power et al. 2012)."""
    rp = np.loadtxt(rp_path)            # (n_timepoints, 6)
    # columns 0-2: translations (mm), columns 3-5: rotations (rad)
    rp_mm = rp.copy()
    rp_mm[:, 3:] = rp[:, 3:] * HEAD_RADIUS_MM   # rad -> mm on sphere surface
    diff = np.diff(rp_mm, axis=0)                 # frame-to-frame change
    fd = np.sum(np.abs(diff), axis=1)             # FD per pair
    return float(np.mean(fd))

print("\nComputing FD...")
fd_dict = {}
for s, usub_path, rp_path in valid_subs:
    fd_dict[s] = compute_mean_fd(rp_path)
    print(f"  {s}  mean_fd = {fd_dict[s]:.3f} mm")

# ── Step 2 + 3: Extract ROI time series and compute FC ────────────────
from nilearn.maskers import NiftiSpheresMasker
from nilearn.connectome import ConnectivityMeasure

masker = NiftiSpheresMasker(
    seeds=roi_coords, radius=8, t_r=2.0,
    high_pass=0.01, low_pass=0.1,
    smoothing_fwhm=6.0, standardize=True, detrend=True, verbose=0,
)

fc_rows = []
failed = []

print("\nExtracting FC from motion-corrected BOLD...")
for i, (s, usub_path, rp_path) in enumerate(valid_subs):
    try:
        ts = masker.fit_transform(str(usub_path))   # (300, 6)
        conn = ConnectivityMeasure(kind="correlation",
                                   standardize="zscore_sample")
        fc = conn.fit_transform([ts])[0]             # (6, 6)
        fc_z = np.arctanh(np.clip(fc, -0.999, 0.999))
        np.fill_diagonal(fc_z, 0.0)

        idx = {n: j for j, n in enumerate(roi_labels)}
        upper = fc_z[np.triu_indices(6, k=1)]

        fc_rows.append({
            "participant_id": s,
            "mean_lang_fc": float(upper.mean()),
            "IFG_STG_left": float(fc_z[idx["IFG_L"], idx["STG_L"]]),
            "IFG_STG_right": float(fc_z[idx["IFG_R"], idx["STG_R"]]),
            "mean_fd": fd_dict[s],
        })
        np.save(out / f"{s}_fc_matrix.npy", fc_z)
        print(f"  [{i+1}/{len(valid_subs)}] {s}  FC={upper.mean():.3f}  FD={fd_dict[s]:.3f}")
    except Exception as e:
        print(f"  [{i+1}/{len(valid_subs)}] {s}  FAILED: {e}")
        failed.append(s)

fc_df = pd.DataFrame(fc_rows)
fc_df.to_csv(out / "fc_outcomes_conn.csv", index=False)
print(f"\nCompleted: {len(fc_df)}/{len(valid_subs)}   Failed: {failed}")

# ── Step 3b: Merge with design matrix and run GLM ─────────────────────
import statsmodels.formula.api as smf

design = pd.read_csv(base / "shared_design_matrix.csv")
df = fc_df.merge(design, on="participant_id")
df["mean_fd_z"] = sp_stats.zscore(df["mean_fd"])

print(f"\nGLM sample: N = {len(df)}")
print(f"nlang range: {df['nlang'].min()}-{df['nlang'].max()}")
print(f"entropy range: {df['entropy_curr_tot_exp'].min():.2f}-{df['entropy_curr_tot_exp'].max():.2f}")
print(f"mean_fd range: {df['mean_fd'].min():.3f}-{df['mean_fd'].max():.3f} mm")

outcomes = ["mean_lang_fc", "IFG_STG_left", "IFG_STG_right"]
all_results = []

for oc in outcomes:
    formula = f"{oc} ~ nlang_z + entropy_z + age_z + edu_z + sex_binary + mean_fd_z"
    model = smf.ols(formula, data=df).fit()

    print(f"\n{'='*60}")
    print(f"Outcome: {oc}")
    print(f"R2 = {model.rsquared:.3f},  F = {model.fvalue:.3f},  p = {model.f_pvalue:.4f}")
    print(f"{'Predictor':<15} {'Beta':>8} {'SE':>8} {'t':>8} {'p':>8} {'sig':>5}")
    print("-" * 55)
    for pred in ["nlang_z", "entropy_z", "age_z", "edu_z", "sex_binary", "mean_fd_z"]:
        b = model.params[pred]
        se = model.bse[pred]
        t = model.tvalues[pred]
        p = model.pvalues[pred]
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"{pred:<15} {b:>8.3f} {se:>8.3f} {t:>8.3f} {p:>8.4f} {sig:>5}")

    for pred in ["nlang_z", "entropy_z"]:
        all_results.append({
            "outcome": oc, "predictor": pred,
            "beta": model.params[pred], "se": model.bse[pred],
            "t": model.tvalues[pred], "p": model.pvalues[pred],
            "p_bonferroni": min(model.pvalues[pred] * len(outcomes), 1.0),
        })

res_df = pd.DataFrame(all_results)
res_df.to_csv(out / "fc_glm_results_conn.csv", index=False)

print("\n\n=== SUMMARY (key predictors, Bonferroni across 3 outcomes) ===")
print(f"{'Outcome':<20} {'Predictor':<12} {'Beta':>7} {'t':>7} {'p':>8} {'p_bonf':>8}")
print("-" * 65)
for _, r in res_df.iterrows():
    print(f"{r['outcome']:<20} {r['predictor']:<12} {r['beta']:>7.3f} "
          f"{r['t']:>7.3f} {r['p']:>8.4f} {r['p_bonferroni']:>8.4f}")

# ── Step 4: Figures ────────────────────────────────────────────────────
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from nilearn import plotting
import glob as glob_mod

# 4a) Group mean FC heatmap (diagonal zeroed)
mats = [np.load(f) for f in sorted(glob_mod.glob(str(out / "sub-*_fc_matrix.npy")))]
if mats:
    M = np.mean(mats, axis=0)
    off = M[np.triu_indices(6, k=1)]
    vmax = max(float(np.max(np.abs(off))), 0.5)
    plt.figure(figsize=(6.5, 5.2))
    mask = np.eye(6, dtype=bool)
    sns.heatmap(M, mask=mask, annot=True, fmt=".2f",
                xticklabels=roi_labels, yticklabels=roi_labels,
                cmap="RdBu_r", center=0, vmin=-vmax, vmax=vmax,
                square=True, linewidths=0.5, linecolor="white",
                cbar_kws={"label": "Fisher-z"})
    plt.title(f"Group-mean FC (motion-corrected), N={len(mats)}")
    plt.tight_layout()
    plt.savefig(out / "group_fc_matrix_conn.png", dpi=200)
    plt.close()
    print(f"\n[OK] group_fc_matrix_conn.png (N={len(mats)})")

    # 4b) Connectome glass brain
    edge_thresh = float(np.percentile(np.abs(off), 50))
    fig = plt.figure(figsize=(11, 4.5))
    plotting.plot_connectome(
        M, roi_coords, node_size=80,
        edge_threshold=edge_thresh, edge_cmap="Reds",
        edge_vmin=0, edge_vmax=vmax,
        display_mode="lyrz", colorbar=True,
        title=f"Connectome (motion-corrected, N={len(mats)})",
        figure=fig)
    fig.savefig(out / "connectome_conn.png", dpi=200)
    plt.close()
    print("[OK] connectome_conn.png")

# 4c) Scatter plots
preds = [("nlang_z", "steelblue", "Diversity (nlang z)"),
         ("entropy_z", "coral", "Balance (entropy z)")]
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for col, oc in enumerate(outcomes):
    for row, (p, color, label) in enumerate(preds):
        ax = axes[row, col]
        ax.scatter(df[p], df[oc], alpha=0.6, color=color, s=35)
        m, b = np.polyfit(df[p], df[oc], 1)
        xs = np.linspace(df[p].min(), df[p].max(), 100)
        ax.plot(xs, m * xs + b, color=color, linewidth=2)
        ax.set_xlabel(label); ax.set_ylabel(oc)
        ax.set_title(f"{oc}  vs  {p}")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(out / "fc_scatter_conn.png", dpi=200)
plt.close()
print(f"[OK] fc_scatter_conn.png (N={len(df)})")

print(f"\nAll outputs in: {out}")
