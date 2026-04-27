%% Alice Localizer First-Level GLM — SPM Batch
% Defines individual language network maps per subject
% Contrast: intact speech > degraded speech (language > control)
%
% Task conditions from events.tsv:
%   intact         — native language intact speech
%   degraded       — native language degraded (acoustic control)
%   foreign        — foreign language intact
%   foreignDegraded — foreign language degraded
%   fix            — fixation baseline
%
% Key contrast for language network: (intact + foreign) > (degraded + foreignDegraded)
% This isolates linguistic processing from acoustic processing

clear; clc;

%% Paths
bids_root = 'C:\Users\Aditi\ds005613';
out_root  = 'C:\Users\Aditi\ds005613\derivatives\alice_localizer_glm';
if ~exist(out_root,'dir'), mkdir(out_root); end

%% Parameters
TR = 2;
nruns = 3;

%% Load subject list
fid = fopen(fullfile(bids_root, 'subset_50_participants.txt'));
subs = textscan(fid, '%s'); subs = subs{1};
fclose(fid);
nsub = numel(subs);

%% Loop over subjects
for s = 1:nsub
    sid = subs{s};
    fprintf('\n=== [%d/%d] %s ===\n', s, nsub, sid);
    
    sub_out = fullfile(out_root, sid);
    if ~exist(sub_out,'dir'), mkdir(sub_out); end
    
    % SPM job structure
    matlabbatch = {};
    matlabbatch{1}.spm.stats.fmri_spec.dir = {sub_out};
    matlabbatch{1}.spm.stats.fmri_spec.timing.units = 'secs';
    matlabbatch{1}.spm.stats.fmri_spec.timing.RT = TR;
    matlabbatch{1}.spm.stats.fmri_spec.timing.fmri_t = 72;
    matlabbatch{1}.spm.stats.fmri_spec.timing.fmri_t0 = 36;
    
    for r = 1:nruns
        run_str = sprintf('%03d', r);
        
        % Functional file (preprocessed — update path after preprocessing)
        func_file = fullfile(bids_root, sid, 'ses-01', 'func', ...
            [sid '_ses-01_task-aliceloc_run-' run_str '_bold.nii.gz']);
        
        matlabbatch{1}.spm.stats.fmri_spec.sess(r).scans = {func_file};
        matlabbatch{1}.spm.stats.fmri_spec.sess(r).multi = {''};
        matlabbatch{1}.spm.stats.fmri_spec.sess(r).hpf = 128;
        
        % Load events
        events_file = fullfile(bids_root, sid, 'ses-01', 'func', ...
            [sid '_ses-01_task-aliceloc_run-' run_str '_events.tsv']);
        events = readtable(events_file, 'FileType', 'text', 'Delimiter', '\t');
        
        % Define conditions
        cond_names = {'intact', 'degraded', 'foreign', 'foreignDegraded'};
        for c = 1:numel(cond_names)
            idx = strcmp(events.trial_type, cond_names{c});
            matlabbatch{1}.spm.stats.fmri_spec.sess(r).cond(c).name = cond_names{c};
            matlabbatch{1}.spm.stats.fmri_spec.sess(r).cond(c).onset = events.onset(idx);
            matlabbatch{1}.spm.stats.fmri_spec.sess(r).cond(c).duration = events.duration(idx);
            matlabbatch{1}.spm.stats.fmri_spec.sess(r).cond(c).tmod = 0;
            matlabbatch{1}.spm.stats.fmri_spec.sess(r).cond(c).pmod = struct('name',{},'param',{},'poly',{});
            matlabbatch{1}.spm.stats.fmri_spec.sess(r).cond(c).orth = 1;
        end
    end
    
    % Model estimation
    matlabbatch{2}.spm.stats.fmri_est.spmmat = {fullfile(sub_out, 'SPM.mat')};
    matlabbatch{2}.spm.stats.fmri_est.write_residuals = 0;
    matlabbatch{2}.spm.stats.fmri_est.method.Classical = 1;
    
    % Contrast: Language > Control
    % (intact + foreign) > (degraded + foreignDegraded)
    % Conditions order: intact, degraded, foreign, foreignDegraded
    % Weights per run: [1 -1 1 -1], replicated across 3 runs
    con_vec = repmat([1 -1 1 -1], 1, nruns);
    
    matlabbatch{3}.spm.stats.con.spmmat = {fullfile(sub_out, 'SPM.mat')};
    matlabbatch{3}.spm.stats.con.consess{1}.tcon.name = 'Language_gt_Control';
    matlabbatch{3}.spm.stats.con.consess{1}.tcon.weights = con_vec;
    matlabbatch{3}.spm.stats.con.consess{1}.tcon.sessrep = 'none';
    matlabbatch{3}.spm.stats.con.delete = 1;
    
    % Save batch for this subject
    save(fullfile(sub_out, 'alice_glm_batch.mat'), 'matlabbatch');
    
    % Uncomment to run:
    % spm_jobman('run', matlabbatch);
end

fprintf('\n\nAll %d subject batches saved to: %s\n', nsub, out_root);
fprintf('Run with: spm_jobman(''run'', matlabbatch)\n');
fprintf('Output: spmT_0001.nii per subject = individual language network map\n');
