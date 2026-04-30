# 10-Minute Presentation: Multilingual Experience and the Multimodal Brain
## NEBULA101 (n = 51) — slide-by-slide guide

This is a **600-second** talk. Plan for ~12 slides at ~50s/slide on average,
with two slower "results" slides at ~75s. Keep one number on each slide
that the audience must remember. Everything else is scaffolding.

The story arc, from the first sentence to the last, is:

> The literature on multilingualism and the brain is mixed because
> "multilingualism" has been operationalised in many ways. We tested two
> complementary measures — diversity (count) and balance (entropy) —
> against rs-fMRI and DWI in 51 NEBULA101 adults. Neither survived
> correction. The pipeline is sound (we recover the language network and
> sensible sex/motion effects); the null result therefore *bounds* the
> linear, questionnaire-driven effect detectable in this sample.

---

## Slide-by-slide

### Slide 1 — Title (30 s)
**Headline:** *Multilingual experience and the multimodal brain*
**Subhead:** rs-fMRI + DWI in 51 healthy adults from NEBULA101 (ds005613)
**Image:** none, or a small NEBULA101/Geneva logo if you want it.
**Talk track:** name + course + one-line orientation: "I'll show you a
multimodal MRI test of two ways of measuring multilingualism, and I'll
show you what the absence of an effect actually tells us."

### Slide 2 — Why ask this? (45 s)
**Headline:** *Half the world is multilingual; the brain literature is mixed.*
**Image:** a quick 2-row layout of small icons (book, two-speech-bubble,
arcuate fasciculus stylised). If you want a real figure, the predictor
panel works (`derivatives/results/figures/fig1_predictors.png`) — but
that's better on Slide 3. Here you can keep it text-only.
**Talk track:** "Some studies report higher arcuate FA in multilinguals,
others find null. One reason for the inconsistency is that
'multilingualism' has been measured very differently — sometimes as a
count, sometimes as a balance, sometimes as age of acquisition." End
with the framing question:
> Do *language diversity* and *language use balance* make independent
> contributions to brain structure and function?

### Slide 3 — Two predictors (60 s)
**Headline:** *Diversity vs. balance — two complementary numbers from one questionnaire.*
**Image:** `derivatives/results/figures/fig1_predictors.png`
(the three-panel: nlang histogram | entropy histogram | scatter with r = 0.43).
**Talk track:** Define each in one sentence each.
- **nlang** = count of languages a participant reports speaking. Captures *diversity*.
- **entropy_curr_tot_exp** = Shannon entropy of daily exposure across
  speak/hear/read/write. Captures *balance* — high entropy means
  someone uses multiple languages relatively evenly.
- They correlate r = 0.43, so they're related but not redundant — partial
  regressions matter.

### Slide 4 — Hypotheses (35 s)
**Headline:** *Two pre-specified hypotheses.*
**Image:** none, two clean text boxes:
- **H1 (white matter):** higher nlang and/or entropy → higher FA in
  language-related tracts.
- **H2 (functional connectivity):** higher nlang and/or entropy →
  altered resting coupling within the language network.
**Talk track:** "We pre-specified the predictors, the outcomes, and the
correction strategies before running the second-level models."

### Slide 5 — Cohort (30 s)
**Headline:** *NEBULA101 → n = 51 with all three modalities.*
**Image:** small demographics table (you can also paste it from the .docx).
Key numbers to show:
- n = 51 (31 M / 20 F), age 24.4 ± 5.0 years, education 16.2 ± 2.9 years,
  nlang 5.10 ± 1.68 (range 1–10), entropy 0.69 ± 0.35 (range 0.00–1.30).
**Talk track:** "We retained 51 of the 101 NEBULA participants — all who
had complete T1, rs-fMRI and DWI that passed motion QC. Selection was
*stratified* on nlang to preserve the full 1–10 range."

