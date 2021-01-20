#Starting varibles

# Currency to trade
currency = 'BTC-USD'
money = 'USD'
fee = .0035
sizelimit = 0.002

# Granularity (in seconds). 300/5min, 900/15min, 3600/hour
period = 3600

# Email varibles
CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']
EmailSubject = "CBPro"

# Starting varibles
price = ""
currentBuy = ""
currentSell = ""
minusbuyprice = ""
plusssellprice = ""
pasttrade = 0
bidbuysell = ""
orderstatus = ""
iteration = 1
iterationbuy = 0
iterationsell = 0
iterationcancel = 0
Buyprice = 0
buysell = ""
buysell_log = []
ordercount = 0
Buyvolume = 0

# CSV Fill data varibles
buyl = "'side': '"
buyr = "', 'type'"
pricel = "price': '"
pricer = "', 'size':"
statusl = "status': '"
statusr = "', 'settled"
sidel = "'side': '"
sider = "', 'settled'"
tradel = "'trade_id': "
trader = ", 'product_id"
voll = "usd_volume': '"
volr = "'}, None"
sizel = "size': '"
sizer = "', 'fee':"
feel = "fee': '"
feer = "', 'side':"
