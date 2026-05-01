"""
Embed existing PNG figures into PROJECT_REPORT.md.

Usage (from repo root):
  .venv\\Scripts\\python.exe embed_report_figures.py

The script writes/replaces everything between:
  <!-- REPORT_FIGURES_AUTO_BEGIN -->
  <!-- REPORT_FIGURES_AUTO_END -->

If those markers are missing, it inserts the block immediately before "## 8. Discussion".

Only files that exist on disk are included. Paths in markdown use forward slashes
(relative to the repository root) so GitHub / Pandoc / VS Code preview resolve correctly.
"""
from __future__ import annotations

import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPORT = BASE / "PROJECT_REPORT.md"

MARK_BEGIN = "<!-- REPORT_FIGURES_AUTO_BEGIN -->"
MARK_END = "<!-- REPORT_FIGURES_AUTO_END -->"


def rel(p: Path) -> str:
    return p.relative_to(BASE).as_posix()


def exists(rel_posix: str) -> bool:
    return (BASE / rel_posix).is_file()


def img_md(path_posix: str, alt: str, caption: str | None = None) -> str:
    lines = [f"![{alt}]({path_posix})", ""]
    if caption:
        lines.insert(0, f"*{caption}*")
        lines.insert(1, "")
    return "\n".join(lines)


def collect_sections() -> list[tuple[str, list[tuple[str, str, str | None]]]]:
    """
    (section_title, [(rel_path, alt, optional_caption), ...])
    Order is intentional: sample/design -> ROIs -> FC -> motion/predictors -> TBSS -> summary.
    """
    sections: list[tuple[str, list[tuple[str, str, str | None]]]] = []

    results_dir = [
        ("derivatives/results/figures/fig1_predictors.png", "Fig 1 predictors", "Design / predictors summary (`derivatives/results/figures/`)."),
        ("derivatives/results/figures/fig2_pipeline.png", "Fig 2 pipeline", "Methods pipeline schematic."),
        ("derivatives/results/figures/fig3_tbss.png", "Fig 3 TBSS", "TBSS / skeleton / group diffusion QC."),
        ("derivatives/results/figures/fig4_fc_results.png", "Fig 4 FC results", "Functional connectivity results summary."),
        ("derivatives/results/figures/fig5_results_table.png", "Fig 5 results table", "Tabular results figure."),
        ("derivatives/results/figures/fig6_power.png", "Fig 6 power", "Power / effect-size context (if generated)."),
    ]

    legacy_figures = [
        ("derivatives/figures/predictor_distributions.png", "Predictor distributions", "`derivatives/figures/` — cohort demographics / predictors."),
        ("derivatives/figures/rois_mni.png", "ROIs on MNI", "Seed ROIs in MNI space."),
        ("derivatives/figures/rois_legend.png", "ROI legend", "ROI colour legend."),
        ("derivatives/figures/group_fc_matrix.png", "Group FC matrix", "Group-mean connectivity matrix."),
        ("derivatives/figures/connectome_glass.png", "Connectome glass brain", "Glass-brain connectome."),
        ("derivatives/figures/fc_scatter.png", "FC scatter", "Scatter / predictor vs FC."),
    ]

    unified = [
        ("derivatives/fc_unified_n51/group_fc_matrix_unified.png", "Unified group FC matrix", "`fc_unified_n51` — 51-subject FC matrix."),
        ("derivatives/fc_unified_n51/connectome_unified.png", "Unified connectome", None),
        ("derivatives/fc_unified_n51/fc_scatter_unified.png", "Unified FC scatter", None),
    ]

    conn_pre = [
        ("derivatives/fc_conn_preprocessed/group_fc_matrix_conn.png", "CONN-style FC matrix", "`fc_conn_preprocessed` variant."),
        ("derivatives/fc_conn_preprocessed/connectome_conn.png", "CONN-style connectome", None),
        ("derivatives/fc_conn_preprocessed/fc_scatter_conn.png", "CONN-style FC scatter", None),
    ]

    tbss = [
        (
            "derivatives/dwi_processed/tbss/FA/slicesdir/grota.png",
            "TBSS FA slicesdir montage A",
            "FSL `slicesdir` montage after `tbss_1_preproc` (`FA/slicesdir/grota.png` … `groti.png` are companion panels).",
        ),
        (
            "derivatives/dwi_processed/tbss/FA/slicesdir/sub-pp128_FA_FA.png",
            "Example subject FA (TBSS input)",
            "Single-subject FA snapshot (`sub-pp*_FA_FA.png` exists for each cohort ID).",
        ),
        (
            "derivatives/dwi_processed/tbss/slicesdir/grota.png",
            "TBSS root slicesdir grota",
            "Alternate `slicesdir` at `tbss/slicesdir/` (post-registration stage).",
        ),
    ]

    def filt(items: list[tuple[str, str, str | None]]) -> list[tuple[str, str, str | None]]:
        return [t for t in items if exists(t[0])]

    if r := filt(results_dir):
        sections.append(("### A. Curated results figures (`derivatives/results/figures/`)", r))
    if r := filt(legacy_figures):
        sections.append(("### B. General analysis figures (`derivatives/figures/`)", r))
    if r := filt(unified):
        sections.append(("### C. Unified n=51 FC outputs (`derivatives/fc_unified_n51/`)", r))
    if r := filt(conn_pre):
        sections.append(("### D. CONN-pipeline-style FC (`derivatives/fc_conn_preprocessed/`)", r))
    if r := filt(tbss):
        sections.append(("### E. DWI / TBSS QC montages (`slicesdir`) ", r))

    return sections


def build_block() -> str:
    lines = [
        MARK_BEGIN,
        "",
        "## Figure gallery (embedded from existing project files)",
        "",
        "The images below are **not** recomputed here; they are **linked** from paths under `derivatives/`. ",
        "Re-run **`embed_report_figures.py`** after you add or replace PNGs.",
        "",
    ]
    sections = collect_sections()
    if not sections:
        lines.append("*No matching PNG files were found under the expected `derivatives/` paths.*")
        lines.append("")
        lines.append(MARK_END)
        return "\n".join(lines)

    for title, items in sections:
        lines.append(title)
        lines.append("")
        for path_posix, alt, cap in items:
            lines.append(img_md(path_posix, alt, cap))
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "**Note:** NIfTI statistical maps (`tbss_results_*.nii.gz`) are not shown inline; open them in "
        "FSLeyes / MRIcroGL. PDF QC reports live under `derivatives/validation/`."
    )
    lines.append("")
    lines.append(MARK_END)
    return "\n".join(lines)


def patch_report(text: str, block: str) -> str:
    pattern = re.compile(
        re.escape(MARK_BEGIN) + r"[\s\S]*?" + re.escape(MARK_END),
        re.MULTILINE,
    )
    if pattern.search(text):
        return pattern.sub(block, text, count=1)

    anchor = "\n## 8. Discussion\n"
    idx = text.find(anchor)
    if idx == -1:
        raise SystemExit("Could not find '## 8. Discussion' and no figure markers present.")
    insert = "\n" + block + "\n"
    return text[:idx] + insert + text[idx:]


def main() -> None:
    if not REPORT.is_file():
        raise SystemExit(f"Missing {REPORT}")
    block = build_block()
    text = REPORT.read_text(encoding="utf-8")
    new_text = patch_report(text, block)
    REPORT.write_text(new_text, encoding="utf-8", newline="\n")
    n_figs = sum(len(items) for _, items in collect_sections())
    print(f"Updated {REPORT.name} ({n_figs} figure link(s) in gallery).")


if __name__ == "__main__":
    main()
