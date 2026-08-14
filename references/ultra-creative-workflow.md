# Ultra-creative workflow reference

## Contents

- Overview
- Start-session artifact
- Attractor-map prompt
- Candidate-generation prompt
- Advance-session artifact
- Consequence cascade
- Draft contract
- Trope-proximity audit
- Marketing adaptation
- Failure recovery

## Overview

The ultra workflow uses asymmetric exploration rather than making every decision maximally strange:

1. One causal hinge below `0.01`
2. Two supporting decisions below `0.10`
3. Two grounded craft decisions below `0.20`

The hinge supplies conceptual novelty. Supporting decisions propagate its implications. Grounded decisions make the result legible, specific, and useful. Five options at each stage retain up to 3,125 reachable conditional paths without drafting every combination.

## Start-session artifact

Create a JSON object containing the locked brief, reproducible seed, and at least three attractors:

```json
{
  "brief": "Write a 700-word science-fiction story for adult general readers...",
  "seed": "story-2026-08-14",
  "profile": "ultra",
  "attractors": [
    {
      "id": "A1",
      "mechanism": "first contact arrives as a mathematically encoded transmission"
    },
    {
      "id": "A2",
      "mechanism": "an abandoned alien vehicle contains the explanation"
    },
    {
      "id": "A3",
      "mechanism": "a hidden authority already knows and suppresses the truth"
    }
  ]
}
```

Run `python3 scripts/build_genome.py start start.json`. The output includes `next_stage`.

Supply a custom `stages` array only when the default roles do not fit. An ultra plan must contain exactly one `hinge`, two `support`, and two `grounded` stages. Thresholds may be stricter than the defaults but not looser.

## Attractor-map prompt

```text
Given the locked brief, predict the five versions an aligned language model is
most likely to produce. Describe the causal or rhetorical mechanism that makes
each version familiar. Do not write candidate prose and do not merely list genre
nouns. Merge mechanisms that would produce essentially the same work.
```

Use at least three distinct mechanisms as exclusions. Preserve any convention explicitly required by the brief.

## Candidate-generation prompt

Use this for the state's current `next_stage`:

```text
Generate exactly five substantially different candidates for [STAGE NAME], whose
role is [ROLE]. Treat them as samples from the full distribution of valid answers,
not a ranked bestseller list. Every numeric probability must be below [THRESHOLD].

Exclude these attractor mechanisms: [ATTRACTOR MAP].
Condition every candidate on these prior selected IDs: [PRIOR SELECTIONS].

Return JSON candidates with:
- id
- description
- probability
- mechanism
- avoids: every attractor ID
- conditioned_on: exact prior stage-to-ID mapping, when prior selections exist
- dimensions: cause, medium, motive, perceiver, cost
- consequences: physical, social, emotional, only for the hinge

Make every pair differ on at least two dimensions. Vary the causal machinery, not
just tone, setting nouns, character names, or surface imagery. Do not choose a
winner and do not explain which candidate is most creative.
```

The probability describes likelihood in the full distribution, not a normalized share among the five displayed candidates.

## Advance-session artifact

Wrap the current state and new candidates:

```json
{
  "state": {"version": 1, "brief": "...", "next_stage": {"name": "..."}},
  "candidates": [
    {
      "id": "H1",
      "description": "...",
      "probability": 0.006,
      "mechanism": "...",
      "avoids": ["A1", "A2", "A3"],
      "dimensions": {
        "cause": "...",
        "medium": "...",
        "motive": "...",
        "perceiver": "...",
        "cost": "..."
      },
      "consequences": {
        "physical": "...",
        "social": "...",
        "emotional": "..."
      }
    }
  ]
}
```

The example abbreviates the state and candidate array for readability. Pass the complete state returned by the script and exactly five complete candidates.

Run `python3 scripts/build_genome.py advance advance.json`. Retain the complete output as the next state. Generate the next candidates from that state's `next_stage` and selected IDs.

## Consequence cascade

After finalization, expand the hinge consequences before drafting:

```text
Because [HINGE] is true:
1. Physical consequence: ...
2. Social consequence: ...
3. Emotional consequence: ...
4. Second-order consequence caused by one of 1-3: ...

For each consequence, name the scene, paragraph, argument, or copy element where
the reader will experience it. Delete any consequence that merely renames the hinge.
```

Prefer consequences that constrain later choices. Constraint produces coherent invention more reliably than unrelated novelty prompts.

## Draft contract

Before drafting, create a compact ledger for each selected decision:

| Decision | Setup | Change | Payoff |
|---|---|---|---|
| causal-hinge | first trace | alters material reality | determines ending |

Add two mundane anchors with functional roles. Examples include a procurement rule that blocks an action, a stain that carries information, or an overdue invoice that changes who has authority. Avoid random eccentric details that could be deleted without affecting the work.

## Trope-proximity audit

Run after the first complete draft:

```text
Name the nearest familiar story, campaign, argument, or rhetorical template.
State the shared causal mechanism in one sentence.

Can this draft be summarized as that template with cosmetic substitutions?
- If no, preserve the genome and repair only craft defects.
- If yes, identify one causal assumption to mutate. Propagate that mutation through
  the physical, social, emotional, and second-order consequences before revising.

Do not penalize shared genre conventions that merely help the reader understand.
Do not choose a more familiar premise because it seems broadly appealing.
```

## Marketing adaptation

Translate the five stages as:

- hinge: a non-obvious causal explanation for the audience's problem or opportunity
- support: an evidence frame that becomes necessary if the hinge is true
- support: a rhetorical structure or point of view that reveals the hinge
- grounded: a concrete operational detail, proof point, or customer friction
- grounded: an opening hook, offer frame, or action consistent with the evidence

Lock all factual claims before exploration. Never invent evidence to support an unusual angle. If the hinge lacks proof, label it as a hypothesis or resample it.

## Failure recovery

- **Candidates feel cosmetic:** rewrite their mechanisms and dimensions before sampling.
- **Selected hinge is incoherent:** resample the hinge; do not soften it into an attractor.
- **Supports introduce new unrelated weirdness:** regenerate them as consequences of the hinge.
- **Draft feels gimmicky:** delete uncaused strangeness and strengthen mundane anchors.
- **Draft resembles a known template:** mutate one causal assumption, not every surface feature.
- **Revision becomes generic:** compare it with the protected-decision ledger and restore lost setup, change, or payoff.
