"""Remote Mythic narration contracts: privacy, prompt grounding, transport, and fallback."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread

from narrative_helpers import exact_result


class _CaptureHandler(BaseHTTPRequestHandler):
    captured = None

    def log_message(self, *_args):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        type(self).captured = json.loads(self.rfile.read(length))
        payload = {"choices": [{"finish_reason": "stop", "message": {"content": "## The Living Pattern\n\nA grounded mythic reading."}}]}
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def test_remote_packet_contains_derived_symbolic_facts_but_no_identity_or_raw_psychology():
    from mythic_remote import build_symbolic_packet

    result = exact_result()
    packet = build_symbolic_packet(result)
    encoded = json.dumps(packet, sort_keys=True)
    assert "Kirk Evan Brown" not in encoded
    assert "Knowurknot" not in encoded
    assert "1982" not in encoded
    assert "Evanston" not in encoded
    assert "ENTP" not in encoded
    assert "8w7" not in encoded
    assert "user_context" not in encoded
    assert packet["astrology"]["sun"] == "Aquarius"
    assert packet["astrology"]["moon"] == "Gemini"
    assert packet["astrology"]["ascendant"] == "Scorpio"
    assert packet["human_design"]["type"] == "Generator"
    assert packet["name_symbols"]["pythagorean_expression"] == 1


def test_prompt_demands_a_lush_story_without_inventing_chart_facts_or_claiming_proof():
    from mythic_remote import build_messages, build_symbolic_packet

    messages = build_messages(build_symbolic_packet(exact_result()))
    text = "\n".join(m["content"] for m in messages)
    assert "Do not invent" in text
    assert "symbolic" in text.casefold()
    assert "prediction" in text.casefold()
    assert "scientific" in text.casefold()
    assert "astrology" in text.casefold()
    assert "tarot" in text.casefold()
    assert "story" in text.casefold()
    assert "biographical fact" in text.casefold()


def test_openrouter_transport_uses_exact_qwen38_flash_model_and_server_built_prompt():
    from mythic_remote import MODEL, request_openrouter

    server = ThreadingHTTPServer(("127.0.0.1", 0), _CaptureHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        story = request_openrouter(
            [{"role": "system", "content": "system"}, {"role": "user", "content": "facts"}],
            api_key="test-key",
            endpoint=f"http://127.0.0.1:{server.server_port}/api/v1/chat/completions",
            timeout=5,
        )
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)
    assert story.startswith("## The Living Pattern")
    assert MODEL == "qwen/qwen3.8-flash"
    assert _CaptureHandler.captured["model"] == MODEL
    assert _CaptureHandler.captured["provider"]["sort"] == "throughput"
    assert _CaptureHandler.captured["reasoning"]["effort"] == "none"
    assert _CaptureHandler.captured["messages"][1]["content"] == "facts"


def test_remote_generation_requires_server_side_key(monkeypatch):
    from mythic_remote import RemoteMythicUnavailable, generate_remote_mythic

    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    try:
        generate_remote_mythic(exact_result())
    except RemoteMythicUnavailable as exc:
        assert "OPENROUTER_API_KEY" in str(exc)
    else:
        raise AssertionError("remote Mythic must not silently pretend to run without a key")


class _TruncatedHandler(_CaptureHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        payload = {"choices": [{"finish_reason": "length", "message": {"content": "# Cut off\n\nThis story never finishes"}}]}
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def test_openrouter_rejects_truncated_completion():
    from mythic_remote import RemoteMythicInvalid, request_openrouter
    server = ThreadingHTTPServer(("127.0.0.1", 0), _TruncatedHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        try:
            request_openrouter([{"role":"user","content":"facts"}], api_key="test-key", endpoint=f"http://127.0.0.1:{server.server_port}/api/v1/chat/completions", timeout=5)
        except RemoteMythicInvalid as exc:
            assert "truncated" in str(exc).casefold()
        else:
            raise AssertionError("length-limited Mythic output must be rejected")
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)


def test_story_fact_validator_rejects_invented_aspect_pairs_but_accepts_returned_ones():
    from mythic_remote import _story_fact_errors, build_symbolic_packet
    packet = build_symbolic_packet(exact_result())
    assert not _story_fact_errors("Venus squares Saturn at an orb of 2.0 degrees.", packet)
    errors = _story_fact_errors("Venus is conjunct Neptune, forming a fused value-dream axis.", packet)
    assert any("unsupported astrology aspect" in item for item in errors)


def test_style_validator_rejects_unqualified_identity_claims():
    from mythic_remote import _story_style_errors
    assert _story_style_errors("Your Sun is in Aquarius. Symbolically, this can suggest experimentation.") == []
    errors = _story_style_errors("The person is a paradox.")
    assert errors
    assert any("identity" in item.casefold() for item in errors)
