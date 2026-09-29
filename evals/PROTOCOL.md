> **Historical protocol.** This self-contained API study was superseded by the [browser web-research protocol](BROWSER_WEB_PROTOCOL.md) on 2026-09-29. Its 107 completed responses are excluded from the new comparison.

# Evaluation protocol

Protocol frozen before the final runs on 2026-09-29. The pilot began while the evaluation tooling was being checked. The prompts, final cases, and criteria are in this repository; raw Oracle outputs and usage records are kept in a separate experiment directory and the publishable extracts are copied back after scoring.

## Question

Do the three prompts improve useful answers compared with a plain user request on the same task and model? A longer answer or more reported reasoning tokens alone does not count as improvement.

## Design

- A three-task pilot checks the engine, two-turn continuation, data capture, and rubric. Pilot cases are excluded from final estimates.
- The final set contains 15 distinct, self-contained cases: four factual, four analytical, four practical, and three ambiguous. All case details and scoring checkpoints were written before final model outputs were observed.
- Every case is run in five arms with three independent repetitions per arm: 225 conversations. Arms are shuffled with seed `20260929` and executed through Oracle's `oracle-task-orchestrator` batch scripts.
- `base`: exact case request, one turn. `verify`: same request plus the published Verification First prompt. `horizon`: same request plus the published Question Horizon prompt.
- `two_turn_base`: short underspecified seed, then complete case details in a user follow-up. `clarify`: same seed plus the published Clarify Then Investigate prompt, then the identical complete case details in a user follow-up. Both get the same facts and number of response opportunities.
- All arms use `gpt-5.6-sol` through Oracle API mode, `reasoning-effort=high`, `reasoning-mode=standard`, with no attached files or external tools. API mode is used because the updated Oracle browser path failed its model-selector smoke test. These results measure the API model and do not prove identical behavior in the ChatGPT website or other providers.
- Each replicate starts a fresh Oracle session. No response is fed to another replicate.

## Outcomes

The frozen `required` and `latent` arrays in `tasks.json` are the scoring anchors.

1. **Task completion (primary for Verification First):** fraction of required checkpoints that the final answer correctly and explicitly satisfies. A contradicted checkpoint scores zero. Report each task and category, not just a pooled mean.
2. **Useful expansion (primary for Question Horizon):** fraction of predefined latent issues substantively addressed and connected to the user's decision. Merely listing an issue without an explanation scores zero. Also report direct task completion so expansive but inaccurate output cannot appear successful.
3. **Clarification quality (primary for Clarify Then Investigate):** fraction of predefined `clarify` topics covered by the first turn, plus whether it asks 5–15 distinct questions, avoids duplicate or irrelevant questions, and waits for the user's reply. Final task completion is compared with `two_turn_base` after the identical facts are supplied.
4. **Error and cost guardrails:** count material false claims, unsupported categorical recommendations, response words, provider-reported input/output/reasoning tokens, wall time, and estimated API cost. Reasoning tokens are descriptive only; they are not a correctness metric.

An arm is called *supported as useful on this case set* only if its primary score improves by at least 0.10 absolute against its matched control, the task-cluster bootstrap 95% interval for the difference excludes zero, and its material-error rate does not increase by more than 0.05 absolute. Otherwise the result is described as inconclusive, mixed, or negative. These thresholds are practical conventions rather than universal laws.

## Scoring and analysis

- An evaluator sees anonymized, randomly ordered responses and the frozen case-specific rubric. It assigns binary checkpoint scores with a short quotation or reason for every zero and every material-error flag. Arm labels are hidden during scoring.
- An independent manual audit checks at least 20% of graded responses, oversampling disagreements and surprising results. Corrections are logged, not silently overwritten.
- Each task contributes one average of its three repetitions to the headline comparison. A nonparametric bootstrap resamples tasks, not individual repetitions, for 95% intervals. This preserves the 15-task unit of generalization.
- Report wins, ties, losses by task; category breakdown; within-task repeat range; and score per dollar and per second. Do not infer general superiority from this small, synthetic case set.
- Raw prompts, outputs, model settings, usage, scoring decisions, and analysis code remain available for audit. Published charts are generated from the same result file as the tables.

## Limits

The cases are deliberately self-contained to keep changing web search results from confounding the comparison. They test analysis and response structure, not real-world source retrieval. Checkpoints are authored by the project and can miss valid alternative answers. An automated judge can misread a response, so the audit and raw answers matter. ChatGPT web routing, other model families, and human preferences require separate studies.
