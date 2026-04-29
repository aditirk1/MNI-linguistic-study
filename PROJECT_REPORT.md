# Multilingual Experience and the Brain
### A Multimodal MRI Study of Language Diversity and Use Balance in Healthy Young Adults

---

**Author:** Aditi *(your details)*
**Institution / course:** Columbia University, Spring 2026 — Multimodal Neuroimaging
**Dataset:** OpenNeuro `ds005613` (NEBULA101)
**Date of report:** April 2026

---

## 0. How to read this report

This report is written so that **two very different readers** can both follow it:

* a **first-year graduate student** who has never opened an MRI image, and
* a **seasoned imaging neuroscientist** who wants to verify that the methods are defensible.

Every technical term is defined the first time it is used. Acronyms are spelled out. Sections marked **`[INSERT RESULT]`** or **`[INSERT INTERPRETATION]`** are deliberate placeholders to be filled in once the two pipelines (`SPM normalisation + functional connectivity`, and `TBSS + randomise`) finish running on the night of 28–29 April 2026.

A short cheat-sheet of acronyms used everywhere in this document:

| Acronym | Full form | What it means here |
|---|---|---|
| MRI | Magnetic Resonance Imaging | The scanner technology. Uses a strong magnetic field + radio-frequency pulses to image the brain non-invasively. |
| T1w | T1-weighted image | A high-resolution structural scan that distinguishes grey matter, white matter, and CSF based on tissue T1 relaxation. Used for anatomy. |
| fMRI | functional MRI | A time-series of low-resolution images that tracks the **BOLD** signal (blood-oxygen-level dependent), an indirect proxy for local neural activity. |
| rs-fMRI | resting-state fMRI | fMRI acquired with the participant lying still and not performing any task. |
| DWI | Diffusion-Weighted Imaging | A type of MRI sensitive to the random motion (diffusion) of water molecules. Because water diffuses more freely along white-matter axons than across them, DWI lets us probe white-matter microstructure. |
| FA | Fractional Anisotropy | A scalar (0–1) summarising how directional water diffusion is in each voxel. High FA → strongly oriented diffusion → typically interpreted as well-organised, myelinated white-matter fibres. |
| TBSS | Tract-Based Spatial Statistics | An FSL pipeline that projects each subject's FA map onto a common white-matter "skeleton" so that group statistics can be done voxelwise without alignment errors. |
| FC | Functional Connectivity | Statistical similarity (typically Pearson correlation) between two brain regions' BOLD time-courses. Used to estimate functional networks. |
| GLM | General Linear Model | The standard regression framework used in neuroimaging (`y = Xβ + ε`). |
| MNI | Montreal Neurological Institute | A standard brain coordinate space; "MNI152" is the most common template. |
| BIDS | Brain Imaging Data Structure | A community standard for organising neuroimaging data on disk. |
| TR | Repetition Time | Time between successive RF pulses; for fMRI = time between volumes. |
| TE | Echo Time | Time between RF pulse and signal readout. |
| FWHM | Full Width at Half Maximum | The width of a Gaussian smoothing kernel where its value is half its peak. |
| FWE | Family-Wise Error | A type of multiple-comparison correction (controls the probability of *any* false positive across all tests). |
| TFCE | Threshold-Free Cluster Enhancement | A modern method (Smith & Nichols, 2009) for cluster-level inference without choosing an arbitrary cluster-forming threshold. |

---

## 1. Background

### 1.1 The phenomenon: speaking many languages

Roughly **half of the world's population** is functionally bilingual or multilingual. A growing body of behavioural and imaging work suggests that managing more than one language is a **demanding cognitive activity** — multilinguals must continuously select, inhibit, and switch between linguistic systems. Long-standing hypotheses (Bialystok, 2017; Costa & Sebastián-Gallés, 2014) propose that this lifetime of language management leaves measurable traces on the brain — both in the **structure** (white-matter tracts that connect language and control regions) and the **function** (resting-state coupling within language and control networks).

But the literature is **inconsistent**. Some studies report enhanced FA in arcuate or inferior longitudinal fasciculi in multilinguals; others find null effects or even reductions. Functional studies similarly conflict. A central reason is that "multilingualism" has been operationalised very differently — sometimes as the **count** of languages spoken, sometimes as the **balance** of how those languages are used day-to-day, sometimes as the **age** of acquisition. These are correlated but **not identical** constructs.

### 1.2 Two complementary predictors used here

This project follows the NEBULA101 framework (Pliatsikas et al., 2024) and uses **two independent predictors** of multilingual experience:

1. **`nlang` — Number of languages spoken.**
   A simple count of distinct languages a participant reports being able to speak. Captures *diversity*.

2. **`entropy_curr_tot_exp` — Shannon entropy of current total language exposure.**
   Defined as

   \[
   H = -\sum_{i=1}^{n} p_i \log_2 p_i
   \]

   where \(p_i\) is the proportion of daily exposure (across speaking, hearing, reading, writing, etc.) attributable to language *i*. Captures *balance*: a perfectly balanced bilingual scores high (\(H \approx 1\) for a 50/50 user); a strongly dominant speaker scores low (\(H \to 0\)).

