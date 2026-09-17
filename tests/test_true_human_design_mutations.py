import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import unittest

from true_human_design.astronomy import civil_to_julian_day, planetary_positions, solve_design_jd
from true_human_design.mandala import GATE_SPAN, map_longitude
from true_human_design.topology import build_topology, resolve_type


class LegacyMutationGuards(unittest.TestCase):
    def setUp(self):
        self.time = civil_to_julian_day(1982, 2, 4, 1, 42, "America/Denver")

    def test_fixed_eighty_eight_day_shortcut_is_detected(self):
        exact = solve_design_jd(self.time.julian_day)
        personality_sun = planetary_positions(self.time.julian_day)["Sun"].longitude
        fixed_sun = planetary_positions(self.time.julian_day - 88.0)["Sun"].longitude
        fixed_arc = (personality_sun - fixed_sun) % 360
        self.assertLess(abs(exact.residual_degrees), 1e-6)
        self.assertGreater(abs(fixed_arc - 88.0), 0.1)

    def test_sequential_gate_numbering_is_detected(self):
        longitude = 358.25
        correct = map_longitude(longitude).gate
        sequential = int(((longitude - 358.25) % 360) / GATE_SPAN) + 1
        self.assertEqual(correct, 25)
        self.assertNotEqual(correct, sequential)

    def test_gate_count_type_mutation_is_detected(self):
        gates = {1, 2, 3, 4, 5, 6, 7, 9, 11}
        correct = resolve_type(build_topology(gates)).value
        gate_count_mutation = "Generator" if len(gates) > 8 else "Projector"
        self.assertEqual(correct, "Reflector")
        self.assertNotEqual(correct, gate_count_mutation)

    def test_hardcoded_centers_mutation_is_detected(self):
        correct = build_topology(set()).defined_centers
        hardcoded = {"Head", "Ajna", "Throat", "G", "Solar Plexus", "Spleen", "Root"}
        self.assertEqual(correct, frozenset())
        self.assertNotEqual(set(correct), hardcoded)

    def test_one_sided_channel_mutation_is_detected(self):
        correct = build_topology({21})
        one_sided_mutation = {"Heart", "Throat"} if 21 in correct.active_gates else set()
        self.assertEqual(correct.defined_centers, frozenset())
        self.assertNotEqual(set(correct.defined_centers), one_sided_mutation)

    def test_modulo_profile_mutation_is_detected(self):
        from true_human_design.engine import BirthRecord, calculate_chart
        chart = calculate_chart(BirthRecord(1982, 2, 4, 1, 42, "America/Denver"))
        profile = chart["resolutions"]["profile"]["value"]
        personality_gate = chart["activations"]["personality"]["Sun"]["gate"]
        design_gate = chart["activations"]["design"]["Sun"]["gate"]
        modulo = f"{(personality_gate % 6) + 1}/{(design_gate % 6) + 1}"
        self.assertNotEqual(profile, modulo)


if __name__ == "__main__":
    unittest.main(verbosity=2)
