# API and command-line reference

This page covers the public calculation and I/O functions exported by
`saxsabs`, plus the installed `saxsabs` command. Inputs are not inferred when
their physical meaning is ambiguous; callers must supply the applicable
measurement semantics and provenance.

## Core calculations

### Monitor normalization

```python
compute_norm_factor(exp: float | None, mon: float | None,
                    trans: float | None, mode: str) -> float
```

Returns the normalization product for `mode="rate"` (`exp * mon * trans`) or
`mode="integrated"` (`mon * trans`). Transmission must be in `(0, 1]`; missing,
non-positive, or non-finite required values return `math.nan`. An unknown mode
raises `ValueError`.

```python
from saxsabs import compute_norm_factor

factor = compute_norm_factor(1.0, 100000.0, 0.8, "rate")
assert factor == 80000.0
```

### Robust K-factor estimation

```python
estimate_k_factor_robust(
    q_meas: np.ndarray, i_meas_per_cm: np.ndarray,
    q_ref: np.ndarray | None = None, i_ref: np.ndarray | None = None,
    q_window: tuple[float, float] = (0.01, 0.2),
    positive_floor: float = 1e-9, min_points: int = 3, *,
    i_ref_standard_uncertainty: np.ndarray | None = None,
    coverage_factor: float | None = None,
    standard_thickness_cm: float | None = None,
    parallelism_relative_tolerance: float | None = None,
) -> KFactorEstimationResult
```

Interpolates the measured profile on the reference q grid in `q_window`, forms
`I_ref / I_meas`, and applies median/MAD outlier rejection. If both reference
arrays are omitted, it uses the built-in NIST SRM 3600 reference. The result
contains the estimate and diagnostics; inspect it before applying a scale.

```python
from saxsabs import estimate_k_factor_robust

result = estimate_k_factor_robust(q_meas, i_meas_per_cm, q_ref, i_ref)
print(result.k_factor, result.points_used)
```

### Attenuation and thickness

```python
calculate_mu(composition: dict[str, float], density_g_cm3: float,
             energy_keV: float) -> MuResult
calculate_material_attenuation(composition: Mapping[str, object], *,
    composition_basis: str, table: AttenuationTable = NIST_30_KEV_TABLE,
    material_key: str | None = None, material_name: str | None = None,
    porosity_risk: bool = False) -> MaterialAttenuationResult
derive_fixed_thickness(material: MaterialAttenuationResult,
    transmissions: Iterable[object], *,
    anchor_scope: str = "provided_transmissions",
    drift_warning_relative_span: float = ...) -> FixedThicknessDerivation
```

`calculate_mu` accepts element weight fractions or weight percent, bulk density
in g/cm³, and energy in keV. `calculate_material_attenuation` requires
`composition_basis="wt_fraction"` exactly, so wt% and atomic fractions are not
silently guessed. `derive_fixed_thickness` derives a fixed thickness from the
median supplied transmission and returns warnings alongside its provenance.

```python
from saxsabs import calculate_mu

mu = calculate_mu({"Ti": 0.9, "Nb": 0.1}, density_g_cm3=5.0, energy_keV=30.0)
print(mu.mu_linear_cm_inv)
```

### State checks, subtraction, and uncertainty

```python
assess_intensity_state(profile: Mapping[str, object]) -> IntensityStateAssessment
subtract_buffer(q_sample, i_sample, err_sample, q_buffer, i_buffer, err_buffer,
                alpha: float = 1.0, high_q_diag: tuple[float, float] = (0.15, 0.25),
                *, alpha_uncertainty: float | None = None) -> BufferSubtractionResult
propagate_absolute_uncertainty(intensity: np.ndarray, *,
    statistical_standard_uncertainty=None, k_relative_standard_uncertainty=None,
    standard_relative_standard_uncertainty=None,
    transmission_relative_standard_uncertainty=None,
    monitor_relative_standard_uncertainty=None,
    thickness_relative_standard_uncertainty=None,
    mu_relative_standard_uncertainty=None, alpha_standard_uncertainty=None,
    buffer_intensity=None, coverage_factor=None) -> AbsoluteUncertaintyBudget
```

