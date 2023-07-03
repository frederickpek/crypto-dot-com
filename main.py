# %% VsCode Interactive
import pandas as pd
from datetime import datetime

from crypto_dot_com.secret import API_KEY, SECRET_KEY
from crypto_dot_com.sdk.api import CdcApi


# %% VsCode Interactive
api = CdcApi(api_key=API_KEY, secret_key=SECRET_KEY)


# %% VsCode Interactive
data = api.get_user_balance()
total_cash_balance = float(data['total_cash_balance'])
position_balances = data['position_balances']

df = pd.DataFrame(position_balances)
df['market_value'] = df['market_value'].map(lambda v: float(v))
df['notional'] = df['market_value'].map(lambda v: f'${v:,.2f}')
df = df.sort_values(by=['market_value'], ascending=False)
df = df[['instrument_name', 'notional']]

print(df)
print(f'${total_cash_balance:,.2f}')


# %% VsCode Interactive
user_balance_history = api.get_user_balance_history(timeframe='H1')

df = pd.DataFrame(user_balance_history)
df['t'] = df['t'].map(lambda v: datetime.fromtimestamp(int(v) // 1000))
df['c'] = df['c'].map(lambda v: float(v))
df = df.sort_values(by=['t'], ascending=False)
df = df.head(n=24)

plot = df.plot.line(x='t', y='c')


# %%

from snap_cdc_exch_balance.lambda_function import lambda_handler


lambda_handler(None, None)
# %%
