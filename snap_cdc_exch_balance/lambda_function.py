import json
import pandas as pd

from crypto_dot_com.sdk.api import CdcApi
from crypto_dot_com.secret import API_KEY, SECRET_KEY
from crypto_dot_com.utils.telegram_bot import telegram_bot_sendtext


def lambda_handler(event, context):
    api = CdcApi(api_key=API_KEY, secret_key=SECRET_KEY)
    data = api.get_user_balance()
    total_cash_balance = float(data['total_cash_balance'])
    position_balances = data['position_balances']
    
    df = pd.DataFrame(position_balances)
    df['market_value'] = df['market_value'].map(lambda v: float(v))
    df['notional'] = df['market_value'].map(lambda v: f'${v:,.2f}')
    df = df.sort_values(by=['market_value'], ascending=False)
    df = df[['instrument_name', 'notional']]
    
    table = str(df).replace('_', '-')
    msg = f'```{table}\n\n${total_cash_balance:,.2f}```'
    resp = telegram_bot_sendtext(msg)

    return {
        'statusCode': 200,
        'body': json.dumps(resp)
    }

