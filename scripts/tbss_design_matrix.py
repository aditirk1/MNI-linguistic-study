"""
Generate FSL-format design matrix (.mat) and contrast (.con) files for TBSS randomise.
These go into the TBSS stats step after tbss_4_prestats.

Model: FA ~ nlang_z + entropy_z + age_z + edu_z + sex_binary + TIV_z + intercept
"""

import pandas as pd
import numpy as np
from pathlib import Path

root = Path(r"C:\Users\Aditi\ds005613")
out_dir = root / "derivatives" / "dwi_fsl" / "tbss_design"
out_dir.mkdir(parents=True, exist_ok=True)

design = pd.read_csv(root / "subset_50_design_matrix.csv")

# TIV placeholder (update after structural processing)
if "TIV_z" not in design.columns:
    design["TIV_z"] = 0.0

# Sort subjects alphabetically (must match TBSS FA file order)
design = design.sort_values("participant_id").reset_index(drop=True)

# Predictors in order
pred_cols = ["nlang_z", "entropy_z", "age_z", "edu_z", "sex_binary", "TIV_z"]
n = len(design)
p = len(pred_cols) + 1  # +1 for intercept

# Build design matrix (intercept last, FSL convention)
X = design[pred_cols].values
X = np.column_stack([X, np.ones(n)])

# Write .mat file (FSL VEST format)
mat_file = out_dir / "design.mat"
with open(mat_file, "w") as f:
    f.write(f"/NumWaves\t{p}\n")
    f.write(f"/NumPoints\t{n}\n")
    f.write("/PPheights\t" + "\t".join(["1.0"] * p) + "\n")
    f.write("\n/Matrix\n")
    for row in X:
        f.write("\t".join(f"{v:.6f}" for v in row) + "\n")

# Contrasts:
# C1: nlang positive effect
# C2: nlang negative effect
# C3: entropy positive effect
# C4: entropy negative effect
contrasts = {
    "nlang_pos":    [1, 0, 0, 0, 0, 0, 0],
    "nlang_neg":    [-1, 0, 0, 0, 0, 0, 0],
    "entropy_pos":  [0, 1, 0, 0, 0, 0, 0],
    "entropy_neg":  [0, -1, 0, 0, 0, 0, 0],
}

con_file = out_dir / "design.con"
ncon = len(contrasts)
with open(con_file, "w") as f:
    f.write(f"/NumWaves\t{p}\n")
    f.write(f"/NumContrasts\t{ncon}\n")
    f.write("/PPheights\t" + "\t".join(["1.0"] * ncon) + "\n")
    f.write(f"/RequiredEffect\t" + "\t".join(["1.0"] * ncon) + "\n")
    f.write("\n/Matrix\n")
    for name, vec in contrasts.items():
        f.write("\t".join(f"{v:.1f}" for v in vec) + "\n")

# Save subject order for reference
order_file = out_dir / "subject_order.txt"
design[["participant_id"]].to_csv(order_file, index=False, header=False)

print(f"Design matrix:  {mat_file}  ({n} subjects x {p} regressors)")
print(f"Contrasts:      {con_file}  ({ncon} contrasts)")
print(f"Subject order:  {order_file}")
print(f"\nRegressor order: {pred_cols + ['intercept']}")
print(f"\nContrasts defined:")
for name, vec in contrasts.items():
    print(f"  {name}: {vec}")
print(f"\nUsage in FSL (after tbss_4_prestats):")
print(f"  randomise -i all_FA_skeletonised -o tbss \\")
print(f"    -m mean_FA_skeleton_mask \\")
print(f"    -d {mat_file} -t {con_file} \\")
print(f"    -n 5000 --T2")
