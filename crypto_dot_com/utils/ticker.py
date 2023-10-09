import aiohttp


async def get_yfinance_chart(
    ticker,
    range="1m",
    interval="1d",
    include_pre_post="false",
    events="div,splits,capitalGains",
) -> dict:
    BASE_URL = "https://query2.finance.yahoo.com/v8/finance/chart/"
    params = {
        "range": range,
        "interval": interval,
        "includePrePost": include_pre_post,
        "events": events,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL + ticker, params=params) as response:
            return await response.json()


async def get_yfinance_ticker_price(ticker) -> float:
    data = await get_yfinance_chart(ticker=ticker)
    return data["chart"]["result"][0]["meta"]["regularMarketPrice"]
