#!/usr/bin/env python3
"""Build a reproducible creative genome one conditional stage at a time."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


VERSION = 1
DIMENSION_KEYS = ("cause", "medium", "motive", "perceiver", "cost")
DEFAULT_STAGES = [
    {"name": "causal-hinge", "role": "hinge", "threshold": 0.01},
    {"name": "consequence-carrier", "role": "support", "threshold": 0.10},
    {"name": "viewpoint-or-structure", "role": "support", "threshold": 0.10},
    {"name": "material-anchor", "role": "grounded", "threshold": 0.20},
    {"name": "ending-or-voice", "role": "grounded", "threshold": 0.20},
]


class GenomeError(ValueError):
    """Report malformed creative-session data."""


def read_json(source: str) -> Any:
    try:
        raw = sys.stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8")
        return json.loads(raw)
    except OSError as exc:
        raise GenomeError(f"could not read {source}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise GenomeError(f"invalid JSON from {source}: {exc}") from exc


def nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GenomeError(f"{label} must be a non-empty string")
    return value.strip()


def normalized(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def token_set(value: str) -> set[str]:
    return set(normalized(value).split())


def jaccard(left: str, right: str) -> float:
    left_tokens = token_set(left)
    right_tokens = token_set(right)
    union = left_tokens | right_tokens
    return len(left_tokens & right_tokens) / len(union) if union else 1.0


def validate_stage_plan(stages: Any, profile: str) -> list[dict[str, Any]]:
    if not isinstance(stages, list) or not stages:
        raise GenomeError("stages must be a non-empty array")

    cleaned: list[dict[str, Any]] = []
    names: set[str] = set()
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            raise GenomeError(f"stage {index} must be an object")
        name = nonempty_string(stage.get("name"), f"stage {index} name")
        role = nonempty_string(stage.get("role"), f"stage {name} role")
        if role not in {"hinge", "support", "grounded"}:
            raise GenomeError(f"stage {name} role must be hinge, support, or grounded")
        threshold = stage.get("threshold")
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
            raise GenomeError(f"stage {name} threshold must be numeric")
        threshold = float(threshold)
        if not math.isfinite(threshold) or not 0.0 < threshold <= 1.0:
            raise GenomeError(f"stage {name} threshold must be greater than 0 and at most 1")
        if name in names:
            raise GenomeError(f"duplicate stage name: {name}")
        names.add(name)
        cleaned.append({"name": name, "role": role, "threshold": threshold})

    if profile == "ultra":
        counts = {role: sum(stage["role"] == role for stage in cleaned) for role in ("hinge", "support", "grounded")}
        if counts != {"hinge": 1, "support": 2, "grounded": 2}:
            raise GenomeError("ultra profile requires 1 hinge, 2 support, and 2 grounded stages")
        maxima = {"hinge": 0.01, "support": 0.10, "grounded": 0.20}
        for stage in cleaned:
            if stage["threshold"] > maxima[stage["role"]]:
                raise GenomeError(
                    f"ultra {stage['role']} threshold must be at most {maxima[stage['role']]:g}"
                )
    return cleaned


def validate_attractors(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list) or len(value) < 3:
        raise GenomeError("provide at least three obvious attractors")
    result: list[dict[str, str]] = []
    ids: set[str] = set()
    mechanisms: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise GenomeError(f"attractor {index} must be an object")
        item_id = nonempty_string(item.get("id"), f"attractor {index} id")
        mechanism = nonempty_string(item.get("mechanism"), f"attractor {item_id} mechanism")
        mechanism_key = normalized(mechanism)
        if item_id in ids:
            raise GenomeError(f"duplicate attractor id: {item_id}")
        if mechanism_key in mechanisms:
            raise GenomeError(f"duplicate attractor mechanism: {mechanism}")
        ids.add(item_id)
        mechanisms.add(mechanism_key)
        result.append({"id": item_id, "mechanism": mechanism})
    return result


def start_session(config: Any) -> dict[str, Any]:
    if not isinstance(config, dict):
        raise GenomeError("start input must be an object")
    brief = nonempty_string(config.get("brief"), "brief")
    seed = nonempty_string(config.get("seed"), "seed")
    profile = config.get("profile", "ultra")
    if profile not in {"ultra", "custom"}:
        raise GenomeError("profile must be ultra or custom")
    stages = validate_stage_plan(config.get("stages", DEFAULT_STAGES), profile)
    attractors = validate_attractors(config.get("attractors"))
    return {
        "version": VERSION,
        "profile": profile,
        "brief": brief,
        "seed": seed,
        "attractors": attractors,
        "stage_plan": stages,
        "selected": [],
        "next_stage": stages[0],
    }


def validate_state(state: Any) -> dict[str, Any]:
    if not isinstance(state, dict) or state.get("version") != VERSION:
        raise GenomeError(f"state must use version {VERSION}")
    nonempty_string(state.get("brief"), "state brief")
    nonempty_string(state.get("seed"), "state seed")
    if state.get("profile") not in {"ultra", "custom"}:
        raise GenomeError("state profile must be ultra or custom")
    plan = validate_stage_plan(state.get("stage_plan"), state["profile"])
    validate_attractors(state.get("attractors"))
    selected = state.get("selected")
    if not isinstance(selected, list) or len(selected) > len(plan):
        raise GenomeError("state selected must be an array no longer than the stage plan")
    for index, item in enumerate(selected):
        if not isinstance(item, dict):
            raise GenomeError(f"selected item {index} must be an object")
        expected_stage = plan[index]
        if item.get("stage") != expected_stage["name"] or item.get("role") != expected_stage["role"]:
            raise GenomeError(f"selected item {index} does not match stage plan")
        if item.get("threshold") != expected_stage["threshold"]:
            raise GenomeError(f"selected item {index} threshold does not match stage plan")
        if item.get("selection_seed") != derived_seed(state["seed"], index, expected_stage["name"]):
            raise GenomeError(f"selected item {index} has an invalid selection seed")
        candidate = item.get("candidate")
        if not isinstance(candidate, dict):
            raise GenomeError(f"selected item {index} candidate must be an object")
        nonempty_string(candidate.get("id"), f"selected item {index} candidate id")
    expected_next = plan[len(selected)] if len(selected) < len(plan) else None
    if state.get("next_stage") != expected_next:
        raise GenomeError("state next_stage does not match selected stages")
    return state


def expected_conditioning(state: dict[str, Any]) -> dict[str, str]:
    return {item["stage"]: str(item["candidate"]["id"]) for item in state["selected"]}


def validate_candidates(
    candidates: Any, stage: dict[str, Any], state: dict[str, Any]
) -> list[dict[str, Any]]:
    if not isinstance(candidates, list) or len(candidates) != 5:
        raise GenomeError(f"stage {stage['name']} requires exactly five candidates")

    attractor_ids = {item["id"] for item in state["attractors"]}
    attractor_mechanisms = [item["mechanism"] for item in state["attractors"]]
    conditioning = expected_conditioning(state)
    result: list[dict[str, Any]] = []
    ids: set[str] = set()
    mechanisms: set[str] = set()

    for index, raw in enumerate(candidates):
        if not isinstance(raw, dict):
            raise GenomeError(f"candidate {index} must be an object")
        candidate = deepcopy(raw)
        item_id = nonempty_string(candidate.get("id"), f"candidate {index} id")
        description = nonempty_string(candidate.get("description"), f"candidate {item_id} description")
        mechanism = nonempty_string(candidate.get("mechanism"), f"candidate {item_id} mechanism")
        if item_id in ids:
            raise GenomeError(f"duplicate candidate id: {item_id}")
        mechanism_key = normalized(mechanism)
        if mechanism_key in mechanisms:
            raise GenomeError(f"duplicate candidate mechanism: {mechanism}")
        ids.add(item_id)
        mechanisms.add(mechanism_key)

        probability = candidate.get("probability")
        if isinstance(probability, bool) or not isinstance(probability, (int, float)):
            raise GenomeError(f"candidate {item_id} probability must be numeric")
        probability = float(probability)
        if not math.isfinite(probability) or not 0.0 <= probability < stage["threshold"]:
            raise GenomeError(
                f"candidate {item_id} probability must be at least 0 and below {stage['threshold']:g}"
            )

        avoids = candidate.get("avoids")
        if not isinstance(avoids, list) or set(map(str, avoids)) != attractor_ids:
            raise GenomeError(f"candidate {item_id} must explicitly avoid every attractor id")
        for attractor in attractor_mechanisms:
            if normalized(mechanism) == normalized(attractor):
                raise GenomeError(f"candidate {item_id} repeats attractor mechanism: {attractor}")

        dimensions = candidate.get("dimensions")
        if not isinstance(dimensions, dict):
            raise GenomeError(f"candidate {item_id} dimensions must be an object")
        cleaned_dimensions = {
            key: nonempty_string(dimensions.get(key), f"candidate {item_id} dimension {key}")
            for key in DIMENSION_KEYS
        }

        if state["selected"]:
            raw_conditioning = candidate.get("conditioned_on")
            if not isinstance(raw_conditioning, dict):
                raise GenomeError(f"candidate {item_id} must include conditioned_on")
            actual_conditioning = {str(key): str(value) for key, value in raw_conditioning.items()}
            if actual_conditioning != conditioning:
                raise GenomeError(
                    f"candidate {item_id} conditioning must match prior selections {conditioning}"
                )

        if stage["role"] == "hinge":
            consequences = candidate.get("consequences")
            if not isinstance(consequences, dict):
                raise GenomeError(f"hinge candidate {item_id} requires consequences")
            candidate["consequences"] = {
                key: nonempty_string(consequences.get(key), f"candidate {item_id} consequence {key}")
                for key in ("physical", "social", "emotional")
            }

        candidate.update(
            {
                "id": item_id,
                "description": description,
                "mechanism": mechanism,
                "probability": probability,
                "dimensions": cleaned_dimensions,
                "avoids": sorted(attractor_ids),
            }
        )
        result.append(candidate)

    for left_index, left in enumerate(result):
        for right in result[left_index + 1 :]:
            if jaccard(left["description"], right["description"]) >= 0.82:
                raise GenomeError(f"candidate descriptions {left['id']} and {right['id']} are near-duplicates")
            differences = sum(
                normalized(left["dimensions"][key]) != normalized(right["dimensions"][key])
                for key in DIMENSION_KEYS
            )
            if differences < 2:
                raise GenomeError(
                    f"candidates {left['id']} and {right['id']} must differ on at least two dimensions"
                )
    return result


def derived_seed(root_seed: str, index: int, stage_name: str) -> str:
    payload = f"{root_seed}|{index}|{stage_name}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def advance_session(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise GenomeError("advance input must contain state and candidates")
    state = deepcopy(validate_state(payload.get("state")))
    index = len(state["selected"])
    if index >= len(state["stage_plan"]):
        raise GenomeError("all stages are already selected")
    stage = state["stage_plan"][index]
    candidates = validate_candidates(payload.get("candidates"), stage, state)
    stage_seed = derived_seed(state["seed"], index, stage["name"])
    selected = random.Random(stage_seed).choice(candidates)
    state["selected"].append(
        {
            "stage": stage["name"],
            "role": stage["role"],
            "threshold": stage["threshold"],
            "selection_seed": stage_seed,
            "candidate": selected,
        }
    )
    next_index = index + 1
    state["next_stage"] = (
        state["stage_plan"][next_index] if next_index < len(state["stage_plan"]) else None
    )
    return state


def finalize_session(state: Any) -> dict[str, Any]:
    state = validate_state(deepcopy(state))
    if len(state["selected"]) != len(state["stage_plan"]):
        raise GenomeError("cannot finalize until every stage has been selected")
    hinge = next(item for item in state["selected"] if item["role"] == "hinge")
    return {
        "creative_genome": {
            "version": VERSION,
            "profile": state["profile"],
            "brief": state["brief"],
            "seed": state["seed"],
            "excluded_attractors": state["attractors"],
            "decisions": state["selected"],
            "consequence_cascade": hinge["candidate"]["consequences"],
            "revision_contract": {
                "protect": [item["stage"] for item in state["selected"]],
                "require_for_each": ["setup", "change", "payoff"],
                "require_mundane_anchor": True,
                "require_trope_proximity_audit": True,
            },
        }
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("start", "advance", "finalize"))
    parser.add_argument("input", help="JSON file or - for stdin")
    parser.add_argument("--compact", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = read_json(args.input)
        if args.command == "start":
            result = start_session(data)
        elif args.command == "advance":
            result = advance_session(data)
        else:
            result = finalize_session(data)
    except GenomeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
