from __future__ import annotations

from datetime import date
import json
from pathlib import Path

import pytest

from scripts.validate_release_metadata import (
    FINAL_RELEASE_MESSAGE,
    ReleaseMetadataError,
    validate_release_metadata,
)


TITLE = (
    "saxsabs: Absolute-intensity calibration and provenance tracking for "
    "small-angle X-ray scattering"
)


def _write_valid_release(root: Path) -> None:
    (root / "paper").mkdir(parents=True)
    (root / "pyproject.toml").write_text(
        '[project]\nname = "saxsabs"\nversion = "2.0.0"\n',
        encoding="utf-8",
    )
    (root / "CHANGELOG.md").write_text(
        "## [2.0.0] - 2026-08-26\n\n- Final release.\n",
        encoding="utf-8",
    )
    (root / "CITATION.cff").write_text(
        f'cff-version: 1.2.0\nmessage: "{FINAL_RELEASE_MESSAGE}"\n'
        'version: "2.0.0"\ndate-released: "2026-08-26"\n',
        encoding="utf-8",
    )
    (root / "codemeta.json").write_text(
        json.dumps({"version": "2.0.0"}),
        encoding="utf-8",
    )
    (root / ".zenodo.json").write_text(
        json.dumps({"title": TITLE, "version": "2.0.0"}),
        encoding="utf-8",
    )
    (root / "paper" / "paper.md").write_text(
        f"---\ntitle: '{TITLE}'\n---\n\n# Summary\n",
        encoding="utf-8",
    )


def test_valid_release_metadata_passes(tmp_path: Path) -> None:
    _write_valid_release(tmp_path)

    assert validate_release_metadata(tmp_path, "v2.0.0") == (
        "2.0.0",
        date(2026, 8, 26),
    )


@pytest.mark.parametrize("bad_date", ["2026-99-99", "2026-02-30", "26 August 2026"])
def test_invalid_changelog_calendar_date_is_rejected(tmp_path: Path, bad_date: str) -> None:
    _write_valid_release(tmp_path)
    (tmp_path / "CHANGELOG.md").write_text(
        f"## [2.0.0] - {bad_date}\n",
        encoding="utf-8",
    )

    with pytest.raises(ReleaseMetadataError, match="valid ISO calendar date"):
        validate_release_metadata(tmp_path, "v2.0.0")


@pytest.mark.parametrize(
    "message",
    [
        "version 2.0.0 is currently unreleased",
        "version 2.0.0 is unreleased",
        "UNRELEASED candidate",
        "version 2.0.0 is not yet released",
        "version 2.0.0 has not been released",
        "pre-release candidate",
        "release DOI pending",
        "version 2.0.0 is not archived",
    ],
)
def test_nonfinal_citation_message_is_rejected(tmp_path: Path, message: str) -> None:
    _write_valid_release(tmp_path)
    (tmp_path / "CITATION.cff").write_text(
        f'cff-version: 1.2.0\nmessage: "{message}"\n'
        'version: "2.0.0"\ndate-released: "2026-08-26"\n',
        encoding="utf-8",
    )

    with pytest.raises(ReleaseMetadataError, match="message is not the finalized"):
        validate_release_metadata(tmp_path, "v2.0.0")


def test_release_identity_mismatches_are_rejected(tmp_path: Path) -> None:
    cases = {
        "tag": ("v2.0.1", "release tag"),
        "citation-date": ("v2.0.0", "date-released does not match"),
        "zenodo-title": ("v2.0.0", "title does not match"),
        "codemeta-version": ("v2.0.0", "codemeta.json version"),
    }
    for name, (tag, expected) in cases.items():
        root = tmp_path / name
        _write_valid_release(root)
        if name == "citation-date":
            path = root / "CITATION.cff"
            path.write_text(
                path.read_text(encoding="utf-8").replace("2026-08-26", "2026-08-27"),
                encoding="utf-8",
            )
        elif name == "zenodo-title":
            (root / ".zenodo.json").write_text(
                json.dumps({"title": "Wrong title", "version": "2.0.0"}),
                encoding="utf-8",
            )
        elif name == "codemeta-version":
            (root / "codemeta.json").write_text(
                json.dumps({"version": "9.9.9"}),
                encoding="utf-8",
            )

        with pytest.raises(ReleaseMetadataError, match=expected):
            validate_release_metadata(root, tag)
