"""MCP server (stdio) exposing LockSmith as a single tool.

Run it with an MCP host (Claude Desktop, Cursor, any MCP client):

    lock-smith-mcp            # after pip install
    python -m lock_smith_mcp  # from a checkout

Configuration is entirely from the environment of whoever runs it:

    AGENT_PRIVATE_KEY   EVM private key (0x...) of YOUR wallet holding
                        USDC on Base — used to pay the $0.50/call x402
                        charge automatically. Never shared with the tool
                        author; the key stays on your machine.
    AGENT_KEY_FILE      Alternative: path to a file containing the key.
    LOCK_SMITH_URL   Override the service base URL
                        (default: production).
    LOCK_SMITH_MAX_AMOUNT_UNITS
                        Spend guard per call, in USDC micro-units
                        (default 500000 = $0.50, the known price).

With no signer configured the tool never pays: it returns the parsed
402 challenge as a structured error so the calling agent can see the
price, asset, network and payTo and decide what to do.
"""

from __future__ import annotations

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_AMOUNT_UNITS,
    PaymentRequiredError,
    LockSmithClient,
    LockSmithError,
    load_account_from_env,
)

mcp = FastMCP("lock-smith")


def build_client(env: dict | None = None) -> LockSmithClient:
    env = os.environ if env is None else env
    max_units_raw = (env.get("LOCK_SMITH_MAX_AMOUNT_UNITS") or "").strip()
    return LockSmithClient(
        base_url=(env.get("LOCK_SMITH_URL") or DEFAULT_BASE_URL),
        account=load_account_from_env(env),
        max_amount_units=int(max_units_raw) if max_units_raw else DEFAULT_MAX_AMOUNT_UNITS,
    )


def run_audit(
    endpoint_url: str, client: LockSmithClient | None = None
) -> dict[str, Any]:
    """The tool's logic, kept transport-free so tests can drive it with a
    mock HTTP client. Returns the audit JSON, or a structured error
    dict (payment_required / upstream_error)."""
    client = client or build_client()
    try:
        return client.get_audit(endpoint_url)
    except PaymentRequiredError as exc:
        return exc.structured_error()
    except LockSmithError as exc:
        return {
            "error": "upstream_error",
            "status": exc.status,
            "detail": exc.detail,
        }


@mcp.tool()
def lock_audit(endpoint_url: str) -> dict[str, Any]:
    """Run LockSmith's automated security audit on one x402 endpoint.

    Calls LockSmith (POST /v1/audit, $0.50 USDC on Base via x402). The
    audit is an 8-check non-destructive battery run with UNPAID probes
    only — paywall presence, challenge sanity, garbage/forged payment
    rejection, exposure surface (.env/.git/debug paths), error hygiene,
    body-cap sanity, discovery consistency — and returns a verdict
    (SECURE / FINDINGS / EXPOSED) with per-check status and detail.
    These are automated security checks, not a penetration test.

    Args:
        endpoint_url: Full URL of the x402 endpoint (paid route) to audit.
    """
    return run_audit(endpoint_url)


def main() -> None:
    mcp.run()  # stdio transport


if __name__ == "__main__":
    main()
