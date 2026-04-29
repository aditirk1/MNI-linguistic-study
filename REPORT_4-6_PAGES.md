# Language Diversity, Use Balance, and Multimodal Brain Measures in the NEBULA101 Subsample

**Author:** Aditi  
**Context:** Graduate coursework in multimodal neuroimaging, Columbia University, Spring 2026  
**Data:** OpenNeuro dataset ds005613 (NEBULA101)

## Abstract

Multilingual experience is often hypothesized to shape both white matter microstructure and resting functional coupling among language regions. Using fifty one adults from the public NEBULA101 release, we asked whether the number of languages spoken and the Shannon entropy of current language exposure each predict diffusion tensor fractional anisotropy along a tract based spatial statistics skeleton and seed based resting state functional connectivity. Functional magnetic resonance imaging volumes were spatially normalized to Montreal Neurological Institute standard space using Statistical Parametric Mapping version twenty five. Diffusion weighted images were preprocessed in FMRIB Software Library and analysed with tract based spatial statistics followed by permutation testing with threshold free cluster enhancement. Neither general linear models of functional connectivity nor voxelwise skeleton statistics showed family wise error significant associations for the language predictors at prespecified thresholds. Sex remained a strong covariate in connectivity models. Results constrain the expected effect sizes detectable in a modest cohort and highlight the value of reporting negative findings with transparent preprocessing and alignment checks.

## 1. Introduction

Bilingual and multilingual populations are large, yet the neural correlates of life long language juggling remain inconsistent across studies. Operational definitions of multilingualism differ across publications. One may emphasize how many languages an individual commands. Another may emphasize how evenly daily exposure is distributed across those languages, which can be summarized with Shannon entropy of self reported usage proportions. These constructs are related but not redundant, so both may be included in separate regression terms while holding demographics constant.

The NEBULA101 study released structural magnetic resonance imaging, diffusion weighted imaging, resting functional magnetic resonance imaging, and rich language history questionnaires for one hundred and one participants. Here we focus on a capacity matched subsample of fifty one individuals with complete T1 weighted anatomy, resting scans, diffusion data, and questionnaire derived predictors. The primary question is whether standardized number of languages and standardized entropy independently predict brain measures after adjustment for age, years of education, and self reported sex. Resting functional connectivity models further adjust for mean head motion. The preregistered imaging targets are skeleton wise fractional anisotropy and Fisher transformed correlations among six canonical left and right hemisphere seeds placed in inferior frontal, superior temporal, supplementary motor, and homologous regions in standard space.

## 2. Methods

**Participants and predictors.** Participant identifiers were taken from a fixed list of fifty one subjects balanced to retain spread in number of languages relative to the parent cohort. Behavioral values came from the project design matrix shared with analysis scripts. Predictors of interest were z scored number of languages and z scored entropy of current total exposure. Covariates were z scored age, z scored education, and a binary sex code. For functional connectivity only, mean framewise displacement was computed from six realignment parameters following the power formulation and was entered z scored. Fifty one rows of the design matrix used in tract based statistics were verified to follow the same alphabetical subject order as the fifty one volumes in the four dimensional skeletonised fractional anisotropy stack. Randomise was run with five thousand permutations per contrast and TFCE two option for t contrast output.

**Functional pipeline.** Motion parameters were produced earlier with SPM realignment estimate on native resting blood oxygen level dependent series. High resolution T1 weighted images were segmented, and mean functional images were coregistered to T1. Normalisation wrote warped functional time series into MNI space at three millimetre isotropic resolution followed by six millimetre full width at half maximum Gaussian smoothing. The analysis read smoothed warped NIfTI files together with realignment text files. Sphere maskers extracted band passed and detrended time courses at six seeds, partialing six motion columns, then formed Pearson correlations and Fisher z transforms. Group level ordinary least squares regressed each of three composite outcomes on the language predictors and covariates. Outcomes were mean Fisher z over the fifteen unique inter seed edges, left inferior frontal gyrus to left superior temporal gyrus Fisher z, and right homologous Fisher z.