### Slide 6 — Pipeline (45 s)
**Headline:** *Two analysis branches; both end in standard (MNI) space.*
**Image:** `derivatives/results/figures/fig2_pipeline.png` (the schematic; regenerated from
`check_script.py` — boxes now spell out **BOLD→T1 coregistration**, **normalise to MNI**, and
**TBSS → skeleton**).
**Talk track:** "Resting fMRI: **SPM25** aligns the **mean functional volume to each participant’s T1**,
then **segments the T1** and applies the **same warp** to write BOLD into **MNI152**, **6 mm smooth**,
then **six 8 mm MNI seeds** in Nilearn → 6×6 Fisher-z → group GLM on three pre-specified outcomes.
Diffusion: **FSL** eddy + dtifit → **TBSS** registers FA to template space and the **skeleton** →
**randomise** with TFCE. **Multimodal** here means shared **MNI coordinates** for seeds and integration
QC, not a single joint acquisition space."

### Slide 6b — Multimodal alignment / coregistration QC (~45 s, **recommended for course**)
**Headline:** *Both modalities in MNI space — what that looks like on the template.*
**Image:** Two figures side by side (or two slides):
- `derivatives/results/figures/fig_coreg_dwi_mni.png` — group mean FA + skeleton (TBSS) on MNI T1.
- `derivatives/results/figures/fig_coreg_fmri_mni.png` — resting fMRI in **MNI152** after **SPM25**
  (title is a **methods result**, not an “example” label; volume = first sorted pipeline output per
  `coregistration_qc_and_coupling.py`).
**Generate / refresh:** `.\.venv\Scripts\python.exe coregistration_qc_and_coupling.py`
**Talk track:** "These are **quality-control / methods** panels: DWI-derived FA is in **TBSS template
space**; fMRI is **warped BOLD** on the **same template class** (MNI152). That is the **coregistration
story** your multimodal class expects: **anatomical bridge for fMRI**, **template registration for DWI**,
then **common coordinates** for ROIs and exploratory coupling."

### Slide 6c — Exploratory structure–function coupling (~40 s, **optional**)
**Headline:** *Same MNI ROIs: does local skeleton FA track mean language FC?*
**Image:** `derivatives/results/figures/fig8_roi_coupling.png` (with `roi_structure_function.csv` if
you want numbers on the slide).
**Talk track:** "This is **not** a pre-registered hypothesis test — it uses **TBSS skeleton FA** and
**Nilearn FC** at **identical seed coordinates**. It shows **whether** local structure and coupling
**co-vary** across people. **Null** coupling is still informative for a multimodal narrative."

### Slide 7 — The pipeline works (45 s) — Reassurance slide
**Headline:** *Before testing the predictors, check the network is recoverable.*
**Image:** Prefer the **report** group-mean FC matrix (motion pipeline, diagonal masked):
`report_assets/generated/fig_group_mean_fc_matrix.png` after
`.\.venv\Scripts\python.exe build_project_report_docx.py`.  
Alternatives: `derivatives/figures/group_fc_matrix.png` and
`derivatives/figures/connectome_glass.png` — regenerate with
`make_fc_figures.py` (reads **`nilearn_fc_motion`**; same files are **mirrored** under
`derivatives/results/figures/` so they sit with fig1–fig8).
**Talk track:** "We see the dorsal language pattern we expect: strong
IFG–STG and bilateral IFG coupling; angular gyrus sits at the periphery.
This means any nulls below are not a broken pipeline."

### Slide 8 — Result 1: FC, no effect (75 s)
**Headline:** *Neither nlang nor entropy predicts language-network FC.*
**Image:** EITHER the descriptive scatter
(`report_assets/story_generated/fig_descriptive_fc_scatter.png` from the
build script) OR a clean *table* with the 6 GLM rows. The table is more
honest because it shows partial coefficients.
**Headline numbers to show on the slide:**
- mean_lang_fc: nlang β = −0.016, p = 0.69; entropy β = −0.043, p = 0.19
- IFG_STG_left: nlang β = −0.009, p = 0.86; entropy β = −0.038, p = 0.34
- IFG_STG_right: nlang β = +0.012, p = 0.82; entropy β = −0.032, p = 0.46
- Bonferroni × 3 outcomes: all p ≥ 0.57
**Talk track:** "All six tests are null. Note the partial β are tiny
in standardised units — even if you wanted to chase a small effect,
this is the size you'd be chasing."

