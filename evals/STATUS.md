# Evaluation status

The three-case pilot completed and checked the Oracle engine, two-turn continuation, and blind scoring format. The separate final batch was preregistered for 15 cases × five conditions × three independent repetitions (225 conversations).

As of 2026-09-29, 107 final conversations completed and 118 did not complete. Most incomplete sessions were rejected because the OpenAI API account ran out of credits; one hit a transient rate limit and another timed out. The completed sessions and their usage records are preserved in the separate Oracle run directory. The final comparison is **not yet scored or interpretable**: this repository does not report a final winner from the partial batch.

Oracle 0.21.3 browser-mode smoke tests were also attempted. Strict model selection could not locate ChatGPT's model selector. The `current` and `ignore` picker strategies reached the composer but could not confirm that a short prompt was submitted. The browser path was therefore not substituted for the API runs.

After API billing is restored, the remaining items can be run with `--resume --concurrency 2` against the existing final batch; completed items will be skipped. The blind judge batch, manual audit, report, and charts follow only after all 225 conversations are complete. See [REPRODUCE.md](REPRODUCE.md) for the full workflow.
