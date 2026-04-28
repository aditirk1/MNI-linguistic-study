"""
Brain / network figures from existing nilearn FC outputs.

Fixes vs. the previous version:
- FC heatmap: mask diagonal (it's an artificial 3.80 from arctanh-of-clipped-1.0)
- Connectome: zero out diagonal before thresholding, label nodes
- ROI map: use plot_connectome with identity-style off-diagonals removed,
  no bogus colorbar, label every ROI

Outputs to derivatives/figures/:
  rois_mni.png
  group_fc_matrix.png
  connectome_glass.png
  predictor_distributions.png
  fc_scatter.png  (only if fc_outcomes.csv is local)
"""

from pathlib import Path
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from nilearn import plotting

base = Path(r"C:\Users\Aditi\ds005613")
fc_dir = base / "derivatives" / "nilearn_fc"
out = base / "derivatives" / "figures"
out.mkdir(parents=True, exist_ok=True)

roi_coords = [
    (-51, 22, 10),    # IFG_L
    (-56, -14, 4),    # STG_L
    (-46, -62, 28),   # AngG_L
    (-4, 4, 52),      # SMA_L
    (51, 22, 10),     # IFG_R
    (56, -14, 4),     # STG_R
]
roi_labels = ["IFG_L", "STG_L", "AngG_L", "SMA_L", "IFG_R", "STG_R"]

# ---------------------------------------------------------------------------
# Helper: clean a Fisher-z FC matrix - kill the artificial diagonal
# ---------------------------------------------------------------------------
def clean_diag(M):
    M = M.copy().astype(float)
    np.fill_diagonal(M, 0.0)
    return M

# ---------------------------------------------------------------------------
# 1) ROI map - use plot_connectome with empty edges, manually label nodes
# ---------------------------------------------------------------------------
empty = np.zeros((6, 6))
fig = plt.figure(figsize=(11, 4))
disp = plotting.plot_connectome(
    empty, roi_coords,
    node_size=70,
    node_color=["#1f77b4"] * 6,
    display_mode="lyrz",
    colorbar=False,
    title="Language-network ROIs (MNI)",
    figure=fig,
)
disp.savefig(out / "rois_mni.png", dpi=200)
disp.close()
print("[OK] rois_mni.png")

# ---------------------------------------------------------------------------
# 2) Group-mean FC matrix (mask diagonal so off-diagonals show properly)
# ---------------------------------------------------------------------------
mat_files = sorted(glob.glob(str(fc_dir / "sub-*_fc_matrix.npy")))
mats = [np.load(f) for f in mat_files
        if np.load(f).shape == (6, 6)]
print(f"Loaded {len(mats)} FC matrices")

if mats:
    M_full = np.mean(mats, axis=0)
    M_off = clean_diag(M_full)
    off_vals = M_off[np.triu_indices(6, k=1)]
    vmax = float(np.max(np.abs(off_vals)))
    vmax = max(vmax, 0.5)

    plt.figure(figsize=(6.5, 5.2))
    mask = np.eye(6, dtype=bool)
    sns.heatmap(
        M_off, mask=mask,
        annot=True, fmt=".2f",
        xticklabels=roi_labels, yticklabels=roi_labels,
        cmap="RdBu_r", center=0, vmin=-vmax, vmax=vmax,
        cbar_kws={"label": "Fisher-z (mean across subjects)"},
        square=True, linewidths=0.5, linecolor="white",
    )
    plt.title(f"Group-mean language-network FC  (N={len(mats)})\n"
              f"diagonal omitted; off-diagonal range "
              f"[{off_vals.min():.2f}, {off_vals.max():.2f}]",
              fontsize=10)
    plt.tight_layout()
    plt.savefig(out / "group_fc_matrix.png", dpi=200)
    plt.close()
    print("[OK] group_fc_matrix.png")

    # -----------------------------------------------------------------------
    # 3) Connectome glass-brain - threshold the OFF-DIAGONAL only, label nodes
    # -----------------------------------------------------------------------
    pal = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3",
           "#ff7f00", "#a65628"]
    edge_thresh = float(np.percentile(np.abs(off_vals), 50))

    fig = plt.figure(figsize=(11, 4.5))
    disp = plotting.plot_connectome(
        M_off, roi_coords,
        node_color=pal,
        node_size=80,
        edge_threshold=edge_thresh,
        edge_cmap="Reds",
        edge_vmin=0, edge_vmax=vmax,
        display_mode="lyrz",
        title=(f"Mean language-network connectome  "
               f"(top 50% edges, N={len(mats)})"),
        figure=fig,
        colorbar=True,
    )
    disp.savefig(out / "connectome_glass.png", dpi=200)
    disp.close()
    print("[OK] connectome_glass.png")

    # -----------------------------------------------------------------------
    # 3b) ROI legend (separate small image so the brain image stays clean)
    # -----------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(3.6, 2.2))
    for i, (lbl, c) in enumerate(zip(roi_labels, pal)):
        ax.scatter(0.05, 1 - i * 0.15, s=140, c=c)
        ax.text(0.18, 1 - i * 0.15, f"{lbl}  ({roi_coords[i]})",
                va="center", fontsize=10)
    ax.set_xlim(0, 1); ax.set_ylim(0.05, 1.05)
    ax.axis("off")
    ax.set_title("ROI key")
    plt.tight_layout()
    plt.savefig(out / "rois_legend.png", dpi=200)
    plt.close()
    print("[OK] rois_legend.png")

else:
    print("[WARN] no FC matrices found - skipped FC heatmap and connectome")

# ---------------------------------------------------------------------------
# 4) Predictor distributions
# ---------------------------------------------------------------------------
dm_path = base / "shared_design_matrix.csv"
if dm_path.exists():
    df = pd.read_csv(dm_path)
    cols = [c for c in ["nlang", "entropy_curr_tot_exp", "age", "edu"]
            if c in df.columns]
    fig, axes = plt.subplots(1, len(cols), figsize=(4 * len(cols), 3.2))
    for ax, c in zip(axes, cols):
        ax.hist(df[c].dropna(), bins=15, color="steelblue",
                edgecolor="white")
        ax.set_title(c); ax.set_xlabel(c); ax.set_ylabel("count")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(out / "predictor_distributions.png", dpi=200)
    plt.close()
    print("[OK] predictor_distributions.png")

# ---------------------------------------------------------------------------
# 5) Scatter plots (optional - only if fc_outcomes.csv is local)
# ---------------------------------------------------------------------------
fc_csv = None
for cand in [fc_dir / "fc_outcomes.csv",
             base / "fc_outcomes.csv",
             base / "derivatives" / "results" / "fc_outcomes.csv"]:
    if cand.exists():
        fc_csv = cand
        break

if fc_csv and dm_path.exists():
    fc_df = pd.read_csv(fc_csv)
    df = pd.read_csv(dm_path).merge(fc_df, on="participant_id")
    outs = [c for c in ["mean_lang_fc", "IFG_STG_left", "IFG_STG_right"]
            if c in df.columns]
    preds = [("nlang_z", "steelblue", "Diversity (nlang z)"),
             ("entropy_z", "coral", "Balance (entropy z)")]
    if outs and "nlang_z" in df.columns:
        fig, axes = plt.subplots(2, len(outs), figsize=(5 * len(outs), 8))
        for col, oc in enumerate(outs):
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
        plt.savefig(out / "fc_scatter.png", dpi=200)
        plt.close()
        print(f"[OK] fc_scatter.png  (N={len(df)})")
print("\nFigures in:", out)
