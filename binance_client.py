import httpx


from datetime import datetime, timezone


BINANCE_BASE_URL = "https://api.binance.com"



async def get_spot_price(symbol: str) -> dict:
    """
        Fetch the current spot price and 24h stats per trading pair.


        Args:
        symbol: Binance trading pair in BASEQUOTE format e.g "BTCUSDT".
        
        Returns:
            {
                "symbol": "BTCUSDT",
                "price": 82235.12,
                "changePercent24h": 2.34,
                "high24h": 86912.75,
                "low24h": 83400.00,
                "asOf": "2026-10-02T12:28:10Z",
            }

    """


    params = {
        "symbol": symbol
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BINANCE_BASE_URL}/api/v3/ticker/24hr",
            params=params,
            timeout=10.0
        )
        response.raise_for_status()


        raw = response.json()

        # print(raw)

        # binance_symbol = raw["symbol"]
        # binance_price = raw["lastPrice"]
        # binance_price_change = float(raw["priceChangePercent"])
    return {
    "symbol": raw["symbol"],
    "price": float(raw["lastPrice"]),
    "changePercent24h": float(raw["priceChangePercent"]),
    "high24h": float(raw["highPrice"]),
    "low24h": float(raw["lowPrice"]),
    "asOf": datetime.fromtimestamp(
        raw["closeTime"] / 1000, tz=timezone.utc
    ).strftime("%Y-%m-%dT%H:%M:%SZ"),
}