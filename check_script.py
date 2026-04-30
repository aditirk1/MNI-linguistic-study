from nilearn import plotting
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

fig_dir = Path(r'C:\Users\Aditi\ds005613\derivatives\results\figures')
fig_dir.mkdir(parents=True, exist_ok=True)
stats_dir = Path(r'C:\Users\Aditi\ds005613\derivatives\dwi_processed\tbss\stats')

# ── FIGURE 1: Predictor distributions and correlation ──────────────────
leapq = pd.read_csv(r'C:\Users\Aditi\ds005613\derivatives\nebula_101_leapq_data.tsv', sep='\t')
subset = Path(r'C:\Users\Aditi\ds005613\subset_50_participants.txt').read_text().splitlines()
subset = [s.strip() for s in subset if s.strip()]
leapq_sub = leapq[leapq['participant_id'].isin(subset)]

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
fig.patch.set_facecolor('white')

axes[0].hist(leapq_sub['nlang'], bins=10, color='steelblue', edgecolor='white', linewidth=0.5)
axes[0].set_xlabel('Number of languages (nlang)', fontsize=11)
axes[0].set_ylabel('Count', fontsize=11)
axes[0].set_title('Language Diversity', fontsize=12, fontweight='bold')
axes[0].spines['top'].set_visible(False)
axes[0].spines['right'].set_visible(False)

axes[1].hist(leapq_sub['entropy_curr_tot_exp'], bins=12, color='coral', edgecolor='white', linewidth=0.5)
axes[1].set_xlabel('Entropy of current exposure', fontsize=11)
axes[1].set_ylabel('Count', fontsize=11)
axes[1].set_title('Exposure Balance', fontsize=12, fontweight='bold')
axes[1].spines['top'].set_visible(False)
axes[1].spines['right'].set_visible(False)

axes[2].scatter(leapq_sub['nlang'], leapq_sub['entropy_curr_tot_exp'],
                alpha=0.6, color='purple', s=40)
m, b = np.polyfit(leapq_sub['nlang'], leapq_sub['entropy_curr_tot_exp'], 1)
x = np.linspace(leapq_sub['nlang'].min(), leapq_sub['nlang'].max(), 100)
axes[2].plot(x, m*x+b, 'purple', linewidth=2)
r, p = stats.pearsonr(leapq_sub['nlang'], leapq_sub['entropy_curr_tot_exp'])
axes[2].set_xlabel('nlang', fontsize=11)
axes[2].set_ylabel('entropy', fontsize=11)
axes[2].set_title(f'Predictor correlation\nr = {r:.2f}, p < 0.001', fontsize=12, fontweight='bold')
axes[2].spines['top'].set_visible(False)
axes[2].spines['right'].set_visible(False)

