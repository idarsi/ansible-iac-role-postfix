#!/usr/bin/env python3
"""Check selected repository source artifacts and GitHub workflow declarations."""

from __future__ import annotations

from pathlib import Path
import sys
import subprocess
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DOC_CONTENT = {
    "README.md": ("ANSIBLE-IAC-ROLE-POSTFIX", "iac_blueprint.postfix"),
    "CONTRIBUTING.md": ("# Contributing", "iac_blueprint.postfix"),
    "docs/security/osps-assessment.md": (
        "# OpenSSF OSPS Baseline Level 1 self-assessment",
        "## Requirement results",
        "Status:** Unverified",
    ),
}
WORKFLOW_DIRECTORY = ".github/workflows"


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark,
                f"duplicate key {key!r}", key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def parse_workflow(text: str) -> dict[str, Any]:
    """Parse GitHub Actions YAML and validate declarations, not effective settings."""
    workflow = yaml.load(text, Loader=UniqueKeyLoader)
    if not isinstance(workflow, dict):
        raise ValueError("workflow must be a YAML mapping")
    # PyYAML's YAML 1.1 resolver parses the GitHub Actions `on` key as True.
    events = workflow.get("on", workflow.get(True))
    if not isinstance(events, (dict, list, str, bool)):
        raise ValueError("workflow must declare an event mapping, list, or scalar")
    sensitive_events = {"pull_request_target", "workflow_run"}
    declared_events = events.keys() if isinstance(events, dict) else events if isinstance(events, list) else []
    if sensitive_events & set(declared_events):
        raise ValueError("untrusted-code sensitive trigger requires explicit security review")

    _check_permissions(workflow.get("permissions"), "workflow")
    jobs = workflow.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        raise ValueError("workflow must contain jobs")
    for name, job in jobs.items():
        if not isinstance(job, dict):
            raise ValueError(f"job {name!r} must be a mapping")
        if "permissions" in job:
            _check_permissions(job["permissions"], f"job {name!r}")
    return workflow


def _check_permissions(value: Any, scope: str) -> None:
    if value != {"contents": "read"}:
        raise ValueError(f"{scope} permissions must explicitly be contents: read only")


def check_artifacts(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for relative, markers in EXPECTED_DOC_CONTENT.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing required artifact: {relative}")
            continue
        content = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in content:
                errors.append(f"{relative} is missing expected project marker: {marker}")

    license_text = (root / "LICENSE").read_text(encoding="utf-8") if (root / "LICENSE").is_file() else ""
    if "MIT License" not in license_text or "Permission is hereby granted" not in license_text:
        errors.append("LICENSE does not contain the expected MIT license text")

    try:
        tracked = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--", f"{WORKFLOW_DIRECTORY}/*.yml", f"{WORKFLOW_DIRECTORY}/*.yaml"],
            check=True, capture_output=True, text=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError) as error:
        errors.append(f"{WORKFLOW_DIRECTORY}: unable to enumerate tracked workflows: {error}")
        tracked = []
    for relative in tracked:
        try:
            parse_workflow((root / relative).read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError, ValueError) as error:
            errors.append(f"{relative}: {error}")
    return errors


def main() -> int:
    errors = check_artifacts()
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print("Source artifacts and declared workflow policy passed (static evidence only).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
