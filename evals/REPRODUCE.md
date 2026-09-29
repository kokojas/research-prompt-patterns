# Reproducing the browser comparison

The active comparison uses `oracle-task-orchestrator` with GPT-5.6 Sol, verified High, Web Search, and an isolated ChatGPT project. The frozen [protocol](BROWSER_WEB_PROTOCOL.md), [15 cases](browser-web-tasks.json), [pilot cases](browser-web-pilot-tasks.json), and [batch builder](build_browser_batches.py) are in this directory. `preregistration.json` inside each run records case and prompt hashes before model execution.

The local Oracle engine is version `0.21.3-chatwork.1`, a compatibility build for the ChatGPT browser layout. It is documented in the local engine repair report; an official upstream release should be tested separately before substitution.

```bash
python3 evals/build_browser_batches.py --pilot --repeats 1 --run-id browser-web-pilot-20260929 --concurrency 3
python3 "$HOME/.codex/skills/oracle-task-orchestrator/scripts/run_batch.py" \
  --batch "$(pwd)/../oracle-runs/research-prompt-benchmark/browser-web-pilot-20260929/batch.json" \
  --resume --concurrency 3

python3 evals/build_browser_batches.py --repeats 3 --run-id browser-web-final-20260929 --concurrency 3
python3 "$HOME/.codex/skills/oracle-task-orchestrator/scripts/run_batch.py" \
  --batch "$(pwd)/../oracle-runs/research-prompt-benchmark/browser-web-final-20260929/batch.json" \
  --resume --concurrency 3
```

Batch creation must use a **new run ID** for an independent replication; the commands above refer to the existing frozen runs. Resume the existing final batch if interrupted. Completed items are skipped. Before retrying a failed item, inspect its transcript and manifest to establish whether a user message reached the website; document and exclude any invalid partial conversation. The older API run with 107 responses is archived and excluded.

A successful run has `mode=browser`, a nonempty `chat.md`, direct source URLs where required, verified `browserModelSelection` for GPT-5.6 Sol, verified `browserThinkingSelection` with `resolvedLabel=High`, and `--browser-research search` in its command. Browser token values are estimates; do not interpret them as API charges or observed private reasoning.
