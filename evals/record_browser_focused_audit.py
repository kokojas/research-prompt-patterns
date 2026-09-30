#!/usr/bin/env python3
"""Record the focused 45-dialogue evidence review and explicit score revisions.

This audit examines the sampled answer openings, criterion evidence extracts,
first-turn questions, and complete text for disputed criteria. It inventories
source URLs but does not certify support for every material claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


# One-based criterion indexes. Every override below was checked against the
# saved final answer; the unmodified 45 packets were also inspected.
REVISIONS = {
    "58-p04-base-r1": {"required": {6: (0, "No explicit clean-environment install/test of the built wheel.")},
                         "latent": {2: (0, "Wheel test is present; sdist-content or editable-behavior check is not.")}},
    "93-p04-base-r2": {"latent": {2: (0, "Actual-wheel validation does not check sdist content or editable behavior."),
                                      3: (1, "Explicitly states setup.py remains a valid configuration file.")}},
    "04-p04-base-r3": {"latent": {2: (0, "Builds both artifacts but does not examine sdist contents or editable behavior.")}},
    "54-a03-base-r2": {"latent": {1: (0, "Calls ShakeMap an estimate but does not explain that it may be revised.")}},
    "102-p04-verify-r1": {"latent": {3: (1, "Explicitly distinguishes deprecated setup.py CLI from retained configuration file.")}},
    "16-f03-two-turn-base-r2": {"latent": {3: (1, "Says Apophis study is scheduled for 2029, distinguishing plan from completed events.")}},
    "100-a03-two-turn-base-r1": {"required": {3: (1, "Opening explicitly rejects both identical intensity and equal inspection priority.")}},
    "119-u02-two-turn-base-r3": {"required": {1: (1, "Explicitly says neither town can be chosen before local shaking evidence.")}},
    "144-a02-two-turn-base-r3": {"required": {3: (1, "Explicitly rejects definitive breach of the long-term Paris level.")}},
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", required=True)
    ap.add_argument("--records", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    sample = json.loads(Path(args.sample).read_text(encoding="utf-8"))
    records = {r["item_id"]: r for r in json.loads(Path(args.records).read_text(encoding="utf-8"))}
    rows = []
    for selected in sample:
        r = records[selected["item_id"]]
        revised_required = r["required_hits"].copy()
        revised_latent = r["latent_hits"].copy()
        changes = []
        for group, scores in (("required", revised_required), ("latent", revised_latent)):
            for index, (value, reason) in REVISIONS.get(r["item_id"], {}).get(group, {}).items():
                old = scores[index - 1]
                if old == value:
                    raise ValueError(f"Redundant revision: {r['item_id']} {group} {index}")
                scores[index - 1] = value
                changes.append({"group": group, "checkpoint": index, "old": old, "new": value, "reason": reason})
        rows.append({
            "item_id": r["item_id"], "task_id": r["task_id"], "arm": r["arm"],
            "sample_reason": selected["reason"], "answer_sha256": r["answer_sha256"],
            "scope": "answer opening, all criterion evidence extracts, source-host inventory, and targeted full-text review of disputed criteria",
            "source_inventory": "native citation markers without direct URL" if r["marker_only_export"] else
                                "at least one task-relevant official host URL" if r["official_link_present"] else
                                "direct URL present but no task-relevant official host detected",
            "screened_required": r["required_hits"], "reviewed_required": revised_required,
            "screened_latent": r["latent_hits"], "reviewed_latent": revised_latent,
            "screened_clarify": r["clarify_hits"],
            "changes": changes,
            "source_support_certified": False,
            "material_error_rate_certified": False,
        })
    if len(rows) != 45 or len({r["item_id"] for r in rows}) != 45:
        raise ValueError("Expected 45 unique audit records")
    output = {
        "scope_note": "Focused review of 45 sampled dialogues (20%). This is not a full claim-by-claim fact check; source-host presence is not source support. Grading was not fully blind, a deviation from the frozen protocol.",
        "n_reviewed": len(rows),
        "n_changed_dialogues": sum(bool(r["changes"]) for r in rows),
        "n_changed_checkpoints": sum(len(r["changes"]) for r in rows),
        "rows": rows,
    }
    Path(args.out).write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: output[k] for k in ("n_reviewed", "n_changed_dialogues", "n_changed_checkpoints")}))


if __name__ == "__main__":
    main()
