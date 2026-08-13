import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_cli_writes_redacted_chart(self):
        payload = {
            "year": 2000,
            "month": 1,
            "day": 1,
            "hour": 12,
            "minute": 0,
            "timezone_name": "UTC",
            "subject_id": "secret-subject",
            "expected_result": {"type": "Projector"},
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            input_path = Path(temporary_directory) / "input.json"
            output_path = Path(temporary_directory) / "output.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            run = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_true_human_design.py"),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            chart = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertNotIn("secret-subject", json.dumps(chart))
            self.assertIn("calculation_hash", chart["ledger"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
