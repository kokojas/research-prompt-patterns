#!/usr/bin/env python3
"""Make concise evidence packets for direct local review of sampled answers."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from browser_local_rules import C, L, R
from score_browser_local import substantive_text


def evidence(text, group, limit=2):
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith('#')]
    matches = []
    for pattern in group:
        for line in lines:
            if re.search(pattern, line, re.I):
                clean = re.sub(r":chatgpt-content-reference\{[^{}]*\}", "", line)
                clean = re.sub(r"\[([^]]+)\]\(https?://[^)]+\)", r"\1", clean)
                if clean not in matches:
                    matches.append(clean[:350])
                break
    return matches[:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", required=True)
    ap.add_argument("--records", required=True)
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    sample = json.loads(Path(args.sample).read_text(encoding="utf-8"))
    rows = {r["item_id"]: r for r in json.loads(Path(args.records).read_text(encoding="utf-8"))}
    tasks = {t["id"]: t for t in json.loads(Path(args.tasks).read_text(encoding="utf-8"))}
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for selected in sample:
        row = rows[selected["item_id"]]
        task = tasks[row["task_id"]]
        lines = [f"# {row['item_id']} — {row['task_id']} / {row['arm']} / repeat {row['repeat']}",
                 f"Selection: {selected['reason']}", f"Seed: {task['seed']}",
                 f"Final answer: {row['final_words']} words; URLs: {row['direct_url_count']}; marker-only: {row['marker_only_export']}",
                 f"Source URLs: {' ; '.join(row['source_urls'][:6]) or '(none)'}", "",
                 "## First-turn questions"]
        lines.extend(f"- {q[:300]}" for q in row["first_question_lines"][:17])
        if not row["first_question_lines"]:
            lines.append("(none)")
        answer = substantive_text(row["final_answer"])
        lines.extend(["", "## Direct answer opening", answer[:900].replace("\n", " "), "", "## Rubric evidence"])
        for label, criteria, patterns, scores in (("Required", task["required"], R[row["task_id"]], row["required_hits"]),
                                                   ("Latent", task["latent"], L[row["task_id"]], row["latent_hits"])):
            lines.append(f"### {label}")
            for idx, (criterion, group, score) in enumerate(zip(criteria, patterns, scores, strict=True), 1):
                lines.append(f"{idx}. [{score}] {criterion}")
                snippets = evidence(answer, group)
                lines.extend(f"   - {s}" for s in snippets)
        if row["two_turn"]:
            lines.append("### Clarification topics")
            for idx, (criterion, score) in enumerate(zip(task["clarify"], row["clarify_hits"], strict=True), 1):
                lines.append(f"{idx}. [{score}] {criterion}")
        (out / f"{row['item_id']}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(sample)} packets: {out}")


if __name__ == "__main__":
    main()
