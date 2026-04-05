"""Custom exception hierarchy for Oris."""


class OrisError(Exception):
    """Base exception for all framework errors."""


class ConfigurationError(OrisError):
    """Raised when pipeline configuration is invalid."""


class PipelineExecutionError(OrisError):
    """Raised when pipeline execution fails."""


class ComponentExecutionError(PipelineExecutionError):
    """Raised when a component fails during runtime."""


class GuardViolationError(PipelineExecutionError):
    """Raised when input or output policy checks fail."""
