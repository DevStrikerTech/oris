"""Oris CLI entrypoint."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from oris.cli.pipeline_service import run_pipeline_from_path, validate_pipeline_path
from oris.core.exceptions import ConfigurationError, OrisError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="oris", description="Oris Responsible AI runtime CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a pipeline YAML file")
    run_parser.add_argument("pipeline_path", type=str, help="Path to pipeline YAML")
    run_parser.add_argument(
        "--input-json",
        type=str,
        default="{}",
        help="JSON object payload for pipeline input",
    )

    validate_parser = subparsers.add_parser("validate", help="Validate a pipeline YAML file")
    validate_parser.add_argument("pipeline_path", type=str, help="Path to pipeline YAML")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "run":
            input_data = _parse_input_json(args.input_json)
            result = run_pipeline_from_path(args.pipeline_path, input_data)
            print(json.dumps(result.to_run_summary(), sort_keys=True))
            return 0
        if args.command == "validate":
            validate_pipeline_path(args.pipeline_path)
            print("Pipeline is valid.")
            return 0
        parser.print_help()
        return 2
    except OrisError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def _parse_input_json(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        msg = "Invalid JSON for --input-json."
        raise ConfigurationError(msg) from exc
    if not isinstance(parsed, dict):
        msg = "--input-json must be a JSON object."
        raise ConfigurationError(msg)
    return parsed
