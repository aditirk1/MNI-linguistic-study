#!/usr/bin/env bash
#
# TBSS post-randomise: inspect TFCE-corrected maps, record counts/thresholds, optional figures, archive.
#
# Run in Ubuntu (WSL):
#   chmod +x /mnt/c/Users/Aditi/ds005613/tbss_inspect_and_archive.sh   # may fail on /mnt/c — use: bash ...
#   bash /mnt/c/Users/Aditi/ds005613/tbss_inspect_and_archive.sh
#   FSLEYES_GUI=1 bash ...    # open FSLeyes after summary (default: skip GUI)
#
# corrp maps: values are (1 - p) FWE-corrected under TFCE; convention: > 0.95 ~= p < 0.05 FWE.

set -euo pipefail

# ---- paths (edit if your username or drive letter differs) ----
BASE_WIN="C:\\Users\\Aditi\\ds005613"
STATS="/mnt/c/Users/Aditi/ds005613/derivatives/dwi_processed/tbss/stats"
ARCHIVE_DIR="/mnt/c/Users/Aditi/ds005613/derivatives/tbss_randomise_archive_$(date +%Y%m%d_%H%M%S)"
REPORT_TXT="/mnt/c/Users/Aditi/ds005613/derivatives/tbss_inspection_report.txt"

# Optional: launch fsleyes after text summary (set FSLEYES_GUI=1)
FSLEYES_GUI="${FSLEYES_GUI:-0}"

# Threshold for "significant" FWE p<0.05 in corrp space
CORRP_THRESH=0.95

# ---- FSL environment ----
if [[ -f /etc/fsl/fsl.sh ]]; then
  # shellcheck source=/dev/null
  source /etc/fsl/fsl.sh
elif [[ -f "${HOME}/fsl/etc/fslconf/fsl.sh" ]]; then
  # shellcheck source=/dev/null
  source "${HOME}/fsl/etc/fslconf/fsl.sh"
elif [[ -f "${FSLDIR}/etc/fslconf/fsl.sh" ]]; then
  # shellcheck source=/dev/null
  source "${FSLDIR}/etc/fslconf/fsl.sh"
else
  echo "ERROR: Could not find fsl.sh. Install FSL or set FSLDIR and source fsl.sh manually." >&2
  exit 1
fi

cd "$STATS" || exit 1

echo "=== TBSS stats directory ==="
echo "$STATS"
echo ""
echo "=== Files ==="
ls -la mean_FA_skeleton*.nii.gz all_FA_skeletonised.nii.gz design.mat design.con tbss_results_*.nii.gz randomise.log 2>/dev/null || true
echo ""

{
  echo "TBSS randomise inspection report"
  echo "Generated: $(date -Iseconds)"
  echo "Working directory: $STATS"
  echo "corrp threshold (FWE p<0.05 convention): ${CORRP_THRESH}"
  echo ""

  echo "=== fslstats: skeleton mask voxels (nonzero in mask) ==="
  fslstats mean_FA_skeleton_mask -V | awk '{print "voxels_in_mask:", $1, "  non-zero vol count check"}'
  echo ""

  for c in 1 2 3 4; do
    tst="tbss_results_tstat${c}"
    cor="tbss_results_tfce_corrp_tstat${c}"
    echo "--- Contrast ${c} ---"
    echo "  Raw t-stat (masked by skeleton):"
    fslstats "${tst}" -k mean_FA_skeleton_mask -R | awk '{print "    min max:", $1, $2}'
    echo "  TFCE 1-p (corrp), masked:"
    fslstats "${cor}" -k mean_FA_skeleton_mask -R | awk '{print "    min max:", $1, $2}'
    echo "  Voxels with corrp > ${CORRP_THRESH} (within mask):"
    # Count voxels above threshold: binarise then count voxels in mask * bin
    fslmaths "${cor}" -thr "${CORRP_THRESH}" -bin -mul mean_FA_skeleton_mask "${cor}_thr_tmp" -odt float
    fslstats "${cor}_thr_tmp" -V | awk -v t="$CORRP_THRESH" '{print "    count:", $1, "  (corrp > " t ")"}'
    rm -f "${cor}_thr_tmp.nii.gz" 2>/dev/null || true
    echo ""
  done

  echo "=== Optional cluster (only runs if any contrast has voxels above threshold) ==="
} | tee "$REPORT_TXT"

