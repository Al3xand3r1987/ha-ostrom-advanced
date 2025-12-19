"""Tests for integration manifest."""

from __future__ import annotations

import json
from pathlib import Path

from custom_components.ostrom_advanced.const import DOMAIN


def test_manifest_domain_matches_const() -> None:
    """Verify manifest domain matches the integration domain."""
    manifest_path = (
        Path(__file__).resolve().parents[1]
        / "custom_components"
        / "ostrom_advanced"
        / "manifest.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["domain"] == DOMAIN
