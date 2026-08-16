# Submission readiness snapshot

Updated: 16 August 2026 (Asia/Shanghai)

Review the unreleased 2.0.0 tree on `main`, not GitHub Release v1.1.1. Do not
create `v2.0.0`, a GitHub Release, or a Zenodo version archive during review.

## Locally verified

- Full source suite: PASS in a fully provisioned Python 3.13 environment; exact
  count and duration are retained in the dated external validation record.
- Ruff: root modules, package, tests, paper scripts, and submission gate pass.
- README: 5 local images and all local links resolve; SVG/image audit passes.
- Minimal 2D example: K and sample maximum relative errors are
  `0.001933697...`; CSV, TSV, XML, and HDF5 outputs are written.
- Fresh-copy distribution build: wheel and sdist PASS from a source tree
  outside every Git checkout. The exact archive inventory is retained in the
  dated external validation record; the sdist includes README assets,
  workflows, docs, examples, tests, and paper sources.
- Installed-wheel smoke: CLI reports `saxsabs 2.0.0`; `SASAbs`,
  `saxs_mpl_style`, and `saxsabs` import from the temporary environment; the
  copied minimal example passes outside the checkout. A fresh Python 3.13
  environment resolves the declared GUI/HDF5 extras with no broken
  requirements.
- Paper: 1100-word body by the documented Pandoc method; 16 references; current
  Inara TeX and well-formed JATS resolve both figures.
- Review PDF: the official CI paper job produces a five-page draft whose pages,
  bounds, figures, citations, and embedded fonts have been visually checked.
  Exact run URL, byte size, and SHA-256 belong in the dated external validation
  record because CI evidence must identify the submitted commit. The 1280 x 900
  GUI image is a real, reproducible full-window Workbench capture.
- Public CI gate: immediately before submission, the exact submitted HEAD must
  have green push and Draft-PR runs for the complete matrix. Immutable commit
  IDs and run URLs belong in the dated external validation record rather than
  this tracked file, because editing the evidence here creates a new HEAD.
- External format checks (offline 15 August 2026, not in CI): the deterministic
  example's canSAS1d XML validated against the official 1.1 XSD with zero
  errors. Its NXcanSAS HDF5 output passed punx 0.3.5 with bundled v2018.5
  definitions (97 OK, 0 WARN, 0 ERROR); current NeXus definitions and
  third-party consumers remain unverified.

## Must be resolved before submission

1. Recheck the public-history gate on or after 26 August 2026. JOSS requires
   more than six months of public, iterative development; the repository was
   created on 25 February 2026.
2. Add a verifiable research-use case. Synthetic validation and tests do not
   establish demonstrated research impact.
3. Confirm the complete author list/order, corresponding author, current email,
   affiliations, ORCIDs, and contribution roles.
4. Complete the AI disclosure with recoverable product/model/version details,
   usage scope, and the author's final human-review assertion.
5. Supply truthful funding, sponsor-role, acknowledgement, and competing-
   interest statements.
6. Before submission, verify that the public GitHub description, homepage
   concept DOI, visible README, submitted branch, and green CI all identify the
   exact candidate revision.
Run the strict decision gate with Pandoc available:

```bash
python scripts/check_submission_readiness.py \
  --as-of YYYY-MM-DD \
  --manual-confirmations path/to/submission-confirmations.json
```

The gate must run on the exact branch and commit submitted to JOSS. PR #1 is
already on `main`; rerun the gate on the clean `main` commit that will be
submitted and record `submitted_branch` and `submitted_commit` accordingly.
Evidence from an earlier revision is not evidence for a later commit.

After that local PASS, run:

```bash
python scripts/check_public_candidate.py \
  --confirmations path/to/submission-confirmations.json
```

This second fail-closed gate uses the public GitHub API to verify the repository,
concept-DOI homepage, license, submitted branch and SHA, visible README and
paper blobs, and successful CI run for that exact SHA. It also reports the
editorialbot branch command when the paper is not on `main`.

The current strict result is intentionally **FAIL** because the paper still has
four author-input placeholders, no confirmed corresponding author, and no paper
email. The mechanical preflight passes when
`--allow-author-placeholders --as-of 2026-08-26` is used; this override is not a
submission authorization.

## Review-completion actions

JOSS asks authors to make a tagged release and archive the reviewed revision
after successful review. Do not create `v2.0.0`, a GitHub Release, or a Zenodo
version archive until the candidate revision and remote workflow have been
confirmed.

The paper source is dated 26 August 2026, the earliest conservative submission
date. If submission occurs later, update the YAML date to the actual submission
date; the strict readiness gate will reject a mismatch.

The local review PDF still shows Inara pre-submission placeholders such as
`DOI: N/A`, 1970 dates, and volume/page fields. They are build metadata supplied
by the publication workflow, not text in `paper/paper.md`.
