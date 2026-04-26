from pathlib import Path
import subprocess
root = Path(r'C:\Users\Aditi\ds005613')
subs = sorted([p.name for p in root.glob('sub-pp*') if p.is_dir()])
out = subprocess.check_output(['git','annex','find','--in=here'], text=True, encoding='utf-8', errors='ignore')
have = set(x.strip().replace('\\','/') for x in out.splitlines() if x.strip())
good = []
for s in subs:
    req = [
        f'{s}/ses-01/anat/{s}_ses-01_rec-defaced_T1w.nii.gz',
        f'{s}/ses-01/func/{s}_ses-01_task-rest_run-001_bold.nii.gz',
        f'{s}/ses-01/func/{s}_ses-01_task-aliceloc_run-001_bold.nii.gz',
        f'{s}/ses-01/func/{s}_ses-01_task-aliceloc_run-002_bold.nii.gz',
        f'{s}/ses-01/func/{s}_ses-01_task-aliceloc_run-003_bold.nii.gz',
    ]
    if all(r in have for r in req):
        good.append(s.replace('sub-',''))
batch = good[:10]
Path('participants_batch1.txt').write_text('\n'.join(batch) + '\n')
print('Batch1 subjects:', batch)