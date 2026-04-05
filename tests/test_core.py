"""Core module tests."""

from oris.core.enums import ExecutionStatus
from oris.core.exceptions import ConfigurationError, OrisError


def test_execution_status_values() -> None:
    assert ExecutionStatus.SUCCEEDED.value == "succeeded"


def test_exception_hierarchy() -> None:
    err = ConfigurationError("bad config")
    assert isinstance(err, OrisError)
