import numpy as np
import pandas as pd
from pathlib import Path
from nilearn import image, masking
from nilearn.maskers import NiftiLabelsMasker, NiftiSpheresMasker
from nilearn.connectome import ConnectivityMeasure
from nilearn.image import clean_img, smooth_img, resample_to_img
import nibabel as nib
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ── PATHS ──────────────────────────────────────────────────────────────
base = Path(r'C:\Users\Aditi\ds005613')
subset_file = base / 'subset_50_participants.txt'
out_dir = base / 'derivatives' / 'nilearn_fc'
out_dir.mkdir(parents=True, exist_ok=True)

subs = [l.strip() for l in subset_file.read_text().splitlines() if l.strip()]
design = pd.read_csv(base / 'shared_design_matrix.csv')
design = design[design['participant_id'].isin(subs)].reset_index(drop=True)

print(f"Subjects: {len(subs)}")
print(f"Design matrix: {design.shape}")

# ── LANGUAGE NETWORK ROIs (Fedorenko et al. MNI coordinates) ──────────
# IFG, STG, angular gyrus, SMA — core language network
language_rois = {
    'IFG_L':  (-51, 22, 10),
    'STG_L':  (-56, -14, 4),
    'AngG_L': (-46, -62, 28),
    'SMA_L':  (-4, 4, 52),
    'IFG_R':  (51, 22, 10),
    'STG_R':  (56, -14, 4),
}

roi_names = list(language_rois.keys())
roi_coords = list(language_rois.values())

# ── PREPROCESSING PARAMETERS ──────────────────────────────────────────
TR = 2.0          # check your JSON sidecar to confirm
SMOOTHING = 6.0   # mm FWHM
HP_FREQ = 0.01    # high-pass filter Hz
LP_FREQ = 0.1     # low-pass filter Hz

# ── PER-SUBJECT PROCESSING ────────────────────────────────────────────
fc_matrices = []
valid_subs = []
failed_subs = []

masker = NiftiSpheresMasker(
    seeds=roi_coords,
    radius=8,           # 8mm sphere around each coordinate
    t_r=TR,
    high_pass=HP_FREQ,
    low_pass=LP_FREQ,
    smoothing_fwhm=SMOOTHING,
    standardize=True,
    detrend=True,
    verbose=0
)

for i, sub in enumerate(subs):
    print(f"[{i+1}/{len(subs)}] {sub}...")
    
    rest_path = base / sub / 'ses-01' / 'func' / \
                f'{sub}_ses-01_task-rest_run-001_bold.nii.gz'
    
    try:
        # Extract ROI timeseries
        # This handles smoothing, filtering, detrending, standardizing
        timeseries = masker.fit_transform(str(rest_path))
        # timeseries shape: (n_timepoints, n_rois)
        
        # Compute FC matrix (partial correlation for better specificity)
        conn_measure = ConnectivityMeasure(
            kind='correlation',
            standardize='zscore_sample'
        )
        fc_matrix = conn_measure.fit_transform([timeseries])[0]
        # fc_matrix shape: (n_rois, n_rois)
        
        fc_matrices.append(fc_matrix)
        valid_subs.append(sub)
        
        # Save individual FC matrix
        np.save(out_dir / f'{sub}_fc_matrix.npy', fc_matrix)
        print(f"  OK — FC matrix shape: {fc_matrix.shape}")
        
    except Exception as e:
        print(f"  FAILED: {e}")
        failed_subs.append(sub)

print(f"\nCompleted: {len(valid_subs)}/51")
print(f"Failed: {len(failed_subs)}: {failed_subs}")

# ── EXTRACT KEY FC VALUES FOR GLM ─────────────────────────────────────
# Primary outcome: mean language network connectivity
# = average of all pairwise correlations within language network
roi_idx = {name: i for i, name in enumerate(roi_names)}

fc_outcomes = []
for sub, fc in zip(valid_subs, fc_matrices):
    # Fisher-z transform for normality
    fc_z = np.arctanh(np.clip(fc, -0.999, 0.999))
    
    # Mean within-network connectivity (upper triangle)
    upper = fc_z[np.triu_indices(len(roi_names), k=1)]
    mean_fc = upper.mean()
    
    # Key pairwise connections (theoretically motivated)
    ifg_stg_l = fc_z[roi_idx['IFG_L'], roi_idx['STG_L']]
    ifg_stg_r = fc_z[roi_idx['IFG_R'], roi_idx['STG_R']]
    
    fc_outcomes.append({
        'participant_id': sub,
        'mean_lang_fc': mean_fc,
        'IFG_STG_left': ifg_stg_l,
        'IFG_STG_right': ifg_stg_r,
    })

fc_df = pd.DataFrame(fc_outcomes)
fc_df.to_csv(out_dir / 'fc_outcomes.csv', index=False)
print(f"\nFC outcomes saved: {out_dir / 'fc_outcomes.csv'}")
print(fc_df.describe())