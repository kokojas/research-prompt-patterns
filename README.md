# Research Prompt Patterns

Three research prompts for checking conclusions, finding missing questions, and clarifying context before investigation.

[Explore the site](https://kokojas.github.io/research-prompt-patterns/) · [Evaluation and results](https://kokojas.github.io/research-prompt-patterns/evaluation.html) · [Українська версія](README.uk.md)

## Quick start

Open the relevant prompt, copy its English text, and append it to your task request. For the third prompt, answer its clarification questions in the next message.

## Browse prompts

| Prompt | What it does |
|---|---|
| [Verification First](prompts/verification-first.md) | A compact contract for checking assumptions, alternatives, calculations, and uncertainty before answering. |
| [Question Horizon](prompts/question-horizon.md) | Turn one question into a bounded tree of prerequisites, likely follow-ups, expert blind spots, and competing explanations. |
| [Clarify, Then Investigate](prompts/clarify-then-investigate.md) | First ask the few consequential questions; after the user's reply, investigate with the same verification discipline. |

## Compatibility

Evaluated through Oracle on the GPT-5.6 Sol API. The plain-text format can be pasted into ChatGPT, Claude, and Gemini; behavior in those interfaces and models has not been measured here.

## Quality and testing

Results from the 15 final cases will appear after scoring is complete. Quality is measured through correctness, useful expansion, clarification, errors, and cost. [Protocol](evals/PROTOCOL.md) · [Cases](evals/tasks.json) · [Results](evals/results.json) · [Report](evals/REPORT.md).

## Repository structure

- `prompts/`: canonical texts and individual GitHub pages.
- `docs/`: bilingual GitHub Pages site and illustrations.
- `evals/`: protocol, cases, responses, grades, and analysis code.
- [REFERENCES.md](REFERENCES.md): sources and evidence limits.

## License

[MIT](LICENSE) · Copyright © 2026 Maksym Klymenko.
