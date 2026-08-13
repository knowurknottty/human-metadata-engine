"""Backward-compatible import for the canonical birth validator."""

from birth_validation import BirthValidationError, canonical_birth_record, validate_birth

__all__ = ["BirthValidationError", "canonical_birth_record", "validate_birth"]
