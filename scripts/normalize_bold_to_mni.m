function normalize_bold_to_mni()
% SPM12/25 normalize all 51 resting BOLDs to MNI using each subject's T1.
%
% Steps per subject:
%   1) Segment T1                       -> y_T1.nii (deformation field)
%   2) Coregister mean BOLD -> T1       (header update only)
%   3) Normalise: Write BOLD with y_T1  -> w*.nii (in MNI)
%   4) Smooth 6 mm                      -> sw*.nii
%
% Inputs assumed present:
%   sub-XXXX/ses-01/anat/sub-XXXX_ses-01_*T1w.nii   (uncompressed)
%   sub-XXXX/ses-01/func/sub-XXXX_ses-01_task-rest_run-001_bold.nii
%   sub-XXXX/ses-01/func/rp_*task-rest*.txt
%
% Output written next to each BOLD file (sw*.nii is what FC will use).

base = 'C:\Users\Aditi\ds005613';
fid  = fopen(fullfile(base,'subset_50_participants.txt'));
S    = textscan(fid,'%s'); fclose(fid);
subs = S{1};
subs = subs(~cellfun('isempty', strtrim(subs)));

spm('defaults','fmri');
spm_jobman('initcfg');

tpm = fullfile(spm('dir'),'tpm','TPM.nii');
if ~exist(tpm,'file'); error('TPM not found at %s', tpm); end

logf = fopen(fullfile(base,'normalize_bold_log.txt'),'a');
fprintf(logf, '\n--- Run started %s ---\n', datestr(now));

