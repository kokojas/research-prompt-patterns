#!/usr/bin/env python3
"""Extract observable metrics from the frozen browser dialogues, with no judge model."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

HEADER = "## Initial response\n\n### Answer\n"
FOLLOWUP = "\n## Follow-up 1\n\n### Prompt\n"
URL = re.compile(r"https?://[^\s<>\]\)]+")
WORD = re.compile(r"\b[\w'-]+\b", re.UNICODE)


def split_answer(text: str, two_turn: bool) -> tuple[str | None, str]:
    if not two_turn:
        if not text.strip():
            raise ValueError("Empty answer")
        return None, text.strip()
    if not text.startswith(HEADER) or FOLLOWUP not in text:
        raise ValueError("Unexpected two-turn transcript shape")
    first, rest = text[len(HEADER):].split(FOLLOWUP, 1)
    if "\n### Answer\n" not in rest:
        raise ValueError("Missing final answer")
    final = rest.split("\n### Answer\n", 1)[1].strip()
    if not first.strip() or not final:
        raise ValueError("Empty first or final answer")
    return first.strip(), final


def clean_url(value: str) -> str:
    parts = urlsplit(value.rstrip(".,;"))
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if not k.startswith("utm_")])
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path, query, ""))


def urls(text: str) -> list[str]:
    return sorted(set(clean_url(match.group(0)) for match in URL.finditer(text)))


def question_lines(first: str) -> list[str]:
    lines = first.splitlines()
    # URL query strings (notably ?utm_source=...) are not clarification questions.
    def is_question(line: str) -> bool:
        return "?" in URL.sub("", line)
    numbered = [line.strip() for line in lines if re.match(r"^\s*(?:\d{1,2}[.)]|[-*])\s+", line) and is_question(line)]
    if numbered:
        return numbered
    return [line.strip() for line in lines if is_question(line) and not line.strip().startswith("*")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-batch", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    source_path = Path(args.source_batch).resolve()
    batch = json.loads(source_path.read_text(encoding="utf-8"))
    design = {r["item_id"]: r for r in json.loads((source_path.parent / "design.json").read_text(encoding="utf-8"))}
    tasks = {r["id"]: r for r in json.loads((source_path.parent / "tasks.json").read_text(encoding="utf-8"))}
    records = []
    for item in batch["items"]:
        if item["status"] != "completed":
            raise ValueError(f"Incomplete item: {item['id']}")
        row = design[item["id"]]
        two_turn = row["arm"] in ("clarify", "two_turn_base")
        item_dir = Path(item["itemDir"])
        raw = (item_dir / "chat.md").read_text(encoding="utf-8")
        first, final = split_answer(raw, two_turn)
        manifest = json.loads((item_dir / "manifest.json").read_text(encoding="utf-8"))
        usage = manifest.get("oracleUsage") or {}
        if usage.get("mode") != "browser" or not usage.get("browserModelSelection", {}).get("verified") or not usage.get("browserThinkingSelection", {}).get("verified"):
            raise ValueError(f"Unverified model or effort: {item['id']}")
        source_urls = urls(final)
        records.append({
            "item_id": item["id"], "task_id": row["task_id"], "category": row["category"],
            "arm": row["arm"], "repeat": row["repeat"], "two_turn": two_turn,
            "answer_sha256": hashlib.sha256(raw.encode()).hexdigest(),
            "first_turn": first, "final_answer": final,
            "first_words": len(WORD.findall(first)) if first else 0,
            "final_words": len(WORD.findall(final)), "total_response_words": len(WORD.findall(first)) + len(WORD.findall(final)) if first else len(WORD.findall(final)),
            "first_question_lines": question_lines(first) if first else [],
            "question_mark_count": first.count("?") if first else None,
            "source_urls": source_urls, "direct_url_count": len(source_urls),
            "native_citation_count": len(re.findall(r":chatgpt-content-reference", final)),
            "marker_only_export": bool(re.search(r":chatgpt-content-reference", final)) and not bool(source_urls),
            "elapsed_s": (usage.get("elapsedMs") or 0) / 1000,
            "official_anchor_urls": tasks[row["task_id"]]["sources"],
        })
    if len(records) != 225 or len({r["item_id"] for r in records}) != 225:
        raise ValueError("Expected 225 unique answers")
    combo = Counter((r["task_id"], r["arm"]) for r in records)
    if len(combo) != 75 or any(n != 3 for n in combo.values()):
        raise ValueError("Expected three repeats for each of 75 task-arm pairs")
    records.sort(key=lambda r: (r["task_id"], r["arm"], r["repeat"]))
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "local_records.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    by_arm = defaultdict(list)
    for r in records:
        by_arm[r["arm"]].append(r)
    summary = {a: {
        "n": len(v), "mean_final_words": sum(r["final_words"] for r in v) / len(v),
        "mean_total_words": sum(r["total_response_words"] for r in v) / len(v),
        "mean_elapsed_s": sum(r["elapsed_s"] for r in v) / len(v),
        "with_direct_url": sum(bool(r["direct_url_count"]) for r in v),
        "marker_only_exports": sum(r["marker_only_export"] for r in v),
        "mean_first_question_lines": (sum(len(r["first_question_lines"]) for r in v) / len(v)) if v[0]["two_turn"] else None,
    } for a, v in by_arm.items()}
    (out / "local_observables.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
