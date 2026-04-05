"""Audit logging with redaction support."""

from __future__ import annotations

import json
import logging
from typing import Any

SENSITIVE_KEYS = {"password", "secret", "token", "api_key", "authorization"}


class AuditLogger:
    """Structured audit logger that redacts sensitive fields."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger("oris.audit")

    def log_event(self, event: str, payload: dict[str, Any]) -> None:
        safe_payload = self._redact_payload(payload)
        self._logger.info("%s %s", event, json.dumps(safe_payload, sort_keys=True))

    def _redact_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        redacted: dict[str, Any] = {}
        for key, value in payload.items():
            if key.lower() in SENSITIVE_KEYS:
                redacted[key] = "***REDACTED***"
                continue
            redacted[key] = value
        return redacted
