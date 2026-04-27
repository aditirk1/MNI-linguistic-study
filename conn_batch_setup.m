%% CONN Batch Setup — NEBULA101 Resting-State FC Analysis
% Stratified n=51 subjects | TR=2s | 72 slices
% Output: subject-level language network FC values for second-level GLM
%
% Prerequisites: SPM12 + CONN toolbox on MATLAB path
% Run from: C:\Users\Aditi\ds005613

clear; clc;

%% Paths
bids_root = 'C:\Users\Aditi\ds005613';
out_dir   = 'C:\Users\Aditi\ds005613\derivatives\conn_restfc';
if ~exist(out_dir,'dir'), mkdir(out_dir); end

% Ensure SPM + CONN are on path
addpath('C:\Users\Aditi\spm');
addpath(genpath('C:\Users\Aditi\spm\toolbox\conn'));

%% Load subject list
fid = fopen(fullfile(bids_root, 'subset_50_participants.txt'));
subs = textscan(fid, '%s'); subs = subs{1};
fclose(fid);
nsub = numel(subs);
fprintf('Subjects: %d\n', nsub);

%% Acquisition parameters
TR = 2;       % seconds
nslices = 72;

%% Build CONN batch structure
batch = [];
batch.filename = fullfile(out_dir, 'conn_nebula101_restfc.mat');

% Setup
batch.Setup.isnew = 1;
batch.Setup.nsubjects = nsub;
batch.Setup.RT = TR;
batch.Setup.acquisitiontype = 1; % continuous
batch.Setup.analyses = [1,2]; % ROI-to-ROI and seed-to-voxel

% Structural and functional files
for i = 1:nsub
    sid = subs{i};
    
    % T1w structural
    batch.Setup.structurals{i} = fullfile(bids_root, sid, 'ses-01', 'anat', ...
        [sid '_ses-01_rec-defaced_T1w.nii.gz']);
    
    % Resting-state functional
    batch.Setup.functionals{i}{1} = fullfile(bids_root, sid, 'ses-01', 'func', ...
        [sid '_ses-01_task-rest_run-001_bold.nii.gz']);
end

% Conditions (rest = single block covering entire scan)
batch.Setup.conditions.names = {'rest'};
for i = 1:nsub
    batch.Setup.conditions.onsets{1}{i}{1} = 0;
    batch.Setup.conditions.durations{1}{i}{1} = Inf;
end

%% Preprocessing
batch.Setup.preprocessing.steps = {'default_mni'};
batch.Setup.preprocessing.sliceorder = 'interleaved (Siemens)';
batch.Setup.preprocessing.art_thresholds = [3, 0.5];
batch.Setup.done = 1;
batch.Setup.overwrite = 'Yes';

%% Denoising
batch.Denoising.filter = [0.008, 0.09]; % bandpass
batch.Denoising.done = 1;
batch.Denoising.overwrite = 'Yes';

%% First-level analysis
batch.Analysis.done = 1;
batch.Analysis.overwrite = 'Yes';
batch.Analysis.measure = 1; % bivariate correlation
batch.Analysis.type = 3;    % ROI-to-ROI
batch.Analysis.analysis_name = 'SBC_01';
batch.Analysis.sources = {'networks'};

%% Save and optionally run
save(fullfile(out_dir, 'conn_batch_struct.mat'), 'batch');
fprintf('CONN batch saved to: %s\n', out_dir);
fprintf('Running conn_batch now...\n');
conn_batch(batch);
fprintf('CONN batch completed.\n');
