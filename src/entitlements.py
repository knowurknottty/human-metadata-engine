"""Provider-neutral verification for future paid household entitlements.

The application does not issue these tokens. A future payment/webhook service may
mint signed entitlement-v1 claims after server-side payment verification.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from typing import Any


ENTITLEMENT_VERSION = "entitlement-v1"
PAID_FLAG = "HME_HOUSEHOLD_PAID_ENABLED"
SIGNING_KEY_ENV = "HME_ENTITLEMENT_SIGNING_KEY"


@dataclass(frozen=True)
class EntitlementDecision:
    allowed: bool
    code: str
    subject_limit: int = 0
    expires_at: int | None = None


def household_paid_enabled() -> bool:
    return os.environ.get(PAID_FLAG, "").strip().lower() in {"1", "true", "yes", "on"}


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _canonical_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def verify_entitlement_token(
    token: str | None,
    *,
    household_id: str,
    required_added_subjects: int,
    secret: str | None = None,
    now: int | None = None,
) -> EntitlementDecision:
    """Verify one externally-issued signed entitlement.

    Token format: base64url(canonical-json) + "." + base64url(HMAC-SHA256(payload)).
    No mint/issue function is provided by the public application.
    """
    if not household_paid_enabled():
        return EntitlementDecision(False, "paid_feature_disabled")
    key = secret if secret is not None else os.environ.get(SIGNING_KEY_ENV)
    if not isinstance(key, str) or len(key) < 32:
        return EntitlementDecision(False, "entitlement_verifier_unconfigured")
    if not isinstance(token, str) or token.count(".") != 1:
        return EntitlementDecision(False, "missing_or_malformed_entitlement")
    encoded_payload, encoded_signature = token.split(".", 1)
    try:
        raw_payload = _b64decode(encoded_payload)
        supplied_signature = _b64decode(encoded_signature)
        payload = json.loads(raw_payload)
    except Exception:
        return EntitlementDecision(False, "missing_or_malformed_entitlement")
    expected_signature = hmac.new(key.encode("utf-8"), raw_payload, hashlib.sha256).digest()
    if not hmac.compare_digest(supplied_signature, expected_signature):
        return EntitlementDecision(False, "invalid_entitlement_signature")
    if not isinstance(payload, dict):
        return EntitlementDecision(False, "invalid_entitlement_claims")
    required = {"schema_version", "scope", "household_id", "subject_limit", "issued_at", "expires_at", "jti"}
    if set(payload) != required:
        return EntitlementDecision(False, "invalid_entitlement_claims")
    if payload.get("schema_version") != ENTITLEMENT_VERSION or payload.get("scope") != "household":
        return EntitlementDecision(False, "invalid_entitlement_claims")
    if payload.get("household_id") != household_id:
        return EntitlementDecision(False, "entitlement_household_mismatch")
    subject_limit = payload.get("subject_limit")
    issued_at = payload.get("issued_at")
    expires_at = payload.get("expires_at")
    jti = payload.get("jti")
    if (
        type(subject_limit) is not int or not 1 <= subject_limit <= 7
        or type(issued_at) is not int or issued_at < 0
        or type(expires_at) is not int or expires_at <= 0
        or not isinstance(jti, str) or not 16 <= len(jti) <= 128
    ):
        return EntitlementDecision(False, "invalid_entitlement_claims")
    current = int(time.time()) if now is None else int(now)
    if issued_at > current + 300:
        return EntitlementDecision(False, "entitlement_not_yet_valid")
    if expires_at <= current:
        return EntitlementDecision(False, "entitlement_expired", subject_limit, expires_at)
    if required_added_subjects < 1 or required_added_subjects > subject_limit:
        return EntitlementDecision(False, "entitlement_subject_limit_exceeded", subject_limit, expires_at)
    return EntitlementDecision(True, "allowed", subject_limit, expires_at)


def household_feature_state() -> dict[str, Any]:
    configured = bool(os.environ.get(SIGNING_KEY_ENV, "")) and len(os.environ.get(SIGNING_KEY_ENV, "")) >= 32
    enabled = household_paid_enabled()
    return {
        "single_scan_free": True,
        "household_contract": "household-v1",
        "relational_contract": "relational-view-v1",
        "entitlement_contract": ENTITLEMENT_VERSION,
        "paid_household_enabled": enabled,
        "entitlement_verifier_configured": configured,
        "public_add_subject_enabled": enabled and configured,
        "pricing_model": "pair_or_household_tier",
        "configured_prices": None,
        "payment_provider": None,
    }
