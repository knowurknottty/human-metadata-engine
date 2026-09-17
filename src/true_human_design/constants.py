MANDALA_VERSION = "rave-mandala-v1"
HD_START_DEGREE = 358.25
GATE_SPAN = 360.0 / 64.0
LINE_SPAN = GATE_SPAN / 6.0

MANDALA_SEQUENCE = (
    25, 17, 21, 51, 42, 3,
    27, 24, 2, 23, 8, 20,
    16, 35, 45, 12, 15, 52,
    39, 53, 62, 56, 31, 33,
    7, 4, 29, 59, 40, 64,
    47, 6, 46, 18, 48, 57,
    32, 50, 28, 44, 1, 43,
    14, 34, 9, 5, 26, 11,
    10, 58, 38, 54, 61, 60,
    41, 19, 13, 49, 30, 55,
    37, 63, 22, 36,
)

GATE_TO_CENTER = {
    61: "Head", 63: "Head", 64: "Head",
    4: "Ajna", 11: "Ajna", 17: "Ajna", 24: "Ajna", 43: "Ajna", 47: "Ajna",
    8: "Throat", 12: "Throat", 16: "Throat", 20: "Throat", 23: "Throat", 31: "Throat", 33: "Throat", 35: "Throat", 45: "Throat", 56: "Throat", 62: "Throat",
    1: "G", 2: "G", 7: "G", 10: "G", 13: "G", 15: "G", 25: "G", 46: "G",
    21: "Heart", 26: "Heart", 40: "Heart", 51: "Heart",
    3: "Sacral", 5: "Sacral", 9: "Sacral", 14: "Sacral", 27: "Sacral", 29: "Sacral", 34: "Sacral", 42: "Sacral", 59: "Sacral",
    18: "Spleen", 28: "Spleen", 32: "Spleen", 44: "Spleen", 48: "Spleen", 50: "Spleen", 57: "Spleen",
    6: "Solar Plexus", 22: "Solar Plexus", 30: "Solar Plexus", 36: "Solar Plexus", 37: "Solar Plexus", 49: "Solar Plexus", 55: "Solar Plexus",
    19: "Root", 38: "Root", 39: "Root", 41: "Root", 52: "Root", 53: "Root", 54: "Root", 58: "Root", 60: "Root",
}

CHANNELS = {
    (1, 8): ("G", "Throat"),
    (2, 14): ("G", "Sacral"),
    (3, 60): ("Sacral", "Root"),
    (4, 63): ("Ajna", "Head"),
    (5, 15): ("Sacral", "G"),
    (6, 59): ("Solar Plexus", "Sacral"),
    (7, 31): ("G", "Throat"),
    (9, 52): ("Sacral", "Root"),
    (10, 20): ("G", "Throat"),
    (10, 34): ("G", "Sacral"),
    (10, 57): ("G", "Spleen"),
    (11, 56): ("Ajna", "Throat"),
    (12, 22): ("Throat", "Solar Plexus"),
    (13, 33): ("G", "Throat"),
    (16, 48): ("Throat", "Spleen"),
    (17, 62): ("Ajna", "Throat"),
    (18, 58): ("Spleen", "Root"),
    (19, 49): ("Root", "Solar Plexus"),
    (20, 34): ("Throat", "Sacral"),
    (20, 57): ("Throat", "Spleen"),
    (21, 45): ("Heart", "Throat"),
    (23, 43): ("Throat", "Ajna"),
    (24, 61): ("Ajna", "Head"),
    (25, 51): ("G", "Heart"),
    (26, 44): ("Heart", "Spleen"),
    (27, 50): ("Sacral", "Spleen"),
    (28, 38): ("Spleen", "Root"),
    (29, 46): ("Sacral", "G"),
    (30, 41): ("Solar Plexus", "Root"),
    (32, 54): ("Spleen", "Root"),
    (34, 57): ("Sacral", "Spleen"),
    (35, 36): ("Throat", "Solar Plexus"),
    (37, 40): ("Solar Plexus", "Heart"),
    (39, 55): ("Root", "Solar Plexus"),
    (42, 53): ("Sacral", "Root"),
    (47, 64): ("Ajna", "Head"),
}

ALL_CENTERS = frozenset({"Head", "Ajna", "Throat", "G", "Heart", "Sacral", "Spleen", "Solar Plexus", "Root"})
MOTOR_CENTERS = frozenset({"Heart", "Sacral", "Solar Plexus", "Root"})
