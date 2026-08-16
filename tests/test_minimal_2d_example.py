import json
import os
from pathlib import Path
import subprocess
import sys


def test_minimal_2d_example_uses_deterministic_raw_frame_golden(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]
    script = repo / "examples" / "minimal_2d" / "run_minimal_2d_pipeline.py"
    output = tmp_path / "outputs"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo / "src")

    completed = subprocess.run(
        [sys.executable, str(script), "--output-dir", str(output)],
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    assert summary["validation_type"] == "deterministic_synthetic_raw_frames"
    assert summary["detector_shape"] == [9, 9]
    assert summary["reduction"] == "homemade_integer_bin_radial_average"
    assert summary["uses_pyfai"] is False
    assert summary["uses_bl19b2_campaign"] is False
    assert summary["k_relative_error"] < 0.005
    assert summary["sample_max_relative_error"] < 0.01
    assert summary["uncertainty_status"] == "unknown_without_input_variances"
    xml_text = (output / "absolute_profile.xml").read_text(encoding="utf-8")
    assert "1/cm" in xml_text