### Slide 9 — But sex and motion *do* land (35 s) — Important sub-result
**Headline:** *The model isn't empty — sex and motion explain real variance.*
**Image:** none, or three callout boxes with these numbers:
- Sex (male = 1) on mean_lang_fc:  β = −0.20,  p = 0.002
- Sex (male = 1) on IFG_STG_left:  β = −0.29,  p = 0.001
- mean FD on IFG_STG_right:        β = +0.097, p = 0.023
**Talk track:** "Two things matter to make the audience trust the null
above. First, the model's R² ranges 0.29–0.32 across the three FC
outcomes — it isn't an empty model. Second, sex and motion land in
exactly the directions and magnitudes the prior literature predicts.
That's a sanity check. The pipeline is sensitive when there's
something to find."

### Slide 10 — Result 2: TBSS / DWI, also no effect (75 s)
**Headline:** *No FA voxel survives FWE p < 0.05 on the TBSS skeleton.*
**Image:** `derivatives/results/figures/fig3_tbss.png` (the four-contrast panel).
**Headline numbers to show:**
- Skeleton mask: 101,510 voxels.
- Permutations: 5,000 with TFCE.
- Max corrp across the four contrasts: 0.59 (+nlang), 0.37 (−nlang),
  0.57 (+entropy), 0.36 (−entropy). FWE threshold is 0.95. Not close.
**Talk track:** "Four contrasts; none come within 0.36 of the FWE
threshold. Raw t-stats range roughly ±2.3 across the skeleton, which is
well within what you'd expect under the null with this many voxels and
this many permutations."

### Slide 11 — Why null? (60 s)
**Headline:** *Four reasons the null is the right answer in this dataset.*
**Image:** `derivatives/results/figures/fig6_power.png` (post-hoc power curve).
**Talk track (one sentence each):**
1. **Power.** With n = 51, power for r = 0.20 is well under 80%. The power curve says it directly.
2. **Construct overlap.** nlang and entropy correlate r = 0.43, so partial coefficients are by construction smaller than bivariate r — and any shared signal can't be partitioned.
3. **Range restriction.** Highly educated, all healthy young adults; the *between-person* variation in proficiency / age of acquisition is constrained.
4. **Summary measures.** Single-tensor FA on a skeleton; six fixed seeds. Multi-shell NODDI / fixel and ICA-level FC could be more sensitive.

### Slide 12 — Take-home + future directions (45 s)
**Headline:** *A bound, not a verdict.*
**Image:** none, three short lines:
- A reproducible multimodal pipeline runs on NEBULA101.
- Linear questionnaire→brain effects of nlang/entropy are *bounded*
  in this n = 51 subsample at conventional thresholds.
- Three concrete extensions, in order of payoff:
  1. **Subject-specific language ROIs** from the Alice in Wonderland
     localiser (already preprocessed; not used at second-level here).
  2. **Multi-shell diffusion** (NODDI / fixel) — the data already exist
     at b = 700/1000/2800.
  3. **Network-level FC** (ICA / dictionary learning) instead of fixed
     a-priori seeds.

End with one sentence: "Absence of evidence is not evidence of absence —
but it constrains where to look next."

---

## Time budget

