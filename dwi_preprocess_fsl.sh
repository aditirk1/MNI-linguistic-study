#!/bin/bash
# DWI Preprocessing Pipeline — FSL (run in WSL after FSL install)
# Steps: eddy correction → brain extraction → DTI fitting → TBSS prep
#
# Usage: bash dwi_preprocess_fsl.sh
# Run from: /mnt/c/Users/Aditi/ds005613 (WSL path)

BIDS_ROOT="/mnt/c/Users/Aditi/ds005613"
OUT_ROOT="/mnt/c/Users/Aditi/ds005613/derivatives/dwi_fsl"
SUBJECTS_FILE="/mnt/c/Users/Aditi/ds005613/subset_50_participants.txt"

mkdir -p "$OUT_ROOT"

# Read subject list
mapfile -t SUBJECTS < "$SUBJECTS_FILE"
NSUB=${#SUBJECTS[@]}
echo "Processing $NSUB subjects for DWI"

for ((i=0; i<NSUB; i++)); do
    SID=${SUBJECTS[$i]}
    echo ""
    echo "=== [$((i+1))/$NSUB] $SID ==="
    
    DWI_DIR="$BIDS_ROOT/$SID/ses-01/dwi"
    DWI_NII="$DWI_DIR/${SID}_ses-01_dwi.nii.gz"
    BVAL="$DWI_DIR/${SID}_ses-01_dwi.bval"
    BVEC="$DWI_DIR/${SID}_ses-01_dwi.bvec"
    
    SUB_OUT="$OUT_ROOT/$SID"
    mkdir -p "$SUB_OUT"
    
    # Skip if already processed
    if [ -f "$SUB_OUT/dti_FA.nii.gz" ]; then
        echo "  Already processed, skipping."
        continue
    fi
    
    # Step 1: Eddy current correction
    echo "  [1/4] Eddy correction..."
    eddy_correct "$DWI_NII" "$SUB_OUT/dwi_eddy.nii.gz" 0
    
    # Step 2: Brain extraction on mean b0
    echo "  [2/4] Brain extraction..."
    fslroi "$SUB_OUT/dwi_eddy.nii.gz" "$SUB_OUT/b0.nii.gz" 0 1
    bet "$SUB_OUT/b0.nii.gz" "$SUB_OUT/b0_brain" -m -f 0.3
    
    # Step 3: DTI fitting
    echo "  [3/4] DTIFIT..."
    dtifit \
        -k "$SUB_OUT/dwi_eddy.nii.gz" \
        -o "$SUB_OUT/dti" \
        -m "$SUB_OUT/b0_brain_mask.nii.gz" \
        -r "$BVEC" \
        -b "$BVAL"
    
    # Step 4: Copy FA map for TBSS
    echo "  [4/4] Preparing FA for TBSS..."
    cp "$SUB_OUT/dti_FA.nii.gz" "$OUT_ROOT/FA/${SID}_FA.nii.gz" 2>/dev/null
    
    echo "  Done: $SID"
done

# Create FA directory for TBSS
mkdir -p "$OUT_ROOT/FA"
for SID in "${SUBJECTS[@]}"; do
    if [ -f "$OUT_ROOT/$SID/dti_FA.nii.gz" ]; then
        cp "$OUT_ROOT/$SID/dti_FA.nii.gz" "$OUT_ROOT/FA/${SID}_FA.nii.gz"
    fi
done

echo ""
echo "=== DWI preprocessing complete ==="
echo "FA maps in: $OUT_ROOT/FA/"
echo ""
echo "Next: Run TBSS"
echo "  cd $OUT_ROOT/FA"
echo "  tbss_1_preproc *.nii.gz"
echo "  tbss_2_reg -T"
echo "  tbss_3_postreg -S"
echo "  tbss_4_prestats 0.2"
echo ""
echo "Then run randomise with design matrix for group stats:"
echo "  randomise -i all_FA_skeletonised -o tbss_results -m mean_FA_skeleton_mask -d design.mat -t design.con -n 5000 --T2"
