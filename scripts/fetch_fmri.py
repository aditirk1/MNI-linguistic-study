import subprocess
from pathlib import Path

root = Path(r"C:\Users\Aditi\ds005613")

out = subprocess.check_output(
    ["git", "annex", "find", "--in=here"],
    text=True, encoding="utf-8", errors="ignore"
)
have = set(line.strip().replace("\\", "/") for line in out.splitlines() if line.strip())

subs = sorted([p.name for p in root.glob("sub-pp*") if p.is_dir()])

complete, missing = [], []
for s in subs:
    req = [
        f"{s}/ses-01/func/{s}_ses-01_task-rest_run-001_bold.nii.gz",
        f"{s}/ses-01/func/{s}_ses-01_task-aliceloc_run-001_bold.nii.gz",
        f"{s}/ses-01/func/{s}_ses-01_task-aliceloc_run-002_bold.nii.gz",
        f"{s}/ses-01/func/{s}_ses-01_task-aliceloc_run-003_bold.nii.gz",
    ]
    if all(r in have for r in req):
        complete.append(s)
    else:
        missing.append(s)

print(f"Fully complete (annex local): {len(complete)}/{len(subs)}")
print("Missing:", missing)