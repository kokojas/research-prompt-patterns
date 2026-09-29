# Research basis and visual references

The source documents for this project are private research notes. This page lists public references used to check the mechanisms and guide the illustrations. None of the papers below validates the exact prompt texts in this repository; the local evaluation addresses those texts directly.

## Prompt mechanisms

- [Hylak, “Think harder: how prompts interact with reasoning options” (2026)](https://www.raindrop.ai/blog/think-harder/). The author reports more provider-counted reasoning tokens from an exact short “Think hard” user prompt on three easy math questions. This is evidence about token use for that short prompt, not evidence that the longer Verification First prompt improves answer accuracy.
- [Press et al., “Measuring and Narrowing the Compositionality Gap in Language Models” (2023)](https://arxiv.org/abs/2210.03350). Introduces Self-Ask: generating and answering intermediate questions for multi-hop tasks. It supports the question-decomposition idea, not the exact Question Horizon wording.
- [Dhuliawala et al., “Chain-of-Verification Reduces Hallucination in Large Language Models” (2023)](https://arxiv.org/abs/2309.11495). Studies draft, independent verification questions, verification, and revision. It motivates checking critical claims but does not prove that a single instruction reliably reproduces the whole procedure.
- [Madaan et al., “Self-Refine: Iterative Refinement with Self-Feedback” (2023)](https://arxiv.org/abs/2303.17651). Studies iterative feedback and refinement. It informed the explicit revision and stopping rules.

## Publishing and visuals

- [GitHub Docs, “About the repository README file”](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) and [“Configuring a publishing source for your GitHub Pages site”](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) informed the split between the landing README, separate prompt files, and `/docs` site.
- [Datopian, “SCQH & Issue Trees”](https://www.datopian.com/playbook/scqh) and the [Self-Ask paper](https://arxiv.org/abs/2210.03350) informed the root-and-branch visual vocabulary of Question Horizon.
- The [Chain-of-Verification paper](https://arxiv.org/abs/2309.11495) and [Self-Refine paper](https://arxiv.org/abs/2303.17651) informed verification gates and revision loops in the Verification First illustrations.
- The two-stage clarification illustrations synthesize standard decision-flow and gap-matrix conventions. They are conceptual explanations, not diagrams of measured model internals.

The illustrations are original, reference-informed visualizations. They do not reproduce any one source diagram.
