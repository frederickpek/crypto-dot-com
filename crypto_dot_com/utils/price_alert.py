import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from crypto_dot_com.utils.telegram_bot import telegram_bot_sendtext
from crypto_dot_com.secret import PRICE_CHANGE_ALERT_BOT_TOKEN

TRIGGERS = {
    ("5m", 0.7, 1),
    ("15m", 1.0, 3),
    ("1h", 3.0, 12),
}


def alert_price_changes(ccy_candlesticks: dict):
    alerts = list()
    for ccy, candlesticks in ccy_candlesticks.items():
        candlesticks.sort(reverse=True, key=lambda d: d["t"])
        for interval, percentage_trigger, period in TRIGGERS:
            end = candlesticks[1]
            start = candlesticks[period]
            open_price = float(start["o"])
            close_price = float(end["c"])
            price_change = close_price - open_price
            percentage_price_change = price_change / open_price * 100
            if abs(percentage_price_change) < percentage_trigger:
                continue
            alerts.append(
                {
                    "ccy": ccy,
                    "interval": interval,
                    "price_change": f"{percentage_price_change:,.2f}%",
                }
            )
    if not alerts:
        return

    alert_df = pd.DataFrame(alerts)
    alert_df = alert_df.sort_values(by="ccy")
    alert_table = alert_df.to_string(index=False)

    time_fmt = " %d %B %Y, %H:%M %p"
    time_zone = ZoneInfo("Asia/Singapore")
    dt = datetime.now(tz=time_zone).strftime(time_fmt)

    msg = "\n\n".join([dt, alert_table])
    msg = "```" + msg + "```"

    telegram_bot_sendtext(msg, bot_token=PRICE_CHANGE_ALERT_BOT_TOKEN)
