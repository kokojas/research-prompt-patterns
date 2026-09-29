#!/usr/bin/env python3
"""Draw bilingual task-level comparison plots from the scored results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parents[1]
PANELS = (
    ("verify", "Verification First", "Перевірка перед висновком", "Required checkpoints", "Обов’язкові критерії"),
    ("horizon", "Question Horizon", "Горизонт питань", "Useful latent issues", "Корисні приховані аспекти"),
    ("clarify", "Clarify Then Investigate", "Уточнити, потім дослідити", "Clarification topics", "Теми уточнень"),
)
CATEGORIES = ("factual", "analytical", "practical", "ambiguous")
COLORS = {"factual": "#087f78", "analytical": "#3376b4", "practical": "#bc6538", "ambiguous": "#824fa1"}


def build(summary: dict, path: Path, *, uk: bool) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": "#cbd5df", "axes.labelcolor": "#263544", "text.color": "#142433"})
    fig, axes = plt.subplots(3, 1, figsize=(11.5, 10.0), sharex=True)
    fig.subplots_adjust(left=.20, right=.96, top=.86, bottom=.08, hspace=.33)
    for ax, (arm, title_en, title_uk, metric_en, metric_uk) in zip(axes, PANELS, strict=True):
        comp = summary["comparisons"][arm]
        task_diffs = comp["task_differences"]
        tasks_by_cat = {cat: [(tid, value) for tid, value in task_diffs.items() if summary["task_categories"][tid] == cat] for cat in CATEGORIES}
        for i, cat in enumerate(CATEGORIES):
            points = tasks_by_cat[cat]
            n = len(points)
            for j, (task_id, value) in enumerate(points):
                offset = ((j - (n - 1) / 2) / max(n, 1)) * .42
                ax.scatter(value * 100, 3 - i + offset, s=42, color=COLORS[cat], edgecolors="white", linewidth=.8, zorder=3)
        mean = comp["difference"] * 100
        low, high = (x * 100 for x in comp["bootstrap_95"])
        ax.plot([low, high], [-.72, -.72], color="#122b3d", linewidth=2.8, solid_capstyle="round")
        ax.scatter([mean], [-.72], marker="D", s=75, color="#122b3d", zorder=4)
        ax.axvline(0, color="#7e8e99", linewidth=1.15, linestyle="--", zorder=1)
        ax.set_yticks([3, 2, 1, 0, -.72])
        ax.set_yticklabels(("Factual", "Analytical", "Practical", "Ambiguous", "Mean + 95% CI") if not uk else ("Фактологічні", "Аналітичні", "Практичні", "Неоднозначні", "Середнє + 95% ДІ"))
        ax.set_ylim(-1.08, 3.5)
        ax.set_xlim(-105, 110)
        ax.grid(axis="x", color="#e4eaf0", linewidth=.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.set_title(f"{title_uk if uk else title_en}  ·  {metric_uk if uk else metric_en}", loc="left", fontweight="bold", fontsize=12, pad=12)
        ax.text(106, 3.34, f"Mean {mean:+.1f} pp" if not uk else f"Середнє {mean:+.1f} в.п.", va="top", ha="right", fontsize=9, fontweight="bold", color="#122b3d")
    axes[-1].set_xlabel("Різниця проти відповідного контролю, відсоткові пункти" if uk else "Difference against matched control, percentage points", labelpad=10)
    fig.suptitle("Промпти проти відповідних контрольних запитів" if uk else "Prompt patterns against matched controls", x=.20, y=.965, ha="left", fontweight="bold", fontsize=18)
    fig.text(.20, .925, "15 задач, 3 повтори на умову; кожна кольорова точка — середнє для однієї задачі." if uk else "15 cases, 3 repeats per condition; each colored dot is one case mean.", fontsize=10, color="#506273")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=170, facecolor="white")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", default=str(ROOT / "evals/summary.json"))
    parser.add_argument("--out-dir", default=str(ROOT / "docs/assets/figures"))
    args = parser.parse_args()
    summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    out = Path(args.out_dir)
    build(summary, out / "paired-differences.png", uk=False)
    build(summary, out / "paired-differences-uk.png", uk=True)
    print(out)


if __name__ == "__main__":
    main()
