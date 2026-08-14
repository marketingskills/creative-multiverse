from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "sample_tail.py"
SPEC = importlib.util.spec_from_file_location("sample_tail", SCRIPT)
assert SPEC and SPEC.loader
sample_tail = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = sample_tail
SPEC.loader.exec_module(sample_tail)


class SampleTailTests(unittest.TestCase):
    def setUp(self):
        self.candidates = [
            {"id": "a", "probability": 0.14},
            {"id": "b", "probability": 0.09},
            {"id": "c", "probability": 0.03},
            {"id": "d", "probability": 0.01},
        ]

    def test_uniform_selection_is_reproducible_and_thresholded(self):
        first = sample_tail.select_candidate(self.candidates, 0.10, "seed", "uniform")
        second = sample_tail.select_candidate(self.candidates, 0.10, "seed", "uniform")
        self.assertEqual(first, second)
        self.assertNotEqual(first["selected"]["id"], "a")
        self.assertEqual(first["selection"]["eligible_count"], 3)

    def test_probability_mode_rejects_all_zero_weights(self):
        with self.assertRaisesRegex(ValueError, "positive eligible probability"):
            sample_tail.select_candidate(
                [{"id": "a", "probability": 0.0}], 0.10, "seed", "probability"
            )

    def test_rejects_empty_tail(self):
        with self.assertRaisesRegex(ValueError, "no candidates"):
            sample_tail.select_candidate(self.candidates, 0.001, "seed", "uniform")


if __name__ == "__main__":
    unittest.main()
