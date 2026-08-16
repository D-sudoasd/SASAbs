"""Build the GitHub Release header from the project-level concept DOI."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised by the Python 3.10 CI job
    import tomli as tomllib


DOI_URL_PATTERN = re.compile(r"https://doi\.org/[0-9]+\.[0-9]+/\S+\Z")


def read_concept_doi(pyproject_path: Path) -> str:
    metadata = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    try:
        doi_url = metadata["project"]["urls"]["Concept DOI"]
    except KeyError as exc:
        raise ValueError("pyproject.toml is missing project.urls['Concept DOI']") from exc
    if not isinstance(doi_url, str) or DOI_URL_PATTERN.fullmatch(doi_url) is None:
        raise ValueError(f"invalid project Concept DOI URL: {doi_url!r}")
    return doi_url


def build_release_body(doi_url: str) -> str:
    return (
        f"Project DOI: {doi_url}\n\n"
        "Use the project DOI for general citation. A release-specific DOI is available "
        "only after Zenodo archives that release.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pyproject", type=Path, default=Path("pyproject.toml"))
    parser.add_argument("--output", type=Path, default=Path("release-body.md"))
    args = parser.parse_args()

    doi_url = read_concept_doi(args.pyproject)
    args.output.write_text(build_release_body(doi_url), encoding="utf-8")


if __name__ == "__main__":
    main()
