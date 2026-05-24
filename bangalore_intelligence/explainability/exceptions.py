"""Explainability registry exceptions."""


class ExplainabilityRegistryError(Exception):
    """Base exception for explainability registry failures."""


class ExplainabilityValidationError(ExplainabilityRegistryError):
    """Raised when registry metadata violates its schema or integrity rules."""


class DuplicateExplainabilityEntryError(ExplainabilityValidationError):
    """Raised when more than one entry uses the same surface ID."""


__all__ = [
    "DuplicateExplainabilityEntryError",
    "ExplainabilityRegistryError",
    "ExplainabilityValidationError",
]
