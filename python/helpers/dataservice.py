
from python.helpers.breezeclient import BreezeClient
import yfinance as yf

def getDataFromBreeze(from_date,to_date,stock,optionType,strikePrice,interval):
        breezeClient = BreezeClient(True)      
        data = breezeClient.getNSEorOptionsDataWithInDates(from_date,to_date,stock,optionType,strikePrice,interval) 
        return data

def getDataFromYahoo(from_date,to_date,stock,optionType,strikePrice,interval):
    #'1sec','1min', '5min', '30min', or '1day' -- breeze
    #Valid intervals: [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]') - yfinance
    if stock == 'CNXBAN':
        stock = '^NSEBANK'
    
    if interval == '1min':
        interval = '1m'
    elif interval == '5min':
        interval = '5m'        
    elif interval == '30min':
        interval = '30m'
    elif interval == '1day':    
        interval = '1d'

    data = yf.download(stock, start=from_date, end=to_date,interval=interval)    
    data = data.reset_index()
    data.columns = data.columns.str.lower()
    print(data.head(2))
    
    return data