ANY_SIG=0
for c in 1 2 3 4; do
  cor="tbss_results_tfce_corrp_tstat${c}"
  fslmaths "${cor}" -thr "${CORRP_THRESH}" -bin -mul mean_FA_skeleton_mask "${cor}_sigchk" -odt float
  N=$(fslstats "${cor}_sigchk" -V | awk '{print int($1)}')
  rm -f "${cor}_sigchk.nii.gz" 2>/dev/null || true
  if [[ "$N" -gt 0 ]]; then
    ANY_SIG=1
  fi
done

if [[ "$ANY_SIG" -eq 1 ]]; then
  {
    echo "Found voxels with corrp > ${CORRP_THRESH}; running cluster (per contrast)."
    for c in 1 2 3 4; do
      cor="tbss_results_tfce_corrp_tstat${c}"
      fslmaths "${cor}" -thr "${CORRP_THRESH}" -bin -mul mean_FA_skeleton_mask "${cor}_sig" -odt float
      N=$(fslstats "${cor}_sig" -V | awk '{print int($1)}')
      rm -f "${cor}_sig.nii.gz" 2>/dev/null || true
      echo "Contrast ${c}: suprathreshold voxels = ${N}"
      if [[ "${N}" -gt 0 ]]; then
        # FSL 6.x: cluster -i ... -t ...; older: cluster --in= ...
        if cluster -i "${cor}" -t "${CORRP_THRESH}" 2>/dev/null | tee "cluster_table_contrast${c}.txt"; then
          :
        else
          cluster --in="${cor}" --thresh="${CORRP_THRESH}" \
            | tee "cluster_table_contrast${c}.txt" || true
        fi
      fi
    done
  } | tee -a "$REPORT_TXT"
else
  {
    echo "No voxels with corrp > ${CORRP_THRESH} in any contrast (within skeleton mask)."
    echo "Skipping cluster -- no meaningful suprathreshold clusters for publication."
  } | tee -a "$REPORT_TXT"
fi

# DrvFS (/mnt/c): `cp -a` often errors on "preserving times" and breaks set -e.
archive_copy() {
  cp -f "$1" "$2"
}

# ---- Archive reproducibility bundle ----
mkdir -p "$ARCHIVE_DIR"
for f in \
  design.mat design.con \
  mean_FA_skeleton_mask.nii.gz \
  mean_FA_skeleton.nii.gz \
  all_FA_skeletonised.nii.gz \
  tbss_results_tstat1.nii.gz \
  tbss_results_tstat2.nii.gz \
  tbss_results_tstat3.nii.gz \
  tbss_results_tstat4.nii.gz \
  tbss_results_tfce_corrp_tstat1.nii.gz \
  tbss_results_tfce_corrp_tstat2.nii.gz \
  tbss_results_tfce_corrp_tstat3.nii.gz \
  tbss_results_tfce_corrp_tstat4.nii.gz
do
  if [[ -f "$f" ]]; then
    archive_copy "$f" "$ARCHIVE_DIR/"
  fi
done
# randomise log: .../derivatives/randomise_log.txt (from stats: ../../.. = derivatives/)
for cand in \
  ../../../randomise_log.txt \
  randomise_log.txt \
  /mnt/c/Users/Aditi/ds005613/derivatives/randomise_log.txt
do
  if [[ -f "$cand" ]]; then
    archive_copy "$cand" "$ARCHIVE_DIR/randomise_log.txt"
    break
  fi
done
archive_copy "$REPORT_TXT" "$ARCHIVE_DIR/" 2>/dev/null || true
echo "" | tee -a "$REPORT_TXT"
echo "Archive copied to: $ARCHIVE_DIR" | tee -a "$REPORT_TXT"
ls -la "$ARCHIVE_DIR" | tee -a "$REPORT_TXT"

# ---- FSLeyes (optional) ----
if [[ "${FSLEYES_GUI}" == "1" ]]; then
  echo ""
  echo "Launching FSLeyes (close window when done)..."
  # Underlay: mean FA skeleton; overlay corrp maps one at a time — user can add/remove in GUI.
  fsleyes mean_FA_skeleton.nii.gz \
    tbss_results_tfce_corrp_tstat1.nii.gz -cm red-yellow -dr 0.95 1 &
else
  echo ""
  echo "FSLeyes not started (set FSLEYES_GUI=1 to open)."
  echo "Manual overlay example:"
  echo "  cd $STATS"
  echo "  fsleyes mean_FA_skeleton.nii.gz tbss_results_tfce_corrp_tstat1.nii.gz -cm red-yellow -dr 0.95 1"
fi

echo ""
echo "Done. Read summary: $REPORT_TXT"
echo "Windows path hints: $BASE_WIN\\\\derivatives\\\\tbss_inspection_report.txt"
