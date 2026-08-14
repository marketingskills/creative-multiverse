#!/usr/bin/env python3
"""Select one eligible verbalized-sampling candidate reproducibly."""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select one candidate below a probability threshold."
    )
    parser.add_argument(
        "input",
        type=str,
        help="JSON file containing a candidates array, or - to read JSON from stdin",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.10,
        help="Keep candidates with probability strictly below this value (default: 0.10)",
    )
    parser.add_argument("--seed", type=str, default=None, help="Reproducible random seed")
    parser.add_argument(
        "--mode",
        choices=("uniform", "probability"),
        default="uniform",
        help="Uniform maximizes exploration; probability preserves relative frequency",
    )
    parser.add_argument(
        "--compact", action="store_true", help="Print compact JSON instead of indented JSON"
    )
    return parser.parse_args()


def load_candidates(source: str) -> list[dict[str, Any]]:
    try:
        if source == "-":
            raw = sys.stdin.read()
        else:
            raw = Path(source).read_text(encoding="utf-8")
        payload = json.loads(raw)
    except OSError as exc:
        raise ValueError(f"could not read {source}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON from {source}: {exc}") from exc

    candidates = payload.get("candidates") if isinstance(payload, dict) else payload
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("input must be a non-empty array or an object with a candidates array")

    validated: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            raise ValueError(f"candidate {index} must be an object")
        candidate_id = candidate.get("id")
        if not isinstance(candidate_id, (str, int)):
            raise ValueError(f"candidate {index} must have a string or integer id")
        id_key = str(candidate_id)
        if id_key in seen_ids:
            raise ValueError(f"duplicate candidate id: {candidate_id}")
        seen_ids.add(id_key)

        probability = candidate.get("probability")
        if isinstance(probability, bool) or not isinstance(probability, (int, float)):
            raise ValueError(f"candidate {candidate_id} must have a numeric probability")
        probability = float(probability)
        if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
            raise ValueError(f"candidate {candidate_id} probability must be between 0 and 1")

        normalized = dict(candidate)
        normalized["probability"] = probability
        validated.append(normalized)
    return validated


def select_candidate(
    candidates: list[dict[str, Any]], threshold: float, seed: str | None, mode: str
) -> dict[str, Any]:
    if not math.isfinite(threshold) or not 0.0 < threshold <= 1.0:
        raise ValueError("threshold must be greater than 0 and at most 1")

    eligible = [candidate for candidate in candidates if candidate["probability"] < threshold]
    if not eligible:
        raise ValueError(f"no candidates have probability below {threshold:g}")

    rng = random.Random(seed)
    if mode == "uniform":
        selected = rng.choice(eligible)
    else:
        weights = [candidate["probability"] for candidate in eligible]
        if not any(weights):
            raise ValueError("probability mode requires at least one positive eligible probability")
        selected = rng.choices(eligible, weights=weights, k=1)[0]

    return {
        "selected": selected,
        "selection": {
            "mode": mode,
            "seed": seed,
            "threshold": threshold,
            "eligible_count": len(eligible),
            "total_count": len(candidates),
        },
    }


def main() -> int:
    args = parse_args()
    try:
        result = select_candidate(
            load_candidates(args.input), args.threshold, args.seed, args.mode
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    indent = None if args.compact else 2
    print(json.dumps(result, ensure_ascii=False, indent=indent, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
