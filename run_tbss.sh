#!/bin/bash
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
