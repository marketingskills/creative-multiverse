# Verbalized sampling reference

## Contents

- Research basis
- Why the prompt works
- Practical settings
- Selection policy
- Quality controls
- Claims and limitations
- Sources

## Research basis

Zhang et al. identify typicality bias in preference data: annotators tend to favor familiar, fluent, and predictable text even when multiple responses have similar task utility. Post-training can therefore sharpen an aligned model toward typical completions.

Verbalized Sampling changes the semantic target. Instead of requesting one instance or an unweighted list, request a distribution of candidates with explicit probabilities. A representative answer to a distribution-level prompt is itself diverse, so the same preference for representativeness can recover part of the underlying model's variation.

The paper reports creative-writing diversity gains of roughly 1.6-2.1x over direct prompting, a 25.7% improvement in its reported human evaluation result, and recovery of 66.8% of base-model diversity. Treat those as results from the paper's tasks and models, not guarantees for every writing task.

## Why the prompt works

- An instance prompt tends toward one prototypical answer.
- A list prompt tends toward a "bestseller list" of several familiar modes.
- A distribution prompt makes a varied set the representative response.
- Adding a low probability threshold directs generation toward the tail without requiring logit access.

Probabilities are verbalized estimates, not calibrated token probabilities. Their primary value here is to induce distributional framing and expose a controllable tail.

## Practical settings

Use five candidates per call by default. The paper uses `k=5` for creative-writing experiments and reports that increasing `k` can increase diversity, while an excessively large `k` can reduce generation quality.

Suggested working thresholds:

- `< 0.20`: mild divergence
- `< 0.10`: strong general-purpose divergence and the authors' current quick-start recommendation
- `< 0.05`: aggressive tail exploration
- `< 0.01`: experimental exploration with higher coherence risk

Generate later decisions after selecting earlier ones. Five options across five conditional decisions create up to 3,125 reachable paths (`5^5`) without paying to draft all paths.

Verbalized sampling is compatible with decoding controls such as temperature and top-p. Do not confuse a prompt-level threshold with an API sampling temperature.

## Selection policy

Use uniform mechanical selection for maximum creative exploration. Do not let the same language model rank candidates for "best creativity": that preference step can reintroduce typicality bias.

Use probability-weighted selection when the task aims to simulate realistic frequencies or behaviors rather than maximize novelty. The paper's dialogue experiments explored both uniform and probability-weighted strategies and found the appropriate balance depended on how the candidate count was set.

Filter before sampling only for hard constraint failures, semantic duplicates, unusable format, or incoherence severe enough to prevent execution. Do not filter on familiarity.

## Quality controls

Treat creativity as novelty plus fitness. First sample decisions without a quality ranking. Then judge the resulting draft against fixed constraints and craft requirements.

Protect the sampled creative decisions during editing. Allow local repairs, but resample explicitly if a premise or device fails. Silent replacement turns revision into another route back to the mode.

For higher assurance, draft two independently sampled genomes and run a blind fitness check that excludes "familiarity," "broad appeal," and "sounds professional" unless the brief explicitly requires them.

## Claims and limitations

- Do not call the method literally 1000x more creative. The 3,125 figure describes a combinatorial decision space, not measured output quality.
- One side-by-side example is illustrative, not an evaluation.
- Greater semantic distance can produce incoherence or constraint failures.
- More capable models tended to benefit more in the paper's experiments.
- Verbalized probabilities may be poorly calibrated.
- The workflow costs more tokens and latency than one direct answer. The paper reports a modest overhead for VS-Standard in its setup, with larger overhead for multi-turn variants.
- Do not use creative tail exploration to vary facts, legal obligations, medical advice, crisis facts, or safety requirements.

## Sources

- Paper, version 4: https://arxiv.org/html/2510.01171v4
- Abstract and version history: https://arxiv.org/abs/2510.01171
- Authors' implementation and current quick start: https://github.com/CHATS-lab/verbalized-sampling
