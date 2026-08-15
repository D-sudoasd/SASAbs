from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_release_notes_use_project_concept_doi(tmp_path: Path) -> None:
    output = tmp_path / "release-body.md"

    result = subprocess.run(
        [
            sys.executable,
            str(REPOSITORY_ROOT / "scripts" / "build_release_notes.py"),
            "--pyproject",
            str(REPOSITORY_ROOT / "pyproject.toml"),
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    body = output.read_text(encoding="utf-8")
    assert "https://doi.org/10.5281/zenodo.19687103" in body
    assert "release-specific DOI" in body


def test_release_notes_fail_closed_without_concept_doi(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "example"\nversion = "1.0.0"\n[project.urls]\n',
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(REPOSITORY_ROOT / "scripts" / "build_release_notes.py"),
            "--pyproject",
            str(pyproject),
            "--output",
            str(tmp_path / "release-body.md"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "missing project.urls['Concept DOI']" in result.stderr
