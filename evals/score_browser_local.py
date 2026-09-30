#!/usr/bin/env python3
"""Run transparent, conservative content checks on saved browser replies.

This is a screening analysis. Regex hits are not a substitute for claim-level
semantic/source adjudication; the report must say so explicitly.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

from browser_local_rules import C, L, R


def mean(values):
    return sum(values) / len(values) if values else None


def score_groups(groups, text):
    return [int(all(re.search(pattern, text, re.I | re.S) for pattern in group)) for group in groups]


def substantive_text(final):
    match = re.search(r"^#{1,3}\s+A\.\s*Direct answer\b", final, re.I | re.M)
    if match:
        final = final[match.start():]
    return final


def official_link_present(row):
    anchor_hosts = {urlsplit(u).netloc.lower().removeprefix("www.") for u in row["official_anchor_urls"]}
    # Only the current task's source family may satisfy this inventory check.
    extras = {
        "F03": {"jpl.nasa.gov"}, "F04": {"noaa.gov", "wmo.int"},
        "A02": {"wmo.int"},
        "A01": {"github.com"}, "P03": {"github.com"},
        "A04": {"pypa.io"}, "P04": {"pypa.io"},
        "U01": {"energystar.gov"},
    }
    allowed_hosts = anchor_hosts | extras.get(row["task_id"], set())
    def match_host(u):
        host = urlsplit(u).netloc.lower().removeprefix("www.")
        return any(host == allowed or host.endswith("." + allowed) for allowed in allowed_hosts)
    return any(match_host(u) for u in row["source_urls"])


def task_bootstrap(diffs, rng, n=10000):
    keys = list(diffs)
    draws = sorted(mean([diffs[rng.choice(keys)] for _ in keys]) for _ in range(n))
    return [draws[int(.025 * n)], draws[int(.975 * n)-1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    records = json.loads(Path(args.records).read_text(encoding="utf-8"))
    for row in records:
        task = row["task_id"]
        final = substantive_text(row["final_answer"])
        questions = "\n".join(row["first_question_lines"])
        row["required_hits"] = score_groups(R[task], final)
        # These frozen checkpoints forbid a specific error. Silence about the
        # wrong primitive or a private-sector deadline is not an omission.
        if task == "U03":
            row["required_hits"][2] = int(not bool(re.search(r"ML[- ]?KEM.{0,70}(?:for|is|as).{0,35}signatur|signatur.{0,60}(?:use|with).{0,30}ML[- ]?KEM", final, re.I | re.S)))
        if task in {"P01", "U03"}:
            idx = 5
            row["required_hits"][idx] = int(not bool(re.search(r"(?:your (?:company|team)|private (?:company|team)).{0,90}(?:must|required|mandatory).{0,45}(?:2030|2035|deadline)|(?:must|required|mandatory).{0,80}(?:2030|2035).{0,80}(?:your (?:company|team)|private (?:company|team))", final, re.I | re.S)))
        row["latent_hits"] = score_groups(L[task], final)
        row["clarify_hits"] = score_groups(C[task], questions) if row["two_turn"] else None
        row["required_coverage"] = mean(row["required_hits"])
        row["latent_coverage"] = mean(row["latent_hits"])
        row["clarify_coverage"] = mean(row["clarify_hits"]) if row["two_turn"] else None
        row["official_link_present"] = official_link_present(row)
        row["linked_required_proxy"] = row["required_coverage"] * int(row["official_link_present"])
        row["question_count_proxy"] = len(row["first_question_lines"]) if row["two_turn"] else None
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "local_scored_records.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    grouped = defaultdict(list)
    by_arm = defaultdict(list)
    for r in records:
        grouped[(r["task_id"], r["arm"])].append(r)
        by_arm[r["arm"]].append(r)
    arms = {}
    for arm, rows in by_arm.items():
        arms[arm] = {
            "n": len(rows), "required_coverage": mean([r["required_coverage"] for r in rows]),
            "latent_coverage": mean([r["latent_coverage"] for r in rows]),
            "clarify_coverage": mean([r["clarify_coverage"] for r in rows if r["clarify_coverage"] is not None]),
            "linked_required_proxy": mean([r["linked_required_proxy"] for r in rows]),
            "official_link_rate": mean([r["official_link_present"] for r in rows]),
            "direct_url_rate": mean([bool(r["direct_url_count"]) for r in rows]),
            "mean_final_words": mean([r["final_words"] for r in rows]),
            "mean_total_words": mean([r["total_response_words"] for r in rows]),
            "mean_elapsed_s": mean([r["elapsed_s"] for r in rows]),
            "mean_question_count_proxy": mean([r["question_count_proxy"] for r in rows if r["question_count_proxy"] is not None]),
            "questions_5_to_15": sum(5 <= r["question_count_proxy"] <= 15 for r in rows if r["question_count_proxy"] is not None),
        }
    rng = random.Random(70419)
    comparisons = {}
    for arm, control, metric in (("verify", "base", "linked_required_proxy"), ("horizon", "base", "latent_coverage"), ("clarify", "two_turn_base", "clarify_coverage")):
        task_ids = sorted({r["task_id"] for r in records})
        diffs = {task: mean([r[metric] for r in grouped[(task, arm)]]) - mean([r[metric] for r in grouped[(task, control)]]) for task in task_ids}
        comparisons[arm] = {"control": control, "metric": metric, "difference": mean(list(diffs.values())),
                            "bootstrap_95": task_bootstrap(diffs, rng), "task_differences": diffs,
                            "wins": sum(v > 1e-9 for v in diffs.values()),
                            "ties": sum(abs(v) <= 1e-9 for v in diffs.values()),
                            "losses": sum(v < -1e-9 for v in diffs.values())}
    category = {cat: {arm: {m: mean([r[m] for r in rows if r["category"] == cat]) for m in ("required_coverage", "latent_coverage", "linked_required_proxy")} for arm, rows in by_arm.items()} for cat in ("factual", "analytical", "practical", "ambiguous")}
    summary = {"method": "transparent local phrase checks and direct-link inventory; not final semantic grading",
               "n_tasks": 15, "n_responses": len(records), "arms": arms, "comparisons": comparisons, "category": category}
    (out / "local_score_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"arms": arms, "comparisons": {k: {x:y for x,y in v.items() if x != "task_differences"} for k,v in comparisons.items()}}, indent=2))


if __name__ == "__main__":
    main()
