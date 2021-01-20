import os, cbpro, time, ctypes, base64
import numpy as np
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Google import Create_Service
from keys import SandboxKey, SandboxSecret, SandboxPassphrase, Sandboxapi_url
from Requirements import *

#currency = input("Enter the current to trade (BTC-USD, ETC-USD, etc): ")

# Set window Title
ctypes.windll.kernel32.SetConsoleTitleW("Auto-Trader - " + currency)

# Set True to disable buy/selling and stop loss in order to verify scripting.
test = False

# Define clear screen and color codes
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

colors = {'GREEN':'\033[92m', 'RED':'\033[91m', 'YELLOW':'\033[93m', 'CYAN':'\033[96m', 'reset':'\033[00m'}

cls()
print("Gathering data for " + currency + " . . .")
 
# Buy/Sell Logging
buysellLog="D:\AutoLog - " + currency + ".csv"
if not os.path.isfile(buysellLog):
  pass
  f = open(buysellLog,"w")
  f.close() 

#############################################################################################################################
                    ### API STUFF ###

# CB Pro granted api credentials as strings
auth_client = cbpro.AuthenticatedClient(SandboxKey,SandboxSecret,SandboxPassphrase,Sandboxapi_url)

#############################################################################################################################
                    ### Email Details ###

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
mimeMessage = MIMEMultipart()
mimeMessage['to'] = '[destination]@gmail.com'

#############################################################################################################################
                    ### Investment Details ###

# Set buy size limit
sizelimit = 0.004

# Will return the ID of your specific currency account
def getSpecificAccount(cur):
    x = auth_client.get_accounts()
    for account in x:
        if account['currency'] == cur:
            return account['id']
    for account in x:
        if account['money'] == cur:
            return account['id']

# Get the currency's specific ID
specificID = getSpecificAccount(currency[:3])
specificUSD = getSpecificAccount(money[:3])

# Set stop loss limit
wallet = (format(float(auth_client.get_account(specificUSD)['balance']), '.5f'))
funding = float(wallet) * 0.8 
stoplosslimit = (float(wallet) / 2) * 0.8

# Verify if there are any owned crypto curreny in the account and set buy varible
# Get last buy price from log if Selling, set Profit Total, set starting portfolio for profit/loss comparision
owned = float(auth_client.get_account(specificID)['available'])
newData = auth_client.get_product_ticker(product_id=currency)
currentPrice=newData['price']
possibleIncome = float(currentPrice) * owned
possibleprofit = (float(possibleIncome) * (1 + fee)) - float(Buyvolume)
portfolioS = float(possibleIncome) + float(wallet)

if not owned == 0.0:
    funding = float(funding) - float(possibleIncome)
    with open(buysellLog,'r') as file:
        opened_file = file.readlines()
        csvfile = opened_file[-1].split(',')[7]
        csvprice = csvfile.translate({ord(i): None for i in "'price': "})
        Buyprice = format(float(csvprice), '.5f')
        pasttrade = opened_file[-1].split(',')[1]
        pasttrade = pasttrade.translate({ord(i): None for i in "'trade_id': "}) 
        pastvolume = opened_file[-1].split(',')[12]
        pastvolume = pastvolume[pastvolume.index("'usd_volume': '")+len("'usd_volume': '"):pastvolume.index("'}")]
        Buyvolume = format(float(pastvolume), '.5f')
 
# Verify if orders are pending and set varibles
getorders=list(auth_client.get_orders(id=specificID))
if getorders == []:
    orders = False
    orderstatus = ""
else:
    orders = True
    csvorders = [ getorders[0], None ]
    csvorders = str(csvorders)
    csvorderbuy = csvorders[csvorders.index(buyl)+len(buyl):csvorders.index(buyr)]
    csvorderprice = csvorders[csvorders.index(pricel)+len(pricel):csvorders.index(pricer)]
    csvordersize = csvorders[csvorders.index("'size': '")+len("'size': '"):csvorders.index("', 'product_id': '")]
    csvorderopen = csvorders[csvorders.index(statusl)+len(statusl):csvorders.index(statusr)]
    orderstatus = " A " + csvorderbuy + " order for " + str(csvordersize) + " " + currency + " is pending as - " + csvorderopen + "."

