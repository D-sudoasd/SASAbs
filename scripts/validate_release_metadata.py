"""Fail closed before publishing a version tag as a GitHub Release."""

from __future__ import annotations

import argparse
from datetime import date
import json
import os
from pathlib import Path
import re

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised by the Python 3.10 CI job
    import tomli as tomllib


class ReleaseMetadataError(ValueError):
    """Raised when a tagged release still contains provisional metadata."""


FINAL_RELEASE_MESSAGE = "Cite the version-specific archive record for this release."


def _yaml_scalar(text: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", text)
    if match is None:
        raise ReleaseMetadataError(f"CITATION.cff is missing {key}")
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    if not value:
        raise ReleaseMetadataError(f"CITATION.cff has an empty {key}")
    return value


def _paper_title(paper: str) -> str:
    front_matter = re.match(r"\A---\s*\n(.*?)\n---\s*\n", paper, re.DOTALL)
    if front_matter is None:
        raise ReleaseMetadataError("paper/paper.md has no parseable YAML front matter")
    match = re.search(r"(?m)^title:\s*(.+?)\s*$", front_matter.group(1))
    if match is None:
        raise ReleaseMetadataError("paper/paper.md has no title")
    title = match.group(1).strip()
    if len(title) >= 2 and title[0] == title[-1] and title[0] in {"'", '"'}:
        title = title[1:-1]
    if not title:
        raise ReleaseMetadataError("paper/paper.md has an empty title")
    return title


def _dated_changelog_release(changelog: str, version: str) -> date:
    headings = re.findall(
        rf"(?m)^## \[{re.escape(version)}\] - (.+?)\s*$",
        changelog,
    )
    if len(headings) != 1:
        raise ReleaseMetadataError(
            f"CHANGELOG must contain exactly one heading for version {version}"
        )
    value = headings[0].strip()
    if value.casefold() == "unreleased":
        raise ReleaseMetadataError(f"finalize the CHANGELOG date for {version} before tagging")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ReleaseMetadataError(
            f"CHANGELOG release date {value!r} is not a valid ISO calendar date"
        ) from exc
    if parsed.isoformat() != value:
        raise ReleaseMetadataError(
            f"CHANGELOG release date {value!r} must use zero-padded YYYY-MM-DD"
        )
    return parsed


def validate_release_metadata(root: Path, tag: str) -> tuple[str, date]:
    """Validate tag, changelog, CFF, CodeMeta, Zenodo, and paper identity."""
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    try:
        version = pyproject["project"]["version"]
    except KeyError as exc:
        raise ReleaseMetadataError("pyproject.toml is missing project.version") from exc
    if not isinstance(version, str) or not version.strip():
        raise ReleaseMetadataError("pyproject.toml project.version is not a non-empty string")

    expected_tag = f"v{version}"
    if tag != expected_tag:
        raise ReleaseMetadataError(f"release tag {tag!r} does not match {expected_tag!r}")

    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    release_date = _dated_changelog_release(changelog, version)

    citation = (root / "CITATION.cff").read_text(encoding="utf-8")
    if _yaml_scalar(citation, "message") != FINAL_RELEASE_MESSAGE:
        raise ReleaseMetadataError(
            "CITATION.cff message is not the finalized release citation instruction"
        )
    if _yaml_scalar(citation, "version") != version:
        raise ReleaseMetadataError("CITATION.cff version does not match project.version")
    citation_date = _yaml_scalar(citation, "date-released")
    try:
        parsed_citation_date = date.fromisoformat(citation_date)
    except ValueError as exc:
        raise ReleaseMetadataError(
            f"CITATION.cff date-released {citation_date!r} is not a valid ISO calendar date"
        ) from exc
    if parsed_citation_date != release_date or citation_date != release_date.isoformat():
        raise ReleaseMetadataError(
            "CITATION.cff date-released does not match the dated CHANGELOG heading"
        )

    codemeta = json.loads((root / "codemeta.json").read_text(encoding="utf-8"))
    if codemeta.get("version") != version:
        raise ReleaseMetadataError("codemeta.json version does not match project.version")

    zenodo = json.loads((root / ".zenodo.json").read_text(encoding="utf-8"))
    if zenodo.get("version") != version:
        raise ReleaseMetadataError(".zenodo.json version does not match project.version")
    paper_title = _paper_title((root / "paper" / "paper.md").read_text(encoding="utf-8"))
    if zenodo.get("title") != paper_title:
        raise ReleaseMetadataError(".zenodo.json title does not match the JOSS paper title")

    return version, release_date


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--tag", default=os.environ.get("GITHUB_REF_NAME", ""))
    args = parser.parse_args()
    try:
        version, release_date = validate_release_metadata(args.root, args.tag)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"release metadata invalid: {exc}\n")
    print(f"release_metadata=PASS version={version} date={release_date.isoformat()}")


if __name__ == "__main__":
    main()
