#!/usr/bin/env python3
"""Validate blind grades and compute task-clustered prompt-evaluation summaries."""

from __future__ import annotations

import argparse
import json
import random
import re
import statistics as stats
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPARISONS = {"verify": "base", "horizon": "base", "clarify": "two_turn_base"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_json_answer(text: str):
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    return json.loads(stripped)


def mean(values):
    return sum(values) / len(values) if values else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-batch", required=True)
    parser.add_argument("--judge-batch", required=True)
    parser.add_argument("--out-dir", default=str(ROOT / "evals"))
    args = parser.parse_args()
    source_path = Path(args.source_batch).resolve()
    judge_path = Path(args.judge_batch).resolve()
    source = load_json(source_path)
    judge = load_json(judge_path)
    design = {row["item_id"]: row for row in load_json(source_path.parent / "design.json")}
    blind_map = {(row["task_id"], row["response_id"]): row for row in load_json(judge_path.parent / "blind_map.json")}
    tasks = {task["id"]: task for task in load_json(source_path.parent / "tasks.json")}
    source_items = {item["id"]: item for item in source["items"]}
    records = []

    for judge_item in judge["items"]:
        task_id = judge_item["title"].removeprefix("blind-grade-")
        task = tasks[task_id]
        data = parse_json_answer((Path(judge_item["itemDir"]) / "chat.md").read_text(encoding="utf-8"))
        scores = data.get("scores")
        expected_ids = {code for key, code in blind_map if key == task_id}
        if not isinstance(scores, list) or {score.get("id") for score in scores} != expected_ids:
            raise ValueError(f"Judge IDs mismatch for {task_id}")
        for score in scores:
            for key, expected_length in (("required", len(task["required"])), ("latent", len(task["latent"]))):
                if not isinstance(score.get(key), list) or len(score[key]) != expected_length or any(value not in (0, 1) for value in score[key]):
                    raise ValueError(f"Invalid {key} scores for {task_id}/{score.get('id')}")
            mapping = blind_map[(task_id, score["id"])]
            item = source_items[mapping["item_id"]]
            item_dir = Path(item["itemDir"])
            final = (item_dir / "chat.md").read_text(encoding="utf-8")
            first_path = item_dir / "round_1.md"
            first = first_path.read_text(encoding="utf-8") if first_path.exists() else None
            if first is not None:
                if not isinstance(score.get("clarify"), list) or len(score["clarify"]) != len(task["clarify"]) or any(value not in (0, 1) for value in score["clarify"]):
                    raise ValueError(f"Invalid clarification scores for {task_id}/{score['id']}")
            manifest = load_json(item_dir / "manifest.json")
            usages = manifest.get("roundUsages") or ([manifest.get("oracleUsage")] if manifest.get("oracleUsage") else [])
            cost = sum((entry.get("usage") or {}).get("cost") or 0 for entry in usages)
            elapsed = sum((entry.get("elapsedMs") or 0) for entry in usages)
            in_tokens = sum((entry.get("usage") or {}).get("inputTokens") or 0 for entry in usages)
            out_tokens = sum((entry.get("usage") or {}).get("outputTokens") or 0 for entry in usages)
            reasoning_values = [(entry.get("usage") or {}).get("reasoningTokens") for entry in usages]
            reasoning_tokens = sum(value for value in reasoning_values if isinstance(value, (int, float)))
            # Oracle's API usage object can report zero for an unavailable counter.
            # Keep that value out of efficiency comparisons unless it is positive.
            reasoning_tokens = reasoning_tokens if reasoning_tokens > 0 else None
            records.append({
                "task_id": task_id, "category": task["category"], "arm": mapping["arm"], "repeat": mapping["repeat"],
                "item_id": mapping["item_id"], "required": score["required"], "required_score": mean(score["required"]),
                "latent": score["latent"], "latent_score": mean(score["latent"]),
                "clarify": score.get("clarify"), "clarify_score": mean(score["clarify"]) if first is not None else None,
                "question_count": score.get("question_count"), "duplicate_questions": score.get("duplicate_questions"),
                "irrelevant_questions": score.get("irrelevant_questions"), "waited": score.get("waited"),
                "material_errors": score.get("material_errors"), "judge_reason": score.get("brief_reason"),
                "words": len(re.findall(r"\b[\w'-]+\b", final)), "cost_usd": cost, "elapsed_ms": elapsed,
                "input_tokens": in_tokens, "output_tokens": out_tokens, "reasoning_tokens": reasoning_tokens,
                "first_turn": first, "final_answer": final,
            })

    expected = len(source["items"])
    if len(records) != expected:
        raise ValueError(f"Expected {expected} responses, got {len(records)}")
    records.sort(key=lambda row: (row["task_id"], row["arm"], row["repeat"]))
    by_task_arm = defaultdict(list)
    by_arm = defaultdict(list)
    for row in records:
        by_task_arm[(row["task_id"], row["arm"])].append(row)
        by_arm[row["arm"]].append(row)
    arms = {}
    for arm, rows in by_arm.items():
        arms[arm] = {
            "n": len(rows),
            "required": mean([mean([r["required_score"] for r in by_task_arm[(task_id, arm)]]) for task_id in tasks]),
            "latent": mean([mean([r["latent_score"] for r in by_task_arm[(task_id, arm)]]) for task_id in tasks]),
            "clarify": mean([r["clarify_score"] for r in rows if r["clarify_score"] is not None]),
            "error_rate": mean([int((r["material_errors"] or 0) > 0) for r in rows]),
            "words": mean([r["words"] for r in rows]),
            "cost_usd": mean([r["cost_usd"] for r in rows]),
            "elapsed_s": mean([r["elapsed_ms"] / 1000 for r in rows]),
            "reasoning_tokens": mean([r["reasoning_tokens"] for r in rows if r["reasoning_tokens"] is not None]),
            "question_count": mean([r["question_count"] for r in rows if r["question_count"] is not None]),
            "duplicate_questions": mean([r["duplicate_questions"] for r in rows if r["duplicate_questions"] is not None]),
            "irrelevant_questions": mean([r["irrelevant_questions"] for r in rows if r["irrelevant_questions"] is not None]),
            "wait_rate": mean([int(r["waited"]) for r in rows if r["waited"] is not None]),
        }

    rng = random.Random(70419)
    comparisons = {}
    for arm, control in COMPARISONS.items():
        metric = "clarify_score" if arm == "clarify" else "latent_score" if arm == "horizon" else "required_score"
        task_diffs = {
            task_id: mean([row[metric] for row in by_task_arm[(task_id, arm)]]) - mean([row[metric] for row in by_task_arm[(task_id, control)]])
            for task_id in tasks
        }
        ids = list(tasks)
        bootstrap = sorted(mean([task_diffs[rng.choice(ids)] for _ in ids]) for _ in range(10000))
        difference = mean(list(task_diffs.values()))
        error_difference = arms[arm]["error_rate"] - arms[control]["error_rate"]
        lower, upper = bootstrap[250], bootstrap[9749]
        comparisons[arm] = {
            "control": control, "primary_metric": metric, "difference": difference,
            "bootstrap_95": [lower, upper], "task_differences": task_diffs,
            "task_wins": sum(v > 0.00001 for v in task_diffs.values()),
            "task_ties": sum(abs(v) <= 0.00001 for v in task_diffs.values()),
            "task_losses": sum(v < -0.00001 for v in task_diffs.values()),
            "error_rate_difference": error_difference,
            "supported_as_useful": difference >= 0.10 and lower > 0 and error_difference <= 0.05,
        }
    category = {}
    for cat in sorted({task["category"] for task in tasks.values()}):
        category[cat] = {
            arm: mean([row["required_score"] for row in records if row["category"] == cat and row["arm"] == arm])
            for arm in by_arm
        }
    summary = {
        "source_run": source_path.parent.name, "judge_run": judge_path.parent.name,
        "model": "gpt-5.6-sol", "judge_model": "gpt-6-astra", "task_count": len(tasks),
        "repeats": len({row["repeat"] for row in records}), "response_count": len(records),
        "arms": arms, "comparisons": comparisons, "category_required": category,
        "task_categories": {task_id: task["category"] for task_id, task in tasks.items()},
        "total_generation_cost_usd": sum(row["cost_usd"] for row in records),
    }
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"task_count": len(tasks), "response_count": len(records), "comparisons": comparisons, "total_generation_cost_usd": summary["total_generation_cost_usd"]}, indent=2))


if __name__ == "__main__":
    main()
