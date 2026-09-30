#!/usr/bin/env python3
"""Render observable output-cost comparison for the local benchmark report."""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    arms = json.loads(Path(args.summary).read_text(encoding="utf-8"))["arms"]
    order = ["base", "verify", "horizon", "two_turn_base", "clarify"]
    labels = ["Base", "Verification", "Question Horizon", "Two-turn base", "Clarify"]
    colors = ["#1f5c91", "#bd7d27", "#d16f4c", "#718643", "#a95b8e"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), constrained_layout=True)
    data = [
        ("Total response words", "mean_total_words", "words"),
        ("Elapsed browser run time", "mean_elapsed_s", "seconds"),
    ]
    for ax, (title, key, unit) in zip(axes, data):
        vals = [arms[a][key] for a in order]
        bars = ax.barh(labels, vals, color=colors, height=.62)
        ax.invert_yaxis()
        ax.set_title(title, loc="left", weight="bold", fontsize=13, pad=13)
        ax.set_xlabel(unit)
        ax.set_xlim(0, max(vals) * 1.19)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.xaxis.grid(True, color="#e2e8ed", linewidth=.8)
        ax.set_axisbelow(True)
        ax.tick_params(axis="y", length=0)
        for bar, v in zip(bars, vals):
            ax.text(v + max(vals) * .012, bar.get_y() + bar.get_height() / 2,
                    f"{v:,.0f}" if key == "mean_total_words" else f"{v:.1f}",
                    va="center", fontsize=9.5, color="#263743")
    fig.suptitle("Observable output cost by condition", x=.01, ha="left", fontsize=17,
                 fontweight="bold", color="#1b2733")
    fig.text(.01, 0, "45 dialogues per condition. Time includes browser execution; internal reasoning tokens and billed cost were not observed.",
             fontsize=8.5, color="#52616e")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=210, bbox_inches="tight", facecolor="white")
    print(out)


if __name__ == "__main__":
    main()
