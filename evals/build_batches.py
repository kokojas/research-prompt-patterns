#!/usr/bin/env python3
"""Create preregistered, independently repeated Oracle prompt-evaluation batches."""

from __future__ import annotations

import argparse
import json
import random
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORACLE_ROOT = Path("/Users/maksym/Downloads/Codex (1)/oracle-runs")
CREATE_BATCH = Path("/Users/maksym/.codex/skills/oracle-task-orchestrator/scripts/create_batch.py")
PROMPTS = {
    "verify": (ROOT / "prompts/verification-first.txt").read_text(encoding="utf-8").strip(),
    "horizon": (ROOT / "prompts/question-horizon.txt").read_text(encoding="utf-8").strip(),
    "clarify": (ROOT / "prompts/clarify-then-investigate.txt").read_text(encoding="utf-8").strip(),
}
ARMS = ("base", "verify", "horizon", "two_turn_base", "clarify")

SEEDS = {
    "F01": "Can Mira get a refund for a digital course?",
    "F02": "Which clinic should a patient choose from its treatment success statistics?",
    "F03": "Was my grant application submitted before the deadline?",
    "F04": "How many rows qualify for this report and what is the sum?",
    "A01": "What does a positive screening result mean for this person?",
    "A02": "What is the shortest schedule for our jobs on two machines?",
    "A03": "Did our new dashboard cause the server errors?",
    "A04": "Should we build this feature now or first run an experiment?",
    "P01": "Which database recovery option should our firm buy?",
    "P02": "What should our only available engineer do first today?",
    "P03": "How should we migrate our large database while preserving rollback?",
    "P04": "Why did checkout conversion fall after our redesign?",
    "U01": "Should our five-person team buy an analytics platform or build our own?",
    "U02": "Why did sign-ups fall this month? What should we do next?",
    "U03": "I know some Python. What should I learn next to become useful on a data team?",
    "PILOT01": "What is the final price after this discount, tax, and shipping?",
    "PILOT02": "Should we move our team's internal notes to a new tool?",
    "PILOT03": "Is this battery defect covered by the warranty?",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--concurrency", type=int, default=5)
    args = parser.parse_args()
    if args.repeats < 1:
        raise SystemExit("--repeats must be >= 1")

    task_file = ROOT / "evals" / ("pilot-tasks.json" if args.pilot else "tasks.json")
    tasks = json.loads(task_file.read_text(encoding="utf-8"))
    task_ids = [task["id"] for task in tasks]
    if len(task_ids) != len(set(task_ids)):
        raise SystemExit("Duplicate task ids")

    design = [
        {"task_id": task["id"], "arm": arm, "repeat": repeat, "category": task["category"]}
        for task in tasks
        for repeat in range(1, args.repeats + 1)
        for arm in ARMS
    ]
    random.Random(20260929).shuffle(design)
    staging = ORACLE_ROOT / "research-prompt-benchmark" / f"{args.run_id}-items.json"
    staging.parent.mkdir(parents=True, exist_ok=True)
    staging.write_text(
        json.dumps([{"title": f"{row['task_id']}-{row['arm']}-r{row['repeat']}", "brief": "Preregistered prompt evaluation"} for row in design], indent=2) + "\n",
        encoding="utf-8",
    )
    command = [
        "python3", str(CREATE_BATCH), "--brief", "Research prompt comparison: five arms with identical model and effort",
        "--artifact", "text", "--items-file", str(staging),
        "--task-slug", "research-prompt-benchmark", "--run-id", args.run_id,
        "--engine", "api", "--model", "gpt-5.6-sol", "--reasoning-effort", "high",
        "--reasoning-mode", "standard", "--independent-replicates",
        "--concurrency", str(args.concurrency), "--output-root", str(ORACLE_ROOT),
    ]
    batch_path = Path(subprocess.check_output(command, text=True).strip())
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    task_by_id = {task["id"]: task for task in tasks}
    for row, item in zip(design, batch["items"], strict=True):
        task = task_by_id[row["task_id"]]
        seed = SEEDS[task["id"]]
        followup = "Here are the complete case details and my answers to your relevant questions. Please now give your final answer to the original question.\n\n" + task["prompt"]
        arm = row["arm"]
        if arm == "base":
            initial, followups = task["prompt"], []
        elif arm == "verify":
            initial, followups = task["prompt"] + "\n\n" + PROMPTS["verify"], []
        elif arm == "horizon":
            initial, followups = task["prompt"] + "\n\n" + PROMPTS["horizon"], []
        elif arm == "two_turn_base":
            initial, followups = seed, [followup]
        else:
            initial, followups = seed + "\n\n" + PROMPTS["clarify"], [followup]
        chain_path = Path(item["chainPath"])
        chain = json.loads(chain_path.read_text(encoding="utf-8"))
        chain["promptChain"] = {"initialPrompt": initial, "followUps": followups}
        chain_path.write_text(json.dumps(chain, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        row["item_id"] = item["id"]
        row["seed"] = seed
    (batch_path.parent / "design.json").write_text(json.dumps(design, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (batch_path.parent / "tasks.json").write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(batch_path)
    print(f"{len(tasks)} tasks × {args.repeats} repeats × {len(ARMS)} arms = {len(design)} independent conversations")


if __name__ == "__main__":
    main()
