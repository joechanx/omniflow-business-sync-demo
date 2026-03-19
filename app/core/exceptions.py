class SyncError(Exception):
    """Base exception for sync failures."""


class ProviderError(SyncError):
    """Raised when a provider integration fails."""


class ConnectorError(SyncError):
    """Raised when a downstream connector fails."""


class WorkflowError(SyncError):
    """Raised when workflow execution fails."""
