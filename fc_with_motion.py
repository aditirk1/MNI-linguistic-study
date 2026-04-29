"""
H1 functional connectivity with SPM-realign motion regression.

Inputs per subject (in sub-XXXX/ses-01/func/):
  - sub-XXXX_ses-01_task-rest_run-001_bold.nii(.gz)
  - rp_*task-rest*.txt   (6 motion params from SPM Realign: Estimate)

Outputs (in derivatives/nilearn_fc_motion/):
  - sub-XXXX_fc_matrix.npy           per-subject 6x6 Fisher-z FC
  - fc_outcomes_motion.csv           per-subject FC summaries + mean_FD
  - fc_glm_motion_results.csv        GLM with mean_FD_z added
"""

from pathlib import Path
import numpy as np
import pandas as pd
from nilearn.maskers import NiftiSpheresMasker
from nilearn.connectome import ConnectivityMeasure
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings("ignore")

base = Path(r"C:\Users\Aditi\ds005613")
out_dir = base / "derivatives" / "nilearn_fc_motion"
out_dir.mkdir(parents=True, exist_ok=True)

subs = [s.strip() for s in
        (base / "subset_50_participants.txt").read_text().splitlines()
        if s.strip()]
print(f"Subjects: {len(subs)}")

roi_coords = [
    (-51, 22, 10),    # IFG_L
    (-56, -14, 4),    # STG_L
    (-46, -62, 28),   # AngG_L
    (-4,  4,  52),    # SMA_L
    (51, 22, 10),     # IFG_R
    (56, -14, 4),     # STG_R
]
roi_names = ["IFG_L", "STG_L", "AngG_L", "SMA_L", "IFG_R", "STG_R"]


def load_rp(rp_path: Path) -> np.ndarray:
    rp = np.loadtxt(rp_path)
    return rp


def mean_fd_power(rp: np.ndarray, radius_mm: float = 50.0) -> float:
    """Power-style FD: |dx|+|dy|+|dz| + radius*(|drot1|+|drot2|+|drot3|)."""
    trans = rp[:, :3]
    rot = rp[:, 3:6] * radius_mm
    d = np.diff(np.hstack([trans, rot]), axis=0)
    fd = np.sum(np.abs(d), axis=1)
    return float(np.mean(fd))


def find_bold(sub: str) -> Path | None:
    """Prefer the SPM-normalized + smoothed MNI BOLD (sw*) over native-space."""
    func = base / sub / "ses-01" / "func"
    for name in [
        f"sw{sub}_ses-01_task-rest_run-001_bold.nii",
        f"w{sub}_ses-01_task-rest_run-001_bold.nii",
        f"{sub}_ses-01_task-rest_run-001_bold.nii.gz",
        f"{sub}_ses-01_task-rest_run-001_bold.nii",
    ]:
        if (func / name).exists():
            return func / name
    return None


def find_rp(sub: str) -> Path | None:
    func = base / sub / "ses-01" / "func"
    for cand in func.glob("rp_*task-rest*.txt"):
        return cand
    return None


masker = NiftiSpheresMasker(
    seeds=roi_coords,
    radius=8,
    t_r=2.0,
    high_pass=0.01,
    low_pass=0.1,
    smoothing_fwhm=None,
    standardize=True,
    detrend=True,
    verbose=0,
)

rows = []
failed = []

for i, sub in enumerate(subs, 1):
    bold = find_bold(sub)
    rp_file = find_rp(sub)
    if bold is None or rp_file is None:
        print(f"[{i}/{len(subs)}] {sub} MISSING bold or rp -> skip")
        failed.append(sub)
        continue
    try:
        rp = load_rp(rp_file)
        mfd = mean_fd_power(rp)

        ts = masker.fit_transform(str(bold), confounds=rp)

        cm = ConnectivityMeasure(kind="correlation",
                                 standardize="zscore_sample")
        fc = cm.fit_transform([ts])[0]
        fc_z = np.arctanh(np.clip(fc, -0.999, 0.999))

        idx = {n: j for j, n in enumerate(roi_names)}
        upper = fc_z[np.triu_indices(len(roi_names), k=1)]

        rows.append({
            "participant_id": sub,
            "mean_lang_fc": float(upper.mean()),
            "IFG_STG_left": float(fc_z[idx["IFG_L"], idx["STG_L"]]),
            "IFG_STG_right": float(fc_z[idx["IFG_R"], idx["STG_R"]]),
            "mean_FD": mfd,
        })
        np.save(out_dir / f"{sub}_fc_matrix.npy", fc_z)
        print(f"[{i}/{len(subs)}] {sub} OK  meanFC={upper.mean():.3f}  "
              f"FD={mfd:.3f}")
    except Exception as e:
        print(f"[{i}/{len(subs)}] {sub} FAILED: {e}")
        failed.append(sub)

fc_df = pd.DataFrame(rows)
fc_df.to_csv(out_dir / "fc_outcomes_motion.csv", index=False)
print(f"\nCompleted: {len(fc_df)}/{len(subs)}  Failed: {failed}")

design = pd.read_csv(base / "shared_design_matrix.csv")
df = fc_df.merge(design, on="participant_id")
df["mean_FD_z"] = (df["mean_FD"] - df["mean_FD"].mean()) / df["mean_FD"].std()
print(f"Analysis N: {len(df)}  mean_FD range: "
      f"{df['mean_FD'].min():.3f}-{df['mean_FD'].max():.3f}")

outcomes = ["mean_lang_fc", "IFG_STG_left", "IFG_STG_right"]
results = []
for y in outcomes:
    formula = (f"{y} ~ nlang_z + entropy_z + age_z + edu_z + "
               f"sex_binary + mean_FD_z")
    m = smf.ols(formula, data=df).fit()
    print(f"\n=== {y}  R2={m.rsquared:.3f}  F p={m.f_pvalue:.4f} ===")
    print(m.summary().tables[1])
    for pred in ["nlang_z", "entropy_z", "mean_FD_z"]:
        results.append({
            "outcome": y, "predictor": pred,
            "beta": float(m.params[pred]),
            "se": float(m.bse[pred]),
            "t": float(m.tvalues[pred]),
            "p": float(m.pvalues[pred]),
            "p_bonf_3outcomes": min(float(m.pvalues[pred]) * 3, 1.0),
        })

res = pd.DataFrame(results)
res.to_csv(out_dir / "fc_glm_motion_results.csv", index=False)
print("\nSaved:", out_dir / "fc_glm_motion_results.csv")
