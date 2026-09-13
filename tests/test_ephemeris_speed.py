from encoders.astrology import compute_chart


def test_tropical_chart_requests_velocity_before_labeling_retrograde():
    chart = compute_chart(
        2000, 1, 7,
        hour=12, minute=0, timezone_offset=8,
        location="Beijing, China", lat=39.9042, lon=116.4074,
    )
    saturn = next(planet for planet in chart.planets if planet.planet == "Saturn")
    assert saturn.is_retrograde is True