**Diffusion pipeline.** Single shell style fractional anisotropy maps were produced per subject with eddy correction and tensor fitting in FSL. Tract based spatial statistics followed standard steps through skeletonisation at fractional anisotropy threshold zero point two and projection of all subjects onto the group mean skeleton. The design matrix matched columns for z scored number of languages, z scored entropy, z scored age, z scored education, and binary sex. Four contrasts targeted positive and negative weights on number of languages and on entropy. Inference used FSL randomise on the skeletonised four dimensional data with the binary skeleton mask.

## 3. Results

**Functional connectivity.** All fifty one subjects contributed usable resting series and motion summaries. Cross subject mean framewise displacement spanned zero point zero four to zero point four two millimetres. For the mean edge outcome, the model explained about twenty nine percent of variance with a significant omnibus F statistic. Coefficients for z scored number of languages and z scored entropy were small negative and not significant at the two sided alpha zero point zero five level, with p values zero point six nine and zero point one nine respectively. The same pattern held for the left inferior frontal to superior temporal edge, where p values were zero point eight six and zero point three four. For the right homologous edge, language predictors again lacked significance while z scored mean framewise displacement carried a positive coefficient significant at p zero point zero two three, consistent with motion inflating apparent coupling. Sex coded as male relative to female predicted lower connectivity magnitudes in all three outcomes with p values from zero point zero zero two to zero point zero one two in the printed full models. These sex effects do not bear on the language hypothesis but confirm that nuisance structure was detected when present.

**White matter skeleton statistics.** Skeleton masks contained one hundred one thousand five hundred ten voxels entering inference. Raw t statistic extrema on the mask ranged from about minus two point three to plus two point three depending on contrast direction. Threshold free cluster enhancement corrected one minus p maps reached maxima zero point five nine, zero point three seven, zero point five seven, and zero point three six for the four contrasts respectively. No voxel inside the mask exceeded zero point nine five on any corrected map, which corresponds to the conventional reporting rule for family wise error p below zero point zero five under this implementation. Therefore no cluster based statistics were derived. Visual inspection in FSLeyes with display scaling zero point nine five to one showed no coloured voxels on the mean skeleton underlay, matching the numerical summary.

## 4. Discussion

Within this fifty one person cohort, strict skeleton wise testing did not reveal multilingualism measures associated with fractional anisotropy at family wise corrected thresholds, and standardised language predictors did not track seed based resting connectivity after motion and demographic adjustment. The absence of findings should not be read as proof that multilingual experience leaves no trace in the adult brain. The study is cross sectional, modest in size for continuous predictors, and uses simplified diffusion metrics. Functional analysis ignores task defined language areas and whole brain connectivity patterns. Predictors correlate with one another, which limits how cleanly variance can be partitioned even when partial regression coefficients remain interpretable. Multiple comparison control on the skeleton is intentionally strict. Future work could enlarge effective sample, adopt fixel or multicompartment diffusion models, or define regions of interest from participant specific language localisers rather than fixed MNI spheres.

Transparency checks support internal consistency. The four dimensional skeletonised data have fifty one volumes at one millimetre grid spacing on the standard template used by tract based spatial statistics. Design matrix rows follow the same subject sequence recorded in TBSS logs. Randomise completed all four contrasts with five thousand permutations each.

## 5. References

Ashburner J, Friston KJ. Unified segmentation. Neuroimage. 2005.

Smith SM, Nichols TE. Threshold free cluster enhancement. Neuroimage. 2009.

Smith SM, Jenkinson M, Johansen Berg H, et al. Tract based spatial statistics in voxelwise analysis of multi subject diffusion data. Neuroimage. 2006.

Pliatsikas C et al. NEBULA101 multimodal dataset and documentation. OpenNeuro ds005613. 2024.

Power JD, Barnes KA, Snyder AZ, et al. Spurious but systematic correlations in functional connectivity MRI networks arise from subject motion. Neuroimage. 2012.

---

*End of concise report. Paste into a word processor, set 11 or 12 point font with one inch margins, and adjust spacing if a strict page count is required. Numeric results above are taken from fc_glm_motion_results.csv, fc_with_motion_run.log, and tbss_inspection_report.txt in the project derivatives folder.*
