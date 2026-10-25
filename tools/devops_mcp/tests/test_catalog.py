import json

import pytest

from devops_mcp import catalog


def test_catalog_entries_have_existing_allowlisted_guides():
    entries = catalog.load_catalog()

    assert len(entries) >= 20
    assert len({entry["slug"] for entry in entries}) == len(entries)
    for entry in entries:
        assert catalog.read_catalog_file(entry, "guide")
        if entry["answer"] is not None:
            assert catalog.read_catalog_file(entry, "answer")


def test_catalog_rejects_paths_outside_repository(tmp_path, monkeypatch):
    unsafe_catalog = tmp_path / "catalog.json"
    entry = {
        "slug": "unsafe",
        "title": "Unsafe",
        "phase": "test",
        "domain": "test",
        "level": "foundation",
        "duration_minutes": 1,
        "prerequisites": [],
        "environment": "test",
        "risk_cost": "test",
        "goal": "test",
        "verification": [],
        "cleanup": "test",
        "guide": "../../../../etc/passwd",
        "answer": None,
        "tags": [],
    }
    unsafe_catalog.write_text(json.dumps([entry]), encoding="utf-8")
    monkeypatch.setattr(catalog, "CATALOG_PATH", unsafe_catalog)

    with pytest.raises(catalog.CatalogError, match="relative Markdown paths"):
        catalog.load_catalog()


def test_only_catalogued_markdown_can_be_read():
    entry = catalog.find_practical("docker-production-image")
    assert entry is not None
    with pytest.raises(catalog.CatalogError, match="only guide and answer"):
        catalog.read_catalog_file(entry, "../../README.md")


def test_catalog_rejects_missing_guide(tmp_path, monkeypatch):
    catalog_path = tmp_path / "catalog.json"
    entry = {
        "slug": "missing-guide",
        "title": "Missing guide",
        "phase": "test",
        "domain": "test",
        "level": "foundation",
        "duration_minutes": 1,
        "prerequisites": [],
        "environment": "test",
        "risk_cost": "test",
        "goal": "test",
        "verification": [],
        "cleanup": "test",
        "guide": "README_DOES_NOT_EXIST.md",
        "answer": None,
        "tags": [],
    }
    catalog_path.write_text(json.dumps([entry]), encoding="utf-8")
    monkeypatch.setattr(catalog, "CATALOG_PATH", catalog_path)

    with pytest.raises(catalog.CatalogError, match="does not exist"):
        catalog.load_catalog()
