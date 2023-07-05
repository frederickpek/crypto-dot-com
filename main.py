# %% VsCode Interactive
import time
import numpy as np
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from crypto_dot_com.secret import API_KEY, SECRET_KEY
from crypto_dot_com.sdk.api import CdcApi
from crypto_dot_com.utils.telegram_bot import telegram_bot_sendtext

start = time.time()

# %% VsCode Interactive
api = CdcApi(api_key=API_KEY, secret_key=SECRET_KEY)


# %% VsCode Interactive
user_balance = api.get_user_balance()
tickers = api.get_tickers()

tickers_map = {ticker['i']: ticker for ticker in tickers}

total_cash_balance = float(user_balance['total_cash_balance'])
position_balances = user_balance['position_balances']

m = {'5m': 5, '1h': 60, '6h': 60 * 6, '24h': 60 * 24}

for position_balance in position_balances:
    ccy = position_balance['ccy']
    ticker = tickers_map.get(f'{ccy}_USDT') or tickers_map.get(f'{ccy}_USD')
    if ticker:
        instrument_name = ticker['i']
        bid, ask = float(ticker['b']), float(ticker['k'])
        price = (bid + ask) / 2
        candlesticks = api.get_candlestick(instrument_name, timeframe='5m', count=300)
        candlesticks.sort(reverse=True, key=lambda d: d['t'])
        base_interval = 5
        for key, interval in m.items():
            open_price = float(candlesticks[interval // base_interval - 1]['o'])
            percentage = (price - open_price) / price * 100
            position_balance[key] = f'{percentage:,.1f}'

df = pd.DataFrame(position_balances)
df['market_value'] = df['market_value'].map(lambda v: float(v))
df['notional'] = df['market_value'].map(lambda v: f'${v:,.2f}')
df = df.sort_values(by=['market_value'], ascending=False)
df = df[['ccy', 'notional', *m.keys()]]
df = df.replace(np.nan, '')

time_fmt = "%d %B %Y, %H:%M %p"
time_zone = ZoneInfo('Asia/Singapore')
dt = datetime.now(tz=time_zone).strftime(time_fmt)
table = df.to_string(index=False).replace('_', '-')
end = time.time()
msg = f'``` {dt}\n\n{table}\n\n${total_cash_balance:,.2f}\n\n[finished in {end-start:,.3f}s]```'
print(msg)

# %% VsCode Interactive
user_balance_history = api.get_user_balance_history(timeframe='H1')

df = pd.DataFrame(user_balance_history)
df['t'] = df['t'].map(lambda v: datetime.fromtimestamp(int(v) // 1000))
df['c'] = df['c'].map(lambda v: float(v))
df = df.sort_values(by=['t'], ascending=False)
df = df.head(n=24)

plot = df.plot.line(x='t', y='c')


# %%