| Slides | Time | Cumulative |
|--------|------|------------|
| 1 (title)              | 0:30 | 0:30 |
| 2 (why)                | 0:45 | 1:15 |
| 3 (two predictors)     | 1:00 | 2:15 |
| 4 (hypotheses)         | 0:35 | 2:50 |
| 5 (cohort)             | 0:30 | 3:20 |
| 6 (pipeline)           | 0:45 | 4:05 |
| 7 (network recovered)  | 0:45 | 4:50 |
| 8 (FC null)            | 1:15 | 6:05 |
| 9 (sex/motion landed)  | 0:35 | 6:40 |
| 10 (TBSS null)         | 1:15 | 7:55 |
| 11 (why null)          | 1:00 | 8:55 |
| 12 (take-home)         | 0:45 | 9:40 |
| Q&A buffer / wrap      | 0:20 | 10:00 |

**Optional:** Slides **6b** and **6c** (coregistration QC + coupling) add about **1:15** combined.
Keep the 10-minute cap by trimming ~30–45 s from Slides 2 and 11, or run a 13-slide deck if allowed.

---

## Image checklist — what you already have, and what is worth adding

### Multimodal / coregistration (recommended for the course)
- `derivatives/results/figures/fig_coreg_dwi_mni.png` — Slide **6b** (group mean FA + skeleton on MNI).
- `derivatives/results/figures/fig_coreg_fmri_mni.png` — Slide **6b** (resting fMRI in MNI152 after SPM25).
- `derivatives/results/figures/fig8_roi_coupling.png` — Slide **6c** optional (ROI skeleton FA vs mean FC).
- `derivatives/results/figures/roi_structure_function.csv` — numeric *r* / *p* for that slide or appendix.
- **Generate:** `.\.venv\Scripts\python.exe coregistration_qc_and_coupling.py`  
- **Written report:** section **3.6** in `NEBULA_Multimodal_Report.docx` from `build_project_report_docx.py`
  embeds these figures when the files exist.

### Use as-is (already on disk, narrative-relevant)
- `derivatives/results/figures/fig1_predictors.png` — Slide 3.
- `derivatives/results/figures/fig2_pipeline.png` — Slide 6 (**updated** schematic: coreg, MNI, TBSS).
- `derivatives/results/figures/fig3_tbss.png` — Slide 10. Caption it as
  "no voxel survives FWE p < 0.05".
- `derivatives/results/figures/fig6_power.png` — Slide 11.
- `report_assets/generated/fig_group_mean_fc_matrix.png` — Slide 7 (**preferred**; run
  `build_project_report_docx.py`).
- `derivatives/figures/group_fc_matrix.png` — Slide 7 (`make_fc_figures.py` → **`nilearn_fc_motion`**).
  Duplicate: `derivatives/results/figures/group_fc_matrix.png`.
- `derivatives/figures/connectome_glass.png` — Slide 7 backup / glass brain (same). Duplicate under
  `derivatives/results/figures/`.

### Use the *regenerated* versions instead of the legacy ones
After running `.\.venv\Scripts\python.exe build_project_report_docx.py`, prefer:
- `report_assets/generated/fig_group_mean_fc_matrix.png` — Slide 7 (matches `nilearn_fc_motion` + annotated heatmap).

After running `build_NEBULA_story_docx.py` (if you still use it), older paths were:
- `report_assets/story_generated/fig_group_mean_fc.png` — superseded for Word report by the path above.
- `report_assets/story_generated/fig_descriptive_fc_scatter.png` — Slide 8.
- `report_assets/story_generated/fig_motion_fd.png` — back-up for QC slide.
- `report_assets/story_generated/fig_predictors.png` — back-up for Slide 3.

### Skip these (stale numbers vs. the final GLM)
- `derivatives/results/figures/fig5_results_table.png` — its tabulated
  p-values do **not** match `fc_glm_motion_results.csv` (e.g., fig5
  shows nlang→mean_lang_fc p = 0.856, but the CSV says p = 0.693). It
  was generated from an earlier model. Use a clean Word/PowerPoint
  table with the CSV numbers (Slide 8).
