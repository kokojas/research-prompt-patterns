#!/usr/bin/env python3
"""Select 45 browser answers for a reproducible, arm-balanced evidence review."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

ARMS = ("base", "verify", "horizon", "two_turn_base", "clarify")
PRIMARY = {"base": "linked_required_proxy", "verify": "linked_required_proxy", "horizon": "latent_coverage", "two_turn_base": "clarify_coverage", "clarify": "clarify_coverage"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rows = json.loads(Path(args.records).read_text(encoding="utf-8"))
    if len(rows) != 225:
        raise ValueError("Expected 225 records")
    rng = random.Random(450929)
    sample = []
    for arm in ARMS:
        pool = [r for r in rows if r["arm"] == arm]
        if len(pool) != 45:
            raise ValueError(f"Expected 45 in {arm}")
        by_task = defaultdict(list)
        for r in pool:
            by_task[r["task_id"]].append(r)
        metric = PRIMARY[arm]
        def surprise(r):
            value = r[metric] if r[metric] is not None else 0
            task_values = [x[metric] if x[metric] is not None else 0 for x in by_task[r["task_id"]]]
            return abs(value - sum(task_values) / len(task_values))
        chosen = []
        def take(r, reason):
            if r["item_id"] not in {x["item_id"] for x in chosen} and len(chosen) < 9:
                chosen.append({"item_id": r["item_id"], "task_id": r["task_id"], "category": r["category"],
                               "arm": arm, "repeat": r["repeat"], "reason": reason})
        for r in pool:
            if r["marker_only_export"]:
                take(r, "native citation marker without direct URL")
        for r in sorted(pool, key=lambda x: (-surprise(x), x["task_id"], x["repeat"]))[:3]:
            take(r, "large within-task deviation")
        for category in ("factual", "analytical", "practical", "ambiguous"):
            if not any(x["category"] == category for x in chosen):
                candidates = [r for r in pool if r["category"] == category and r["item_id"] not in {x["item_id"] for x in chosen}]
                if candidates:
                    take(rng.choice(candidates), "category-stratified random draw")
        remaining = [r for r in pool if r["item_id"] not in {x["item_id"] for x in chosen}]
        for r in rng.sample(remaining, 9 - len(chosen)):
            take(r, "random draw")
        sample.extend(chosen)
    if len(sample) != 45 or len({r["item_id"] for r in sample}) != 45:
        raise ValueError("Audit sample is not 45 unique answers")
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(sample, indent=2) + "\n", encoding="utf-8")
    print(f"45 answers selected (nine per arm): {dest}")


if __name__ == "__main__":
    main()
