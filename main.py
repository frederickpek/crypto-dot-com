import pandas as pd

from crypto_dot_com.secret import API_KEY, SECRET_KEY
from crypto_dot_com.sdk.api import CdcApi


def main():
    api = CdcApi(api_key=API_KEY, secret_key=SECRET_KEY)
    data = api.get_user_balance()
    total_cash_balance = data['total_cash_balance']
    position_balances = data['position_balances']

    df = pd.DataFrame(position_balances)
    df = df[['instrument_name', 'market_value']]
    df['market_value'] = df['market_value'].map(lambda v: float(v))
    df = df.sort_values(by=['market_value'], ascending=False)

    print(df)
    print(f'{df["market_value"].sum():,.3f}')


if __name__ == '__main__':
    main()

