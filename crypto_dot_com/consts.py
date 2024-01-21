MAX_LEVEL = 3


GET = "GET"
POST = "POST"


BASE_URL = "https://api.crypto.com/exchange/v1/"


# GET
# 100 requests per second each
GET_TICKERS = "public/get-tickers"
GET_INSTRUMENTS = "public/get-instruments"
GET_CANDLESTICK = "public/get-candlestick"


# POST
# 3 requests per 100ms each
USER_BALANCE = "private/user-balance"
USER_BALANCE_HISTORY = "private/user-balance-history"
POSITIONS = "private/get-positions"
OPEN_ORDERS = "private/get-open-orders"

# 15 requests per 100ms
CREATE_ORDER = "private/create-order"

# 30 requests per 100ms
GET_ORDER_DETAIL = "private/get-order-detail"
