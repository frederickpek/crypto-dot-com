import requests
from crypto_dot_com.secret import TELE_BOT_TOKEN, TELE_BOT_CHAT_ID


def telegram_bot_sendtext(
    bot_message, bot_token=TELE_BOT_TOKEN, chat_id=TELE_BOT_CHAT_ID
):
    send_text = (
        "https://api.telegram.org/bot"
        + bot_token
        + "/sendMessage?chat_id="
        + chat_id
        + "&parse_mode=Markdown&text="
        + bot_message
    )
    response = requests.get(send_text)
    return response.json()
