# crypto-mcp

An MCP server that gives LLM clients (Claude Desktop, Cursor) real-time crypto
market data from Binance — with normalization, caching, and structured error
handling on top of the raw upstream.

## Why this exists



Most MCP servers are thin wrappers: forward a request, hand the raw JSON to the
model, hope it figures out the shape. This one treats the model as a consumer
of a stable contract — numbers are numbers, timestamps are UTC, errors are
structured. The domain (crypto prices) is the setting; the engineering is the
point.

The goal isn't "check BTC." It's to demonstrate the decisions that separate a
demo MCP server from one you'd actually leave running in a live conversation:
normalization, freshness guarantees, caching, and graceful degradation when the
upstream is down.

## Tools

| Tool | Description |
|---|---|
| `get_crypto_price` | Current spot price and 24h stats for a Binance trading pair (e.g. `BTCUSDT`). Returns `{symbol, price, changePercent24h, high24h, low24h, asOf}`. |

## Design decisions



- **Normalization lives in the client, not the tools.** Binance sends every
  numeric field as a string and every timestamp as a millisecond epoch. The
  client (`binance_client.py`) owns all conversion; tools receive clean, typed
  dicts. If Binance changes a field name, one file changes.

- **`asOf` comes from the upstream, not `datetime.now()`.** Every response
  carries the timestamp Binance itself reports for the data. "How fresh is
  this price?" has an honest answer, and a stale upstream cache can't be masked
  by a fresh client-side clock.

- **Strict symbol format.** The schema requires `BASEQUOTE` (e.g. `BTCUSDT`),
  and the tool description says so explicitly. No retry-on-invalid-symbol —
  retries hide bugs and double the request count in exactly the scenarios
  where latency hurts most.

- **Only the fields the model needs.** Binance's 24h ticker returns ~20
  fields. We surface six. The rest is either redundant (the model can compute
  it) or noise. Every extra field increases the chance the model references
  the wrong one.

- **Read-only by design.** No order placement, no account access, no write
  paths. The tool is safe to point an LLM at because it can't do anything
  except read public market data.

## Install

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <your-repo-url>
cd crypto-mcp
uv sync