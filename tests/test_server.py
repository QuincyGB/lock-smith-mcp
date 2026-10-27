"""Server-level tests: the tool is registered with the real endpoint's
input schema, and tool calls route through the (mocked) client logic."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from lock_smith_mcp.schemas import AUDIT_INPUT_SCHEMA, AUDIT_OUTPUT_SCHEMA
from lock_smith_mcp.server import mcp, run_audit

FIXTURES = Path(__file__).parent / "fixtures"
AUDIT = json.loads((FIXTURES / "audit_example.json").read_text())


def test_tool_registered_with_real_input_schema():
    tools = asyncio.run(mcp.list_tools())
    by_name = {t.name: t for t in tools}
    assert "lock_audit" in by_name
    schema = by_name["lock_audit"].inputSchema
    # FastMCP generates the tool schema from the Python signature, so it
    # can't be byte-identical to the service's wire schema — assert the
    # substantive contract matches instead: same fields, same types,
    # endpoint_url required.
    props = schema["properties"]
    assert set(props) == set(AUDIT_INPUT_SCHEMA["properties"])
    assert props["endpoint_url"]["type"] == "string"
    assert schema["required"] == AUDIT_INPUT_SCHEMA["required"]


def test_output_schema_matches_service_contract():
    # The wrapper advertises exactly the service's response shape.
    assert AUDIT_OUTPUT_SCHEMA["required"] == [
        "ok",
        "service",
        "audit_version",
        "target",
        "verdict",
        "summary",
        "terms_observed",
        "checks",
        "probes_used",
        "scope_note",
    ]
    # And the example output satisfies the required keys.
    for key in AUDIT_OUTPUT_SCHEMA["required"]:
        assert key in AUDIT
    assert AUDIT["verdict"] in ("SECURE", "FINDINGS", "EXPOSED")
    # The service's own honesty line travels with every audit.
    assert "not a penetration test" in AUDIT["scope_note"]


def test_tool_call_via_run_audit_happy_path():
    class FakeClient:
        def get_audit(self, endpoint_url):
            assert endpoint_url.startswith("https://")
            return AUDIT

    result = run_audit(
        "https://token-verdict-production.up.railway.app/v1/verdict",
        client=FakeClient(),
    )
    assert result["verdict"] in ("SECURE", "FINDINGS", "EXPOSED")
    assert result["summary"]["passed"] == 8
