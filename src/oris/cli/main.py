"""Oris CLI entrypoint."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from oris.cli.output import (
    build_run_summary_for_cli,
    emit_run_debug,
    emit_validate_debug,
)
from oris.cli.pipeline_service import load_pipeline, run_pipeline_from_path
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
    run_parser.add_argument(
        "--format",
        choices=("json", "pretty"),
        default="json",
        help="Stdout JSON formatting (default: compact json)",
    )
    run_parser.add_argument(
        "--debug",
        action="store_true",
        help="Print trace and step execution details to stderr",
    )

    validate_parser = subparsers.add_parser("validate", help="Validate a pipeline YAML file")
    validate_parser.add_argument("pipeline_path", type=str, help="Path to pipeline YAML")
    validate_parser.add_argument(
        "--debug",
        action="store_true",
        help="Print plan summary (step ids, component names) to stderr",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        return code if isinstance(code, int) else 1

    debug = bool(args.debug)

    try:
        if args.command == "run":
            input_data = _parse_input_json(args.input_json)
            result = run_pipeline_from_path(args.pipeline_path, input_data)
            if debug:
                emit_run_debug(result)
            summary = build_run_summary_for_cli(result, redact=True)
            if args.format == "pretty":
                print(json.dumps(summary, indent=2, sort_keys=True))
            else:
                print(json.dumps(summary, sort_keys=True))
            return 0
        if args.command == "validate":
            pipeline = load_pipeline(args.pipeline_path)
            if debug:
                emit_validate_debug(pipeline)
            print("Pipeline is valid.")
            return 0
        return 2
    except OrisError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print("Error: An unexpected error occurred.", file=sys.stderr)
        if debug:
            print(f"Error: ({type(exc).__name__}) {exc}", file=sys.stderr)
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
