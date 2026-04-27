# In Python
import os
base = r'C:\Users\Aditi\ds005613'
subs = sorted([d for d in os.listdir(base) if d.startswith('sub-pp')])
count = 0
missing = []
for sub in subs:
    dwi = os.path.join(base, sub, 'ses-01', 'dwi', f'{sub}_ses-01_dwi.nii.gz')
    if os.path.exists(dwi) and os.path.getsize(dwi) > 1000000:
        count += 1
    else:
        missing.append(sub)
print(f"DWI complete: {count}/101")
print(f"Missing: {missing}")