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

A browser study with GPT-5.6 Sol, High, and Web Search is running. The prompt text can be used in ChatGPT, Claude, and Gemini; other model families have not been evaluated.

## Quality and testing

Pilot complete; 225 browser conversations are running with concurrency 3. No conclusion yet. Quality is measured through correctness, useful expansion, clarification, sources, errors, and time. [Protocol](evals/BROWSER_WEB_PROTOCOL.md) · [Cases](evals/browser-web-tasks.json) · [Current status](evals/STATUS.md).

## Repository structure

- `prompts/`: canonical texts and individual GitHub pages.
- `docs/`: bilingual GitHub Pages site and illustrations.
- `evals/`: protocol, cases, responses, grades, and analysis code.
- [REFERENCES.md](REFERENCES.md): sources and evidence limits.

## License

[MIT](LICENSE) · Copyright © 2026 Maksym Klymenko.
