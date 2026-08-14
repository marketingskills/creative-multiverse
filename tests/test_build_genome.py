from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "build_genome.py"
SPEC = importlib.util.spec_from_file_location("build_genome", SCRIPT)
assert SPEC and SPEC.loader
build_genome = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = build_genome
SPEC.loader.exec_module(build_genome)


def attractors():
    return [
        {"id": "A1", "mechanism": "a radio signal encoded with prime numbers"},
        {"id": "A2", "mechanism": "an abandoned alien spacecraft"},
        {"id": "A3", "mechanism": "a secret government laboratory"},
    ]


def candidates(state, stage):
    prior = {item["stage"]: item["candidate"]["id"] for item in state["selected"]}
    result = []
    for index in range(5):
        item = {
            "id": f"{stage['name']}-{index}",
            "description": f"Distinct possibility {index} using material system {index}",
            "mechanism": f"causal mechanism {stage['name']} number {index}",
            "probability": stage["threshold"] * (index + 1) / 6,
            "avoids": ["A1", "A2", "A3"],
            "dimensions": {
                "cause": f"cause {index}",
                "medium": f"medium {index}",
                "motive": f"motive {index}",
                "perceiver": f"perceiver {index}",
                "cost": f"cost {index}",
            },
        }
        if prior:
            item["conditioned_on"] = prior
        if stage["role"] == "hinge":
            item["consequences"] = {
                "physical": f"physical consequence {index}",
                "social": f"social consequence {index}",
                "emotional": f"emotional consequence {index}",
            }
        result.append(item)
    return result


class GenomeTests(unittest.TestCase):
    def start(self):
        return build_genome.start_session(
            {
                "brief": "Write an original story.",
                "seed": "test-seed",
                "profile": "ultra",
                "attractors": attractors(),
            }
        )

    def test_complete_ultra_session_is_reproducible(self):
        first = self.start()
        second = self.start()
        while first["next_stage"]:
            stage = first["next_stage"]
            first = build_genome.advance_session(
                {"state": first, "candidates": candidates(first, stage)}
            )
            second = build_genome.advance_session(
                {"state": second, "candidates": candidates(second, second["next_stage"])}
            )
        self.assertEqual(first["selected"], second["selected"])
        genome = build_genome.finalize_session(first)["creative_genome"]
        self.assertEqual(len(genome["decisions"]), 5)
        self.assertEqual(set(genome["consequence_cascade"]), {"physical", "social", "emotional"})

    def test_rejects_incomplete_attractor_map(self):
        with self.assertRaisesRegex(build_genome.GenomeError, "three obvious attractors"):
            build_genome.start_session(
                {"brief": "x", "seed": "y", "profile": "ultra", "attractors": attractors()[:2]}
            )

    def test_rejects_candidate_above_threshold(self):
        state = self.start()
        items = candidates(state, state["next_stage"])
        items[0]["probability"] = 0.01
        with self.assertRaisesRegex(build_genome.GenomeError, "below 0.01"):
            build_genome.advance_session({"state": state, "candidates": items})

    def test_rejects_wrong_conditioning(self):
        state = self.start()
        state = build_genome.advance_session(
            {"state": state, "candidates": candidates(state, state["next_stage"])}
        )
        items = candidates(state, state["next_stage"])
        items[0]["conditioned_on"] = {"causal-hinge": "wrong"}
        with self.assertRaisesRegex(build_genome.GenomeError, "conditioning"):
            build_genome.advance_session({"state": state, "candidates": items})

    def test_rejects_dimensionally_redundant_candidates(self):
        state = self.start()
        items = candidates(state, state["next_stage"])
        items[1]["dimensions"] = dict(items[0]["dimensions"])
        with self.assertRaisesRegex(build_genome.GenomeError, "at least two dimensions"):
            build_genome.advance_session({"state": state, "candidates": items})

    def test_rejects_tampered_state(self):
        state = self.start()
        state = build_genome.advance_session(
            {"state": state, "candidates": candidates(state, state["next_stage"])}
        )
        state["selected"][0]["selection_seed"] = "hand-picked"
        with self.assertRaisesRegex(build_genome.GenomeError, "invalid selection seed"):
            build_genome.validate_state(state)


if __name__ == "__main__":
    unittest.main()
