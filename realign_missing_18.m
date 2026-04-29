% realign_missing_18.m
% Runs SPM realign (estimate only) on the 18 subjects that are missing
% motion parameter files (rp_*.txt). Does NOT modify the BOLD images —
% only estimates motion and writes the rp_*.txt file per subject.
%
% Run in MATLAB with SPM on path:
%   addpath('C:\Users\Aditi\spm');
%   realign_missing_18

addpath('C:\Users\Aditi\spm');
spm('defaults', 'fmri');
spm_jobman('initcfg');

base = 'C:\Users\Aditi\ds005613';

missing_subs = {
    'sub-pp048', 'sub-pp031', 'sub-pp053', 'sub-pp110', ...
    'sub-pp026', 'sub-pp129', 'sub-pp036', 'sub-pp083', ...
    'sub-pp027', 'sub-pp005', 'sub-pp091', 'sub-pp077', ...
    'sub-pp046', 'sub-pp012', 'sub-pp127', 'sub-pp044', ...
    'sub-pp003', 'sub-pp133'
};

fprintf('SPM realign (estimate only) for %d subjects\n', length(missing_subs));
fprintf('This writes rp_*.txt without modifying the BOLD images.\n\n');

for i = 1:length(missing_subs)
    sub = missing_subs{i};
    bold_nii = fullfile(base, sub, 'ses-01', 'func', ...
        [sub '_ses-01_task-rest_run-001_bold.nii']);

    if ~isfile(bold_nii)
        fprintf('[%d/%d] %s SKIP: .nii not found\n', i, length(missing_subs), sub);
        continue;
    end

    fprintf('[%d/%d] %s starting... ', i, length(missing_subs), sub);
    tic;

    % Get number of volumes from the header
    V = spm_vol(bold_nii);
    nvols = length(V);

    % Build the file list: each volume as 'path,frame'
    scans = cell(nvols, 1);
    for v = 1:nvols
        scans{v} = sprintf('%s,%d', bold_nii, v);
    end

    % SPM realign: estimate only (no reslice)
    matlabbatch = {};
    matlabbatch{1}.spm.spatial.realign.estimate.data = {scans};
    matlabbatch{1}.spm.spatial.realign.estimate.eoptions.quality = 0.9;
    matlabbatch{1}.spm.spatial.realign.estimate.eoptions.sep = 4;
    matlabbatch{1}.spm.spatial.realign.estimate.eoptions.fwhm = 5;
    matlabbatch{1}.spm.spatial.realign.estimate.eoptions.rtm = 1;
    matlabbatch{1}.spm.spatial.realign.estimate.eoptions.interp = 2;
    matlabbatch{1}.spm.spatial.realign.estimate.eoptions.wrap = [0 0 0];
    matlabbatch{1}.spm.spatial.realign.estimate.eoptions.weight = '';

    spm_jobman('run', matlabbatch);

    elapsed = toc;

    % Verify rp file was created
    rp_file = fullfile(base, sub, 'ses-01', 'func', ...
        ['rp_' sub '_ses-01_task-rest_run-001_bold.txt']);
    if isfile(rp_file)
        fprintf('OK (%.0fs, %d vols)\n', elapsed, nvols);
    else
        fprintf('WARNING: rp file not created!\n');
    end
end

fprintf('\nDone. Check rp_*.txt files in each subject''s func folder.\n');
