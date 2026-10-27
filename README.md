<!-- mcp-name: io.github.QuincyGB/lock-smith-mcp -->

# lock-smith-mcp

> **Standalone home:** [QuincyGB/lock-smith-mcp](https://github.com/QuincyGB/lock-smith-mcp)
> — sibling of the fleet's token-verdict-mcp, route-verdict-mcp and
> list-smith-mcp wrappers.

MCP server for **[LockSmith](https://lock-smith-production.up.railway.app)**
— an automated security audit for x402 endpoints, sold pay-per-call over
[x402](https://www.x402.org): **$0.50 USDC on Base**, no account, no API
key. Give it the URL of a paid x402 route and it reports whether that
endpoint would pass an informed buyer's security screen — paywall
presence, challenge sanity, garbage/forged payment rejection, exposure
surface (.env/.git/debug paths), error hygiene, body caps, discovery
consistency — as a SECURE / FINDINGS / EXPOSED verdict with per-check
evidence.

**Scope, stated plainly:** these are automated security checks run with
unpaid probes only — not a penetration test, and a SECURE verdict is not
a guarantee. It is a fast, cheap, repeatable screen.

This package gives any MCP host (Claude Desktop, Cursor, …) a native
`lock_audit` tool that handles the full x402 v2 payment flow itself —
402 challenge → EIP-3009 `TransferWithAuthorization` signature (USDC on
Base, EIP-712) → paid retry — using **your** agent wallet.

## Tools

| Tool | What it does | Price |
| --- | --- | --- |
| `lock_audit` | POST `/v1/audit` — 8-check non-destructive security audit of one x402 endpoint URL; returns the verdict, summary counts and per-check detail | $0.50 USDC (Base) |

## Install

```bash
pip install lock-smith-mcp
# or run without installing:
uvx lock-smith-mcp
```

## Configuration

All configuration is environment variables — set them on the MCP server
process in your host's config. Your key never leaves your machine; the
service only ever sees a signed payment authorization.

| Variable | Required | Meaning |
| --- | --- | --- |
| `AGENT_PRIVATE_KEY` | for paid calls | EVM private key (`0x…`) of **your** wallet holding USDC on Base. Used locally to sign the x402 payment. |
| `AGENT_KEY_FILE` | alternative | Path to a file containing that key instead. |
| `LOCK_SMITH_URL` | no | Service base URL override (default: production). |
| `LOCK_SMITH_MAX_AMOUNT_UNITS` | no | Spend guard per call, USDC micro-units (default `500000` = $0.50, the known price). The client refuses to sign any challenge priced above this. |

**Without a signer the tool never pays.** It returns the parsed 402
challenge as a structured error — `{"error": "payment_required",
"accepts": […], …}` — so the calling agent can see the exact price,
asset, network and `payTo` and decide what to do. With a signer, charges
above the spend guard are likewise refused before signing.

## MCP host config

```json
{
  "mcpServers": {
    "lock-smith": {
      "command": "uvx",
      "args": ["lock-smith-mcp"],
      "env": {
        "AGENT_PRIVATE_KEY": "0xYOUR_AGENT_WALLET_KEY"
      }
    }
  }
}
```

## The endpoint being wrapped

```
POST https://lock-smith-production.up.railway.app/v1/audit
{"endpoint_url": "https://token-verdict-production.up.railway.app/v1/verdict"}
→ 200 {"ok": true, "service": "lock-smith", "audit_version": "1.0.0",
      "target": {...}, "verdict": "SECURE",
      "summary": {"passed": 8, "findings": 0, ...},
      "checks": [{"id": "paywall_present", "status": "pass", ...}, ...],
      "scope_note": "Automated security checks, not a penetration test. ..."}
```

The schemas in `src/lock_smith_mcp/schemas.py` are copied verbatim from
the service's own discovery document (`/.well-known/x402`) — the
published contract, not a paraphrase.

## Development

```bash
pip install -e ".[dev]"
pytest
```

Tests mock the HTTP layer and use a throwaway signer generated at test
time — no network, no real money, no key material in the repo. The 402
fixture in `tests/fixtures/` is real: captured from an unpaid probe of
production on 2026-10-27.

## License

MIT
