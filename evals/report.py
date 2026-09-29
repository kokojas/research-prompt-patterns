#!/usr/bin/env python3
"""Create a concise bilingual, data-backed interpretation of the final evaluation."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"
ARMS = ("base", "verify", "horizon", "two_turn_base", "clarify")
NAMES = {
    "base": ("Plain request", "Звичайний запит"),
    "verify": ("Verification First", "Перевірка перед висновком"),
    "horizon": ("Question Horizon", "Горизонт питань"),
    "two_turn_base": ("Two-turn control", "Контроль: два раунди"),
    "clarify": ("Clarify Then Investigate", "Уточнити, потім дослідити"),
}
METRICS = {"verify": "required", "horizon": "latent", "clarify": "clarify"}


def pct(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:.1f}%"


def verdict(comp: dict, uk: bool) -> str:
    if comp["supported_as_useful"]:
        return "Підтверджена перевага на цих задачах" if uk else "Supported improvement on these cases"
    if comp["difference"] < 0 and comp["bootstrap_95"][1] < 0:
        return "Погіршення на цих задачах" if uk else "Worse on these cases"
    return "Надійної переваги не показано" if uk else "No reliable improvement shown"


def make(summary: dict, records: list[dict], uk: bool) -> str:
    n = summary["task_count"]
    runs = summary["response_count"]
    lines = [
        "# Звіт про порівняння промптів" if uk else "# Prompt evaluation report",
        "",
        f"{n} різних задач · {runs} незалежних діалогів · по три повтори для кожної умови. Пілотні задачі вилучені з цих підрахунків." if uk else f"{n} distinct cases · {runs} independent conversations · three repeats per condition. Pilot cases are excluded from these estimates.",
        "",
        "## Основний висновок" if uk else "## Main finding", "",
    ]
    for arm in ("verify", "horizon", "clarify"):
        comp = summary["comparisons"][arm]
        low, high = comp["bootstrap_95"]
        lines.append(f"- **{NAMES[arm][1 if uk else 0]}:** {verdict(comp, uk)}. {comp['difference'] * 100:+.1f} {('в.п.' if uk else 'pp')} (95% {'інтервал' if uk else 'interval'} {low * 100:+.1f} {'до' if uk else 'to'} {high * 100:+.1f}); {comp['task_wins']}/{comp['task_ties']}/{comp['task_losses']} {'краще / без змін / гірше за задачами' if uk else 'case wins / ties / losses'}." )
    lines += ["", "## Числа за умовами" if uk else "## Conditions at a glance", "", "| Умова | Обов’язкові критерії | Корисні приховані аспекти | Теми уточнень | Частка з помилкою | Слів | Секунд | Ціна за діалог |" if uk else "| Condition | Required checkpoints | Useful latent issues | Clarification topics | Material error rate | Words | Seconds | Cost per conversation |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for arm in ARMS:
        data = summary["arms"][arm]
        lines.append(f"| {NAMES[arm][1 if uk else 0]} | {pct(data['required'])} | {pct(data['latent'])} | {pct(data['clarify'])} | {pct(data['error_rate'])} | {data['words']:.0f} | {data['elapsed_s']:.1f} | ${data['cost_usd']:.3f} |")
    lines += ["", "## Виконання задач за типом" if uk else "## Task completion by category", "", "| Тип | Звичайний запит | Перевірка | Горизонт питань | Контроль: два раунди | Уточнення + дослідження |" if uk else "| Category | Plain request | Verification First | Question Horizon | Two-turn control | Clarify Then Investigate |", "|---|---:|---:|---:|---:|---:|"]
    category_uk = {"factual": "Фактологічні", "analytical": "Аналітичні", "practical": "Практичні", "ambiguous": "Неоднозначні"}
    for cat in ("factual", "analytical", "practical", "ambiguous"):
        if cat not in summary["category_required"]:
            continue
        values = summary["category_required"][cat]
        lines.append("| " + (category_uk[cat] if uk else cat.title()) + " | " + " | ".join(pct(values[arm]) for arm in ARMS) + " |")
    lines += ["", "## Що означають порівняння" if uk else "## How to read the comparisons", ""]
    lines.append("Перша й друга надбудови порівнюються з ідентичним однораундовим запитом без надбудови. Третій промпт порівнюється з двораундовим контролем, якому у другому повідомленні передані ті самі факти. Первинна метрика різна за механізмом: правильність обов’язкових пунктів, змістовне охоплення прихованих питань і якість уточнень відповідно." if uk else "The first two patterns are paired with the same one-turn request without the add-on. The third is paired with a two-turn control that receives the same facts in the second user message. The primary metric follows each mechanism: required task checkpoints, substantive coverage of latent issues, and consequential clarification topics respectively.")
    lines += ["", "## Результат за кожною задачею" if uk else "## Case-level differences", "", "| Задача | Тип | Перевірка | Горизонт питань | Уточнення |" if uk else "| Case | Category | Verification First | Question Horizon | Clarify Then Investigate |", "|---|---|---:|---:|---:|"]
    categories = summary["task_categories"]
    category_uk = {"factual": "фактологічна", "analytical": "аналітична", "practical": "практична", "ambiguous": "неоднозначна"}
    for task_id in sorted(categories):
        vals = [summary["comparisons"][arm]["task_differences"][task_id] * 100 for arm in ("verify", "horizon", "clarify")]
        cat = category_uk[categories[task_id]] if uk else categories[task_id]
        lines.append(f"| {task_id} | {cat} | {vals[0]:+.1f} pp | {vals[1]:+.1f} pp | {vals[2]:+.1f} pp |")
    lines += ["", "## Варіативність і витрати" if uk else "## Repeat variability and cost", ""]
    for arm in ("verify", "horizon", "clarify"):
        control = summary["comparisons"][arm]["control"]
        metric = METRICS[arm] + "_score"
        spread = []
        for task_id in categories:
            values = [r[metric] for r in records if r["task_id"] == task_id and r["arm"] == arm]
            spread.append(max(values) - min(values))
        a, b = summary["arms"][arm], summary["arms"][control]
        score_key = METRICS[arm]
        efficiency = a[score_key] / max(a["cost_usd"], 1e-9)
        control_efficiency = b[score_key] / max(b["cost_usd"], 1e-9)
        speed = a[score_key] * 60 / max(a["elapsed_s"], 1e-9)
        control_speed = b[score_key] * 60 / max(b["elapsed_s"], 1e-9)
        lines.append(f"- **{NAMES[arm][1 if uk else 0]}:** {'середній розмах між трьома повторами' if uk else 'mean within-case range across three repeats'} {sum(spread)/len(spread)*100:.1f} pp; {'ціна' if uk else 'cost'} ×{a['cost_usd']/max(b['cost_usd'], 1e-9):.1f}, {'час' if uk else 'time'} ×{a['elapsed_s']/max(b['elapsed_s'], 1e-9):.1f} {'відносно контролю' if uk else 'relative to its control'}. {'Первинна оцінка на $1' if uk else 'Primary score per $1'} {efficiency:.2f} {'проти' if uk else 'vs'} {control_efficiency:.2f}; {'на хвилину' if uk else 'per minute'} {speed:.2f} {'проти' if uk else 'vs'} {control_speed:.2f}." )
    clarify = [r for r in records if r["arm"] == "clarify"]
    compliant = sum(5 <= (r["question_count"] or 0) <= 15 for r in clarify)
    waited = sum(r["waited"] is True for r in clarify)
    c = summary["arms"]["clarify"]
    lines += ["", f"{'Перший раунд третього промпту: 5–15 запитань у' if uk else 'Third-prompt first turn: 5–15 questions in'} {compliant}/{len(clarify)} {'діалогах; очікував відповіді в' if uk else 'conversations; waited for the reply in'} {waited}/{len(clarify)}. {'Середня кількість питань' if uk else 'Mean question count'} {c['question_count']:.1f}; {'зайвих' if uk else 'irrelevant'} {c['irrelevant_questions']:.1f}; {'повторних' if uk else 'duplicates'} {c['duplicate_questions']:.1f}.", ""]
    lines += ["## Межі висновку" if uk else "## Limits of inference", ""]
    lines.append("Це невеликий синтетичний набір із заздалегідь заданими критеріями. Модель-оцінювач може помилятися; дивіться журнал ручної перевірки. Задачі не перевіряють пошук актуальних джерел в інтернеті. Запуски виконані через Oracle 0.21.3 на GPT-5.6 Sol API з high effort та standard mode. Ці оцінки не описують автоматично ChatGPT у браузері чи інші моделі. Лічильник reasoning tokens у провайдера був недоступний/нульовий і не використовувався як доказ якості. Ціна включає лише генерацію відповідей, без роботи оцінювача." if uk else "This is a small synthetic case set with author-defined checkpoints. The model judge can err; see the manual audit log. These cases do not test live source retrieval. Runs used Oracle 0.21.3 with GPT-5.6 Sol API, high effort, standard mode. They do not establish identical behavior in the ChatGPT browser or other models. The provider's reasoning-token field was unavailable/zero and was not treated as an answer-quality measure. Cost includes response generation only, not judging.")
    lines += ["", "## Відтворення" if uk else "## Reproduction", "", "[Протокол](PROTOCOL.md) · [Задачі](tasks.json) · [Відповіді та оцінки](results.json) · [Підсумкові дані](summary.json) · [Ручна перевірка](AUDIT.md)" if uk else "[Protocol](PROTOCOL.md) · [Cases](tasks.json) · [Responses and grades](results.json) · [Summary data](summary.json) · [Manual audit](AUDIT.md)", ""]
    return "\n".join(lines)


def main() -> None:
    summary = json.loads((EVALS / "summary.json").read_text(encoding="utf-8"))
    records = json.loads((EVALS / "results.json").read_text(encoding="utf-8"))
    (EVALS / "REPORT.md").write_text(make(summary, records, False), encoding="utf-8")
    (EVALS / "REPORT.uk.md").write_text(make(summary, records, True), encoding="utf-8")


if __name__ == "__main__":
    main()
