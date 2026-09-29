# Reproducing the comparison

The published prompts and final-case rubric are fixed in `prompts/*.txt` and `evals/tasks.json`. The pilot uses separate cases and is excluded from final estimates. Runs use Oracle 0.21.3 with an OpenAI API key that can access `gpt-5.6-sol` and `gpt-6-astra`.

Oracle's batch wrapper is the local `oracle-task-orchestrator` skill. Its `create_batch.py` and `run_batch.py` paths default to `~/.codex/skills/oracle-task-orchestrator/scripts/`; set `ORACLE_CREATE_BATCH` if the skill is elsewhere. Set `ORACLE_RUNS_DIR` to keep raw sessions outside this repository. The default is a sibling `oracle-runs/` folder.

```bash
export ORACLE_RUNS_DIR="$(pwd)/../oracle-runs"
export ORACLE_CREATE_BATCH="$HOME/.codex/skills/oracle-task-orchestrator/scripts/create_batch.py"

python3 evals/build_batches.py --pilot --repeats 1 --run-id pilot-replication --concurrency 2
python3 "$HOME/.codex/skills/oracle-task-orchestrator/scripts/run_batch.py" \
  --batch "$ORACLE_RUNS_DIR/research-prompt-benchmark/pilot-replication/batch.json" \
  --resume --concurrency 2

python3 evals/build_batches.py --repeats 3 --run-id final-replication --concurrency 3
python3 "$HOME/.codex/skills/oracle-task-orchestrator/scripts/run_batch.py" \
  --batch "$ORACLE_RUNS_DIR/research-prompt-benchmark/final-replication/batch.json" \
  --resume --concurrency 3

python3 evals/build_judge_batches.py \
  --source-batch "$ORACLE_RUNS_DIR/research-prompt-benchmark/final-replication/batch.json" \
  --run-id final-judge-replication
python3 "$HOME/.codex/skills/oracle-task-orchestrator/scripts/run_batch.py" \
  --batch "$ORACLE_RUNS_DIR/research-prompt-benchmark/final-judge-replication/batch.json" \
  --resume --concurrency 2

python3 evals/analyze.py \
  --source-batch "$ORACLE_RUNS_DIR/research-prompt-benchmark/final-replication/batch.json" \
  --judge-batch "$ORACLE_RUNS_DIR/research-prompt-benchmark/final-judge-replication/batch.json" \
  --out-dir evals

python3 -m pip install matplotlib
python3 evals/plot.py
python3 evals/report.py
python3 site/build.py
```

The grader sees shuffled response IDs rather than arm labels. `evals/analyze.py` validates the IDs and score-array lengths before computing task-balanced estimates. The same `results.json` and `summary.json` drive the report, site, and Matplotlib figure. Inspect `evals/AUDIT.md` for manual score checks and corrections.

Oracle API sessions can hit provider limits. Resume the same batch after transient rate limits; never count a failed item as a response. If the account runs out of credits, restore billing before resuming. The saved completed sessions are skipped by `--resume`.