- `derivatives/results/figures/fig4_fc_results.png` — bivariate scatter
  with simple Pearson r in the title strip; can be misread as
  "the GLM result". If you do show it, caption it explicitly as
  *uncorrected, no covariates*.
- `derivatives/fc_unified_n51/group_fc_matrix_unified.png` — a cell
  shows Fisher-z = 1.09 (off-diagonal symmetry suggests an averaging
  bug). Do not show it.

### Optional — additional FSL renders worth generating

These are small, polished images that would substantially improve a
slide deck or a paper-style figure. They can all be made from FSLeyes
on existing files; nothing new needs to be computed.

1. **TBSS-style skeleton overlay**
   - Underlay: `$FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz`
   - Overlay 1 (greyscale, low alpha): `derivatives/dwi_processed/tbss/stats/mean_FA_skeleton.nii.gz`
   - Overlay 2 (lime-green, threshold 0.2): `derivatives/dwi_processed/tbss/stats/mean_FA_skeleton_mask.nii.gz`
   - Save axial / coronal / sagittal screenshots from FSLeyes.
   - Use on Slide 10 to anchor "this is the white-matter skeleton we
     tested".

2. **One descriptive t-stat overlay**
   - Underlay: `$FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz` + the
     skeleton mask in green.
   - Overlay (red-yellow, threshold 1.5–3.0): `derivatives/dwi_processed/tbss/stats/tbss_results_tstat1.nii.gz`
   - Caption explicitly: "raw t for +nlang, **descriptive only**, not
     FWE-significant (max corrp = 0.59)."
   - Useful as a backup slide if you're asked "show me the unthresholded map".

3. **Six MNI seeds rendered on a brain glass**
   - You already have `derivatives/figures/rois_mni.png` — that's good.
     Only regenerate if you want a higher-resolution version with
     labels.

4. **TBSS slicesdir QC** (optional, only if asked about QC)
   - `derivatives/dwi_processed/tbss/FA/slicesdir/index.html` opens a
     gallery of every subject's FA map. For slides, screenshot a single
     row (e.g., `sub-pp003_FA_FA.png`) and label it "example FA after
     dtifit". The full gallery is for the report appendix or Q&A only.

---

## Anticipated audience questions & 30-second answers

**Q. Did you coregister fMRI to anatomy?**
"Yes. **SPM25** coregisters the **mean resting BOLD to each participant’s T1** before applying the
**T1-derived warp** to MNI — that is in `normalize_bold_to_mni.m` and on **Slide 6 / 6b**
(`fig_coreg_fmri_mni.png`). DWI uses **TBSS** to **template** space; both pipelines support **MNI ROI**
integration."

**Q. n = 51 — isn't that just underpowered?**
"Yes. The post-hoc curve says we have ~80% power for r ≈ 0.35, but
much less for r ≈ 0.2, which is a more realistic effect size. The
contribution of this work is therefore a *bound* on the effect, not
a yes/no verdict."

**Q. Why not fMRIPrep?**
"fMRIPrep needs Docker/Singularity, which isn't reliable on the
Windows workstation we used. SPM25 with a 3 mm + 6 mm-FWHM normalise/smooth
recipe is well-validated and reproducible; we control motion at the
seed-extraction stage and add mean FD as a covariate at the group
level."

**Q. Why FA only?**
"Pragmatic. The acquisition supports NODDI (b = 700/1000/2800), and
that is the natural next step. The plan was to land the standard-FA
analysis first."

**Q. Why six seeds?**
"They are conventional language-network coordinates from prior
studies. We acknowledge in the limitations that the seeds are fixed
in MNI space and that subject-specific Alice-localiser ROIs would be
the natural follow-up."

**Q. What's with the sex effect?**
"Secondary, not pre-registered, but consistent with the prior
resting-state literature (lower IFG–STG coupling in male participants
on average). It's reported descriptively only — we are not making a
claim about sex differences here."
