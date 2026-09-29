# Browser web-research replication protocol

Frozen 2026-09-29 before the final batch. This replication supersedes the earlier self-contained API pilot and partial API batch. The earlier 107 API answers are excluded from every browser comparison.

## Question and design

Does a published prompt improve useful, accurate answers for nontrivial web-research questions when the model and browser tools are held constant?

- Three separate pilot cases, five arms, one repetition (15 conversations) validate browser selection, three concurrent sessions, answer capture, two-turn context, and source links. Pilot outputs do not count toward the final comparison.
- Fifteen final cases: four factual, four analytical, four practical, three ambiguous. Each case is run in five arms with three independent repetitions: **225 conversations**. Shuffle seed `20260929`; pilot seed `20260928`.
- Arms: `base` (case prompt); `verify` (same prompt plus Verification First); `horizon` (same prompt plus Question Horizon); `two_turn_base` (underspecified seed, then full case details); `clarify` (same seed plus Clarify Then Investigate, then identical full case details). The two two-turn arms have the same case information in the second user turn. First-turn behavior is assessed separately.
- Every run uses `oracle-task-orchestrator` with Oracle browser engine, GPT-5.6 Sol, verified High, selected Web Search, the isolated ChatGPT project from the skill, and a new session via `--force`. Concurrency is **3**. No API key is used. A run with unverified model or High, failed Search selection, missing answer, or failed follow-up is invalid and rerun from scratch rather than scored.
- The question and sources are stable historical/technical official publications, or a dated official guide as of 2026-09-29. Each prompt requires searching the public web. The frozen `sources` list is a grading anchor, not an attached model input. Alternative equally authoritative primary evidence may receive credit.
- Browser-generated citations can include native ChatGPT markers. Grade direct source URLs, whether each source actually supports the claim, and whether contradictory or outdated source versions were resolved. Citation count alone earns no credit.

## Outcomes

1. **Grounded task completion (primary for Verification First):** proportion of frozen `required` checkpoints correct and supported where a citation is material. A contradicted checkpoint is zero. Report per task and category.
2. **Useful expansion (primary for Question Horizon):** proportion of `latent` issues substantively investigated and linked to the user's goal. A heading or generic list is zero. Also retain grounded completion as a guardrail.
3. **Clarification value (primary for Clarify Then Investigate):** coverage of frozen `clarify` topics in the first turn, whether questions are distinct and consequential, whether it asks 5–15 where that many material gaps exist, and whether it waits. Score the final turn against `two_turn_base` with identical supplied facts.
4. **Source quality and errors:** official-source support rate for material claims, source misrepresentation, false claims, unsupported categorical recommendations, failure to acknowledge missing decision inputs, and material contradictions.
5. **Efficiency and reliability:** final answer words, elapsed time, successful completion rate, and within-task variation across three runs. Browser token counts are estimates; they are not observed internal reasoning tokens or API billing.

An improvement is supported on this case set only if the task-cluster mean primary-score difference against its matched control is at least 0.10, its 95% task-cluster bootstrap interval excludes zero, and the material-error rate does not rise by more than 0.05 absolute. Report all task-level wins, ties, and losses even if the threshold is met. These are analysis conventions, not a claim of general superiority.

## Grading and publication

Blind the five arm labels before judging. Record one evidence-based judgment per checkpoint and retain quotations or links for every zero and flagged error. Manually audit at least 20% of answers, including surprising scores and disagreements. Revisions must be logged. Resample tasks, not individual repeats, for the bootstrap interval. Final analysis and charts must use the same frozen result file. Publish the question set, settings, outputs or usable extracts, failure counts, scoring decisions, and limits alongside conclusions. No conclusion is published from the old partial API run or the pilot.

## Reproduction

```bash
python3 evals/build_browser_batches.py --pilot --repeats 1 --run-id browser-web-pilot-20260929 --concurrency 3
python3 "$HOME/.codex/skills/oracle-task-orchestrator/scripts/run_batch.py" --batch "$(pwd)/../oracle-runs/research-prompt-benchmark/browser-web-pilot-20260929/batch.json" --resume --concurrency 3
python3 evals/build_browser_batches.py --repeats 3 --run-id browser-web-final-20260929 --concurrency 3
python3 "$HOME/.codex/skills/oracle-task-orchestrator/scripts/run_batch.py" --batch "$(pwd)/../oracle-runs/research-prompt-benchmark/browser-web-final-20260929/batch.json" --resume --concurrency 3
```

`design.json`, `tasks.json`, and `preregistration.json` are copied into each run directory before model execution. The latter records SHA-256 hashes of the cases and prompts. Runs can resume by reissuing the final `run_batch.py` command; completed items are skipped. A failed item requires checking whether a ChatGPT conversation was actually submitted before any retry; if so, use a new session ID and document the invalid attempt.