def Details():
    print('\n')
    # Printing here to make the details easier to read in the terminal
    print("========================================",time_string,"=========================================")

    # Color code if Buying or Selling
    if owned == 0.0:
      print("  Iteration =", iteration, "     Buys =", iterationbuy, "     Sells =", iterationsell \
            , "     Cancels =", iterationcancel, "             Buy/Sell =", colors['RED'], "Buying", colors['reset'])
    else:
      print("  Iteration =", iteration, "     Buys =", iterationbuy, "     Sells =", iterationsell \
            , "     Cancels =", iterationcancel, "             Buy/Sell =", colors['GREEN'], "Selling", colors['reset'])
    
    print("=====================================================================================================")
    # Display possible profit price if owning an crypto currency
    if owned == 0.0:
      print(" ", currency, "Price =",colors['YELLOW'], currentPrice, colors['reset'])
    else:
      print(" ", currency, "Price =",colors['YELLOW'], currentPrice, colors['reset'], "   " + currency + " Owned =", owned, \
          "       Bought at =", Buyprice, "        Profit =", (format(possibleprofit, '.5f')))

    print("=====================================================================================================")       
    print("  Stop Loss : Current =", (format(stoploss, '.5f')), "    Limit =", (format(stoplosslimit, '.5f')), \
        "                   Profit/Loss =", (format(portfolioD, '.5f')))
    # Display wallet and profit price if owning an crypto currency
    if owned == 0.0:    
      print("  Portfolio =", portfolioR)
    else:
      print("  Portfolio =", portfolioR, "    Wallet = ", wallet, "   " + currency + " =", (format(possibleIncome, '.5f')))
    print("=====================================================================================================")
    print("  ", colors['CYAN'], orderstatus, colors['reset'])
    print(" ", *buysell_log, sep='\n')

#############################################################################################################################
                ### Begin Loop and get Historic Data ###

while True:
    # Open log file to writing
    file_object = open(buysellLog, 'a')
    
    # Get local time
    named_tuple = time.localtime()
    time_string = time.strftime("%m/%d/%Y (%H:%M)", named_tuple)

    try:
        # Get wallet
        wallet = (format(float(auth_client.get_account(specificUSD)['balance']), '.5f'))

        # Wait to avoid API limit
        time.sleep(0.5)

        # Get history rates
        historicData = auth_client.get_product_historic_rates(currency, granularity=period)

        # Make an array of the historic price data from the matrix
        price = np.squeeze(np.asarray(np.matrix(historicData)[:,4]))

        # Wait to avoid API limit
        time.sleep(0.5)

        # Get latest data - price, bid, and ask
        newData = auth_client.get_product_ticker(product_id=currency)
        currentPrice=newData['price']
        currentPrice = format(float(currentPrice), '.5f')
        currentBuy=newData['bid']
        currentSell=newData['ask']

        # Wait to avoid API limit
        time.sleep(0.5)

    except:
        # In case something went wrong with cbpro
        print("Error Encountered")

#############################################################################################################################
                            ### Strategy ###

    # Calculate the rate of change 11 and 14 units back, then sum them - testing 10 and 20
    ROC11 = np.zeros(13) 
    ROC14 = np.zeros(13) 
    ROCSUM = np.zeros(13)

    for ii in range(0,13): 
        ROC11[ii] = (100*(price[ii]-price[ii+10]) / float(price[ii+10]))  #Default 11, set to 10
        ROC14[ii] = (100*(price[ii]-price[ii+20]) / float(price[ii+20]))  #Default 14, set to 20
        ROCSUM[ii] = ( ROC11[ii] + ROC14[ii] )

    # Calculate the past 4 Coppock values with Weighted Moving Average (WMA)
    coppock = np.zeros(4)
    for ll in range(0,4):
        coppock[ll] = (((1*ROCSUM[ll+9]) + (2*ROCSUM[ll+8]) + (3*ROCSUM[ll+7]) \
        + (4*ROCSUM[ll+6]) + (5*ROCSUM[ll+5])) + (6*ROCSUM[ll+4]) \
        + (7*ROCSUM[ll+3]) + (8*ROCSUM[ll+2]) + (9*ROCSUM[ll+1]) \
        + (10*ROCSUM[ll])/ float(55))

    # Calculate the past 3 derivatives of the Coppock Curve
    coppockD1 = np.zeros(3)
    for mm in range(3):
        coppockD1[mm] = coppock[mm] - coppock[mm+1]

