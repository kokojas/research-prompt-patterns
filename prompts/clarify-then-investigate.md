# Clarify, Then Investigate

First ask the few consequential questions; after the user's reply, investigate with the same verification discipline.

| Field | Value |
|---|---|
| Category | Two-round investigation |
| Version | 1.0.0 |
| Tested model | GPT-5.6 Sol · ChatGPT browser via Oracle |
| Last verified | 2026-09-29 |

![Round one gathers decision-changing answers; round two synthesizes evidence.](../docs/assets/illustrations/clarification-rounds.png)

## Purpose

Use it when a consequential recommendation depends on the user's goals, knowledge, constraints, or evidence that the first message does not contain.

## Prompt

Append this exact text to a task request.

```text
Use this workflow for a consequential, underspecified research question or decision. Treat my first message as the beginning of a two-round exchange.

ROUND 1 — CLARIFY

Infer my likely goal and map what you still need to know about my context, existing knowledge, constraints, success criteria, evidence available, risk tolerance, and intended use of the answer. Do not assume that every category requires a question.

Ask 5 to 15 specific, nonredundant questions whose answers could materially change the investigation or recommendation. Choose the number by information value, not by filling a quota; if fewer than five material gaps exist, say this workflow is unnecessary and ask only the consequential questions. Prioritize missing decisions, definitions, constraints, and facts that would change the answer. Include a brief reason after each question. Make it easy for me to answer in a numbered list.

Do not answer the main question, start the final research, or ask a second batch of routine questions in this round. Wait for my reply.

ROUND 2 — INVESTIGATE AFTER MY REPLY

Use my answers to establish a compact working brief: goal, relevant knowledge level, constraints, success criteria, and unresolved assumptions. If I answered only some questions, proceed with explicit assumptions and conditional branches where possible. Ask another question only if an unanswered fact makes a safe or meaningful answer impossible; otherwise continue.

Treat my original question as a seed, not the boundary. Expand it into a prioritized question tree: direct question, prerequisites, likely follow-ups, expert blind spots, alternatives, risks, edge cases, and facts that could change the conclusion. Pursue material branches and stop when further expansion is unlikely to change the answer.

Treat this as a difficult, multi-step analytical task where correctness matters more than speed.

Think hard about the problem. Be thorough and check your work carefully.

Do not stop at the first plausible answer. Explore the problem sufficiently before committing to a conclusion.

Before finalizing:
- identify the material assumptions behind your conclusion;
- consider credible competing explanations or alternative solutions;
- actively look for counterexamples, contradictory evidence, edge cases, and failure modes;
- verify important factual claims against the strongest available evidence;
- where practical, independently cross-check critical conclusions using a different method, source, or line of reasoning;
- resolve material contradictions rather than silently choosing one side;
- re-check calculations, dates, causal claims, and logical dependencies that materially affect the answer.

Continue analyzing, checking, and revising until the important success criteria of the task are satisfied. Do not manufacture certainty. Distinguish established facts, strong inferences, tentative inferences, and unresolved uncertainty. Use web research when current or niche information matters; if unavailable, say what could not be verified.

Give a direct answer first, then the evidence, key assumptions, worthwhile next questions already answered, material alternatives, practical next steps, and remaining uncertainty. Tailor the depth to my knowledge level. Keep the final explanation clear; do not expose private chain-of-thought.
```

## Example task

> Should our five-person team buy an analytics platform or build one?

![A knowledge matrix highlights missing inputs before research begins.](../docs/assets/illustrations/knowledge-matrix.png)

## Research basis

This is a new synthesis of clarification, bounded question expansion, and verification. Its exact two-round behavior is assessed against a matched two-turn control receiving the same facts. [References](../REFERENCES.md).

## Known limitations

It costs an extra user turn and can over-question simple tasks. If fewer than five material gaps exist, the prompt explicitly allows fewer questions. Partial replies should lead to explicit assumptions, not endless interviewing.

## Evaluation

Protocol, scores, and raw responses: [Evaluation](https://kokojas.github.io/research-prompt-patterns/evaluation.html) · [Protocol](../evals/BROWSER_WEB_PROTOCOL.md).
