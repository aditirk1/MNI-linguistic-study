"""
Prepare everything needed for TBSS + randomise.

Outputs:
  derivatives/dwi_processed/tbss/          <- working directory
  derivatives/dwi_processed/tbss_design/
    design.mat        FSL design matrix
    design.con        FSL contrasts
    subject_order.txt which subject is which row

  run_tbss.sh         ready-to-execute bash script for Ubuntu/WSL
"""

import pandas as pd
import numpy as np
from pathlib import Path

base = Path(r"C:\Users\Aditi\ds005613")
tbss_dir = base / "derivatives" / "dwi_processed" / "tbss"
design_dir = base / "derivatives" / "dwi_processed" / "tbss_design"
tbss_dir.mkdir(parents=True, exist_ok=True)
design_dir.mkdir(parents=True, exist_ok=True)

design = pd.read_csv(base / "shared_design_matrix.csv")
subset = [s.strip() for s in
          (base / "subset_50_participants.txt").read_text().splitlines()
          if s.strip()]

# TBSS processes FA files alphabetically, so we must sort
subset_sorted = sorted(subset)

# Filter design matrix to our subjects, in sorted order
df = design[design["participant_id"].isin(subset_sorted)].copy()
df = df.set_index("participant_id").loc[subset_sorted].reset_index()

print(f"Subjects in design matrix: {len(df)}")
print(f"First 5: {df['participant_id'].tolist()[:5]}")
print(f"Last 5:  {df['participant_id'].tolist()[-5:]}")

# Save subject order for reference
(design_dir / "subject_order.txt").write_text(
    "\n".join(df["participant_id"].tolist()) + "\n"
)

# Build design matrix: nlang_z, entropy_z, age_z, edu_z, sex_binary
predictors = ["nlang_z", "entropy_z", "age_z", "edu_z", "sex_binary"]
X = df[predictors].values
n_subs, n_regs = X.shape

print(f"\nDesign matrix: {n_subs} subjects x {n_regs} regressors")
print(f"Regressors: {predictors}")

# FSL design.mat
mat_path = design_dir / "design.mat"
with open(mat_path, "w") as f:
    f.write(f"/NumWaves\t{n_regs}\n")
    f.write(f"/NumPoints\t{n_subs}\n")
    f.write("/PPheights\t" + "\t".join(["1"] * n_regs) + "\n")
    f.write("\n/Matrix\n")
    for row in X:
        f.write(" ".join([f"{v:.6f}" for v in row]) + "\n")

# FSL design.con — 4 contrasts
con_path = design_dir / "design.con"
with open(con_path, "w") as f:
    f.write(f"/NumWaves\t{n_regs}\n")
    f.write("/NumContrasts\t4\n")
    f.write("/ContrastName1\tnlang_positive\n")
    f.write("/ContrastName2\tnlang_negative\n")
    f.write("/ContrastName3\tentropy_positive\n")
    f.write("/ContrastName4\tentropy_negative\n")
    f.write("\n/Matrix\n")
    f.write("1 0 0 0 0\n")    # nlang +
    f.write("-1 0 0 0 0\n")   # nlang -
    f.write("0 1 0 0 0\n")    # entropy +
    f.write("0 -1 0 0 0\n")   # entropy -

print(f"\nSaved: {mat_path}")
print(f"Saved: {con_path}")
print(f"Saved: {design_dir / 'subject_order.txt'}")

# Verify: print a few rows
print(f"\nFirst 3 rows of design matrix:")
for i in range(min(3, n_subs)):
    print(f"  {df['participant_id'].iloc[i]:>12}  "
          + "  ".join([f"{v:>8.3f}" for v in X[i]]))

print(f"\nContrasts:")
print(f"  1: nlang+   = [1  0  0  0  0]")
print(f"  2: nlang-   = [-1 0  0  0  0]")
print(f"  3: entropy+ = [0  1  0  0  0]")
print(f"  4: entropy- = [0 -1  0  0  0]")

