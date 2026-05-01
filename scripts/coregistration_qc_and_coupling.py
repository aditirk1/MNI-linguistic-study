"""
QC figures for multimodal methods (shared MNI space) + exploratory structure–function coupling.

1) fig_coreg_dwi_mni.png — mean FA and TBSS skeleton in MNI (when TBSS stats exist).
2) fig_coreg_fmri_mni.png — mean resting-state BOLD volume in MNI152 after SPM25 (coregistration,
   normalisation, smoothing); one rendered cohort volume (alphabetically first available wmean*/sw* file).
3) roi_structure_function.csv + fig8_roi_coupling.png — Pearson r per ROI between
   local skeleton FA and mean language FC (requires fc_outcomes_motion + all_FA_skeletonised).

MNI background: FSL MNI152_T1_1mm_brain if FSLDIR is set; otherwise ICBM152 T1 from Nilearn.

Run:  .venv\\Scripts\\python.exe coregistration_qc_and_coupling.py
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import plotting
from nilearn.maskers import NiftiSpheresMasker
from scipy import stats

BASE = Path(__file__).resolve().parent
FIG_DIR = BASE / "derivatives" / "results" / "figures"
STATS_DIR = BASE / "derivatives" / "dwi_processed" / "tbss" / "stats"
FC_DIR = BASE / "derivatives" / "nilearn_fc_motion"
DESIGN_ORDER = BASE / "derivatives" / "dwi_processed" / "tbss_design" / "subject_order.txt"
SUBSET_TXT = BASE / "subset_50_participants.txt"

ROI_COORDS = {
    "IFG_L": (-51, 22, 10),
    "STG_L": (-56, -14, 4),
    "AngG_L": (-46, -62, 28),
    "SMA_L": (-4, 4, 52),
    "IFG_R": (51, 22, 10),
    "STG_R": (56, -14, 4),
}


def resolve_mni_brain() -> str:
    fsl = os.environ.get("FSLDIR")
    if fsl:
        p = Path(fsl) / "data" / "standard" / "MNI152_T1_1mm_brain.nii.gz"
        if p.is_file():
            return str(p)
    from nilearn.datasets import fetch_icbm152_2009

    # T1 1mm MNI — predictable file path for plot_stat_map / plot_epi bg_img
    return str(fetch_icbm152_2009(verbose=0).t1)


def _find_mean_bold_volume_mni() -> Path | None:
    """Mean or warped rest BOLD after SPM; sorted glob → one reproducible cohort volume for display."""
    for pat in (
        "wmean*.nii",
        "wmeane*.nii",
        "mean*_task-rest*_bold.nii",
        "swsub-*_task-rest*_bold.nii",
        "wsub-*_task-rest*_bold.nii",
    ):
        found = sorted(BASE.glob(f"sub-pp*/ses-01/func/{pat}"))
        if found:
            return found[0]
    return None


def make_fig_coreg_dwi() -> None:
    mean_fa = STATS_DIR / "mean_FA.nii.gz"
    skel = STATS_DIR / "mean_FA_skeleton.nii.gz"
    if not mean_fa.is_file():
        print("[skip] fig_coreg_dwi_mni: missing", mean_fa)
        return

    mni = resolve_mni_brain()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(15, 4.8))
    fig.patch.set_facecolor("white")

    plotting.plot_stat_map(
        str(mean_fa),
        bg_img=mni,
        display_mode="z",
        cut_coords=(-20, -5, 10, 25, 40),
        cmap="hot",
        threshold=0.15,
        title="Group mean FA (TBSS space) on MNI T1",
        axes=axes[0],
        annotate=False,
        draw_cross=False,
    )
    if skel.is_file():
        plotting.plot_stat_map(
            str(skel),
            bg_img=str(mean_fa),
            display_mode="z",
            cut_coords=(-20, -5, 10, 25, 40),
            cmap="cool",
            threshold=0.2,
            title="Mean FA skeleton on mean FA",
            axes=axes[1],
            annotate=False,
            draw_cross=False,
            colorbar=False,
        )
    else:
        axes[1].set_axis_off()
        axes[1].text(0.5, 0.5, "mean_FA_skeleton.nii.gz not found", ha="center", va="center")

    fig.suptitle(
        "Coregistration QC: diffusion (TBSS → MNI / template space)",
        fontsize=12,
        fontweight="bold",
    )
    fig.tight_layout()
    out = FIG_DIR / "fig_coreg_dwi_mni.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print("[ok]", out)


def make_fig_coreg_fmri() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    mean_bold = _find_mean_bold_volume_mni()
    mni = resolve_mni_brain()
    if mean_bold is None:
        print("[skip] fig_coreg_fmri_mni: no wmean/w/sw rest BOLD found under sub-*/func")
        return

    fig, ax = plt.subplots(1, 1, figsize=(14, 4.2))
    fig.patch.set_facecolor("white")
    plotting.plot_epi(
        str(mean_bold),
        bg_img=mni,
        display_mode="z",
        cut_coords=(-20, -5, 10, 25, 40),
        cmap="cold_hot",
        title="Resting-state fMRI in MNI152 space (SPM25 coregistration, normalisation, smoothing)",
        axes=ax,
        annotate=False,
        draw_cross=False,
    )
    fig.tight_layout()
    out = FIG_DIR / "fig_coreg_fmri_mni.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print("[ok]", out)


def make_roi_coupling() -> None:
    fa_4d_path = STATS_DIR / "all_FA_skeletonised.nii.gz"
    fc_csv = FC_DIR / "fc_outcomes_motion.csv"

    if not fa_4d_path.is_file():
        print("[skip] ROI coupling: missing", fa_4d_path)
        return
    if not fc_csv.is_file():
        print("[skip] ROI coupling: missing", fc_csv)
        return

    if DESIGN_ORDER.is_file():
        tbss_ids = [s.strip() for s in DESIGN_ORDER.read_text().splitlines() if s.strip()]
    else:
        print("[warn] subject_order.txt missing; using sorted subset list (verify vs TBSS 4D order).")
        tbss_ids = sorted(
            s.strip()
            for s in SUBSET_TXT.read_text().splitlines()
            if s.strip()
        )

    fc_df = pd.read_csv(fc_csv)
    fc_map = fc_df.set_index("participant_id")["mean_lang_fc"].to_dict()

    img = nib.load(str(fa_4d_path))
    data = img.get_fdata()
    if data.ndim != 4:
        print("[skip] ROI coupling: expected 4D all_FA_skeletonised")
        return

    n_vol = data.shape[3]
    ids_use = tbss_ids[:n_vol]
    if len(tbss_ids) != n_vol:
        print(
            f"[warn] subject_order ({len(tbss_ids)}) vs 4D volumes ({n_vol}); using first {n_vol} IDs."
        )

    mfc = np.array([fc_map.get(pid, np.nan) for pid in ids_use])
    valid = ~np.isnan(mfc)
    if valid.sum() < 5:
        print("[skip] ROI coupling: too few subjects with FC after aligning to TBSS order.")
        return

    img4d = nib.Nifti1Image(data, img.affine, img.header)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for roi_name, coord in ROI_COORDS.items():
        masker = NiftiSpheresMasker(seeds=[coord], radius=8, standardize=False)
        ts = masker.fit_transform(img4d)
        ts = np.asarray(ts)
        if ts.ndim == 2:
            ts = ts[:, 0]
        else:
            ts = ts.ravel()
        if ts.shape[0] != n_vol:
            print(f"[skip] {roi_name}: unexpected masker output length")
            continue
        if np.std(ts[valid]) < 1e-12 or np.std(mfc[valid]) < 1e-12:
            r, p = float("nan"), float("nan")
        else:
            r, p = stats.pearsonr(ts[valid], mfc[valid])
        results.append(
            {
                "ROI": roi_name,
                "r_with_mean_FC": r,
                "p": p,
                "mean_FA_roi": float(np.mean(ts[valid])),
                "n": int(valid.sum()),
            }
        )
        print(f"  {roi_name}: r={r:.3f}, p={p:.4f} (n={valid.sum()})")

    res_df = pd.DataFrame(results)
    res_df.to_csv(FIG_DIR / "roi_structure_function.csv", index=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("white")
    colors = ["#2ECC71" if r > 0 else "#E74C3C" for r in res_df["r_with_mean_FC"]]
    x = np.arange(len(res_df))
    ax.bar(x, res_df["r_with_mean_FC"], color=colors, alpha=0.85, edgecolor="gray")
    ax.set_xticks(x)
    ax.set_xticklabels(res_df["ROI"], rotation=25, ha="right")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Pearson r (local FA vs mean language FC)")
    ax.set_xlabel("Language network ROI (MNI)")
    ax.set_title(
        "Exploratory structure–function coupling (skeleton FA vs FC at same MNI coordinates)"
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(-0.55, 0.55)
    fig.tight_layout()
    out = FIG_DIR / "fig8_roi_coupling.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print("[ok]", FIG_DIR / "roi_structure_function.csv")
    print("[ok]", out)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    make_fig_coreg_dwi()
    make_fig_coreg_fmri()
    make_roi_coupling()
    print("Done.")


if __name__ == "__main__":
    main()
