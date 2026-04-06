"""Policy logic for responsible input/output filtering."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from oris.core.exceptions import GuardViolationError


def _string_values(data: dict[str, Any]) -> list[str]:
    """Collect string values from a shallow dict (typical pipeline payloads)."""
    out: list[str] = []
    for value in data.values():
        if isinstance(value, str):
            out.append(value)
    return out


@dataclass(slots=True)
class PolicyEnforcer:
    """Enforces keys/terms, injection heuristics, PII patterns, and output stubs."""

    blocked_input_keys: set[str] = field(default_factory=lambda: {"password", "secret", "token"})
    blocked_terms: set[str] = field(default_factory=lambda: {"exploit", "malware"})
    injection_markers: tuple[str, ...] = (
        "ignore previous instructions",
        "ignore all prior instructions",
        "disregard the above",
        "system prompt",
        "you are now",
        "jailbreak",
        "bypass safety",
    )
    toxicity_stub_marker: str = "__ORIS_TOXIC_STUB__"
    hallucination_stub_marker: str = "__ORIS_HALLUCINATION_STUB__"
    _email_pattern: re.Pattern[str] = field(
        default_factory=lambda: re.compile(
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        ),
    )
    _phone_pattern: re.Pattern[str] = field(
        default_factory=lambda: re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    )
    _ssn_pattern: re.Pattern[str] = field(
        default_factory=lambda: re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    )

    def detect_prompt_injection(self, text: str) -> bool:
        """Basic heuristic for prompt-injection style substrings."""
        lowered = text.lower()
        return any(marker in lowered for marker in self.injection_markers)

    def detect_pii(self, text: str) -> bool:
        """Simple PII placeholders: email, US phone, SSN-shaped tokens."""
        if self._email_pattern.search(text):
            return True
        if self._phone_pattern.search(text):
            return True
        if self._ssn_pattern.search(text):
            return True
        return False

    def detect_toxicity_stub(self, text: str) -> bool:
        """Stub toxicity detector (explicit test marker only)."""
        return self.toxicity_stub_marker in text

    def detect_hallucination_stub(self, text: str) -> bool:
        """Stub grounding/hallucination check (explicit test marker only)."""
        return self.hallucination_stub_marker in text

    def validate_input(self, data: dict[str, Any]) -> None:
        for key in data:
            if key.lower() in self.blocked_input_keys:
                msg = f"Input contains prohibited key '{key}'."
                raise GuardViolationError(msg)
        for text in _string_values(data):
            if self.detect_prompt_injection(text):
                msg = "Input failed prompt-injection heuristic check."
                raise GuardViolationError(msg)
            if self.detect_pii(text):
                msg = "Input appears to contain PII patterns."
                raise GuardViolationError(msg)

    def validate_output(self, data: dict[str, Any]) -> None:
        for value in data.values():
            if isinstance(value, str):
                lowered = value.lower()
                if any(term in lowered for term in self.blocked_terms):
                    msg = "Output contains blocked policy terms."
                    raise GuardViolationError(msg)
                if self.detect_toxicity_stub(value):
                    msg = "Output failed toxicity stub check."
                    raise GuardViolationError(msg)
                if self.detect_hallucination_stub(value):
                    msg = "Output failed hallucination/grounding stub check."
                    raise GuardViolationError(msg)
