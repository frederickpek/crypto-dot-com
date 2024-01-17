import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from crypto_dot_com.utils.telegram_bot import telegram_bot_sendtext
from crypto_dot_com.secret import PRICE_CHANGE_ALERT_BOT_TOKEN

TRIGGERS = [
    (" 5m ", 0.75, 1),
    (" 15m ", 1.15, 3),
    (" 1h ", 3.2, 12),
]


def alert_price_changes(ccy_candlesticks: dict):
    alerts = list()
    for ccy, candlesticks in ccy_candlesticks.items():
        candlesticks.sort(reverse=True, key=lambda d: d["t"])
        end = candlesticks[1]
        close_price = float(end["c"])
        ccy_info = {
            "ccy": ccy,
            "price": f"${close_price:,.2f}",
        }
        triggered = False
        for interval, percentage_trigger, period in TRIGGERS:
            start = candlesticks[period]
            open_price = float(start["o"])
            price_change = close_price - open_price
            percentage_price_change = price_change / open_price * 100
            ccy_info[interval] = f" {percentage_price_change:,.2f} "
            if abs(percentage_price_change) > percentage_trigger:
                ccy_info[interval] = f"({ccy_info[interval].strip()})"
                triggered = True
        if triggered:
            alerts.append(ccy_info)

    if not alerts:
        return

    alert_df = pd.DataFrame(alerts)
    alert_df = alert_df.sort_values(by=["price"])
    alert_table = alert_df.to_string(index=False)

    time_fmt = " %d %B %Y, %H:%M %p"
    time_zone = ZoneInfo("Asia/Singapore")
    dt = datetime.now(tz=time_zone).strftime(time_fmt)

    msg = "\n\n".join([dt, alert_table])
    msg = "```" + msg + "```"

    telegram_bot_sendtext(msg, bot_token=PRICE_CHANGE_ALERT_BOT_TOKEN)
