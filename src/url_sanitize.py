"""URL scheme allowlist sanitizer.

HTML escaping alone is not sufficient for href attributes.  A user or
data source could supply ``javascript:`` or ``data:`` URIs that execute
when rendered as ``<a href="...">``.  This module provides a strict
scheme allowlist used wherever URLs pass from storage into rendered
output.
"""

from __future__ import annotations

from urllib.parse import urlparse

ALLOWED_SCHEMES = frozenset({"https", "http"})


def sanitize_url(url: str | None, *, allow_http: bool = False) -> str | None:
    """Return *url* if its scheme is allowlisted, else ``None``.

    Parameters
    ----------
    url:
        Raw URL string.
    allow_http:
        If *True*, ``http:`` is permitted alongside ``https:``.  The
        default is *False* — only ``https:`` passes.

    Returns
    -------
    str or None
        The original URL when the scheme passes, or ``None`` when it
        does not.  ``None`` inputs always return ``None``.
    """
    if not url or not isinstance(url, str):
        return None
    try:
        parsed = urlparse(url.strip())
    except Exception:
        return None
    scheme = parsed.scheme.lower()
    allowed = ALLOWED_SCHEMES if allow_http else frozenset({"https"})
    if scheme not in allowed:
        return None
    # Reject any URL that still contains control characters or
    # characters that could confuse downstream HTML parsers.
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in url):
        return None
    return url


def validate_source_urls(sources: dict) -> dict[str, str | None]:
    """Return a mapping of source_id -> sanitized URL (or None if bad).

    Intended for test-time validation of the SOURCES dict.
    """
    results: dict[str, str | None] = {}
    for source_id, source_data in sources.items():
        results[source_id] = sanitize_url(source_data.get("url"))
    return results
