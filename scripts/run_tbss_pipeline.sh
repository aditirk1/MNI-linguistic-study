#!/bin/bash
# TBSS pipeline for the 51-subject DWI dataset.
# Run from Ubuntu (WSL):
#   chmod +x /mnt/c/Users/Aditi/ds005613/run_tbss_pipeline.sh
#   nohup /mnt/c/Users/Aditi/ds005613/run_tbss_pipeline.sh > /mnt/c/Users/Aditi/ds005613/derivatives/dwi_processed/tbss_run.log 2>&1 &
#
# After this finishes you will have:
#   tbss/stats/all_FA_skeletonised.nii.gz
#   tbss/stats/mean_FA_skeleton_mask.nii.gz
# and you are ready for randomise.

set -e
source ~/.profile 2>/dev/null || true

OUT_BASE="/mnt/c/Users/Aditi/ds005613/derivatives/dwi_processed"
TBSS_DIR="$OUT_BASE/tbss"
SUBSET="/mnt/c/Users/Aditi/ds005613/subset_50_participants.txt"
LOG="$OUT_BASE/tbss_run.log"

mkdir -p "$TBSS_DIR"
cd "$TBSS_DIR"

mapfile -t SUBS < "$SUBSET"

echo "================ TBSS pipeline ================"
echo "Started: $(date)"
echo "Subjects: ${#SUBS[@]}"
echo "Working dir: $TBSS_DIR"

# 0) Copy FA maps with subject-stamped names (TBSS sorts alphabetically)
echo ""
echo "[0/4] Copying FA maps..."
for SUB in "${SUBS[@]}"; do
    SUB=$(echo "$SUB" | tr -d '[:space:]')
    [ -z "$SUB" ] && continue
    SRC="$OUT_BASE/$SUB/${SUB}_dti_FA.nii.gz"
    DST="$TBSS_DIR/${SUB}_FA.nii.gz"
    if [ -f "$SRC" ]; then
        cp "$SRC" "$DST"
    else
        echo "  MISSING FA: $SUB"
    fi
done
N_FA=$(ls -1 "$TBSS_DIR"/*_FA.nii.gz 2>/dev/null | wc -l)
echo "FA maps copied: $N_FA"

# 1) tbss_1_preproc
echo ""
echo "[1/4] tbss_1_preproc - $(date)"
tbss_1_preproc *_FA.nii.gz

# 2) tbss_2_reg -T  (register all FA -> FMRIB58 template)
echo ""
echo "[2/4] tbss_2_reg -T - $(date)"
tbss_2_reg -T

# 3) tbss_3_postreg -S  (mean FA + skeleton)
echo ""
echo "[3/4] tbss_3_postreg -S - $(date)"
tbss_3_postreg -S

# 4) tbss_4_prestats 0.2  (skeleton threshold + project)
echo ""
echo "[4/4] tbss_4_prestats 0.2 - $(date)"
tbss_4_prestats 0.2

echo ""
echo "================ TBSS done ================"
echo "Finished: $(date)"
ls -la stats/ | head -30
