@echo off
cd C:\Users\Aditi\ds005613

for /d %%s in (sub-pp*) do (
    echo Fetching %%s...
    datalad get %%s\ses-01\func\%%s_ses-01_task-rest_run-001_bold.nii.gz
    datalad get %%s\ses-01\func\%%s_ses-01_task-rest_run-001_bold.json
    datalad get %%s\ses-01\func\%%s_ses-01_task-aliceloc_run-001_bold.nii.gz
    datalad get %%s\ses-01\func\%%s_ses-01_task-aliceloc_run-002_bold.nii.gz
    datalad get %%s\ses-01\func\%%s_ses-01_task-aliceloc_run-003_bold.nii.gz
    datalad get %%s\ses-01\func\%%s_ses-01_task-aliceloc_run-001_events.tsv
    datalad get %%s\ses-01\func\%%s_ses-01_task-aliceloc_run-002_events.tsv
    datalad get %%s\ses-01\func\%%s_ses-01_task-aliceloc_run-003_events.tsv
)

echo DONE