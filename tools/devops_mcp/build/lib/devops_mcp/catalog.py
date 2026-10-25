"""Load and validate the curated, repository-local practical catalog."""

from __future__ import annotations

import json
import re
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any


PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PACKAGE_DIR.parent
REPOSITORY_ROOT = PROJECT_DIR.parents[1]
CATALOG_PATH = PROJECT_DIR / "catalog.json"
MAX_GUIDE_BYTES = 512_000
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_FIELDS = {
    "slug",
    "title",
    "phase",
    "domain",
    "level",
    "duration_minutes",
    "prerequisites",
    "environment",
    "risk_cost",
    "goal",
    "verification",
    "cleanup",
    "guide",
    "answer",
    "tags",
}


class CatalogError(ValueError):
    """Raised when the local catalog is invalid or references unsafe paths."""


def _resolve_catalog_path(value: str | None) -> Path | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise CatalogError("catalog paths must be non-empty relative paths or null")
    relative_path = PurePosixPath(value)
    if relative_path.is_absolute() or ".." in relative_path.parts or relative_path.suffix.lower() != ".md":
        raise CatalogError(f"catalog paths must be relative Markdown paths without traversal: {value}")
    candidate = (REPOSITORY_ROOT / value).resolve()
    try:
        candidate.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise CatalogError(f"catalog path escapes repository: {value}") from error
    if not candidate.is_file():
        raise CatalogError(f"catalog path does not exist: {value}")
    return candidate


def load_catalog() -> list[dict[str, Any]]:
    """Load entries and ensure every referenced guide remains repository-local."""
    try:
        entries = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CatalogError(f"cannot load practical catalog: {error}") from error
    if not isinstance(entries, list):
        raise CatalogError("catalog root must be a JSON array")

    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or not REQUIRED_FIELDS.issubset(entry):
            raise CatalogError("each catalog entry must contain every required field")
        slug = entry["slug"]
        if not isinstance(slug, str) or not SLUG_PATTERN.fullmatch(slug) or slug in seen:
            raise CatalogError(f"invalid or duplicate practical slug: {slug!r}")
        seen.add(slug)
        for field in ("title", "phase", "domain", "level", "environment", "risk_cost", "goal", "cleanup"):
            if not isinstance(entry[field], str) or not entry[field].strip():
                raise CatalogError(f"{slug}: {field} must be a non-empty string")
        if not isinstance(entry["duration_minutes"], int) or entry["duration_minutes"] <= 0:
            raise CatalogError(f"{slug}: duration_minutes must be a positive integer")
        for field in ("prerequisites", "verification", "tags"):
            if not isinstance(entry[field], list) or not all(isinstance(item, str) for item in entry[field]):
                raise CatalogError(f"{slug}: {field} must be a list of strings")
        _resolve_catalog_path(entry["guide"])
        _resolve_catalog_path(entry["answer"])
    return entries


def find_practical(slug: str) -> dict[str, Any] | None:
    return next((entry for entry in load_catalog() if entry["slug"] == slug), None)


def read_catalog_file(entry: dict[str, Any], field: str) -> str | None:
    """Read only a guide or answer path already declared in a validated entry."""
    if field not in {"guide", "answer"}:
        raise CatalogError("only guide and answer files are readable")
    path = _resolve_catalog_path(entry.get(field))
    if path is None:
        return None
    if path.stat().st_size > MAX_GUIDE_BYTES:
        raise CatalogError(f"catalog document exceeds {MAX_GUIDE_BYTES} bytes: {entry['slug']}/{field}")
    return path.read_text(encoding="utf-8")
