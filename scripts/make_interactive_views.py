"""
Interactive HTML brain views (open in any browser, rotate, hover for coords).

Outputs into derivatives/figures/:
  rois_interactive.html        - rotate the 6 ROIs on a brain
  connectome_interactive.html  - rotate the FC connectome
  t1_view.html                 - one subject's T1w in a 3-pane viewer
"""

from pathlib import Path
import glob
import numpy as np
from nilearn import plotting

base = Path(r"C:\Users\Aditi\ds005613")
fc_dir = base / "derivatives" / "nilearn_fc"
out = base / "derivatives" / "figures"
out.mkdir(parents=True, exist_ok=True)

roi_coords = [
    (-51, 22, 10), (-56, -14, 4), (-46, -62, 28),
    (-4, 4, 52),   (51, 22, 10),  (56, -14, 4),
]
roi_labels = ["IFG_L", "STG_L", "AngG_L", "SMA_L", "IFG_R", "STG_R"]

# 1) Interactive ROIs
v = plotting.view_markers(
    roi_coords, marker_labels=roi_labels, marker_size=10,
)
v.save_as_html(str(out / "rois_interactive.html"))
print("[OK] rois_interactive.html")

# 2) Interactive connectome
mats = []
for f in sorted(glob.glob(str(fc_dir / "sub-*_fc_matrix.npy"))):
    m = np.load(f)
    if m.shape == (6, 6):
        mats.append(m)
if mats:
    M = np.mean(mats, axis=0)
    v = plotting.view_connectome(
        M, roi_coords, edge_threshold="60%",
        node_size=8.0,
    )
    v.save_as_html(str(out / "connectome_interactive.html"))
    print(f"[OK] connectome_interactive.html (N={len(mats)})")
else:
    print("[skip] no FC matrices found locally for connectome")

# 3) Interactive T1 viewer for one subject (uses first T1 we find)
t1s = list(base.glob("sub-pp*/ses-01/anat/*T1w.nii.gz"))
real_t1 = next((p for p in t1s if p.stat().st_size > 1_000_000), None)
if real_t1:
    v = plotting.view_img(str(real_t1), bg_img=None,
                          threshold=0, title=real_t1.parent.parent.parent.name)
    v.save_as_html(str(out / "t1_view.html"))
    print(f"[OK] t1_view.html  ({real_t1.name})")
else:
    print("[skip] no real T1 found locally")

print("\nOpen the .html files in your browser:")
print(out)
