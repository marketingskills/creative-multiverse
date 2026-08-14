---
name: creative-multiverse
description: Create unusually original but coherent writing with attractor mapping, verbalized tail sampling, a mechanically selected asymmetric creative genome, causal consequence cascades, mundane specificity, trope-proximity auditing, and constraint-preserving revision. Use when Codex needs to invent or radically improve stories, scenes, scripts, campaign concepts, positioning, headlines, hooks, metaphors, names, brand ideas, or other open-ended prose where novelty matters; when conventional brainstorming produces near-duplicates; or when the user asks for surprising, unconventional, experimental, wild, alien, or ultra-creative work. Do not trigger for purely factual, legal, crisis, compliance, medical, or instructional writing unless the user explicitly requests creative exploration.
---

# Creative Multiverse

Create one strange causal heart, support it with compatible creative decisions, and ground it in specific reality. Separate novelty generation from fitness editing so revision cannot silently collapse the work back to a familiar mode.

Read [references/ultra-creative-workflow.md](references/ultra-creative-workflow.md) before running `ultra`, adapting the method to marketing, or formatting the JSON artifacts. Read [references/verbalized-sampling.md](references/verbalized-sampling.md) when explaining the research, thresholds, claims, or limitations.

## Non-negotiable rules

1. Lock facts, audience, format, length, voice, prohibitions, and safety before diverging.
2. Map the obvious attractors and exclude their causal mechanisms, not merely their words.
3. Generate probability-bearing distributions. Do not substitute a plain list.
4. Select mechanically. Never ask the model which candidate is best or most creative.
5. Use asymmetric exploration: one extreme hinge, two original supports, and two grounded craft choices.
6. Make every unusual decision change events. Decorative weirdness does not count.
7. Preserve selected decisions during editing. Resample explicitly when one fails.
8. Do not claim a numerical creativity multiplier. Reachable combinations are not measured quality gains.

## Select a mode

Default to `ultra` for explicit creative generation. Use a lighter mode when the user prioritizes speed, brand conformity, or a narrow factual task.

| Mode | Process |
|---|---|
| `grounded` | Map attractors; sample 2 decisions below `0.20` |
| `original` | Map attractors; sample 3 decisions below `0.10` |
| `wild` | Map attractors; sample 5 decisions below `0.05` |
| `ultra` | Sample 1 hinge `<0.01`, 2 supports `<0.10`, 2 grounded choices `<0.20` |

Keep five candidates per distribution. More candidates can reduce quality and increase cost.

## Ultra workflow

### 1. Lock the brief

Write a compact internal lock containing:

- reader or audience
- purpose and desired effect
- required facts or promises
- genre, format, length, and voice
- prohibited claims, tropes, styles, and content
- qualities that revision must preserve

Treat factual and safety constraints as immutable. Do not use tail sampling to vary them.

### 2. Map the attractors

Identify at least three answers the model is most likely to produce. Express each as an underlying causal or rhetorical mechanism.

Bad exclusion: `radio`, `spaceship`, `AI`.

Good exclusion: `first contact arrives as a mathematically encoded transmission`; `the mystery is explained by an abandoned alien vehicle`; `a hidden authority already understands the phenomenon`.

Do not include an attractor in the finished work merely to negate or parody it.

### 3. Start a reproducible session

Create the start JSON described in the ultra-workflow reference and run:

```bash
python3 scripts/build_genome.py start start.json
```

Resolve scripts relative to this skill directory. Pass `-` instead of a filename to read JSON from standard input. Keep the returned state for the next stage.

### 4. Generate and select each stage

For the state's `next_stage`, generate exactly five candidates. Require every candidate to:

- fall below that stage's probability threshold
- explicitly avoid every attractor ID
- state its causal mechanism
- differ across cause, medium, motive, perceiver, and cost
- match all prior selections in `conditioned_on`
- include physical, social, and emotional consequences when it is the hinge

Advance the state:

```bash
python3 scripts/build_genome.py advance advance.json
```

Generate the next distribution only after mechanical selection. Condition it on every selected ID. Repeat until `next_stage` is `null`, then run:

```bash
python3 scripts/build_genome.py finalize state.json
```

Use `scripts/sample_tail.py` for lighter one-stage exploration. Never pretend that model-side selection is random when scripts are unavailable; show IDs and let the user provide a number.

### 5. Expand the causal hinge

Use the hinge's required consequence cascade:

- physical: what changes materially because the hinge is true
- social: what behavior, relationship, institution, or power changes
- emotional: what new choice, fear, desire, or cost becomes possible

Make all three appear in the draft. Add at least one second-order consequence: a consequence of one of the first three rather than another restatement of the premise.

### 6. Add mundane specificity

Pair the extraordinary mechanism with at least two ordinary material anchors appropriate to the setting: maintenance procedures, invoices, stains, weather, packaging, forms, tools, bodily discomfort, deadlines, or other concrete friction.

Use specificity to make the strange mechanism causal and tangible. Do not add random quirky objects that never affect the work.

### 7. Draft from the genome

Realize the selected decisions as one coherent work. Give each protected decision:

- setup: establish it without explaining everything
- change: let it alter events, reasoning, or reader expectation
- payoff: make it affect the ending or requested action

Do not mention candidate probabilities, attractors, seeds, or the workflow inside the finished prose unless the user requests process notes.

### 8. Run the fitness gate

Check independently:

**Constraint gate**

- Verify the locked brief, facts, audience, format, length, and safety.
- Remove unsupported claims and accidental prohibited elements.

**Craft gate**

- Make causality legible without an exposition dump.
- Replace generic abstractions with action, image, evidence, or material detail.
- Remove accidental repetition, stock phrasing, and decorative weirdness.
- Ensure every selected decision has setup, change, and payoff.
- Make the ending arise from the consequence cascade.

Repair local execution while protecting the genome. If a decision fails, resample that stage rather than replacing it with an attractor.

### 9. Run the trope-proximity audit

Identify the nearest familiar story, campaign, or rhetorical template. Name the shared mechanism. If the work can be summarized as that template with cosmetic substitutions, mutate one causal assumption and propagate the mutation through all consequences.

Do not mutate merely because the work shares a genre. Preserve useful conventions that support comprehension.

### 10. Deliver

Return the finished work first. Include the attractor map, genome, or audit only when the user requests rationale, alternatives, reproducibility, or an experiment.

For comparisons, keep briefs and output lengths similar. State that one example is illustrative, not a general evaluation.

## Evaluate without collapsing creativity

When evaluation is requested, separate originality from quality and constraints. Prefer blind human judgment across multiple prompts. Measure semantic and structural diversity, quality, constraint failures, cost, and latency. Do not let a single "overall quality" judge reward familiarity by default.
