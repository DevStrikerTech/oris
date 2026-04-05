"""Enumerations used across runtime execution."""

from enum import Enum


class ExecutionStatus(str, Enum):
    """Canonical execution lifecycle statuses."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