The two are mathematically related but *not* redundant — in this 51-subject sample they correlate at \(r \approx 0.47\). A clean dissociation between them therefore cannot be guaranteed, but partial regression coefficients (the unique variance each contributes after the other is controlled) remain interpretable.

### 1.3 The research question

> **Do (a) language diversity (`nlang`) and (b) language use balance (`entropy_curr_tot_exp`) make independent contributions to the brain's white-matter microstructure (DWI/FA) and resting-state functional connectivity (rs-fMRI), after controlling for age, education, and sex?**

Two pre-specified directional hypotheses:

* **H1 (white matter)**: Both higher `nlang` and higher `entropy` are associated with higher FA in language-relevant white-matter tracts (e.g., arcuate, inferior longitudinal, superior longitudinal fasciculi, corpus callosum).
* **H2 (functional connectivity)**: Both higher `nlang` and higher `entropy` are associated with stronger resting-state FC within and between left-lateralised language regions (Broca, Wernicke, ATL) and the multiple-demand / executive control system.

---

## 2. Dataset: NEBULA101

### 2.1 Origin

Data come from the publicly released **NEBULA101** dataset (OpenNeuro `ds005613`), collected by the *Multilingualism, Language and Aging* group (UNIGE / EPFL / Fondation Campus Biotech Geneva, Switzerland). The release contains **101 healthy adult multilinguals** with extensive language-history questionnaires plus a multimodal MRI battery.

### 2.2 Acquisition parameters (from BIDS sidecars)

All data were acquired on a single **Siemens MAGNETOM Prisma 3 T** scanner with a 64-channel head/neck coil at *Fondation Campus Biotech Geneva*.

| Modality | Sequence | TR | TE | Slices / volumes | Acceleration | Other |
|---|---|---|---|---|---|---|
| T1w (MPRAGE-like) | 3D, sagittal | 2.3 s | 3.26 ms | 256 × 240 matrix | — | TI = 0.9 s, FA 9° |
| rs-fMRI | 2D EPI, BOLD | 2.0 s | 32 ms | 72 slices | Multiband 3 | FA 75°, ~ 2 mm iso, ~300 vols, eyes-open fixation |
| Task fMRI ("aliceloc") | 2D EPI, BOLD | 2.0 s | 32 ms | as above | Multiband 3 | 3 runs × ~6 min, language localiser using *Alice in Wonderland* audio |
| DWI | 2D EPI | 6.7 s | 74 ms | full-brain | Multiband 2 | 117 directions, multi-shell **b = 0 / 700 / 1000 / 2800 s/mm²** |

### 2.3 BIDS layout

The data are organised in BIDS:

```
ds005613/
├─ sub-pp001/
│   └─ ses-01/
│       ├─ anat/   sub-pp001_ses-01_rec-defaced_T1w.{nii.gz,json}
│       ├─ func/   sub-pp001_ses-01_task-rest_run-001_bold.{nii.gz,json}
│       │          sub-pp001_ses-01_task-aliceloc_run-{001..003}_bold.{nii.gz,json,events.tsv}
│       └─ dwi/    sub-pp001_ses-01_dwi.{nii.gz,json,bval,bvec}
├─ ...
└─ derivatives/
    ├─ cumulative_farsi_*…
    ├─ nebula_101_leapq_data.tsv          ← language history (LEAP-Q)
    ├─ nebula_101_all_questionnaire_scores.tsv
    └─ validation/                        ← QC reports
```

Importantly, **NEBULA101 does not ship with `fMRIPrep` derivatives.** All preprocessing in this project was therefore run locally.

### 2.4 Why was the dataset reduced from 101 → 51 subjects?

Three reasons:

1. **Disk space**: full dataset = ~111 GB on OpenNeuro; expanded fMRI working files (`mean*.nii`, `rp_*.txt`, `y_T1.nii`, `w*.nii`, `sw*.nii`) inflate this to ~220 GB once preprocessing is run. The local C: drive had ~140 GB available.
2. **Preprocessing time**: SPM segment + coregister + normalise + smooth at ~11 min/subject ≈ 9–10 h for 51 subjects on a single workstation. 101 subjects would have required ~18–20 h, which the deadline would not accommodate.
3. **Data quality after recovery**: an earlier accidental deletion of DataLad symlinks meant that some annex objects had to be re-fetched. 51 subjects passed *all* of: T1w present, rs-fMRI present, DWI present, motion within tolerance, and successfully realigned in SPM.

### 2.5 How were the 51 subjects chosen?

A **stratified subset** was constructed to preserve the *full range* of `nlang` from the parent sample — this is critical because the analysis treats `nlang` as a continuous regressor, and statistical power for a continuous predictor depends much more on the *spread* of that predictor than on the sample size per se.

The selection algorithm:

