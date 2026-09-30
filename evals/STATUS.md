# Evaluation status

**All 225 browser dialogues completed on 30 September 2026.** The dataset contains 15 official-source research cases × 5 conditions × 3 independent repetitions, with 45 dialogues per condition and 90 two-turn dialogues. Runs used oracle-task-orchestrator, GPT-5.6 Sol, verified High and Web Search, with concurrency 3.

The first pass completed 200 and failed 25. Recovery reran those 25 dialogues; three additional Search verification failures occurred during retries. All 28 invalid attempts are logged and excluded from the 225-answer dataset. The [execution audit](EXECUTION_AUDIT.md) reports the checks and seven whole-transcript citation-export warnings; the local final-answer extraction finds nine marker-only final replies. No technically failed dialogue remains.

**Exploratory local screening is complete.** [The analysis](LOCAL_ANALYSIS.md) covers all 225 answers with transparent phrase checks, task-level comparisons, four figures, and a focused 45-dialogue audit. It does not certify claim-level source support or material-error rates for all responses, and the focused audit was not fully blind. The frozen protocol's confirmatory effectiveness decision remains pending. The [case set](browser-web-tasks.json) and canonical prompt hashes remain unchanged.

The separate 15-dialogue pilot and the superseded 107 API responses are excluded from final comparisons.
