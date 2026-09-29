# Evaluation status

**All 225 browser dialogues completed on 30 September 2026.** The dataset contains 15 official-source research cases × 5 conditions × 3 independent repetitions, with 45 dialogues per condition and 90 two-turn dialogues. Runs used oracle-task-orchestrator, GPT-5.6 Sol, verified High and Web Search, with concurrency 3.

The first pass completed 200 and failed 25. Recovery reran those 25 dialogues; three additional Search verification failures occurred during retries. All 28 invalid attempts are logged and excluded from the 225-answer dataset. The [execution audit](EXECUTION_AUDIT.md) reports the checks and seven citation-export warnings. No technically failed dialogue remains.

**Grading is pending.** Completion is not evidence that a prompt is better. Factual grading, source verification, the manual audit, and comparative charts follow the [frozen browser protocol](BROWSER_WEB_PROTOCOL.md). The [case set](browser-web-tasks.json) and canonical prompt hashes remain unchanged.

The separate 15-dialogue pilot and the superseded 107 API responses are excluded from final comparisons.
