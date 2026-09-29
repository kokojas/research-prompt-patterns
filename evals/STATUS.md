# Evaluation status

A new browser-based, official-source comparison started on **29 September 2026** through Oracle's `oracle-task-orchestrator`. It uses GPT-5.6 Sol with verified High thinking and Web Search in the isolated ChatGPT project. The runner has **three concurrent conversations**. The frozen design contains **15 distinct research cases × 5 conditions × 3 independent repetitions = 225 conversations**.

A separate 15-conversation pilot completed successfully. All pilot runs saved responses with direct source URLs; the model and High setting were verified, including the six two-turn conversations. Pilot responses are excluded from the final analysis.

The final batch is **in progress**. No comparison or winner is reported until all valid runs are complete and graded. See [the browser protocol](BROWSER_WEB_PROTOCOL.md), [15 cases and scoring anchors](browser-web-tasks.json), and [the browser batch builder](build_browser_batches.py). Raw run logs and answers are saved separately in the Oracle experiment directory while the study runs.

The earlier API experiment stopped after 107 of 225 conversations because of account credits. Those responses are **superseded** and will not be mixed with browser results. Its original [protocol](PROTOCOL.md) and [cases](tasks.json) remain for historical audit only.
