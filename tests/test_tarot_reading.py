"""Real draw invariants and deterministic replay, without mocked randomness."""
import pytest
from tarot_reading import BY_ID, DECK, SPREADS, draw_reading, realize_reading, spread_catalog


def test_deck_and_three_spread_contracts():
    assert len(DECK) == len(BY_ID) == 78
    assert len([c for c in DECK if c["arcana"] == "Major"]) == 22
    assert [s["card_count"] for s in spread_catalog()] == [1,3,5]
    assert set(SPREADS) == {"focus", "situation", "crossroads"}


@pytest.mark.parametrize("spread,count", [("focus",1),("situation",3),("crossroads",5)])
def test_real_draw_has_no_replacement_and_replays_exactly(spread,count):
    reading = draw_reading({"spread":spread})
    ids = [c["id"] for c in reading["cards"]]
    assert len(ids) == len(set(ids)) == count
    assert reading == realize_reading(spread, ids)
    assert reading["ai_used"] is False
    assert all(len(" ".join(c["paragraphs"]).split()) > 70 for c in reading["cards"])


def test_positions_materially_change_the_same_card_reading():
    a = realize_reading("situation", ["major-09","cups-02","wands-01"])
    b = realize_reading("situation", ["cups-02","major-09","wands-01"])
    assert a["cards"][0]["paragraphs"] != b["cards"][1]["paragraphs"]
    assert a["reading_id"] != b["reading_id"]
    assert "causal chain" in a["synthesis"]


@pytest.mark.parametrize("payload", [None,[],{}, {"spread":"future"}, {"spread":[]}, {"spread":"focus","question":"private"}])
def test_draw_rejects_invalid_types_and_personal_data(payload):
    with pytest.raises(ValueError):
        draw_reading(payload)


@pytest.mark.parametrize("ids", [["major-00"]*3, ["invalid"], [None], []])
def test_replay_rejects_invalid_records(ids):
    with pytest.raises(ValueError):
        realize_reading("situation", ids)


def test_every_card_has_a_complete_authored_reading():
    for card in DECK:
        r = realize_reading("focus", [card["id"]])
        assert r["cards"][0]["name"] == card["name"]
        assert len(r["cards"][0]["paragraphs"]) >= 3
        assert "prediction" in r["disclaimer"]
