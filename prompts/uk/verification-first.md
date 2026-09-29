# Перевірка перед висновком

Інструкція перевіряти припущення, альтернативи, обчислення й невизначеність перед відповіддю.

| Поле | Значення |
|---|---|
| Категорія | Надійність аналізу |
| Версія | 1.0.0 |
| Тестована модель | GPT-5.6 Sol API via Oracle 0.21.3 |
| Остання перевірка | 2026-09-29 |

![Альтернативні відповіді проходять перевірки.](../../docs/assets/illustrations/verification-paths.png)

## Призначення

Використовуйте, коли перша правдоподібна відповідь може бути хибною: для тлумачення правил, числових рішень, причинних тверджень або синтезу доказів.

## Промпт

Англійський текст нижче є тестованою версією; перекладені пояснення не змінюють формулювання.

```text
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

Continue analyzing, checking, and revising until the important success criteria of the task are satisfied.

Do not manufacture certainty. Clearly distinguish established facts, strong inferences, tentative inferences, and unresolved uncertainty.

Optimize the underlying analysis for correctness, completeness, and robustness rather than speed. The final answer may be concise when appropriate, but do not reduce the depth of analysis or verification merely to make it shorter.

Provide the final conclusions, supporting evidence, important caveats, and concise rationale; do not expose private chain-of-thought.
```

## Приклад запиту

> Який із двох планів відновлення відповідає RPO 15 хвилин і RTO дві години?

![Крайовий випадок повертає висновок на перегляд.](../../docs/assets/illustrations/verification-edge-cases.png)

## Дослідницька підстава

У невеликому опублікованому тесті коротка фраза “think hard” збільшила кількість заявлених reasoning tokens; дослідження незалежної перевірки підтримує сам принцип. Жодне з них не доводить точність саме цього повного промпту. [Джерела](../../REFERENCES.md).

## Відомі обмеження

Промпт не змінює гарантовано реальне налаштування зусилля моделі й не доводить, що перевірка відбулася. Без джерел або інструментів самоперевірка може бути поверховою, а довша відповідь — лише дорожчою.

## Результати тесту

Методика, оцінки та сирі відповіді: [Оцінювання](https://kokojas.github.io/research-prompt-patterns/uk/evaluation.html) · [Протокол](../../evals/PROTOCOL.md).
