#!/usr/bin/env python3
"""Generate the code-derived figures used by the JOSS submission.

The workflow figure is a schematic derived from the package modules and public
interfaces.  The K-factor panel uses deterministic synthetic data solely to
illustrate the robust estimator; it is not an experimental performance claim.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from saxsabs import estimate_k_factor_robust
from saxsabs.constants import NIST_SRM3600_DATA


MM_PER_INCH = 25.4
FULL_WIDTH_MM = 183.0
FULL_WIDTH_IN = FULL_WIDTH_MM / MM_PER_INCH

mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "font.size": 7.5,
        "axes.titlesize": 7,
        "axes.labelsize": 7,
        "legend.fontsize": 7,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 0.7,
        "figure.facecolor": "white",
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    }
)

COLORS = {
    "ink": "#23343D",
    "muted": "#60737D",
    "input": "#E8F0FA",
    "interface": "#FFF0D9",
    "core": "#E7F3EA",
    "output": "#F3E8F1",
    "gate": "#EEF1F3",
    "accent": "#2F6F8F",
    "warning": "#C7772A",
}


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    """Save editable vectors and a 600 dpi raster at the declared final size."""

    output_dir.mkdir(parents=True, exist_ok=True)
    svg_path = output_dir / f"{stem}.svg"
    fig.savefig(svg_path)
    # Matplotlib terminates many SVG path lines with a space. Normalize the
    # generated text so the version-controlled source passes Git whitespace checks.
    svg_lines = svg_path.read_text(encoding="utf-8").splitlines()
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_lines) + "\n",
        encoding="utf-8",
    )
    fig.savefig(output_dir / f"{stem}.pdf")
    fig.savefig(output_dir / f"{stem}.png", dpi=600)


def _box(
    ax: plt.Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
    facecolor: str,
    *,
    fontsize: float = 6.6,
    weight: str = "normal",
) -> None:
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.08,rounding_size=0.12",
        facecolor=facecolor,
        edgecolor=COLORS["ink"],
        linewidth=0.8,
    )
    ax.add_patch(patch)
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight=weight,
        color=COLORS["ink"],
        linespacing=1.2,
    )


def _arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str | None = None,
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=8,
            color=color or COLORS["muted"],
            linewidth=0.9,
            shrinkA=3,
            shrinkB=3,
        )
    )


def make_workflow_figure(output_dir: Path) -> None:
    """Render the package architecture and the checks applied before export."""

    fig, ax = plt.subplots(figsize=(FULL_WIDTH_IN, 3.65))
    fig.subplots_adjust(left=0.012, right=0.988, bottom=0.025, top=0.985)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    headings = [
        (1.50, "Inputs", "input"),
        (4.75, "Interfaces", "interface"),
        (8.25, "Scientific core", "core"),
        (12.30, "Outputs", "output"),
    ]
    for x, label, color_key in headings:
        ax.text(x, 7.45, label, ha="center", va="center", fontsize=7, fontweight="bold")
        ax.plot([x - 0.82, x + 0.82], [7.16, 7.16], color=COLORS[color_key], linewidth=4)

    inputs = [
        (6.05, "2D detector frames\nand instrument headers"),
        (4.45, "External 1D profiles\nand correction metadata"),
        (2.85, "SRM 3600, water, or\na user-supplied reference"),
    ]
    for y, label in inputs:
        _box(ax, 1.50, y, 2.45, 0.88, label, COLORS["input"], fontsize=6.2)

    _box(
        ax,
        4.75,
        5.55,
        2.35,
        1.22,
        "CLI utilities and strict\nBL19B2 batch workflow",
        COLORS["interface"],
        fontsize=6.2,
    )
    _box(
        ax,
        4.75,
        3.45,
        2.35,
        1.22,
        "SAXSAbs Workbench\ncalibration and export",
        COLORS["interface"],
        fontsize=6.2,
    )
    _box(
        ax,
        4.75,
        1.55,
        2.35,
        1.0,
        "Python API\npublic package functions",
        COLORS["interface"],
        fontsize=6.2,
    )

    core = [
        (6.35, "Parse, normalize, and\nvalidate inputs"),
        (5.15, "Reduce detector data and\nintegrate with pyFAI"),
        (3.95, "Estimate robust K and\npropagate uncertainty"),
        (2.75, "Check intensity state and\ncorrection history"),
        (1.55, "Write canSAS, NXcanSAS,\nand calibrated 2D outputs"),
    ]
    for y, label in core:
        _box(ax, 8.25, y, 3.05, 0.76, label, COLORS["core"], fontsize=6.0)

    outputs = [
        (5.85, "Absolute-scale 1D profiles\nand calibrated 2D packages"),
        (4.05, "canSAS XML and\nNXcanSAS HDF5"),
        (2.25, "Calibration records, source\nhashes, QC, and run reports"),
    ]
    for y, label in outputs:
        _box(ax, 12.30, y, 2.65, 1.0, label, COLORS["output"], fontsize=6.1)

    _arrow(ax, (2.78, 4.45), (3.52, 4.45), color=COLORS["accent"])
    _arrow(ax, (5.97, 4.45), (6.67, 4.45), color=COLORS["accent"])
    _arrow(ax, (9.80, 4.45), (10.85, 4.45), color=COLORS["accent"])

    gate = FancyBboxPatch(
        (0.18, 0.12),
        13.64,
        0.62,
        boxstyle="round,pad=0.04,rounding_size=0.12",
        facecolor=COLORS["gate"],
        edgecolor=COLORS["warning"],
        linewidth=0.9,
    )
    ax.add_patch(gate)
    ax.text(
        7,
        0.43,
        "Required checks before calibrated output: units · transmission · thickness · "
        "correction state · calibration provenance",
        ha="center",
        va="center",
        fontsize=6.2,
        color=COLORS["ink"],
        fontweight="bold",
    )
    save_figure(fig, output_dir, "fig_workflow")
    plt.close(fig)


def make_kfactor_figure(output_dir: Path) -> None:
    """Illustrate the robust K estimator with deterministic synthetic data."""

    rng = np.random.default_rng(42)
    q_ref = NIST_SRM3600_DATA[:, 0]
    i_ref = NIST_SRM3600_DATA[:, 1]
    k_true = 0.035

    q_dense = np.sort(
        np.unique(np.concatenate([np.linspace(float(q_ref.min()), float(q_ref.max()), 240), q_ref]))
    )
    i_ref_dense = np.interp(q_dense, q_ref, i_ref)
    i_meas_dense = i_ref_dense / k_true * (1 + rng.normal(0, 0.025, q_dense.size))
    outlier_reference_indices = np.array([1, 13])
    outlier_dense_indices = np.searchsorted(q_dense, q_ref[outlier_reference_indices])
    outlier_ratios = np.array([k_true * 3.5, k_true * 0.3])
    i_meas_dense[outlier_dense_indices] = i_ref[outlier_reference_indices] / outlier_ratios
    if np.any(i_ref_dense <= 0.0) or np.any(i_meas_dense <= 0.0):
        raise ValueError("log-scale demonstration requires strictly positive intensities")
    i_meas_at_ref = np.interp(q_ref, q_dense, i_meas_dense)
    ratios = i_ref / i_meas_at_ref
    estimate = estimate_k_factor_robust(
        q_dense,
        i_meas_dense,
        q_ref,
        i_ref,
        q_window=(float(q_ref.min()), float(q_ref.max())),
    )
    inliers = np.array(
        [
            np.any(np.isclose(ratio, estimate.ratios_used, rtol=1e-12, atol=1e-15))
            for ratio in ratios
        ]
    )

    fig, axes = plt.subplots(1, 2, figsize=(FULL_WIDTH_IN, 2.75))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.20, top=0.87, wspace=0.30)

    left, right = axes
    left.semilogy(
        q_ref,
        i_ref,
        "s-",
        color=COLORS["warning"],
        markersize=3.2,
        linewidth=1.0,
    )
    left.semilogy(
        q_dense,
        i_meas_dense * k_true,
        linestyle="none",
        marker=".",
        markersize=2.0,
        color=COLORS["accent"],
        alpha=0.85,
    )
    left.set(xlabel=r"$q$ ($\mathrm{\AA}^{-1}$)", ylabel=r"$I(q)$ ($\mathrm{cm}^{-1}$)")
    left.set_title("Reference and rescaled synthetic profile", loc="left", fontweight="bold")
    left.text(-0.12, 1.04, "a", transform=left.transAxes, fontsize=8, fontweight="bold")
    left.legend(["NIST SRM 3600", "Synthetic measured profile"], frameon=False, loc="upper right")
    left.text(
        0.03,
        0.04,
        "SYNTHETIC DEMO",
        transform=left.transAxes,
        fontsize=7,
        color=COLORS["muted"],
        bbox={"facecolor": "white", "edgecolor": COLORS["muted"], "pad": 2},
    )

    right.scatter(q_ref[inliers], ratios[inliers], s=16, color=COLORS["accent"], label="Inlier")
    right.scatter(
        q_ref[~inliers],
        ratios[~inliers],
        s=30,
        marker="x",
        linewidth=1.4,
        color=COLORS["warning"],
        label="Rejected",
    )
    right.axhline(
        estimate.k_factor,
        color=COLORS["ink"],
        linewidth=1.0,
        label=f"K = {estimate.k_factor:.4f}",
    )
    right.set(xlabel=r"$q$ ($\mathrm{\AA}^{-1}$)", ylabel=r"$I_{ref}/I_{meas}$")
    right.set_title("Robust K estimate", loc="left", fontweight="bold")
    right.text(-0.12, 1.04, "b", transform=right.transAxes, fontsize=8, fontweight="bold")
    right.legend(frameon=False, ncol=2, loc="upper right")

    save_figure(fig, output_dir, "fig_kfactor_demo")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="also render the explicitly synthetic K-factor demonstration",
    )
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    make_workflow_figure(output_dir)
    if args.demo:
        make_kfactor_figure(output_dir)
    print(f"Wrote JOSS figures to {output_dir}")


if __name__ == "__main__":
    main()