# ── Generate the bash script ──────────────────────────────────────────
bash_script = r"""#!/bin/bash
# run_tbss.sh — Run TBSS + randomise on the 51-subject FA maps
# Execute in Ubuntu/WSL:
#   chmod +x /mnt/c/Users/Aditi/ds005613/run_tbss.sh
#   cd /mnt/c/Users/Aditi/ds005613/derivatives/dwi_processed/tbss
#   bash /mnt/c/Users/Aditi/ds005613/run_tbss.sh

set -e
source ~/.profile 2>/dev/null || true

WIN_BASE="/mnt/c/Users/Aditi/ds005613"
DWI_OUT="$WIN_BASE/derivatives/dwi_processed"
TBSS_DIR="$DWI_OUT/tbss"
DESIGN_DIR="$DWI_OUT/tbss_design"
SUBSET="$WIN_BASE/subset_50_participants.txt"

mkdir -p "$TBSS_DIR"
cd "$TBSS_DIR"

echo "========================================"
echo "TBSS Pipeline started: $(date)"
echo "========================================"

# Step 0: Copy FA maps into TBSS directory (sorted alphabetically)
echo ""
echo "--- Copying FA maps ---"
COPIED=0
MISSING=0
mapfile -t SUBS < <(sort "$SUBSET")
for SUB in "${SUBS[@]}"; do
    SUB=$(echo "$SUB" | tr -d '\r\n ')
    FA="$DWI_OUT/$SUB/${SUB}_dti_FA.nii.gz"
    if [ -f "$FA" ]; then
        cp "$FA" "${SUB}_FA.nii.gz"
        COPIED=$((COPIED+1))
    else
        echo "  MISSING FA: $SUB"
        MISSING=$((MISSING+1))
    fi
done
echo "Copied: $COPIED   Missing: $MISSING"

if [ $COPIED -lt 10 ]; then
    echo "ERROR: fewer than 10 FA maps. Aborting."
    exit 1
fi

# Step 1: Preproc (erode + zero end slices)
echo ""
echo "--- tbss_1_preproc ---"
tbss_1_preproc *_FA.nii.gz

# Step 2: Register all FA to FMRIB58 template
echo ""
echo "--- tbss_2_reg (this is the slowest step) ---"
tbss_2_reg -T

# Step 3: Create mean FA and skeleton
echo ""
echo "--- tbss_3_postreg ---"
tbss_3_postreg -S

# Step 4: Project onto skeleton (threshold 0.2)
echo ""
echo "--- tbss_4_prestats ---"
tbss_4_prestats 0.2

echo ""
echo "--- TBSS complete. Starting randomise ---"

# Copy design files into stats/
cp "$DESIGN_DIR/design.mat" stats/
cp "$DESIGN_DIR/design.con" stats/

cd stats/

# Step 5: Randomise with TFCE
echo ""
echo "--- randomise (5000 permutations, TFCE) ---"
randomise \
    -i all_FA_skeletonised \
    -o tbss_results \
    -d design.mat \
    -t design.con \
    -m mean_FA_skeleton_mask \
    -n 5000 \
    --T2 \
    -x

echo ""
echo "========================================"
echo "TBSS + randomise complete: $(date)"
echo "========================================"
echo ""
echo "Output files:"
ls -la tbss_results_tfce_corrp_tstat*.nii.gz 2>/dev/null || echo "  (no corrp files found)"
echo ""
echo "Threshold at p > 0.95 (= corrected p < 0.05)"
echo "View in FSLeyes: overlay tbss_results_tfce_corrp_tstat* on mean_FA_skeleton"
"""

bash_path = base / "run_tbss.sh"
bash_path.write_text(bash_script.replace("\r\n", "\n"))
print(f"\nSaved bash script: {bash_path}")
print("\nWhen DWI finishes, run in Ubuntu:")
print("  chmod +x /mnt/c/Users/Aditi/ds005613/run_tbss.sh")
print("  cd /mnt/c/Users/Aditi/ds005613/derivatives/dwi_processed/tbss")
print("  nohup bash /mnt/c/Users/Aditi/ds005613/run_tbss.sh &")