plt.suptitle('Sample Characterization: Two Dimensions of Multilingual Experience',
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(fig_dir / 'fig1_predictors.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig1_predictors.png")

# ── FIGURE 2: Analysis pipeline diagram ───────────────────────────────
# Multimodal integration: both branches end in MNI space. fMRI path follows
# normalize_bold_to_mni.m (coregister mean BOLD→T1, segment T1, deform to MNI, smooth).
# DWI path: FSL preprocessing + TBSS registration to FMRIB58 / MNI FA skeleton.
# Layout: generous limits + pad so leftmost box is not cropped; pathway labels
# sit clear of the rounded boxes (not on their borders).
fig, ax = plt.subplots(figsize=(14, 5.5))
ax.set_xlim(-0.85, 14.6)
ax.set_ylim(1.08, 5.55)
ax.axis("off")
fig.patch.set_facecolor("white")

boxes = [
    (1.2, 3.5, "Raw Data\n(NEBULA101\nn=51)", "#E8F4FD"),
    (3.7, 4.2, "DWI prep\n(FSL + TBSS\n→ MNI skeleton)", "#D5E8D4"),
    (3.7, 2.65, "fMRI (SPM25)\ncoreg BOLD→T1 → MNI\nsmooth 6 mm", "#FFF2CC"),
    (6.7, 4.2, "TBSS\n(tbss_1–4)", "#D5E8D4"),
    (6.7, 2.65, "FC extraction\n(Nilearn, MNI\nseeds + motion)", "#FFF2CC"),
    (9.7, 4.2, "FA skeleton\nvoxelwise", "#D5E8D4"),
    (9.7, 2.65, "ROI\nconnectivity", "#FFF2CC"),
    (12.7, 3.5, "GLM\nnlang + entropy\n+ covariates", "#F8CECC"),
]

for x, y, label, color in boxes:
    rect = mpatches.FancyBboxPatch(
        (x - 1, y - 0.5),
        2,
        1,
        boxstyle="round,pad=0.1",
        facecolor=color,
        edgecolor="gray",
        linewidth=1.5,
    )
    ax.add_patch(rect)
    ax.text(x, y, label, ha="center", va="center", fontsize=8.5, fontweight="bold")

arrows = [
    (2.2, 3.5, 3.7, 4.2),
    (2.2, 3.5, 3.7, 2.65),
    (4.7, 4.2, 6.7, 4.2),
    (4.7, 2.65, 6.7, 2.65),
    (7.7, 4.2, 9.7, 4.2),
    (7.7, 2.65, 9.7, 2.65),
    (10.7, 4.2, 12.7, 3.5),
    (10.7, 2.65, 12.7, 3.5),
]
for x1, y1, x2, y2 in arrows:
    ax.annotate(
        "",
        xy=(x2 - 0.9, y2),
        xytext=(x1 + 0.05, y1),
        arrowprops=dict(arrowstyle="->", color="gray", lw=1.5),
    )

# Labels above / below the first step of each branch (gap from box edges)
ax.text(
    3.7,
    5.12,
    "DWI pathway",
    ha="center",
    fontsize=9,
    color="#5B9B6B",
    fontweight="bold",
)
ax.text(
    3.7,
    1.52,
    "fMRI pathway",
    ha="center",
    fontsize=9,
    color="#B7A000",
    fontweight="bold",
)

ax.text(
    7.7,
    1.22,
    "Branches converge in MNI space (standard template); multimodal integration uses shared ROI MNI coordinates.",
    ha="center",
    fontsize=8,
    style="italic",
    color="#555555",
)

ax.set_title("Multimodal Analysis Pipeline", fontsize=13, fontweight="bold", pad=16)
fig.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.06)
plt.savefig(
    fig_dir / "fig2_pipeline.png",
    dpi=150,
    bbox_inches="tight",
    pad_inches=0.35,
    facecolor="white",
)
plt.close()
print("Saved fig2_pipeline.png")

# ── FIGURE 3: TBSS results ─────────────────────────────────────────────
mean_fa = str(stats_dir / 'mean_FA.nii.gz')
fig, axes = plt.subplots(2, 2, figsize=(16, 8))
fig.patch.set_facecolor('white')
axes = axes.flatten()

contrasts = [
    ('tbss_results_tfce_corrp_tstat1.nii.gz', 'nlang → FA (positive)\nmax corrp = 0.59'),
    ('tbss_results_tfce_corrp_tstat2.nii.gz', 'nlang → FA (negative)\nmax corrp = 0.37'),
    ('tbss_results_tfce_corrp_tstat3.nii.gz', 'entropy → FA (positive)\nmax corrp = 0.57'),
    ('tbss_results_tfce_corrp_tstat4.nii.gz', 'entropy → FA (negative)\nmax corrp = 0.36'),
]

for idx, (fname, title) in enumerate(contrasts):
    stat_map = str(stats_dir / fname)
    plotting.plot_stat_map(
        stat_map, bg_img=mean_fa,
        threshold=0.3, display_mode='z',
        cut_coords=[-20, -5, 10, 25],
        colorbar=True, title=title,
        axes=axes[idx], cmap='hot', vmax=1.0,
        annotate=False
    )

plt.suptitle('TBSS Results: White Matter FA\n'
             'No voxels survive FWE correction (threshold = 0.95 shown as dashed line)',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(fig_dir / 'fig3_tbss.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig3_tbss.png")

# ── FIGURE 4: FC results ───────────────────────────────────────────────
fc_df = pd.read_csv(r'C:\Users\Aditi\ds005613\derivatives\nilearn_fc_motion\fc_outcomes_motion.csv')
design = pd.read_csv(r'C:\Users\Aditi\ds005613\shared_design_matrix.csv')
df = fc_df.merge(design, on='participant_id')

fig, axes = plt.subplots(2, 3, figsize=(15, 8))
fig.patch.set_facecolor('white')

outcomes = ['mean_lang_fc', 'IFG_STG_left', 'IFG_STG_right']
labels = ['Mean language\nnetwork FC', 'IFG-STG\n(left hemisphere)', 'IFG-STG\n(right hemisphere)']
preds = [
    ('nlang_z', 'Number of languages\n(z-scored)', 'steelblue'),
    ('entropy_z', 'Exposure balance\n(z-scored)', 'coral'),
]

beta_entropy_right = -0.082
p_entropy_right = 0.135

for col, (outcome, olabel) in enumerate(zip(outcomes, labels)):
    for row, (pred, plabel, color) in enumerate(preds):
        ax = axes[row, col]
        ax.scatter(df[pred], df[outcome], alpha=0.5, color=color, s=35, zorder=3)
        m, b_coef = np.polyfit(df[pred], df[outcome], 1)
        x_line = np.linspace(df[pred].min(), df[pred].max(), 100)
        ax.plot(x_line, m*x_line+b_coef, color=color, linewidth=2)
        r_val, p_val = stats.pearsonr(df[pred], df[outcome])
        sig = '*' if p_val < 0.05 else 'ns'
        ax.set_title(f'{olabel}\nr={r_val:.2f}, p={p_val:.3f} ({sig})',
                     fontsize=9, fontweight='bold')
        ax.set_xlabel(plabel, fontsize=8)
        ax.set_ylabel('FC (Fisher-z)', fontsize=8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(labelsize=8)

plt.suptitle('Resting-State FC Results: Language Experience Predictors\n'
             'Motion-corrected, n=51 | No predictor significant after correction',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(fig_dir / 'fig4_fc_results.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig4_fc_results.png")

# ── FIGURE 5: Summary results table ───────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 5))
ax.axis('off')
fig.patch.set_facecolor('white')

table_data = [
    ['DWI / TBSS', 'nlang (diversity)', 'White matter FA', '0.59', 'Null', '—'],
    ['DWI / TBSS', 'entropy (balance)', 'White matter FA', '0.57', 'Null', '—'],
    ['rs-fMRI FC', 'nlang (diversity)', 'Mean language FC', 'p=0.856', 'Null', 'β=0.007'],
    ['rs-fMRI FC', 'entropy (balance)', 'Mean language FC', 'p=0.388', 'Null', 'β=-0.028'],
    ['rs-fMRI FC', 'entropy (balance)', 'IFG-STG right', 'p=0.135', 'Null (trend)', 'β=-0.082'],
    ['rs-fMRI FC', 'Sex (covariate)', 'All FC outcomes', 'p<0.015', 'Significant*', 'β≈-0.26'],
]

columns = ['Modality', 'Predictor', 'Outcome', 'p-value', 'Result', 'Effect size']
table = ax.table(cellText=table_data, colLabels=columns,
                 loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 1.8)

for j in range(len(columns)):
    table[0, j].set_facecolor('#2C3E50')
    table[0, j].set_text_props(color='white', fontweight='bold')

for i in range(1, len(table_data)+1):
    result = table_data[i-1][4]
    if 'Significant' in result:
        color = '#D5E8D4'
    elif 'trend' in result:
        color = '#FFF2CC'
    else:
        color = '#F5F5F5' if i % 2 == 0 else 'white'
    for j in range(len(columns)):
        table[i, j].set_facecolor(color)

ax.set_title('Summary of All Results', fontsize=13, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(fig_dir / 'fig5_results_table.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig5_results_table.png")

# ── FIGURE 6: Power analysis ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
fig.patch.set_facecolor('white')

sample_sizes = np.arange(20, 250, 5)
effect_sizes = [0.20, 0.25, 0.30, 0.35]
colors_power = ['#E74C3C', '#E67E22', '#27AE60', '#2980B9']

for r_target, col in zip(effect_sizes, colors_power):
    powers = []
    for n in sample_sizes:
        t = r_target * np.sqrt(n-2) / np.sqrt(1-r_target**2)
        power = stats.t.cdf(t - stats.t.ppf(0.95, df=n-2), df=n-2)
        powers.append(max(0, min(1, power)))
    ax.plot(sample_sizes, powers, color=col, linewidth=2.5, label=f'r = {r_target}')

ax.axvline(x=51, color='black', linestyle='--', linewidth=2, label='This study (n=51)')
ax.axhline(y=0.80, color='gray', linestyle=':', linewidth=1.5, label='80% power threshold')
ax.fill_between([20, 51], [0, 0], [1, 1], alpha=0.07, color='red')
ax.set_xlabel('Sample size (n)', fontsize=11)
ax.set_ylabel('Statistical power', fontsize=11)
ax.set_title('Post-hoc Power Analysis\nWhy null results are expected at n=51',
             fontsize=12, fontweight='bold')
ax.legend(fontsize=9, loc='lower right')
ax.set_ylim(0, 1.05)
ax.set_xlim(20, 250)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(55, 0.35, 'Underpowered\nregion', fontsize=9, color='red', alpha=0.7)
plt.tight_layout()
plt.savefig(fig_dir / 'fig6_power.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig6_power.png")

print(f"\nAll 6 figures saved to: {fig_dir}")