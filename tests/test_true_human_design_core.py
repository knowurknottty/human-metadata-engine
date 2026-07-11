import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import unittest

from true_human_design.mandala import GATE_SPAN, MANDALA_SEQUENCE, map_longitude
from true_human_design.topology import build_topology, resolve_authority, resolve_type


class MandalaTests(unittest.TestCase):
    def test_mandala_has_64_unique_gates_and_covers_360_degrees(self):
        self.assertEqual(len(MANDALA_SEQUENCE), 64)
        self.assertEqual(set(MANDALA_SEQUENCE), set(range(1, 65)))
        self.assertAlmostEqual(GATE_SPAN * 64, 360.0, places=12)

    def test_boundary_mapping_is_deterministic(self):
        first = map_longitude(358.25)
        before = map_longitude(358.25 - 1e-9)
        self.assertEqual(first.gate, 25)
        self.assertEqual(first.line, 1)
        self.assertNotEqual(before.gate, first.gate)

    def test_line_boundaries_are_deterministic(self):
        start = map_longitude(358.25)
        second_line = map_longitude(358.25 + GATE_SPAN / 6)
        self.assertEqual(start.line, 1)
        self.assertEqual(second_line.line, 2)


class TopologyTests(unittest.TestCase):
    def test_one_gate_does_not_define_a_center(self):
        topology = build_topology({21})
        self.assertEqual(topology.defined_centers, frozenset())
        self.assertEqual(topology.channels, ())

    def test_complete_channel_defines_both_centers(self):
        topology = build_topology({21, 45})
        self.assertIn(("Heart", "Throat"), topology.edges)
        self.assertEqual(topology.defined_centers, frozenset({"Heart", "Throat"}))

    def test_type_uses_topology_not_gate_count(self):
        many_disconnected = build_topology({1, 2, 3, 4, 5, 6, 7, 9, 11})
        self.assertEqual(resolve_type(many_disconnected).value, "Reflector")

    def test_manifestor_requires_undefined_sacral_and_motor_to_throat(self):
        topology = build_topology({21, 45})
        resolution = resolve_type(topology)
        self.assertEqual(resolution.value, "Manifestor")
        self.assertIn("motor_to_throat", resolution.reasons)

    def test_manifesting_generator_requires_defined_sacral_and_motor_path(self):
        topology = build_topology({20, 34})
        self.assertEqual(resolve_type(topology).value, "Manifesting Generator")

    def test_authority_exposes_reasons(self):
        topology = build_topology({12, 22})
        resolution = resolve_authority(topology)
        self.assertEqual(resolution.value, "Emotional")
        self.assertIn("Solar Plexus defined", resolution.reasons)


class AstronomyTests(unittest.TestCase):
    def test_historical_timezone_conversion_uses_zoneinfo(self):
        from true_human_design.astronomy import civil_to_julian_day
        ledger = civil_to_julian_day(1982, 2, 4, 1, 42, "America/Denver")
        self.assertEqual(ledger.utc_iso, "1982-02-04T08:42:00+00:00")
        self.assertEqual(ledger.utc_offset_hours, -7.0)

    def test_earth_is_exact_opposition_to_sun(self):
        from true_human_design.astronomy import planetary_positions
        positions = planetary_positions(2445004.8625)
        delta = (positions["Earth"].longitude - positions["Sun"].longitude) % 360
        self.assertAlmostEqual(delta, 180.0, places=10)

    def test_design_solver_hits_eighty_eight_degree_arc(self):
        from true_human_design.astronomy import civil_to_julian_day, solve_design_jd
        ledger = civil_to_julian_day(1982, 2, 4, 1, 42, "America/Denver")
        solved = solve_design_jd(ledger.julian_day)
        self.assertLess(abs(solved.residual_degrees), 1e-6)
        self.assertGreater(solved.days_before_birth, 80)
        self.assertLess(solved.days_before_birth, 100)

    def test_design_solver_is_not_fixed_eighty_eight_days(self):
        from true_human_design.astronomy import civil_to_julian_day, solve_design_jd
        ledger = civil_to_julian_day(1982, 2, 4, 1, 42, "America/Denver")
        solved = solve_design_jd(ledger.julian_day)
        self.assertGreater(abs(solved.days_before_birth - 88.0), 0.01)

    def test_missing_ephemeris_fails_closed(self):
        from unittest.mock import patch
        import true_human_design.astronomy as astronomy
        with patch.object(astronomy, "swe", None):
            with self.assertRaisesRegex(RuntimeError, "Swiss Ephemeris"):
                astronomy.planetary_positions(2445004.8625)


if __name__ == "__main__":
    unittest.main(verbosity=2)