`assess_intensity_state` classifies metadata, units, and correction information;
conflicting evidence remains ambiguous. `subtract_buffer` interpolates a buffer
onto the sample q grid when necessary and propagates supplied uncertainties.
`propagate_absolute_uncertainty` combines statistical and supplied standard
uncertainty components; relative inputs must be relative standard uncertainties.

## I/O

```python
read_external_1d_profile(path: str | Path) -> dict[str, Any]
write_cansas1d_xml(path: str | Path, q: np.ndarray, i_abs: np.ndarray,
                   err: np.ndarray | None = None,
                   metadata: dict[str, Any] | None = None) -> Path
write_nxcansas_h5(path: str | Path, q: np.ndarray, i_abs: np.ndarray,
                  err: np.ndarray | None = None,
                  metadata: dict[str, Any] | None = None) -> Path
```

`read_external_1d_profile` reads supported text/tabular profiles and routes XML
and HDF5 extensions to canSAS/NXcanSAS readers. The returned mapping includes
the parsed arrays and parsing metadata. Writers expect q in Å⁻¹, absolute
intensity in cm⁻¹, and optional uncertainty in cm⁻¹. NXcanSAS writing requires
the optional `h5py` dependency.

```python
from saxsabs import read_external_1d_profile

profile = read_external_1d_profile("examples/profile_example.csv")
print(profile["x"], profile["i_rel"])
```

The parser deliberately names an uncalibrated intensity array `i_rel`. Do not
pass that array to an absolute-intensity writer. Call `write_cansas1d_xml` or
`write_nxcansas_h5` only after a validated calibration has established the
absolute intensity, uncertainty, units, and provenance.

Workbench K-only scaling is fail-closed: the imported relative profile must
declare `thickness` in `corrections_applied`, a finite positive
`thickness_cm`, and a non-empty `thickness_source`. These provenance keys are
preserved by the text, canSAS, and NXcanSAS paths so a downstream operation does
not rely on a ledger marker alone.

## Command line

Run `saxsabs --help` for the installed command and `saxsabs <command> --help`
for parameters. Required inputs are shown in angle brackets:

```text
saxsabs norm-factor --mon <counts> --trans <0<T<=1> --mode <rate|integrated> [--exp <seconds>]
saxsabs parse-header --header-json <path>
saxsabs parse-external1d --input <path>
saxsabs estimate-k --meas <path> --ref <path> [--q-col <name>] [--i-col <name>]
                    [--ref-q-col <name>] [--ref-i-col <name>] [--qmin <value>] [--qmax <value>]
saxsabs bl19b2-abs2d --input-root <path> (--poni <path>|--pydidas-cali-yaml <path>)
                         (--mu <cm^-1>|--sample-thickness-cm <cm>)
                         --monitor-mode <rate|integrated> [workflow options]
saxsabs bl19b2-abs2d-v1-legacy --input-root <path>
                                   (--poni <path>|--pydidas-cali-yaml <path>) [migration options]
```

The main commands are:

| Command | Input | Output |
| --- | --- | --- |
| `norm-factor` | exposure, monitor, transmission, mode | normalization value |
| `parse-header` | header JSON | extracted exposure/monitor/transmission JSON |
| `parse-external1d` | profile path | parsed-profile summary JSON |
| `estimate-k` | measured and reference tabular profiles | K-factor result JSON |
| `bl19b2-abs2d` | explicit BL19B2 inputs and semantics | batch result JSON and requested files |
| `bl19b2-abs2d-v1-legacy` | explicit migration choices | legacy-compatible batch result with documented assumptions |

The BL19B2 commands require explicit monitor mode and either attenuation
coefficient or fixed thickness. Read the [batch runbook](bl19b2_abs2d_batch_runbook.md)
for their full input contract and provenance requirements.

## Scientific boundary

These APIs provide software operations and checks; they do not establish that a
beamline measurement is calibrated. Users remain responsible for appropriate
reference standards, independently measured inputs, detector geometry, valid
units, and experiment-specific acceptance. The included synthetic 2D example
tests arithmetic and interoperability, not experimental beamline validation.
