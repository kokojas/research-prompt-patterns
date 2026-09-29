#!/usr/bin/env python3
"""Choose a reproducible 20% manual audit sample, balanced across arms."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMS = ("base", "verify", "horizon", "two_turn_base", "clarify")
PRIMARY = {"base": "required_score", "verify": "required_score", "horizon": "latent_score", "two_turn_base": "clarify_score", "clarify": "clarify_score"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default=str(ROOT / "evals/results.json"))
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    records = json.loads(Path(args.results).read_text(encoding="utf-8"))
    rng = random.Random(450929)
    selected = []
    for arm in ARMS:
        rows = [r for r in records if r["arm"] == arm]
        grouped = defaultdict(list)
        for row in rows:
            grouped[row["task_id"]].append(row)
        scored = []
        for row in rows:
            key = PRIMARY[arm]
            value = row[key] if row[key] is not None else 0
            vals = [r[key] if r[key] is not None else 0 for r in grouped[row["task_id"]]]
            disagreement = abs(value - sum(vals) / len(vals))
            surprise = disagreement + .4 * int((row["material_errors"] or 0) > 0)
            scored.append((surprise, row))
        scored.sort(key=lambda item: (-item[0], item[1]["task_id"], item[1]["repeat"]))
        chosen = [row for _, row in scored[:3]]
        remaining = [row for row in rows if row["item_id"] not in {r["item_id"] for r in chosen}]
        for cat in ("factual", "analytical", "practical", "ambiguous"):
            candidates = [r for r in remaining if r["category"] == cat]
            pick = rng.choice(candidates)
            chosen.append(pick)
            remaining.remove(pick)
        chosen.extend(rng.sample(remaining, 2))
        assert len(chosen) == 9
        selected.extend(chosen)
    output = [{"item_id": r["item_id"], "task_id": r["task_id"], "arm": r["arm"], "repeat": r["repeat"], "category": r["category"], "required": r["required"], "latent": r["latent"], "clarify": r["clarify"], "material_errors": r["material_errors"], "judge_reason": r["judge_reason"]} for r in selected]
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(output)} responses (20% of 225), nine in each arm: {dest}")


if __name__ == "__main__":
    main()
