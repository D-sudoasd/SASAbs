# Reviewer FAQ

## Why keep the root Workbench module?

The root module is the maintained Tk desktop application and compatibility
entry point. Reusable scientific and I/O logic lives under `src/saxsabs/`; the
GUI remains separate because the current Workbench and strict BL19B2 campaign
runner have intentionally different ownership boundaries.

## How can this be tested without GUI?

Core logic is exposed as importable APIs and CLI commands. Tests run headlessly in CI.

## Data cannot be fully public. How is reproducibility addressed?

The repository includes synthetic examples, a deterministic raw-frame
validation package (`examples/minimal_2d/`), and automated tests. A manual
verification checklist documents exact commands and expected acceptance ranges.

## Can reviewers verify the numerical 2D chain without beamline data?

Yes. Run:

```bash
python examples/minimal_2d/run_minimal_2d_pipeline.py
```

The script constructs independent dark, blank, SRM 3600, and sample frames,
gates the standard profile as `relative` before $K$, writes labeled
`absolute_cm^-1` outputs (CSV/TSV/canSAS XML and optional NXcanSAS HDF5),
checks that the XML exposes `i_abs` not `i_rel`, and writes numerical K and
sample-intensity errors to `summary.json`. This recovers a planted synthetic
curve within script tolerances. It is a software golden test, not measured
beamline validation or third-party format validation.

## Have the structured exports been checked outside the project readers?

Yes, with a bounded offline result that is not in CI. On 15 August 2026, the
minimal example's XML output validated with zero errors against `cansas1d.xsd`
from the official canSAS `1dwg` repository (blob
`c376e590bf6c297ee5664834183b6d09b5684318`). The HDF5 output passed punx 0.3.5
against its bundled NeXus v2018.5 definitions with 97 OK, 0 WARN, and 0 ERROR
findings. punx 0.3.5 could not parse the current NeXus `main` definitions
(commit `6313522`), so the project does not claim validation against current
definitions or a third-party application consumer.

## Which revision should be reviewed?

Review the unreleased 2.0.0 tree on `main`. GitHub Release v1.1.1 is an earlier
archive and is not this candidate. Do not create `v2.0.0` or a new Zenodo
version record during review.

## What is the software boundary?

`saxsabs` is a reusable SAXS absolute-calibration package with deterministic
software validation and a documented protocol for separate beamline acceptance.
