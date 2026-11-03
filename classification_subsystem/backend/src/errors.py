class ClassificationError(Exception):
    """Base error for this subsystem."""


class InvalidImageError(ClassificationError):
    """The uploaded image cannot be processed."""


class RuleNotFoundError(ClassificationError):
    """No regional rule exists for a known waste class."""
