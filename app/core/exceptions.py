class DailyIntelligenceError(Exception):
    """Base exception for all domain errors in Daily Intelligence."""
    pass


class IngestionError(DailyIntelligenceError):
    """Raised when source collection or RSS parsing fails."""
    pass


class SourceConnectionError(IngestionError):
    """Raised when connecting to a remote news source fails or times out."""
    pass


class ProviderError(DailyIntelligenceError):
    """Raised when an external or local AI/Translation provider fails."""
    pass


class StorageError(DailyIntelligenceError):
    """Raised when database or file operations fail."""
    pass


class EntityNotFoundError(DailyIntelligenceError):
    """Raised when a requested resource does not exist."""
    pass
