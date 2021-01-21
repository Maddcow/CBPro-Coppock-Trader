# CBPro-Coppock-Trader
![image](https://user-images.githubusercontent.com/37763928/105216791-07552100-5b21-11eb-9273-e48c19359b1a.png)

This is a trading bot using the Coinbase Pro API. It uses Coppock values and Weight Moving Average (WMA) to place limit buy and sell orders. It will also send out an authenticated email via gmail once a buy or sell order has been confirmed. If an order is placed and not filled, it will be canceled after 30 mins (3 loops) and the buy/sell varible will be active again to replace an order.

There is a stop loss in place along with a way to update  the stop loss limit if the profit level is 2x the stop loss limit. 

Logging is made local to the D: drive for viewing buy/sell info.

Follow the steps listed here (https://developers.google.com/gmail/api/quickstart/python) to enable the Google API for your gmail account in order for the email function to work. 


To Do:

    ** Clean up the code -- its works but its messy **
    Ask for currency to trade with along with error correction if typed incorrect  - BTC = BTC-USD.
    Set size limits based on currency? or set size limt based funds? I dont know yet.
    Multi-currency watch/trade?
