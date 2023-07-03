import requests
from crypto_dot_com.secret import TELE_BOT_TOKEN, TELE_BOT_CHAT_ID

def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + TELE_BOT_TOKEN + '/sendMessage?chat_id=' + TELE_BOT_CHAT_ID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