for i = 1:numel(subs)
    sub = strtrim(subs{i});
    fprintf('\n[%d/%d] %s starting %s\n', i, numel(subs), sub, datestr(now));
    fprintf(logf,'\n[%d/%d] %s starting %s\n', i, numel(subs), sub, datestr(now));

    anat = fullfile(base, sub, 'ses-01', 'anat');
    func = fullfile(base, sub, 'ses-01', 'func');

    t1 = '';
    d = dir(fullfile(anat, [sub '_ses-01_*T1w.nii']));
    if isempty(d)
        fprintf(logf,'  SKIP no T1 .nii\n'); continue
    end
    t1 = fullfile(anat, d(1).name);

    bold = fullfile(func, [sub '_ses-01_task-rest_run-001_bold.nii']);
    if ~exist(bold,'file')
        fprintf(logf,'  SKIP no bold .nii\n'); continue
    end

    % If sw* already exists, skip
    [bp,bn,~] = fileparts(bold);
    sw_check = fullfile(bp, ['sw' bn '.nii']);
    if exist(sw_check,'file')
        fprintf('  already done -> sw%s exists, skipping\n', bn);
        fprintf(logf,'  already done -> sw exists, skipping\n');
        continue
    end

    % Build cell array of all volumes for the BOLD 4D
    V = spm_vol(bold);
    nVol = numel(V);
    bold_frames = cell(nVol,1);
    for v = 1:nVol
        bold_frames{v} = sprintf('%s,%d', bold, v);
    end
    mean_bold = fullfile(func, ['mean' bn '.nii']);  % SPM realign earlier should have written this

    % If no meanbold, create one quickly
    if ~exist(mean_bold,'file')
        Vs = spm_vol(bold);
        Y = zeros(Vs(1).dim);
        for v = 1:numel(Vs)
            Y = Y + spm_read_vols(Vs(v));
        end
        Y = Y / numel(Vs);
        Vm = Vs(1);
        Vm.fname = mean_bold;
        Vm.dt = [16 0];
        spm_write_vol(Vm, Y);
    end

    % --- 1) Segment T1
    matlabbatch = {};
    matlabbatch{1}.spm.spatial.preproc.channel.vols     = {[t1 ',1']};
    matlabbatch{1}.spm.spatial.preproc.channel.biasreg  = 0.001;
    matlabbatch{1}.spm.spatial.preproc.channel.biasfwhm = 60;
    matlabbatch{1}.spm.spatial.preproc.channel.write    = [0 0];
    ngaus_per_tissue = [1 1 2 3 4 2];   % SPM25 default; MUST be scalar per tissue
    for k = 1:6
        matlabbatch{1}.spm.spatial.preproc.tissue(k).tpm    = {[tpm ',' num2str(k)]};
        matlabbatch{1}.spm.spatial.preproc.tissue(k).ngaus  = ngaus_per_tissue(k);
        matlabbatch{1}.spm.spatial.preproc.tissue(k).native = [0 0];
        matlabbatch{1}.spm.spatial.preproc.tissue(k).warped = [0 0];
    end
    matlabbatch{1}.spm.spatial.preproc.warp.mrf      = 1;
    matlabbatch{1}.spm.spatial.preproc.warp.cleanup  = 1;
    matlabbatch{1}.spm.spatial.preproc.warp.reg      = [0 0.001 0.5 0.05 0.2];
    matlabbatch{1}.spm.spatial.preproc.warp.affreg   = 'mni';
    matlabbatch{1}.spm.spatial.preproc.warp.fwhm     = 0;
    matlabbatch{1}.spm.spatial.preproc.warp.samp     = 3;
    matlabbatch{1}.spm.spatial.preproc.warp.write    = [0 1];   % forward def

    % --- 2) Coregister: Estimate (mean BOLD -> T1)
    matlabbatch{2}.spm.spatial.coreg.estimate.ref    = {[t1 ',1']};
    matlabbatch{2}.spm.spatial.coreg.estimate.source = {[mean_bold ',1']};
    matlabbatch{2}.spm.spatial.coreg.estimate.other  = bold_frames;
    matlabbatch{2}.spm.spatial.coreg.estimate.eoptions.cost_fun = 'nmi';
    matlabbatch{2}.spm.spatial.coreg.estimate.eoptions.sep      = [4 2];
    matlabbatch{2}.spm.spatial.coreg.estimate.eoptions.tol      = ...
        [0.02 0.02 0.02 0.001 0.001 0.001 0.01 0.01 0.01 0.001 0.001 0.001];
    matlabbatch{2}.spm.spatial.coreg.estimate.eoptions.fwhm     = [7 7];

    % --- 3) Normalise: Write BOLD with y_T1
    [tp,tn,~] = fileparts(t1);
    y_field   = fullfile(tp, ['y_' tn '.nii']);
    matlabbatch{3}.spm.spatial.normalise.write.subj.def      = {y_field};
    matlabbatch{3}.spm.spatial.normalise.write.subj.resample = bold_frames;
    matlabbatch{3}.spm.spatial.normalise.write.woptions.bb     = [-78 -112 -70; 78 76 85];
    matlabbatch{3}.spm.spatial.normalise.write.woptions.vox    = [3 3 3];
    matlabbatch{3}.spm.spatial.normalise.write.woptions.interp = 4;
    matlabbatch{3}.spm.spatial.normalise.write.woptions.prefix = 'w';

    % --- 4) Smooth 6 mm
    wfiles = cell(nVol,1);
    for v = 1:nVol
        wfiles{v} = sprintf('%s,%d', fullfile(bp, ['w' bn '.nii']), v);
    end
    matlabbatch{4}.spm.spatial.smooth.data    = wfiles;
    matlabbatch{4}.spm.spatial.smooth.fwhm    = [6 6 6];
    matlabbatch{4}.spm.spatial.smooth.dtype   = 0;
    matlabbatch{4}.spm.spatial.smooth.im      = 0;
    matlabbatch{4}.spm.spatial.smooth.prefix  = 's';

    try
        t0 = tic;
        spm_jobman('run', matlabbatch);
        dt = toc(t0);
        fprintf('  OK  %.0f s\n', dt);
        fprintf(logf,'  OK %.0f s\n', dt);
    catch ME
        fprintf('  FAIL: %s\n', ME.message);
        fprintf(logf,'  FAIL: %s\n', ME.message);
    end
end

fprintf(logf,'--- Run finished %s ---\n', datestr(now));
fclose(logf);
disp('Done. swBOLD files written next to each BOLD.');
end