#############################################################################################################################
                            ### Funds to Use ###

    # The maximum amount of Cryptocurrency that can be purchased with your funds
    #possiblePurchase = (float(funding)) / float(currentPrice)

    # Verify if there are any owned crypto curreny in the account
    owned = float(auth_client.get_account(specificID)['available'])

    # The value of the crypto currency in USD
    possibleIncome = float(currentPrice) * owned
    possibleprofit = (float(possibleIncome) * (1 + fee)) - float(Buyvolume)
    portfolioR = float(possibleIncome) + float(wallet)
    portfolioD = float(portfolioS) - float(portfolioR)

#############################################################################################################################
                             ###Decision Making###
    # Verify if orders are pending and set varibles
    getorders=list(auth_client.get_orders(id=specificID))
    if getorders == []:
        orders = False
        orderstatus = ""
        ordercount = 0
    else:
        orders = True
        ordercount +=1
        if ordercount ==2:
            iterationcancel +=1
            csvorders = [ getorders[0], None ]
            csvorders = str(csvorders)
            csvorderbuy = csvorders[csvorders.index(buyl)+len(buyl):csvorders.index(buyr)]
            csvorderprice = csvorders[csvorders.index(pricel)+len(pricel):csvorders.index(pricer)]
            csvordersize = csvorders[csvorders.index("'size': '")+len("'size': '"):csvorders.index("', 'product_id': '")]
            csvorderopen = csvorders[csvorders.index(statusl)+len(statusl):csvorders.index(statusr)]
            auth_client.cancel_all(product_id=currency)
            orderstatus = "  Cancelling a" + csvorderbuy + " order for " + str(csvordersize) + " " + currency + ". Loop limit reached."
            
    # Get last buy/sell and write to log
    getfills=list(auth_client.get_fills(product_id = currency))
    csvfill = [ getfills[0], None ]
    csvfill = str(csvfill)
    csvprice = csvfill[csvfill.index(pricel)+len(pricel):csvfill.index(pricer)]
    csvprice = format(float(csvprice), '.5f')
    csvsize = csvfill[csvfill.index(sizel)+len(sizel):csvfill.index(sizer)]
    csvsize = format(float(csvsize), '.5f')
    csvfee = csvfill[csvfill.index(feel)+len(feel):csvfill.index(feer)]
    csvfee = format(float(csvfee), '.5f')
    csvvolume = csvfill[csvfill.index(voll)+len(voll):csvfill.index(volr)]
    csvvolume = format(float(csvvolume), '.5f')
    csvtrade = csvfill[csvfill.index(tradel)+len(tradel):csvfill.index(trader)]
    csvside = csvfill[csvfill.index(sidel)+len(sidel):csvfill.index(sider)]

    # verify trade is greater then last trade and display based on buy/sell status
    if str(csvtrade) > str(pasttrade):
        pasttrade = csvtrade

        # Sell side
        if not iteration == 1 and csvside == 'sell':
            iterationsell +=1
            EmailSubject = "CBPro - Sell"
            file_object.write(csvfill)
            funding = float(funding) + float(csvvolume)
            if str(csvvolume) > str(Buyvolume):
                buysell = " ", time_string + " -  Sold   " + str(csvsize) + " " + currency + " for " + str(csvprice) + "/Coin.  TOTAL = " + str(csvvolume) + "   *Profit*"
                file_object.write(",Profit")
                buysell_log.append(buysell)
                file_object.write('\n')

            else:
                buysell = " ", time_string + " -  Sold   " + str(csvsize) + " " + currency + " for " + str(csvprice) + "/Coin.  TOTAL = " + str(csvvolume) + "   *Loss*"
                file_object.write(",Loss")
                buysell_log.append(buysell)
                file_object.write('\n')

        # Buy side
        if not iteration == 1 and csvside == 'buy':
            iterationbuy +=1
            EmailSubject = "CBPro - Buy"
            file_object.write(csvfill)
            buysell = " ", time_string + " - Brought " + str(csvsize) + " " + currency + " for " + str(csvprice) + "/Coin.  TOTAL = " + str(csvvolume)
            file_object.write(",Buy")
            Buyvolume = str(csvvolume)
            Buyprice = format(float(csvprice), '.5f')
            funding = float(funding) - float(csvvolume)
            buysell_log.append(buysell)
            file_object.write('\n')

        if not iteration == 1:
            # Send email using the above buy/sell varibles
            mimeMessage['subject'] = EmailSubject
            emailMsg = buysell
            mimeMessage.attach(MIMEText(emailMsg, 'plain'))
            raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()
            message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
            emailMsg = ""       # Clear the varible
            EmailSubject = ""   # Clear the varible

        time.sleep(0.5)
    
    # Buy Conditions: latest derivative is + and previous is -
    if test == False and owned == 0.0 and orders == False and (coppockD1[0]/abs(coppockD1[0])) == 1.0 and (coppockD1[1]/abs(coppockD1[1])) == -1.0:

        # Place the order
        auth_client.place_limit_order(product_id=currency, side='buy', price=currentBuy, size=sizelimit)
        time.sleep(0.5)
        bidbuysell = " ", time_string + " - BUY Limit order placed for " + str(sizelimit) + " " + currency + " at " + currentBuy + "/Coin."

        # Update variables
        orderstatus = bidbuysell
        time.sleep(0.5)

    # Sell Conditions: latest derivative is - and previous is +
    if test == False and not owned == 0.0 and orders == False and (coppockD1[0]/abs(coppockD1[0])) == -1.0 and (coppockD1[1]/abs(coppockD1[1])) == 1.0:

        # Place the order
        auth_client.place_limit_order(product_id=currency, side='sell', price=currentSell, size=sizelimit)
        time.sleep(0.5)
        bidbuysell = " ", time_string + " - SELL Limit order placed for " + str(sizelimit) + " " + currency + " at " + currentSell + "/Coin."

        # Update variables
        orderstatus = bidbuysell
        time.sleep(0.5)

    # Stop loss: sell everything and stop trading if your value is less than 80% of initial investment
    # Update and define stop loss limits - if stoploss (profits) is 2x limit = update limit.
    stoploss = float(possibleIncome) + float(funding)
    if float(stoploss) / 2 > float(stoplosslimit):
        stoplosslimit = (float(stoploss) / 3) *.8

    if test == False and float(stoplosslimit) >= float(stoploss):
        owned = float(auth_client.get_account(specificID)['available'])
        EmailSubject = "CBPro - Stop Loss"
        if not owned == 0.0:
            # Place the order
            auth_client.place_market_order(product_id=currency, side='sell', size=sizelimit)
            bidbuysell = " ", time_string + " - SELL Limit order placed for " + str(sizelimit) + " " + currency + " at " + currentSell + "/Coin."
            time.sleep(1)
        
        getorders=list(auth_client.get_orders(id=specificID))
        if not getorders == []:
            getfills=list(auth_client.get_fills(product_id = currency))
            csvfill = [ getfills[0], None ]
            csvfill = str(csvfill)
            file_object.write(csvfill)
            csvtrade = csvfill[csvfill.index(tradel)+len(tradel):csvfill.index(trader)]
            csvprice = csvfill[csvfill.index(pricel)+len(pricel):csvfill.index(pricer)]
            csvsize = csvfill[csvfill.index(sizel)+len(sizel):csvfill.index(sizer)]
            csvfee = csvfill[csvfill.index(feel)+len(feel):csvfill.index(feer)]
            csvvolume = csvfill[csvfill.index(voll)+len(voll):csvfill.index(volr)]
            if str(csvtrade) > str(pasttrade):
                buysell = " ", time_string + " -  Sold   " + str(csvsize) + " " + currency + " for " + str(csvprice) + "/Coin.  TOTAL = " + str(csvvolume) + "   *Stop Loss*"
                buysell_log.append(buysell)
                file_object.write(",Stop Loss")
                file_object.write('\n')

        # Send email using the above stoploss varibles
        mimeMessage['subject'] = EmailSubject
        emailMsg = buysell
        mimeMessage.attach(MIMEText(emailMsg, 'plain'))
        raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()
        message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
        time.sleep(0.5)

        # Will break out of the while loop and the program will end
        file_object.close()
        cls()
        Details()
        print('\n')
        print("  STOP LOSS limit reached - Current =", stoploss, "  Limit =", stoplosslimit)
        input("- - - - Press Enter to exit - - - - -")
        break

    #Close log file to save it for viewing - reopen at top of loop
    file_object.close()

    cls()

    # Break if in testing else continue loop
    if test == True:
        print("- - - - TESTING TESTING TESTING - - - - -")
        Details()
        print('\n')
        # Begin Test script


        # End Test script
        print('\n')
        input("- - - - Press Enter to exit TEST - - - -")
        break

    # Wait for 10 minute before repeating
    Details()
    time.sleep(600)
    iteration +=1
