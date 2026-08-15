# Submission readiness snapshot

Updated: 15 August 2026 (Asia/Shanghai)

## Locally verified

- Source suite: 696 passed on Python 3.13.
- Ruff: root modules, package, tests, paper scripts, and submission gate pass.
- README: 5 local images and all local links resolve; SVG/image audit passes.
- Minimal 2D example: K and sample maximum relative errors are
  `0.001933697...`; CSV, TSV, XML, and HDF5 outputs are written.
- Fresh-copy distribution build: 36-entry wheel and 140-entry sdist build from
  a source tree outside every Git checkout. The sdist includes README assets,
  workflows, docs, examples, tests, and paper sources.
- Installed-wheel smoke: CLI reports `saxsabs 2.0.0`; `SASAbs`,
  `saxs_mpl_style`, and `saxsabs` import from the temporary environment; the
  copied minimal example passes outside the checkout. A fresh Python 3.13
  environment resolves the declared GUI/HDF5 extras with no broken
  requirements.
- Paper: 1081-word body by the documented Pandoc method; 15 references; current
  Inara TeX and well-formed JATS resolve both figures.
- Review PDF: three-pass LuaLaTeX build, 5 pages, 697,072 bytes; all five pages
  rendered at 144 dpi and visually checked. The 1280 x 900 GUI image is a real,
  reproducible full-window Workbench capture.
- Public CI: commit `58c82770d96ff3d702c252d4b113900439c33e19`
  completed both the [push run](https://github.com/D-sudoasd/SASAbs/actions/runs/31887917615)
  and [Draft-PR run](https://github.com/D-sudoasd/SASAbs/actions/runs/31887920199)
  with 26/26 successful checks. The matrix covers Ubuntu, Windows, and macOS
  with Python 3.10-3.13, plus the Inara paper build.

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
Run the strict decision gate with Pandoc available:

```bash
python scripts/check_submission_readiness.py \
  --as-of YYYY-MM-DD \
  --manual-confirmations path/to/submission-confirmations.json
```

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
