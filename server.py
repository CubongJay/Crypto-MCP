# from typing import list
import asyncio
import json
from mcp.server import Server

from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import binance_client


app = Server("crypto-mcp")



@app.list_tools()
async def list_tools() -> list[Tool] :
    return [
        Tool(
            name="greet",
            description=(
                "Greets a person by name. Use when thr user wants a personalized hello"
                "Returns JSON {greeting: string, message: string}; greeting is a short salutation; message is a warmer follow up; Relay both verbail to the user or use greeting alone if brevity is needed."),
            inputSchema={
                # name: str
                "type": "object",
                "properties":{
                    "name": {"type":"string", "description": "The person's name"}

                },
                "required": ["name"]

                },
        ),
        Tool(
            name="get_crypto_price",
            description=(
                "Fetch current spot price of any given symbol"
                "Use when user asks about the price of a crypto asset"
                "Returns JSON {symbol, price, changePercent24h, high24h, low24h, asOf} — "
                "the four numeric fields are floats; asOf is an ISO 8601 UTC timestamp. "
                "The symbol must be a Binance trading pair in BASEQUOTE format, "
                "e.g. 'BTCUSDT', 'ETHUSDT', always uppercase with no separator."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Binance trading pair, e.g. 'BTCUSDT'.",
                    },
                },
                "required": ["symbol"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "greet":
        person = arguments.get("name")
        if not person:
            payload = {"error": "Missing required argument: name"}
        else:
            payload = {"greeting": f"Hello, {person}!",
                       "message":  f"Delighted to make your acquaintance, {person}."}

        return [TextContent(type="text", text=json.dumps(payload, indent=2))]

    if name == "get_crypto_price":
        symbol = arguments.get("symbol")
        if not symbol:
            payload = {"error": "Missing required argument: symbol"}
        else:
            payload = await binance_client.get_spot_price(symbol)
        return [TextContent(type="text", text=json.dumps(payload, indent=2))]

    
    payload = {"error":f"Unknown tool: {name}"}
    return [TextContent(type="text", text=json.dumps(payload, indent=2))]


async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())