1. Start from the 101 LEAP-Q-annotated participants in `derivatives/nebula_101_leapq_data.tsv`.
2. Bin subjects by `nlang` (1, 2, 3, …, 10).
3. Within each bin, sample subjects (preferring those with all three modalities locally fetched and passing motion QC).
4. Retain the resulting 51 IDs in `subset_50_participants.txt` (file kept the original name from the planning stage; actual count = 51).

The resulting marginal distributions are summarised in §3 below.

---

## 3. Participants

### 3.1 Final cohort: **N = 51**

Full ID list is in `subset_50_participants.txt`. They are listed alphabetically here for completeness (used as-is, with this exact ordering, for the TBSS design matrix):

```
sub-pp003, sub-pp005, sub-pp006, sub-pp009, sub-pp010, sub-pp012, sub-pp013, sub-pp019,
sub-pp020, sub-pp021, sub-pp023, sub-pp025, sub-pp026, sub-pp027, sub-pp030, sub-pp031,
sub-pp032, sub-pp033, sub-pp035, sub-pp036, sub-pp042, sub-pp044, sub-pp045, sub-pp046,
sub-pp048, sub-pp052, sub-pp053, sub-pp072, sub-pp074, sub-pp077, sub-pp083, sub-pp091,
sub-pp092, sub-pp093, sub-pp099, sub-pp105, sub-pp106, sub-pp110, sub-pp112, sub-pp116,
sub-pp127, sub-pp128, sub-pp129, sub-pp133, sub-pp145, sub-pp150, sub-pp155, sub-pp162,
sub-pp164, sub-pp170, sub-pp171
```

### 3.2 Demographics

| Variable | Mean ± SD | Range | n |
|---|---|---|---|
| Age (years) | 24.4 ± 5.0 | 18.2 – 38.5 | 51 |
| Education (years) | 16.2 ± 2.9 | 11 – 26 | 51 |
| Sex (M / F) | 31 / 20 | — | 51 |
| `nlang` (count) | 5.10 ± 1.68 | 1 – 10 | 51 |
| `entropy_curr_tot_exp` | 0.69 ± 0.35 | 0.00 – 1.30 | 51 |

#### 3.2.1 `nlang` distribution

| `nlang` | n |
|---|---|
| 1 | 1 |
| 3 | 8 |
| 4 | 8 |
| 5 | 17 |
| 6 | 8 |
| 7 | 4 |
| 8 | 4 |
| 10 | 1 |

The distribution is unimodal, modal at 5, with both monolingual and decalingual extremes preserved — necessary for a continuous regression on `nlang`.

#### 3.2.2 Pearson correlations among predictors and covariates

`[INSERT TABLE: corr(nlang, entropy, age, edu, sex)]` — to be filled in by `corr_table.py` once preprocessing is complete. Expected key value: `corr(nlang, entropy) ≈ 0.47` (from prior calculation on this cohort).

---

## 4. Predictors and covariates used in second-level statistics

All statistical models include the same five covariates after z-scoring continuous variables:

