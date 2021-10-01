import yfinance as yf 
import pprint 


msft = yf.Ticker('MSFT')
hist = msft.history(period="max")

#get stock info
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(hist)

