#!/usr/bin/env python3
"""Build the bilingual, dependency-free GitHub Pages site from canonical prompts."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = "https://kokojas.github.io/research-prompt-patterns/"
REPO = "https://github.com/kokojas/research-prompt-patterns"

PATTERNS = [
    {
        "slug": "verification-first", "number": "01", "title": "Verification First", "title_uk": "Перевірка перед висновком",
        "tag": "Analytical reliability", "tag_uk": "Надійність аналізу",
        "summary": "A compact contract for checking assumptions, alternatives, calculations, and uncertainty before answering.",
        "summary_uk": "Інструкція перевіряти припущення, альтернативи, обчислення й невизначеність перед відповіддю.",
        "purpose": "Use it when a plausible first answer could still be wrong: policy interpretation, quantitative decisions, causal claims, or evidence-heavy synthesis.",
        "purpose_uk": "Використовуйте, коли перша правдоподібна відповідь може бути хибною: для тлумачення правил, числових рішень, причинних тверджень або синтезу доказів.",
        "steps": ["Frame the conclusion as provisional", "Test the strongest alternative and edge cases", "Verify critical claims, then state uncertainty"],
        "steps_uk": ["Вважати перший висновок попереднім", "Перевірити сильну альтернативу й крайові випадки", "Звірити ключові твердження та позначити невизначеність"],
        "example": "Which of two recovery plans meets a 15-minute RPO and a two-hour RTO?",
        "example_uk": "Який із двох планів відновлення відповідає RPO 15 хвилин і RTO дві години?",
        "limit": "It cannot switch the model's actual effort setting or guarantee that verification happened. Without evidence or tools, self-checking may be superficial; extra length can add cost without improving accuracy.",
        "limit_uk": "Промпт не змінює гарантовано реальне налаштування зусилля моделі й не доводить, що перевірка відбулася. Без джерел або інструментів самоперевірка може бути поверховою, а довша відповідь — лише дорожчою.",
        "basis": "The short “think hard” cue increased reported reasoning tokens in a small published test; independent-verification research supports the mechanism. Neither establishes the accuracy of this full prompt.",
        "basis_uk": "У невеликому опублікованому тесті коротка фраза “think hard” збільшила кількість заявлених reasoning tokens; дослідження незалежної перевірки підтримує сам принцип. Жодне з них не доводить точність саме цього повного промпту.",
        "sources": [("Think harder experiment", "https://www.raindrop.ai/blog/think-harder/"), ("Chain-of-Verification", "https://arxiv.org/abs/2309.11495")],
        "images": [("verification-paths.png", "Alternative answers pass through verification gates."), ("verification-edge-cases.png", "An edge case can send a conclusion back for revision.")],
        "images_uk": [("verification-paths.png", "Альтернативні відповіді проходять перевірки."), ("verification-edge-cases.png", "Крайовий випадок повертає висновок на перегляд.")],
    },
    {
        "slug": "question-horizon", "number": "02", "title": "Question Horizon", "title_uk": "Горизонт питань",
        "tag": "Anticipatory research", "tag_uk": "Випереджальне дослідження",
        "summary": "Turn one question into a bounded tree of prerequisites, likely follow-ups, expert blind spots, and competing explanations.",
        "summary_uk": "Перетворює одне питання на обмежене дерево передумов, імовірних уточнень, сліпих зон і альтернативних пояснень.",
        "purpose": "Use it for exploratory questions where the user's first formulation probably omits decisions or dependencies they would ask about later.",
        "purpose_uk": "Використовуйте для відкритих запитів, у яких початкове формулювання, ймовірно, пропускає рішення або залежності, про які користувач запитав би згодом.",
        "steps": ["Infer the decision behind the question", "Map prerequisite and next questions", "Investigate high-value branches and stop at diminishing returns"],
        "steps_uk": ["Визначити рішення за початковим питанням", "Побудувати дерево передумов і наступних питань", "Дослідити важливі гілки й зупинитися, коли нова інформація мало що змінює"],
        "example": "Should our team move its internal notes to a new tool?",
        "example_uk": "Чи варто команді переносити внутрішні нотатки до нового інструмента?",
        "limit": "The inferred goal can be wrong. A long question tree can bury the direct answer or introduce irrelevant branches; prioritize by decision impact and stop when new branches stop changing the conclusion.",
        "limit_uk": "Модель може неправильно вгадати мету. Довге дерево питань здатне приховати пряму відповідь або додати зайве; гілки треба ранжувати за впливом на рішення й своєчасно зупинятися.",
        "basis": "Self-Ask research shows value in intermediate questions on multi-hop tasks. This prompt adds anticipatory and expert-blind-spot branches; those additions require direct testing.",
        "basis_uk": "Дослідження Self-Ask показує користь проміжних питань для багатокрокових задач. Цей промпт додатково передбачає майбутні питання та експертні сліпі зони, тож саме ці доповнення потребують прямого тесту.",
        "sources": [("Self-Ask paper", "https://arxiv.org/abs/2210.03350")],
        "images": [("question-tree.png", "Visible questions branch into less obvious dependencies."), ("question-pruning.png", "High-value branches continue; low-value branches stop.")],
        "images_uk": [("question-tree.png", "Явні питання ведуть до менш очевидних залежностей."), ("question-pruning.png", "Важливі гілки продовжуються, малокорисні — зупиняються.")],
    },
    {
        "slug": "clarify-then-investigate", "number": "03", "title": "Clarify, Then Investigate", "title_uk": "Уточнити, потім дослідити",
        "tag": "Two-round investigation", "tag_uk": "Дослідження у два раунди",
        "summary": "First ask the few consequential questions; after the user's reply, investigate with the same verification discipline.",
        "summary_uk": "Спочатку поставити справді потрібні питання, а після відповіді користувача провести перевірене дослідження.",
        "purpose": "Use it when a consequential recommendation depends on the user's goals, knowledge, constraints, or evidence that the first message does not contain.",
        "purpose_uk": "Використовуйте, коли важлива рекомендація залежить від мети, знань, обмежень чи доказів користувача, яких немає в першому повідомленні.",
        "steps": ["Map the user's knowledge and missing decision inputs", "Ask 5–15 consequential questions and wait", "Use the reply to investigate, verify, and answer conditionally where needed"],
        "steps_uk": ["Визначити знання користувача й відсутні дані для рішення", "Поставити 5–15 суттєвих питань і дочекатися відповіді", "На основі відповіді дослідити, перевірити та за потреби дати умовний висновок"],
        "example": "Should our five-person team buy an analytics platform or build one?",
        "example_uk": "Команді з п’яти людей купити аналітичну платформу чи створити власну?",
        "limit": "It costs an extra user turn and can over-question simple tasks. If fewer than five material gaps exist, the prompt explicitly allows fewer questions. Partial replies should lead to explicit assumptions, not endless interviewing.",
        "limit_uk": "Потрібен додатковий раунд з користувачем, а прості задачі можна переускладнити. Якщо важливих прогалин менше п’яти, промпт дозволяє менше питань. Часткова відповідь має вести до явних припущень, а не до нескінченного опитування.",
        "basis": "This is a new synthesis of clarification, bounded question expansion, and verification. Its exact two-round behavior is assessed against a matched two-turn control receiving the same facts.",
        "basis_uk": "Це нове поєднання уточнення, обмеженого розширення питань і перевірки. Його двораундову поведінку порівнюємо з контрольним діалогом на два раунди, який отримує ті самі факти.",
        "sources": [("Self-Ask paper", "https://arxiv.org/abs/2210.03350"), ("Chain-of-Verification", "https://arxiv.org/abs/2309.11495")],
        "images": [("clarification-rounds.png", "Round one gathers decision-changing answers; round two synthesizes evidence."), ("knowledge-matrix.png", "A knowledge matrix highlights missing inputs before research begins.")],
        "images_uk": [("clarification-rounds.png", "Перший раунд збирає важливі відповіді, другий синтезує докази."), ("knowledge-matrix.png", "Матриця знань показує прогалини перед дослідженням.")],
    },
]


def e(value: str) -> str:
    return html.escape(value, quote=True)


def page(title: str, body: str, *, lang: str, root: str) -> str:
    uk = lang == "uk"
    home = "index.html"
    evaluation = "evaluation.html"
    prompts = "".join(f'<a href="{p["slug"]}.html">{e(p["title_uk"] if uk else p["title"])}</a>' for p in PATTERNS)
    switch = ("../" if uk else "uk/") + ("index.html" if title in ("Home", "Головна") else "evaluation.html" if title in ("Evaluation", "Оцінювання") else next((p["slug"] + ".html" for p in PATTERNS if title in (p["title"], p["title_uk"])), "index.html"))
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="Three research prompt patterns with transparent evaluation."><title>{e(title)} · Research Prompt Patterns</title><link rel="stylesheet" href="{root}assets/style.css"></head>
<body><a class="skip-link" href="#main">{"До змісту" if uk else "Skip to content"}</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="{home}"><span class="brand-mark">R<span>·</span>P</span><span>Research Prompt Patterns</span></a><nav aria-label="{"Головна навігація" if uk else "Main navigation"}"><a href="{home}">{"Головна" if uk else "Home"}</a><a href="{evaluation}">{"Тести" if uk else "Evaluation"}</a><a href="{REPO}">GitHub ↗</a><a class="lang-link" href="{switch}" hreflang="{"en" if uk else "uk"}">{"EN" if uk else "УКР"}</a></nav></div></header>
<main id="main">{body}</main><footer class="site-footer"><div class="wrap footer-inner"><div><strong>Research Prompt Patterns</strong><p>{"Три промпти. Прозорі тести. Чіткі межі застосування." if uk else "Three prompts. Transparent tests. Clear limits."}</p></div><div class="footer-links">{prompts}<a href="{REPO}/blob/main/REFERENCES.md">{"Джерела" if uk else "Sources"}</a><a href="{REPO}/blob/main/LICENSE">MIT</a></div></div></footer><script src="{root}assets/site.js" defer></script></body></html>'''


def results_sentence(summary: dict | None, lang: str) -> str:
    if not summary:
        return "Результати 15 фінальних задач будуть додані після завершення перевірки." if lang == "uk" else "Results from the 15 final cases will appear after scoring is complete."
    n = summary["task_count"]
    runs = summary["response_count"]
    return f"{n} задач · {runs} незалежних розмов · GPT-5.6 Sol API · 3 повтори для кожної умови." if lang == "uk" else f"{n} cases · {runs} independent conversations · GPT-5.6 Sol API · three repeats per condition."


def verdict(comp: dict, lang: str) -> str:
    uk = lang == "uk"
    if comp["supported_as_useful"]:
        return "Перевага підтверджена для цих задач" if uk else "Improvement supported on these cases"
    if comp["difference"] < 0 and comp["bootstrap_95"][1] < 0:
        return "Погіршення для цих задач" if uk else "Worse on these cases"
    return "Надійної переваги не показано" if uk else "No reliable advantage shown"


def result_cards(summary: dict, lang: str) -> str:
    uk = lang == "uk"
    title = {"verify": ("Перевірка перед висновком", "Verification First"), "horizon": ("Горизонт питань", "Question Horizon"), "clarify": ("Уточнити, потім дослідити", "Clarify Then Investigate")}
    metric = {"verify": ("обов’язкові критерії", "required checkpoints"), "horizon": ("корисні приховані аспекти", "useful latent issues"), "clarify": ("суттєві уточнення", "material clarification topics")}
    cards = []
    for arm in ("verify", "horizon", "clarify"):
        comp = summary["comparisons"][arm]
        control = comp["control"]
        value = comp["difference"] * 100
        low, high = (x * 100 for x in comp["bootstrap_95"])
        win, tie, loss = (comp[key] for key in ("task_wins", "task_ties", "task_losses"))
        cost_ratio = summary["arms"][arm]["cost_usd"] / max(summary["arms"][control]["cost_usd"], 1e-9)
        words_ratio = summary["arms"][arm]["words"] / max(summary["arms"][control]["words"], 1e-9)
        question_note = (f"<br>{summary["arms"]["clarify"]["question_count"]:.1f} {"питань у середньому; зайвих" if uk else "questions on average; irrelevant"} {summary["arms"]["clarify"]["irrelevant_questions"]:.1f}" if arm == "clarify" else "")
        cards.append(f'''<article class="result-card"><h3>{e(title[arm][0 if uk else 1])}</h3><p class="verdict">{e(verdict(comp, lang))}</p><p class="result-number">{value:+.1f} <small>pp</small></p><p>{e(metric[arm][0 if uk else 1])} · 95% {"інтервал" if uk else "interval"} {low:+.1f} {"до" if uk else "to"} {high:+.1f} pp</p><p class="fine-print">{win} {"краще" if uk else "wins"} · {tie} {"без змін" if uk else "ties"} · {loss} {"гірше" if uk else "losses"} {"за задачами" if uk else "by case"}<br>{"Ціна" if uk else "Cost"} ×{cost_ratio:.1f} · {"Обсяг" if uk else "Words"} ×{words_ratio:.1f} {"проти контролю" if uk else "vs control"}{question_note}</p></article>''')
    return '<div class="result-grid">' + "".join(cards) + '</div>'


def home(lang: str, summary: dict | None) -> str:
    uk = lang == "uk"
    root = "../" if uk else ""
    title = "Дослідження, яке витримує перевірку." if uk else "Research answers that withstand a second look."
    intro = "Три готові промпти допомагають перевірити висновок, знайти пропущені питання та зібрати потрібний контекст до дослідження. Кожен має приклад, межі застосування й відтворюваний тест." if uk else "Three ready-to-use prompts help check a conclusion, find the questions you missed, and gather context before investigating. Each has an example, clear limits, and a reproducible evaluation."
    cards = "".join(f'''<article class="pattern-row"><span class="row-number">{p["number"]}</span><div><p class="eyebrow">{e(p["tag_uk"] if uk else p["tag"])}</p><h2>{e(p["title_uk"] if uk else p["title"])}</h2><p>{e(p["summary_uk"] if uk else p["summary"])}</p><a class="text-link" href="{p["slug"]}.html">{"Переглянути промпт" if uk else "Explore prompt"} <span aria-hidden="true">↗</span></a></div><img src="{root}assets/illustrations/{p["images"][0][0]}" alt="{e((p["images_uk"] if uk else p["images"])[0][1])}" loading="lazy"></article>''' for p in PATTERNS)
    return f'''<section class="hero wrap"><p class="eyebrow">{"Бібліотека промптів для досліджень" if uk else "A small library for consequential questions"}</p><h1>{title}</h1><p class="hero-lead">{intro}</p><div class="hero-actions"><a class="button" href="#patterns">{"Переглянути три промпти" if uk else "Browse the three prompts"}</a><a class="button button-secondary" href="evaluation.html">{"Як їх тестували" if uk else "How they were tested"}</a></div></section><section class="strip"><div class="wrap strip-inner"><span>{"Запит → перевірка → висновок" if uk else "Question → scrutiny → conclusion"}</span><span>{e(results_sentence(summary, lang))}</span></div></section><section class="wrap section" id="patterns"><div class="section-heading"><p class="eyebrow">{"Оберіть за проблемою" if uk else "Choose by the failure mode"}</p><h2>{"Три різні способи покращити запит" if uk else "Three different ways to improve a request"}</h2></div>{cards}</section><section class="section section-muted"><div class="wrap two-col"><div><p class="eyebrow">{"Що вимірюється" if uk else "What gets measured"}</p><h2>{"Точність важливіша за довжину" if uk else "Accuracy before output length"}</h2></div><div><p>{"Тести порівнюють виконання конкретних критеріїв, корисне розширення рамки, якість уточнень, помилки та витрати. Заявлені reasoning tokens описують витрати, а не якість." if uk else "The evaluation compares task checkpoints, useful question expansion, clarification quality, errors, and cost. Reported reasoning tokens describe resource use, not answer quality."}</p><a class="text-link" href="evaluation.html">{"Переглянути протокол і результати" if uk else "Read the protocol and results"} ↗</a></div></div></section>'''


def prompt_page(pattern: dict, lang: str, summary: dict | None) -> str:
    uk = lang == "uk"
    root = "../" if uk else ""
    slug = pattern["slug"]
    title = pattern["title_uk"] if uk else pattern["title"]
    prompt = (ROOT / "prompts" / f"{slug}.txt").read_text(encoding="utf-8").strip()
    steps = pattern["steps_uk"] if uk else pattern["steps"]
    images = pattern["images_uk"] if uk else pattern["images"]
    sources = " · ".join(f'<a href="{url}">{e(label)}</a>' for label, url in pattern["sources"])
    evaluation = ""
    if summary:
        arm = {"verification-first": "verify", "question-horizon": "horizon", "clarify-then-investigate": "clarify"}[slug]
        comp = summary["comparisons"][arm]
        diff = comp["difference"] * 100
        low, high = (v * 100 for v in comp["bootstrap_95"])
        evaluation = f'<div class="result-callout"><strong>{diff:+.1f} pp</strong><span>{e(verdict(comp, lang))} · 95% {"інтервал" if uk else "interval"} {low:+.1f} {"до" if uk else "to"} {high:+.1f} pp</span></div>'
    else:
        evaluation = f'<div class="result-callout"><strong>—</strong><span>{"Фінальний тест триває" if uk else "Final evaluation in progress"}</span></div>'
    step_html = "".join(f'<li><span>0{i}</span><p>{e(step)}</p></li>' for i, step in enumerate(steps, 1))
    return f'''<section class="prompt-hero wrap"><a class="back-link" href="index.html">← {"Усі промпти" if uk else "All prompts"}</a><p class="eyebrow">{pattern["number"]} / {e(pattern["tag_uk"] if uk else pattern["tag"])}</p><h1>{e(title)}</h1><p class="hero-lead">{e(pattern["summary_uk"] if uk else pattern["summary"])}</p><p class="prompt-intent">{e(pattern["purpose_uk"] if uk else pattern["purpose"])}</p><img class="hero-image" src="{root}assets/illustrations/{images[0][0]}" alt="{e(images[0][1])}"></section><section class="wrap section prompt-section"><div class="section-heading"><p class="eyebrow">{"Готовий текст" if uk else "Ready to use"}</p><h2>{"Скопіюйте промпт" if uk else "Copy the prompt"}</h2><p>{"Тестована англійська версія збережена без перекладу, щоб формулювання лишалося однаковим." if uk else "Append this text to your task request. The tested wording is kept intact."}</p></div><div class="prompt-toolbar"><span>prompt / v1.0</span><button type="button" class="copy-button" data-copy-target="prompt-text">{"Скопіювати" if uk else "Copy prompt"}</button></div><pre class="prompt-code" id="prompt-text"><code>{e(prompt)}</code></pre><p class="usage-note"><strong>{"Приклад запиту:" if uk else "Example task:"}</strong> {e(pattern["example_uk"] if uk else pattern["example"])}</p></section><section class="section section-muted"><div class="wrap"><div class="section-heading"><p class="eyebrow">{"Механізм" if uk else "Mechanism"}</p><h2>{"Як працює цей шаблон" if uk else "How this pattern works"}</h2></div><ol class="steps">{step_html}</ol><figure class="diagram"><img src="{root}assets/illustrations/{images[1][0]}" alt="{e(images[1][1])}" loading="lazy"><figcaption>{e(images[1][1])}</figcaption></figure></div></section><section class="wrap section three-col"><div><p class="eyebrow">{"Підстава" if uk else "Research basis"}</p><h2>{"Що підтверджено" if uk else "What is supported"}</h2><p>{e(pattern["basis_uk"] if uk else pattern["basis"])}</p><p class="source-links">{sources}</p></div><div><p class="eyebrow">{"Межі" if uk else "Known limits"}</p><h2>{"Де бути обережним" if uk else "Where to be careful"}</h2><p>{e(pattern["limit_uk"] if uk else pattern["limit"])}</p></div><div><p class="eyebrow">{"Власний тест" if uk else "Local evaluation"}</p><h2>{"Порівняння з контролем" if uk else "Against its control"}</h2>{evaluation}<a class="text-link" href="evaluation.html">{"Методика й дані" if uk else "Method and data"} ↗</a></div></section>'''


def evaluation_page(lang: str, summary: dict | None) -> str:
    uk = lang == "uk"
    root = "../" if uk else ""
    heading = "Чи працюють промпти?" if uk else "Do the prompts actually help?"
    lead = "Порівняння заплановано до запуску: 15 різних задач, п’ять умов, три незалежні повтори кожної. Результат оцінюється за виконанням задачі та корисністю додаткових питань, а не за обсягом тексту." if uk else "The comparison was fixed before the final runs: 15 distinct cases, five conditions, and three independent repeats each. Success means better task completion or useful questions, not more text."
    rows = ""
    if summary:
        labels = {"base": ("Звичайний запит", "Plain request"), "verify": ("Перевірка", "Verification First"), "horizon": ("Горизонт питань", "Question Horizon"), "two_turn_base": ("Контроль: два раунди", "Two-turn control"), "clarify": ("Уточнення + дослідження", "Clarify Then Investigate")}
        for arm in ("base", "verify", "horizon", "two_turn_base", "clarify"):
            data = summary["arms"][arm]
            rows += f'<tr><th scope="row">{e(labels[arm][0 if uk else 1])}</th><td>{data["required"]*100:.1f}%</td><td>{data["latent"]*100:.1f}%</td><td>{data["error_rate"]*100:.1f}%</td><td>{data["words"]:.0f}</td><td>${data["cost_usd"]:.3f}</td></tr>'
        score_table = f'''<div class="table-scroll"><table><caption>{"Середні значення за 15 задачами" if uk else "Task-balanced means across 15 cases"}</caption><thead><tr><th>{"Умова" if uk else "Condition"}</th><th>{"Виконання" if uk else "Task completion"}</th><th>{"Корисне розширення" if uk else "Useful expansion"}</th><th>{"Помилки" if uk else "Material errors"}</th><th>{"Слів" if uk else "Words"}</th><th>{"Ціна" if uk else "Cost"}</th></tr></thead><tbody>{rows}</tbody></table></div>'''
        figure = f'<figure class="results-figure"><img src="{root}assets/figures/paired-differences{"-uk" if uk else ""}.png" alt="{"Різниця оцінок за задачами між промптами й контролями" if uk else "Per-task score differences between prompts and their controls"}"><figcaption>{"Кожна точка — середнє трьох повторів для однієї задачі; вертикальна лінія позначає відсутність різниці." if uk else "Each point is one task averaged over three repeats; the vertical line marks no difference."}</figcaption></figure>'
    else:
        score_table = f'<p class="pending">{"Фінальне оцінювання ще не завершене; таблиця з’явиться тут разом із вихідними даними." if uk else "Final scoring is still in progress. The result table and raw data will appear here together."}</p>'
        figure = ""
    return f'''<section class="wrap prompt-hero eval-hero"><p class="eyebrow">{"Протокол і результати" if uk else "Protocol and results"}</p><h1>{heading}</h1><p class="hero-lead">{lead}</p><p>{e(results_sentence(summary, lang))}</p></section><section class="wrap section"><div class="section-heading"><p class="eyebrow">{"Результати" if uk else "Results"}</p><h2>{"Порівняння умов" if uk else "Condition comparison"}</h2></div>{result_cards(summary, lang) if summary else ""}{score_table}{figure}</section><section class="section section-muted"><div class="wrap two-col"><div><p class="eyebrow">{"Дизайн" if uk else "Design"}</p><h2>{"Контролі відповідають механізму" if uk else "Controls match the workflow"}</h2></div><div><p>{"Аналітичний і дослідницький промпти порівнюються зі звичайним однораундовим запитом. Двораундовий промпт порівнюється з двораундовим контролем, якому надають ті самі факти у другому повідомленні." if uk else "The analysis and question-expansion prompts use the plain one-turn request as control. The clarification prompt uses a two-turn control that receives the same facts in the second user message."}</p><p>{"Усі запуски: Oracle 0.21.3, OpenAI API, GPT-5.6 Sol, high effort, standard mode. Браузерний шлях Oracle не пройшов перевірку вибору моделі; висновки не переносимо автоматично на інтерфейс ChatGPT." if uk else "All generation runs use Oracle 0.21.3, OpenAI API, GPT-5.6 Sol, high effort, standard mode. Oracle's browser path failed model-picker verification, so these findings are not automatically claims about the ChatGPT interface."}</p></div></div></section><section class="wrap section"><div class="section-heading"><p class="eyebrow">{"Повторюваність" if uk else "Reproducibility"}</p><h2>{"Перевірте протокол і дані" if uk else "Inspect the protocol and data"}</h2></div><div class="link-grid"><a href="{REPO}/blob/main/evals/PROTOCOL.md">{"Заздалегідь зафіксований протокол" if uk else "Frozen protocol"} ↗</a><a href="{REPO}/blob/main/evals/tasks.json">{"15 задач і критерії" if uk else "15 cases and criteria"} ↗</a><a href="{REPO}/blob/main/evals/results.json">{"Відповіді, оцінки й витрати" if uk else "Responses, grades, and costs"} ↗</a><a href="{REPO}/blob/main/evals/summary.json">{"Підсумкові обчислення" if uk else "Summary calculations"} ↗</a><a href="{REPO}/blob/main/evals/{"REPORT.uk.md" if uk else "REPORT.md"}">{"Повний звіт" if uk else "Full report"} ↗</a><a href="{REPO}/blob/main/evals/AUDIT.md">{"Ручна перевірка оцінок" if uk else "Manual score audit"} ↗</a></div><p class="fine-print">{"Синтетичні задачі перевіряють структуру відповіді та аналіз. Вони не доводять перевагу для всіх тем, моделей або досліджень із живим вебпошуком." if uk else "These synthetic cases test answer structure and analysis. They do not establish superiority across all topics, models, or live-web research."}</p></section>'''


def prompt_markdown(pattern: dict, lang: str) -> str:
    uk = lang == "uk"
    title = pattern["title_uk"] if uk else pattern["title"]
    slug = pattern["slug"]
    prompt = (ROOT / "prompts" / f"{slug}.txt").read_text(encoding="utf-8").strip()
    desc = pattern["summary_uk"] if uk else pattern["summary"]
    purpose = pattern["purpose_uk"] if uk else pattern["purpose"]
    limit = pattern["limit_uk"] if uk else pattern["limit"]
    basis = pattern["basis_uk"] if uk else pattern["basis"]
    image_root = "../../docs/assets/illustrations/" if uk else "../docs/assets/illustrations/"
    repo_root = "../.." if uk else ".."
    images = pattern["images_uk"] if uk else pattern["images"]
    return f'''# {title}

{desc}

| {"Поле" if uk else "Field"} | {"Значення" if uk else "Value"} |
|---|---|
| {"Категорія" if uk else "Category"} | {pattern["tag_uk"] if uk else pattern["tag"]} |
| {"Версія" if uk else "Version"} | 1.0.0 |
| {"Тестована модель" if uk else "Tested model"} | GPT-5.6 Sol API via Oracle 0.21.3 |
| {"Остання перевірка" if uk else "Last verified"} | 2026-09-29 |

![{images[0][1]}]({image_root}{images[0][0]})

## {"Призначення" if uk else "Purpose"}

{purpose}

## {"Промпт" if uk else "Prompt"}

{"Англійський текст нижче є тестованою версією; перекладені пояснення не змінюють формулювання." if uk else "Append this exact text to a task request."}

```text
{prompt}
```

## {"Приклад запиту" if uk else "Example task"}

> {pattern["example_uk"] if uk else pattern["example"]}

![{images[1][1]}]({image_root}{images[1][0]})

## {"Дослідницька підстава" if uk else "Research basis"}

{basis} [{"Джерела" if uk else "References"}]({repo_root}/REFERENCES.md).

## {"Відомі обмеження" if uk else "Known limitations"}

{limit}

## {"Результати тесту" if uk else "Evaluation"}

{"Методика, оцінки та сирі відповіді:" if uk else "Protocol, scores, and raw responses:"} [{"Оцінювання" if uk else "Evaluation"}]({SITE}{"uk/" if uk else ""}evaluation.html) · [{"Протокол" if uk else "Protocol"}]({repo_root}/evals/PROTOCOL.md).
'''


def readme(lang: str, summary: dict | None) -> str:
    uk = lang == "uk"
    prompt_links = "\n".join(f'| [{p["title_uk"] if uk else p["title"]}](prompts/{"uk/" if uk else ""}{p["slug"]}.md) | {p["summary_uk"] if uk else p["summary"]} |' for p in PATTERNS)
    return f'''# Research Prompt Patterns

{"Три дослідницькі промпти для перевірки висновків, пошуку пропущених питань і змістовних уточнень перед роботою." if uk else "Three research prompts for checking conclusions, finding missing questions, and clarifying context before investigation."}

[{"Відкрити сайт" if uk else "Explore the site"}]({SITE}{"uk/" if uk else ""}) · [{"Методика та результати" if uk else "Evaluation and results"}]({SITE}{"uk/" if uk else ""}evaluation.html) · [{"Українська версія" if not uk else "English version"}]({"README.uk.md" if not uk else "README.md"})

## {"Швидкий початок" if uk else "Quick start"}

{"Відкрийте відповідний промпт, скопіюйте англійський текст і додайте його після власної задачі. Для третього промпту дочекайтеся уточнювальних питань і дайте відповіді в наступному повідомленні." if uk else "Open the relevant prompt, copy its English text, and append it to your task request. For the third prompt, answer its clarification questions in the next message."}

## {"Промпти" if uk else "Browse prompts"}

| {"Промпт" if uk else "Prompt"} | {"Завдання" if uk else "What it does"} |
|---|---|
{prompt_links}

## {"Сумісність" if uk else "Compatibility"}

{"Тестування проведене через Oracle на GPT-5.6 Sol API. Формат тексту придатний для вставлення в ChatGPT, Claude і Gemini, але результати для їхніх інтерфейсів і моделей тут не перевірені." if uk else "Evaluated through Oracle on the GPT-5.6 Sol API. The plain-text format can be pasted into ChatGPT, Claude, and Gemini; behavior in those interfaces and models has not been measured here."}

## {"Якість і тести" if uk else "Quality and testing"}

{results_sentence(summary, "uk" if uk else "en")} {"Якість оцінюється за правильністю, корисним розширенням рамки, уточненнями, помилками та витратами." if uk else "Quality is measured through correctness, useful expansion, clarification, errors, and cost."} [Protocol](evals/PROTOCOL.md) · [Cases](evals/tasks.json) · [Results](evals/results.json) · [Report](evals/{"REPORT.uk.md" if uk else "REPORT.md"}).

## {"Структура" if uk else "Repository structure"}

- `prompts/`: {"канонічні тексти й окремі сторінки" if uk else "canonical texts and individual GitHub pages"}.
- `docs/`: {"двомовний сайт GitHub Pages та ілюстрації" if uk else "bilingual GitHub Pages site and illustrations"}.
- `evals/`: {"протокол, задачі, відповіді, оцінки, код аналізу" if uk else "protocol, cases, responses, grades, and analysis code"}.
- [REFERENCES.md](REFERENCES.md): {"джерела та межі доказів" if uk else "sources and evidence limits"}.

## {"Ліцензія" if uk else "License"}

[MIT](LICENSE) · Copyright © 2026 Maksym Klymenko.
'''


def main() -> None:
    summary_path = ROOT / "evals/summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else None
    DOCS.mkdir(exist_ok=True)
    (DOCS / "uk").mkdir(exist_ok=True)
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (DOCS / "index.html").write_text(page("Home", home("en", summary), lang="en", root=""), encoding="utf-8")
    (DOCS / "uk/index.html").write_text(page("Головна", home("uk", summary), lang="uk", root="../"), encoding="utf-8")
    (DOCS / "evaluation.html").write_text(page("Evaluation", evaluation_page("en", summary), lang="en", root=""), encoding="utf-8")
    (DOCS / "uk/evaluation.html").write_text(page("Оцінювання", evaluation_page("uk", summary), lang="uk", root="../"), encoding="utf-8")
    (ROOT / "prompts/uk").mkdir(exist_ok=True)
    for pattern in PATTERNS:
        slug = pattern["slug"]
        (DOCS / f"{slug}.html").write_text(page(pattern["title"], prompt_page(pattern, "en", summary), lang="en", root=""), encoding="utf-8")
        (DOCS / "uk" / f"{slug}.html").write_text(page(pattern["title_uk"], prompt_page(pattern, "uk", summary), lang="uk", root="../"), encoding="utf-8")
        (ROOT / "prompts" / f"{slug}.md").write_text(prompt_markdown(pattern, "en"), encoding="utf-8")
        (ROOT / "prompts/uk" / f"{slug}.md").write_text(prompt_markdown(pattern, "uk"), encoding="utf-8")
    (ROOT / "README.md").write_text(readme("en", summary), encoding="utf-8")
    (ROOT / "README.uk.md").write_text(readme("uk", summary), encoding="utf-8")
    print("Built README, six prompt pages, and bilingual GitHub Pages site.")


if __name__ == "__main__":
    main()
