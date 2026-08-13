"""Pytest collection bridge for the repository's legacy script suites."""

# These files are executable regression programs, not import-safe pytest
# modules. ``test_legacy_script_suites.py`` runs each in an isolated process so
# failures still fail standard pytest without executing code during collection.
collect_ignore = [
    "test_analytics.py",
    "test_claim_compiler.py",
    "test_coherence_gate.py",
    "test_hardening_regression.py",
    "test_sigil.py",
]
