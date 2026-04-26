import os
import subprocess

base = r'C:\Users\Aditi\ds005613'
subs = sorted([d for d in os.listdir(base) if d.startswith('sub-pp')])
print(f"Found {len(subs)} subjects: {subs[:3]}...")

failed = []
success = []

for i, sub in enumerate(subs):
    print(f"\n[{i+1}/{len(subs)}] Fetching {sub}...")
    
    files = [
        f"{sub}/ses-01/func/{sub}_ses-01_task-rest_run-001_bold.nii.gz",
        f"{sub}/ses-01/func/{sub}_ses-01_task-rest_run-001_bold.json",
        f"{sub}/ses-01/func/{sub}_ses-01_task-alicelocal_run-001_bold.nii.gz",
        f"{sub}/ses-01/func/{sub}_ses-01_task-alicelocal_run-002_bold.nii.gz",
        f"{sub}/ses-01/func/{sub}_ses-01_task-alicelocal_run-003_bold.nii.gz",
        f"{sub}/ses-01/func/{sub}_ses-01_task-alicelocal_run-001_events.tsv",
        f"{sub}/ses-01/func/{sub}_ses-01_task-alicelocal_run-002_events.tsv",
        f"{sub}/ses-01/func/{sub}_ses-01_task-alicelocal_run-003_events.tsv",
    ]
    
    for f in files:
        full_path = os.path.join(base, f)
        
        # Skip if already fetched (file exists and is >1MB)
        if os.path.exists(full_path) and os.path.getsize(full_path) > 100000:
            print(f"  SKIP (already fetched): {os.path.basename(f)}")
            continue
            
        result = subprocess.run(
            ['datalad', 'get', f.replace('/', os.sep)],
            cwd=base,
            capture_output=True,
            text=True
        )
        
        if 'ok' in result.stdout.lower():
            print(f"  OK: {os.path.basename(f)}")
            success.append(f)
        elif 'impossible' in result.stdout.lower() or 'error' in result.stdout.lower():
            print(f"  FAILED: {os.path.basename(f)}")
            print(f"    {result.stdout.strip()}")
            failed.append(f)
        else:
            print(f"  UNKNOWN: {result.stdout.strip()}")

# Final report
print(f"\n{'='*50}")
print(f"FETCH COMPLETE")
print(f"Successful: {len(success)}")
print(f"Failed: {len(failed)}")
if failed:
    print("Failed files:")
    for f in failed:
        print(f"  {f}")