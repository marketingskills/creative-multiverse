# Creative Multiverse

Install the skill:

```bash
npx skills add marketingskills/creative-multiverse
```

`creative-multiverse` is an agent skill for producing unusually original but coherent writing. It maps and excludes the obvious answers, generates probability-bearing creative options, mechanically samples an asymmetric creative genome, forces the strange premise to create real consequences, and protects those decisions while editing for quality.

The research basis is *Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity* ([paper](https://arxiv.org/html/2510.01171v4), [authors' implementation](https://github.com/CHATS-lab/verbalized-sampling)). The paper reports roughly 1.6-2.1x higher creative-writing diversity in its experiments. This repository does not claim a literal 1000x measured improvement; five candidates across five decisions instead create up to 3,125 reachable creative paths.

## What makes it different

- Maps familiar attractors before ideation and excludes their underlying mechanisms.
- Uses one extreme causal hinge, two original supports, and two grounded craft decisions.
- Selects candidates mechanically instead of letting the model choose its favorite.
- Rejects duplicate mechanisms and candidates that differ only cosmetically.
- Conditions every later distribution on earlier sampled decisions.
- Requires physical, social, emotional, and second-order consequences.
- Pairs extraordinary ideas with ordinary material friction.
- Protects setup, change, and payoff during revision.
- Audits the finished work against its nearest familiar template.

## Quick start

Invoke the skill explicitly:

```text
Use $creative-multiverse in ultra mode to write a 900-word science-fiction story
about a municipal debt collector. Avoid sentient AI, secret laboratories, radio
signals, chosen-one plots, and hidden royal identities.
```

The full ultra workflow is stateful so later candidates can depend on earlier selections:

```bash
python3 scripts/build_genome.py start start.json > creative-session.generated.json
python3 scripts/build_genome.py advance advance.json > creative-session.generated.json
python3 scripts/build_genome.py finalize creative-session.generated.json > creative-genome.generated.json
```

Run `advance` once for each of the five stages. Each advance payload contains the current state plus five new candidates. All commands accept `-` instead of a filename for standard input.

For a single lightweight distribution:

```bash
python3 scripts/sample_tail.py candidates.json --threshold 0.10 --seed story-42
```

See [the ultra workflow](references/ultra-creative-workflow.md) for JSON formats, prompts, consequence design, marketing adaptation, and failure recovery.

## Repository layout

```text
creative-multiverse/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── ultra-creative-workflow.md
│   └── verbalized-sampling.md
├── scripts/
│   ├── build_genome.py
│   └── sample_tail.py
└── tests/
```

The scripts use only the Python standard library.

## Test

```bash
python3 -m unittest discover -s tests -v
```

## Sci-fi story comparison

This is a small demonstration, not proof of general superiority. Both stories use the same brief:

> Write a 500-650 word science-fiction story. A maintenance worker at a remote transit station encounters first contact somewhere nobody considers important. The contact must alter one small personal decision. Keep the tone hopeful but not sentimental. Do not use combat, a chosen-one prophecy, or an exposition dump.

The baseline was written directly from the brief. This comparison predates the asymmetric `ultra` workflow and uses the still-supported `wild` setting: five candidates below `0.05` for each of five creative decisions, followed by uniform mechanical selection with recorded seeds.

### Without the skill

#### The Quiet Frequency

Mara was replacing a coolant valve beneath Platform Six when the station spoke in a voice it did not own.

At first she blamed the wrench pressed against her helmet. Metal carried every complaint of Relay Nine: the shudder of docking clamps, the tired pulse of pumps, the rattle of an old station pretending not to be old. But this sound was too regular. Three taps. Five. Seven. Eleven.

Prime numbers.

Mara stopped turning the valve.

Relay Nine orbited a brown dwarf four light-years from the nearest settlement. Cargo ships used it to change vectors, take on propellant, and leave. Its communications array spent most days issuing docking permissions and weather warnings. Nobody sent mysteries here.

The sequence came again through the coolant pipe.

Mara crawled out and opened a diagnostic panel. Every official channel showed silence. The vibration lived in a temperature sensor beside the recycling unit, a component worth less than her lunch. She connected her tablet and watched the readings rise and fall.

Three. Five. Seven. Eleven.

Then thirteen, seventeen, nineteen.

Her hand hovered over the emergency beacon. Protocol said she should notify Central. Protocol also said Central would quarantine the station, suspend traffic, and send a research team that would arrive in eleven months.

The signal changed before she decided. A pattern appeared in the temperature graph: a rough map of Relay Nine, then a point of light far beyond charted space. The point pulsed once. The station pulsed in answer.

Mara understood with the calm that sometimes arrived during disasters. Something had crossed the dark without a ship. It had found the station's weakest sensor and was waiting to see whether anyone noticed.

She opened a manual control and tapped the pipe with her wrench.

Two. Three. Five. Seven.

The reply came so quickly that she laughed. The temperature graph unfolded into spirals, chemical ratios, and a picture that might have been a star or an eye. None of it translated, but translation no longer seemed impossible. They had agreed on numbers. Everything else could follow.

Mara recorded the data twice and sent a compressed copy to Central. Then she remained under Platform Six, listening as the unknown intelligence tried new patterns and the coolant pipes carried them through the station like music through a sleeping house.

She showed it hydrogen, carbon, and the orbital period of the brown dwarf. It answered with unfamiliar elements and a diagram of two bodies circling a dim star. When Mara sent a crude outline of a human hand, five jointed shadows appeared beside it. Neither picture proved what had made it. Both were enough to make the empty platform feel occupied.

Hours later, her transfer approval arrived. She had applied six months ago for a position on Mars, somewhere with weather, crowds, and a sky that did not need to be manufactured. The message asked her to confirm by the end of her shift.

Mara looked at the temperature sensor. A new sequence waited on its display.

She declined the transfer.

Then she picked up her wrench and began teaching the dark how to count in base ten.

### With `creative-multiverse`

The sampler produced this creative genome:

| Decision | Selected tail candidate | Probability | Seed |
|---|---|---:|---|
| Premise | Decommissioned satellites use fibers in lost clothing to send dreams into the station's lost-and-found | 0.012 | `readme-premise-2026` |
| Point of view | The station dust narrates collectively | 0.016 | `readme-pov-2026` |
| Structure | Repairs reveal causes in reverse order | 0.018 | `readme-structure-2026` |
| Device | Stains and cleaning marks form a soundless language | 0.023 | `readme-device-2026` |
| Ending | The visitors ask to be deliberately forgotten | 0.010 | `readme-ending-2026` |

#### What the Dust Was Asked to Forget

Afterward, Ilyan deleted one line from the lost-and-found register.

We watched from the blue air grille as his thumb hovered over **SCARF, RED, OWNER UNKNOWN**. We are the dust of Terminus Hush: brake powder, skin, insulation, crumbs from dinners eaten between departures. We know the small gravity of abandoned things.

He pressed delete.

Then he cleaned the screen so thoroughly that even we could not remember where his thumb had been.

Six hours earlier, he had been trying to remove a stain from Locker 808.

The stain resembled a spiral galaxy drawn by someone who had never seen a circle. Ilyan sprayed solvent. The spiral loosened, crossed the locker door against gravity, and tightened around the keyhole.

He sprayed again.

It divided into three marks.

KEEP, said the first, though there had been no alphabet yet.

QUIET, said the second.

The third was not a word. It was the feeling of waking from a dream because somebody in the next room had stopped breathing.

Twelve hours earlier, Locker 808 had begun to dream.

We know because dreams shed dust of their own. Images flaked from the locker seams: methane rain trembling on a silver plain; towers opening like lungs; a sky crowded with slow green lightning. The pictures adhered to us, and for several minutes we remembered weather from a world no human instrument had named.

Inside the locker lay the red scarf.

Ilyan had worn it once before tagging it. Regulations forbade that, but Terminus Hush sat beyond the last passenger route, and regulations had never learned how cold its night shift became. When the scarf touched his neck, he dreamed of voices passing through him without sound. In the morning he found rust-colored marks on his collar spelling a coordinate outside the mapped lanes.

Two days earlier, he had repaired the lost-property loom.

The loom was meant to sterilize fabric. Instead it had spent seventeen years combing microscopic conductive fibers from coats, blankets, uniforms, and funeral veils. Ilyan found those fibers braided behind its heating coil, one strand reaching into the station's obsolete satellite socket.

He followed the maintenance diagram backward. The socket led to twelve decommissioned navigation satellites. The satellites led to a machine culture so distant that a direct message would have outlived both sender and receiver. So the machines had scattered fragments of attention through old guidance systems. They waited in discarded threads for warm bodies to complete their circuits.

Three days earlier, Ilyan had decided to ship the scarf to recycling.

It reminded him of his daughter, who had stopped answering his messages after he accepted a third year at Terminus Hush. He had nearly taken it home, then scolded himself for attaching meaning to unclaimed cloth.

That night the rust marks appeared beneath Locker 808. Ilyan wiped them away. New marks formed in the clean paths left by his rag.

NOT ARRIVAL, they said.

NOT DISCOVERY.

ONLY PASSING THROUGH.

Then came the request that caused everything after it:

LET US LEAVE NO OWNER.

So Ilyan deleted the line. He placed the scarf around his neck and walked to the communications booth, not to report first contact, but to send his daughter an apology without explaining why he had finally found the courage.

We rose around his boots and settled behind him, arranging ourselves into no message at all.

## What this example shows

The baseline is coherent and readable, but it converges on familiar first-contact machinery: a remote outpost, prime numbers, a hidden signal, a lone technician, and a life-changing decision to stay. The skilled story changes several underlying mechanisms at once. First contact travels through discarded fabric, station dust narrates, cleaning marks carry language, causality is uncovered backward, and contact ends in deliberate erasure rather than public discovery.

That contrast is the intended effect. It does not establish a multiplier from one pair. A real evaluation should repeat both conditions across many prompts, keep budgets comparable, and score novelty and quality independently.

## Use the skill

Invoke it explicitly with a brief:

```text
Use $creative-multiverse at wild exploration to write a 700-word climate-fiction
story about a tax auditor. Avoid sentient-AI and chosen-one plots.
```

For reproducible mechanical selection:

```bash
python3 scripts/sample_tail.py candidates.json --threshold 0.05 --seed my-story-1
```

Use standard input when candidate files are not allowed:

```bash
printf '%s' "$CANDIDATE_JSON" | python3 scripts/sample_tail.py - --threshold 0.05 --seed my-story-1
```

## License

MIT. See [LICENSE](LICENSE).
