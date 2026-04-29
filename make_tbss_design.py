"""
Build FSL design.mat and design.con for randomise on the TBSS skeletonised FA.

Order of subjects MUST match how TBSS sorted them (alphabetical by file name).
Regressors (in this order):
    1. nlang_z
    2. entropy_z
    3. age_z
    4. edu_z
    5. sex_binary

Contrasts:
    1. nlang positive       [ 1  0  0  0  0]
    2. nlang negative       [-1  0  0  0  0]
    3. entropy positive     [ 0  1  0  0  0]
    4. entropy negative     [ 0 -1  0  0  0]
"""
from pathlib import Path
import pandas as pd
import numpy as np

base    = Path(r"C:\Users\Aditi\ds005613")
tbss    = base / "derivatives" / "dwi_processed" / "tbss"
stats   = tbss / "stats"
stats.mkdir(parents=True, exist_ok=True)

subset  = [s.strip() for s in
           (base / "subset_50_participants.txt").read_text().splitlines()
           if s.strip()]
subset_sorted = sorted(subset)

design = pd.read_csv(base / "shared_design_matrix.csv")
df = design[design["participant_id"].isin(subset_sorted)].copy()
df = df.set_index("participant_id").loc[subset_sorted].reset_index()

print(f"Subjects in design.mat: {len(df)}")
print("First 3:", df['participant_id'].tolist()[:3])
print("Last 3 :", df['participant_id'].tolist()[-3:])

cols = ["nlang_z", "entropy_z", "age_z", "edu_z", "sex_binary"]
missing = [c for c in cols if c not in df.columns]
if missing:
    raise SystemExit(f"Missing columns in design CSV: {missing}")

X = df[cols].to_numpy(dtype=float)
nrow, ncol = X.shape

mat = stats / "design.mat"
with open(mat, "w") as f:
    f.write(f"/NumWaves {ncol}\n")
    f.write(f"/NumPoints {nrow}\n")
    f.write("/PPheights " + " ".join(["1"] * ncol) + "\n")
    f.write("/Matrix\n")
    for r in X:
        f.write(" ".join(f"{v:.6f}" for v in r) + "\n")

con = stats / "design.con"
with open(con, "w") as f:
    f.write(f"/NumWaves {ncol}\n")
    f.write("/NumContrasts 4\n")
    f.write("/PPheights 1 1 1 1\n")
    f.write("/Matrix\n")
    f.write(" 1  0  0  0  0\n")
    f.write("-1  0  0  0  0\n")
    f.write(" 0  1  0  0  0\n")
    f.write(" 0 -1  0  0  0\n")

print(f"\nWrote {mat}")
print(f"Wrote {con}")
print("\nNext (run in WSL after TBSS finishes):")
print("  cd /mnt/c/Users/Aditi/ds005613/derivatives/dwi_processed/tbss/stats")
print("  randomise -i all_FA_skeletonised -o tbss_results \\")
print("            -d design.mat -t design.con \\")
print("            -m mean_FA_skeleton_mask -n 5000 --T2")