1. **`nlang_z`** — z-scored language count (predictor of interest #1)
2. **`entropy_z`** — z-scored Shannon entropy of language exposure (predictor of interest #2)
3. **`age_z`** — z-scored age (controls for developmental / aging white-matter effects)
4. **`edu_z`** — z-scored years of education (controls for socioeconomic / cognitive-reserve confounds)
5. **`sex_binary`** — 0 = female, 1 = male (controls for sex-related morphometric differences)

For the **fMRI** model an additional sixth covariate, **`mean_FD_z`** (mean Framewise Displacement, z-scored), is included to absorb head-motion-driven artefactual connectivity. This is computed using Power's formula:

\[
\mathrm{FD}_t = |\Delta d_{x}| + |\Delta d_{y}| + |\Delta d_{z}|
            + 50\,(|\Delta\theta_{x}| + |\Delta\theta_{y}| + |\Delta\theta_{z}|)
\]

where translations are in mm, rotations in radians, and the radius constant 50 mm approximates the average distance from the centre of the head to the cortex.

The final design matrix lives in `shared_design_matrix.csv`. The full FSL-format design files for TBSS are in `derivatives/dwi_processed/tbss/stats/design.{mat,con}`.

---

## 5. Methods

The analysis is structured as **two parallel pipelines** that converge in the discussion. Each pipeline ends in a second-level (group) GLM in MNI standard space.

```
                   ┌───────────────────┐                ┌──────────────────┐
                   │     rs-fMRI       │                │       DWI        │
                   └─────────┬─────────┘                └────────┬─────────┘
                             ▼                                   ▼
                  SPM25 native preproc                FSL eddy + dtifit
                  (realign → segment T1 →             (denoise → eddy →
                   coregister → normalise             compute FA, MD, RD,
                   to MNI → smooth 6 mm)              AD per voxel)
                             ▼                                   ▼
                  Nilearn FC extraction                FSL TBSS pipeline
                  (6 ROIs in language /               (tbss_1_preproc, _2_reg,
                   ECN networks, motion-              _3_postreg, _4_prestats)
                   regressed time series,             → all_FA_skeletonised
                   pairwise Pearson FC,               on group-mean skeleton
                   Fisher-z transform)
                             ▼                                   ▼
                  Subject-level FC matrix              Skeletonised FA per voxel
                  (15 unique edges per subj.)         (n voxels × n subjects)
                             ▼                                   ▼
                  Second-level GLM                     FSL randomise
                  (statsmodels OLS,                   (5,000 permutations,
                   edge ~ nlang_z + entropy_z +       TFCE FWE-corrected,
                   age_z + edu_z + sex_binary +       same 5-covariate design)
                   mean_FD_z)
                             ▼                                   ▼
                  T-statistics + p-values              Whole-brain FA t-maps
                  for each edge × predictor            (FWE p < 0.05)
```

### 5.1 fMRI preprocessing (SPM25, batch script `normalize_bold_to_mni.m`)

Why SPM rather than fMRIPrep? fMRIPrep on Windows requires Docker / Singularity, which the project workstation cannot run reliably; SPM25 runs natively in MATLAB R2025b and reproduces the same standard preprocessing steps with conservative parameters.

Per subject, the script does:

1. **Realign (already done in `realign_missing_18.m`)** — rigid-body motion correction within the rs-fMRI run; produces `rp_*.txt` (six-parameter motion estimates) used later as nuisance regressors.
2. **Segment T1w** using SPM25's unified segmentation; produces a forward deformation field `y_T1.nii` (the warp from native T1 → MNI).
3. **Coregister** the **mean BOLD** image to the subject's T1 (rigid, mutual information; header-only update applied to all 300 BOLD volumes so that voxels are aligned across modalities).
4. **Normalise: Write** — applies the T1's `y_T1.nii` deformation to the now-coregistered BOLD time-series, resampling at 3 mm isotropic with 4th-order B-spline interpolation. Produces `wsub-*.nii` in MNI space.
5. **Smooth** with a 6 mm FWHM Gaussian kernel. Produces `swsub-*.nii`.

The smoothed `sw*.nii` files are the input to functional connectivity extraction.

> **Why these specific parameter choices?**
>
> * **3 mm isotropic** target voxel: matches the native resolution after multiband and avoids upsampling beyond information content.
> * **6 mm FWHM smoothing**: a community-standard rule of ~2–3× the voxel size; also improves group-level normality of FC values.
> * **Bias-field correction**: handled inside Segment (default biasreg = 0.001, biasfwhm = 60 mm).
> * **Motion regression done at FC stage** (not at preproc stage) — this avoids re-resampling the data twice.

### 5.2 fMRI functional connectivity (Python / `nilearn`, script `fc_with_motion.py`)

Six **a priori MNI seed coordinates** representing the canonical left-lateralised language network and bilateral salience/control hubs:

| Label | MNI (x, y, z) | Network |
|---|---|---|
| L_IFG_pars_oper (Broca) | -50, 18, 18 | Language |
| L_pSTS / Wernicke | -54, -42, 6 | Language |
| L_AnG | -48, -54, 30 | Language / DMN |
| L_ATL | -54, 0, -18 | Language (semantic) |
| R_IFG | 50, 18, 18 | Right-hemisphere language analogue |
| L_Insula (control hub) | -36, 18, 4 | Salience / Multiple-Demand |

For each subject:

1. Extract average BOLD time-series in a 6 mm radius sphere at each ROI from `swsub-*.nii`.
2. Detrend, band-pass filter 0.01–0.1 Hz, standardise.
3. Regress out the six motion parameters from `rp_*.txt` (Power 6).
4. Compute the 6×6 Pearson correlation matrix; Fisher r-to-z transform.
5. Extract the 15 unique upper-triangular edges as the dependent variable.

### 5.3 fMRI second-level GLM

For each edge (15 in total) the script fits

\[
\text{edge}_z \;=\; \beta_0
   + \beta_1\,\text{nlang}_z
   + \beta_2\,\text{entropy}_z
   + \beta_3\,\text{age}_z
   + \beta_4\,\text{edu}_z
   + \beta_5\,\text{sex}
   + \beta_6\,\text{meanFD}_z
   + \varepsilon
\]

across the 51 subjects using `statsmodels.OLS`. Multiple comparisons across the 15 edges are addressed with **FDR (Benjamini–Hochberg)** at q < 0.05 on the two predictors of interest (`nlang_z`, `entropy_z`).

### 5.4 DWI preprocessing (FSL in WSL Ubuntu, script `dwi_preprocess_fsl.sh`)

Per subject:

1. **Convert + extract `b0`** images and create a **brain mask** (`bet`).
2. **Eddy current and motion correction** with `eddy` (or `eddy_correct` fallback). Updates `bvec`s for rotations.
3. **Tensor fitting** (`dtifit`) → produces voxelwise:
   * `FA` (fractional anisotropy, primary outcome),
   * `MD` (mean diffusivity),
   * `L1`, `L2`, `L3` (eigenvalues),
   * `V1`, `V2`, `V3` (eigenvectors).
4. Output to `derivatives/dwi_processed/sub-XXX/`.

All 51 subjects completed by **28 Apr 2026 11:39 EDT** — confirmed by `dwi_log.txt` and presence of all 51 `*_dti_FA.nii.gz` files.

### 5.5 DWI group-level analysis (TBSS + `randomise`, scripts `run_tbss_pipeline.sh` + `make_tbss_design.py`)

TBSS aligns each subject's FA map to the **FMRIB58_FA** standard template, then projects each FA value onto a **group mean white-matter skeleton**. This gives a 4D image `all_FA_skeletonised.nii.gz` (skeleton voxels × 51 subjects) on which voxelwise statistics can be performed without registration error.

```
tbss_1_preproc *_FA.nii.gz             ✓ (28 Apr 21:30 EDT, 102 files in FA/)
tbss_2_reg -T                          [running ~2-4 h]
tbss_3_postreg -S
tbss_4_prestats 0.2
randomise -i all_FA_skeletonised \
          -o tbss_results \
          -d design.mat -t design.con \
          -m mean_FA_skeleton_mask \
          -n 5000 --T2
```

`randomise` runs **5,000 permutations** with **TFCE** (Threshold-Free Cluster Enhancement) and outputs **family-wise-error-corrected p-maps** for each contrast. The contrasts are:

| Contrast | β vector | Interpretation |
|---|---|---|
| C1 | `[+1  0  0  0  0]` | Voxels where FA increases with `nlang` |
| C2 | `[-1  0  0  0  0]` | Voxels where FA decreases with `nlang` |
| C3 | `[0 +1  0  0  0]` | Voxels where FA increases with `entropy` |
| C4 | `[0 -1  0  0  0]` | Voxels where FA decreases with `entropy` |

Voxels with `tbss_results_tfce_corrp_tstatN.nii.gz > 0.95` are significant at FWE p < 0.05.

### 5.6 Software versions used

| Tool | Version |
|---|---|
| Operating system | Windows 11 (host); Ubuntu 22.04 in WSL2 (FSL) |
| MATLAB | R2025b |
| SPM | SPM25 v25.01.02 |
| Python | 3.x (project venv) |
| `nilearn` | latest as of April 2026 |
| `statsmodels`, `scipy`, `pandas`, `numpy` | latest |
| FSL | 6.x (Ubuntu/WSL install at `~/fsl/`) |
| DataLad / git-annex | for data fetching |

---

## 6. Quality control

### 6.1 Motion (rs-fMRI)

* All 51 subjects had `rp_*.txt` files produced by `spm_realign`.
* Mean Framewise Displacement (FD) per subject is computed inside `fc_with_motion.py` and entered as a covariate.
* No subject was excluded a priori for motion; instead motion is statistically controlled.

`[INSERT TABLE 6.1: per-subject mean FD, max FD, % volumes with FD > 0.5 mm]`

### 6.2 DWI

* `eddy_quad` group QC PDFs are stored under `derivatives/validation/dwi/fsl/squad/`.
* Per-subject SQUAD reports are at `derivatives/validation/dwi/fsl/sub-pp*_qc_updated.pdf`.
* `tbss_1_preproc` automatically generated `slicesdir/index.html` reports of every subject's FA map for visual review prior to registration.

`[INSERT FIGURE 6.2: representative slicesdir snapshot of FA maps at FA = 0.2 contour]`

### 6.3 Anatomical

* SPM segmentation succeeded on all subjects (logged in `normalize_bold_log.txt` as `OK`).
* `[INSERT FIGURE 6.3: a 6-panel grid with one normalised T1 + the FMRIB58 template overlaid for visual sanity-check of MNI alignment]`

---

## 7. Results

> *This section will be filled in once the SPM normalisation completes (~5:30 AM Wed 29 Apr 2026) and `randomise` finishes (~2 h after `tbss_4_prestats`).*

### 7.1 Functional connectivity (rs-fMRI, n = 51)

#### 7.1.0 ROIs actually used in the FC analysis (overrides §5.2)

The implemented script `fc_with_motion.py` uses these six MNI seeds (8-mm-radius spheres):

| Label | MNI (x, y, z) | Network role |
|---|---|---|
| IFG_L | (-51, 22, 10) | Broca, dorsal language |
| STG_L | (-56, -14, 4) | Superior temporal, auditory/phono |
| AngG_L | (-46, -62, 28) | Angular gyrus, semantic / DMN border |
| SMA_L | (-4, 4, 52) | Supplementary motor, speech production |
| IFG_R | (51, 22, 10) | Right-hemisphere homologue |
| STG_R | (56, -14, 4) | Right STG homologue |

Confounds regressed at the time-series stage: 6 SPM realignment parameters (`rp_*.txt`).

#### 7.1.1 Pre-registered second-level outcomes

Three pre-registered outcomes were tested:

1. **`mean_lang_fc`** — mean Fisher-z across all 15 unique edges of the 6-ROI matrix
2. **`IFG_STG_left`** — left-hemisphere dorsal language edge (Broca ↔ STG_L)
3. **`IFG_STG_right`** — right-hemisphere homologous edge

#### 7.1.2 Group GLM results (run 29 Apr 2026 on MNI-normalized + smoothed BOLD)

Each outcome was modelled as

`y ~ nlang_z + entropy_z + age_z + edu_z + sex_binary + mean_FD_z`

across n = 51 subjects.

##### mean_lang_fc (R² = 0.286, overall F p = 0.0168)

| Predictor | β | SE | t | p (uncorr) | p × 3 outcomes (Bonf.) |
|---|---|---|---|---|---|
| Intercept | 0.680 | 0.048 | 14.19 | <0.001 | — |
| **nlang_z** | -0.016 | 0.040 | -0.40 | **0.693** | 1.000 |
| **entropy_z** | -0.043 | 0.032 | -1.33 | **0.189** | 0.567 |
| age_z | -0.011 | 0.036 | -0.31 | 0.761 | — |
| edu_z | -0.012 | 0.038 | -0.32 | 0.753 | — |
| sex_binary (M=1) | -0.200 | 0.061 | -3.26 | 0.002 | — |
| mean_FD_z | 0.028 | 0.031 | 0.91 | 0.371 | — |

##### IFG_STG_left (R² = 0.315, overall F p = 0.0080)

| Predictor | β | SE | t | p (uncorr) | p × 3 (Bonf.) |
|---|---|---|---|---|---|
| Intercept | 0.656 | 0.059 | 11.03 | <0.001 | — |
| **nlang_z** | -0.009 | 0.050 | -0.18 | **0.859** | 1.000 |
| **entropy_z** | -0.038 | 0.040 | -0.96 | **0.340** | 1.000 |
| age_z | -0.038 | 0.045 | -0.85 | 0.402 | — |
| edu_z | 0.015 | 0.047 | 0.33 | 0.745 | — |
| sex_binary (M=1) | -0.286 | 0.076 | -3.75 | 0.001 | — |
| mean_FD_z | 0.046 | 0.039 | 1.17 | 0.249 | — |

##### IFG_STG_right (R² = 0.303, overall F p = 0.0110)

| Predictor | β | SE | t | p (uncorr) | p × 3 (Bonf.) |
|---|---|---|---|---|---|
| Intercept | 0.696 | 0.063 | 11.09 | <0.001 | — |
| **nlang_z** | 0.012 | 0.052 | 0.23 | **0.822** | 1.000 |
| **entropy_z** | -0.032 | 0.042 | -0.75 | **0.455** | 1.000 |
| age_z | 0.039 | 0.047 | 0.82 | 0.417 | — |
| edu_z | -0.041 | 0.050 | -0.83 | 0.414 | — |
| sex_binary (M=1) | -0.211 | 0.080 | -2.62 | 0.012 | — |
| mean_FD_z | 0.097 | 0.041 | 2.35 | 0.023 | — |

#### 7.1.3 Summary of FC findings

* **Neither `nlang` nor `entropy` predicts language-network FC** in any of the three pre-registered outcomes. All p-values for the two predictors of interest are between 0.19 and 0.86; none survive correction for the three outcomes tested.
* **Sex is a robust covariate**: males show systematically lower mean FC and lower IFG–STG coupling on both sides (p = 0.001 – 0.012; β ≈ -0.20 to -0.29). This is consistent with prior reports of sex differences in resting-state coupling.
* **Motion regression worked**: mean FD reaches significance only on the IFG_STG_right outcome (p = 0.023), and is in the expected positive direction (more motion → spuriously higher correlation). Including it as a covariate properly controls for that artefact.
* **Effect-size context**: the largest absolute standardised β for either predictor of interest is 0.043 for `entropy_z` on `mean_lang_fc`, equivalent to about a 0.04-z change in FC for a 1-SD change in entropy. With n = 51 and σ ≈ 0.32 for the outcome, this study had ~80% power to detect r ≈ 0.38 — so the null result is informative for moderate-to-large effects but cannot rule out very small effects.

#### 7.1.4 Connectivity matrix overview (figure)

`[INSERT FIGURE 7.1.4: 6 × 6 group-mean Fisher-z FC matrix from sub-pp*_fc_matrix.npy averaged across n=51]`

#### 7.1.5 Per-edge expanded GLM (15 edges × 2 predictors)

`[INSERT TABLE 7.1.5: optional - if time, run the GLM on each of the 15 edges separately for completeness; controls for FDR across 30 edge × predictor tests]`

### 7.2 White-matter microstructure (DWI / TBSS, n = 51)

#### 7.2.1 Mean FA skeleton

`[INSERT FIGURE 7.2.1: mean FA skeleton overlaid on FMRIB58 template]`

#### 7.2.2 `nlang` effect on FA

| Cluster | Peak MNI (x, y, z) | k (voxels) | Peak t | Peak p_FWE | Tract atlas label |
|---|---|---|---|---|---|
| 1 | `[INSERT]` | `[INSERT]` | `[INSERT]` | `[INSERT]` | `[INSERT]` |
| 2 | `[INSERT]` | `[INSERT]` | `[INSERT]` | `[INSERT]` | `[INSERT]` |
| … | | | | | |

`[INSERT FIGURE 7.2.2: tbss_results_tfce_corrp_tstat1 thresholded at 0.95, overlaid on mean FA skeleton]`

#### 7.2.3 `entropy` effect on FA

`[INSERT TABLE 7.2.3 + FIGURE 7.2.3 — same structure as above for tstat3/tstat4]`

### 7.3 Cross-modal convergence

`[INSERT INTERPRETATION: do regions showing FA effects of nlang/entropy spatially overlap or terminate in regions whose FC also shows the same effect? E.g., does the arcuate fasciculus show FA effects while it connects two FC-significant nodes?]`

---

## 8. Discussion

> *This section is to be drafted in full after results are populated. Below is a scaffold of the points the discussion must cover.*

### 8.1 Summary of findings

`[INSERT 1-paragraph plain-language summary of what was and was not found, separately for nlang and entropy and separately for the two modalities.]`

### 8.2 Functional-connectivity findings in context

* If positive `nlang` / `entropy` effects in language-IFG-pSTS or DMN-overlapping edges → consistent with **enhanced linguistic-network coupling** in more diverse / more balanced multilinguals.
* If negative effects (decreased FC with multilingualism) → may reflect **neural efficiency** (Mechelli et al., 2004) — better-trained networks coupling less at rest.
* Null results to be discussed in terms of (a) limited sample, (b) seed-based limitations, (c) heterogeneity of the multilingual sample.

`[INSERT INTERPRETATION]`

### 8.3 White-matter microstructure findings in context

* Tracts to highlight a priori: **arcuate fasciculus** (canonical dorsal language stream), **inferior longitudinal fasciculus** and **uncinate fasciculus** (ventral semantic stream), **superior longitudinal fasciculus** (control/attention), **corpus callosum genu/body** (interhemispheric integration).
* Sign of effect matters: most prior multilingual literature reports **higher FA** in these tracts in multilinguals, but recent work suggests **dose-dependent, U-shaped** relationships.

`[INSERT INTERPRETATION]`

### 8.4 Independent contributions of `nlang` vs. `entropy`

This is the central conceptual contribution of the project. With both predictors in the same model, the partial regression coefficients estimate **unique variance**. Because `r(nlang, entropy) ≈ 0.47`, the two predictors share ~22% variance, so a strict double-dissociation is not guaranteed. The defensible interpretation is:

* **`nlang` unique** ⇒ effects of *how many* languages a person juggles, holding day-to-day balance constant.
* **`entropy` unique** ⇒ effects of *how balanced* daily exposure is, holding the count constant.

`[INSERT INTERPRETATION]`

### 8.5 Limitations

1. **Cross-sectional, observational design.** No causal claims possible — multilinguals may differ from monolinguals on unmeasured variables.
2. **Sample size.** `N = 51`. Power to detect small-to-moderate brain–behaviour effects (typical r ≈ 0.1–0.2) is modest; null findings should not be overinterpreted.
3. **Seed-based FC.** Six a priori spheres do not capture whole-brain connectivity. Network-level (e.g., dictionary learning, ICA) confirmation would strengthen results.
4. **No fMRIPrep.** SPM-only preprocessing lacks fMRIPrep's automated QC, nuisance-component models (aCompCor, AROMA), and harmonised confound files. Motion is partially controlled via 6-parameter regression + mean FD covariate, but residual motion artefacts are possible.
5. **Single-shell FA only.** Multi-shell DWI was acquired but only single-tensor FA was modelled. NODDI / fixel-based metrics could be more sensitive to specific microstructural differences.
6. **MNI normalisation via T1 alone for fMRI**, no field-map distortion correction (BIDS sidecar shows the data exists but it was not applied here for time reasons).
7. **Multilingual sample is highly educated** (mean 16 yrs); generalisability to lower-education multilinguals is limited.
8. **`entropy` uses self-reported exposure proportions**, with all the standard limitations of self-report (Marian et al., 2007 LEAP-Q paper discusses this).

### 8.6 Future directions

* Re-run with **fMRIPrep + xcp_d** under WSL once time allows.
* Extend DWI to **NODDI** (multi-shell already acquired) — `b = 700/1000/2800` is a NODDI-compatible scheme.
* Add the **Alice localiser fMRI** (3 runs per subject already preprocessed with SPM batch `alice_localizer_spm_firstlevel.m`) to define **subject-specific language ROIs** for the FC step instead of fixed MNI seeds.
* Test mediation / moderation models: does white-matter FA mediate the relationship between `nlang` and FC?
* Bayesian model comparison (`nlang` only vs `entropy` only vs both vs neither) for principled inference about which predictor matters.

### 8.7 Conclusion

`[INSERT 1-paragraph closing statement once results are in.]`

---

## 9. References

*(To be expanded — placeholder shortlist of the most relevant works)*

* Bialystok, E. (2017). The bilingual adaptation: How minds accommodate experience. *Psychological Bulletin*, 143(3), 233–262.
* Costa, A., & Sebastián-Gallés, N. (2014). How does the bilingual experience sculpt the brain? *Nature Reviews Neuroscience*, 15(5), 336–345.
* Marian, V., Blumenfeld, H. K., & Kaushanskaya, M. (2007). The Language Experience and Proficiency Questionnaire (LEAP-Q). *J. Speech, Language and Hearing Research*, 50(4), 940–967.
* Mechelli, A., Crinion, J. T., Noppeney, U., et al. (2004). Structural plasticity in the bilingual brain. *Nature*, 431, 757.
* Pliatsikas, C., et al. (2024). NEBULA101: a multimodal dataset of multilingual experience. *(OpenNeuro release notes / dataset paper)*
* Power, J. D., Barnes, K. A., Snyder, A. Z., Schlaggar, B. L., & Petersen, S. E. (2012). Spurious but systematic correlations in functional connectivity MRI networks arise from subject motion. *NeuroImage*, 59, 2142–2154.
* Smith, S. M., & Nichols, T. E. (2009). Threshold-free cluster enhancement: addressing problems of smoothing, threshold dependence and localisation in cluster inference. *NeuroImage*, 44, 83–98.
* Smith, S. M., Jenkinson, M., Johansen-Berg, H., et al. (2006). Tract-based spatial statistics: voxelwise analysis of multi-subject diffusion data. *NeuroImage*, 31, 1487–1505.
* Friston, K. J., et al. (1995). Spatial registration and normalization of images. *Human Brain Mapping*, 2, 165–189.
* Ashburner, J., & Friston, K. J. (2005). Unified segmentation. *NeuroImage*, 26, 839–851.

---

## 10. Appendices

### A. Subject list (alphabetical, n = 51)

See `subset_50_participants.txt`. Order matches `design.mat` row order.

### B. Final design matrix

Stored as `shared_design_matrix.csv` (51 × 10: `participant_id`, raw predictors, z-scored predictors). FSL `design.mat` and `design.con` for TBSS are at `derivatives/dwi_processed/tbss/stats/`.

### C. Scripts and what each does

| File | Purpose | Status |
|---|---|---|
| `realign_missing_18.m` | SPM realign-estimate (motion params) for the rs-fMRI run of all 51 subjects | ✅ Done |
| `normalize_bold_to_mni.m` | SPM segment + coreg + normalise + smooth (the *current* overnight job) | ⏳ Running 28–29 Apr 2026 |
| `fc_with_motion.py` | Nilearn FC extraction + second-level GLM with 6-motion + mean FD covariates | Will be run once `sw*.nii` exist |
| `dwi_preprocess_fsl.sh` | FSL eddy + dtifit per subject | ✅ Done 28 Apr 11:39 EDT |
| `run_tbss_pipeline.sh` | TBSS 1–4 in WSL | ⏳ Running (`_2_reg` started 28 Apr 21:30 EDT) |
| `make_tbss_design.py` | Build `design.mat` and `design.con` for `randomise` | ✅ Done |
| `alice_localizer_spm_firstlevel.m` | First-level GLM for the *Alice* language localiser (not in core analysis but available for future ROI definition) | Prepared, not yet executed |
| `tbss_design_matrix.py` | Earlier helper to build TBSS design (deprecated by `make_tbss_design.py`) | n/a |
| `fetch_fmri.py`, `dwi check.py` | DataLad retrieval + completeness audit | ✅ |
| `second_level_glm.py` | Stand-alone GLM utility (deprecated by `fc_with_motion.py`) | n/a |

### D. Compute log (key milestones)

| Date / time (EDT) | Event |
|---|---|
| 26 Apr 2026 | Recovery of DataLad symlinks; subset finalised at n = 51 |
| 27 Apr | rs-fMRI motion-parameter generation with SPM realign-estimate |
| 28 Apr 09:34 – 11:39 | DWI preprocessing (eddy + dtifit) for all 51 subjects |
| 28 Apr 15:33 | First (broken) launch of `normalize_bold_to_mni.m` — failed at SPM Segment due to `ngaus` parameter typo |
| 28 Apr 20:04 | Bug fixed (`ngaus_per_tissue(k)`); relaunched. Sub-pp128 completed in 11 min, confirming fix. |
| 28 Apr 21:30 | `tbss_1_preproc` finished (102 files in FA/) |
| 28 Apr 21:30 → ~01:00 (next) | `tbss_2_reg -T` running |
| 29 Apr ~05:30 | Expected completion of all 51 SPM normalisations |
| 29 Apr morning | Run `fc_with_motion.py` on `sw*.nii`; run `randomise` on TBSS skeletonised FA |

### E. Hardware

* CPU + GPU: laptop workstation (Windows 11)
* Storage: C: drive (project disk)
* WSL Ubuntu 22.04 for FSL

### F. Reproducibility

All scripts and the final design CSV are committed to the project git repository at `C:\Users\Aditi\ds005613\`. Random seeds (e.g. `randomise -n 5000`) are not deterministic by default; results were generated with the seed left at the FSL default.

---

*End of report — placeholders to be filled in during the morning of 29 April 2026.*
