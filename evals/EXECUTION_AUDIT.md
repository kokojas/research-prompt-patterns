# Execution audit — 30 September 2026

**All 225 dialogues completed. No failed or missing dialogue remains.**

The original batch completed 200 dialogues and failed 25: 17 Web Search verification failures and 8 timeouts waiting for the ChatGPT session to become ready. Those 25 dialogues were rerun from scratch using the same frozen prompts and settings. Three further Web Search verification failures occurred during recovery, so 28 invalid attempts are recorded in total. The final dataset contains 225 successful dialogues, rather than counting failed attempts as answers.

Original logs and manifests are retained in `retry-history/20260930-attempt-{1,2,3}/`. The machine-readable audit and private session logs are retained in the separate experiment directory.

The final audit confirmed:

- 225 complete, nonempty saved answers with successful process exit codes.
- 45 dialogues in each of the five conditions.
- Three independent repetitions of every task/condition combination.
- Browser mode, verified GPT-5.6 Sol and verified High for every dialogue.
- 90 two-turn dialogues with the final follow-up answer captured.
- The cases and canonical prompt texts still match the preregistered hashes.

Seven exports contain native ChatGPT citation markers without direct source URLs. These original answers are retained; this is a citation/export warning for source verification during grading. It does not justify replacing an answer based on its apparent quality:
- 57-u03-verify-r1
- 58-p04-base-r1
- 93-p04-base-r2
- 98-p04-horizon-r1
- 190-p03-clarify-r1
- 192-u02-base-r1
- 206-p03-base-r2

This audit establishes execution and capture. Factual correctness, citation support, prompt comparison, and the manual scoring audit remain pending.
