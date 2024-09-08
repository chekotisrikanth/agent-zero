#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from breeze_connect import BreezeConnect
import os
from datetime import datetime, timedelta
import pandas_ta as ta
import requests
from datetime import date,time
from time import sleep
import zipfile
from concurrent.futures import ThreadPoolExecutor
#from Logger import setup_logger
import traceback
import logging
from selenium import webdriver
import urllib
from pyotp import TOTP
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
#https://api.icicidirect.com/apiuser/login?api_key=29051CA13967l00^557R178750Ho42z8

 

token_df = None
breezeClient = None
class BreezeClient:
      
    holidays = {"26-01-2023","07-03-2023","30-03-2023","04-04-2023","07-04-2023","14-04-2023","01-05-2023","28-06-2023",
                    "15-08-2023","19-09-2023","02-10-2023","24-10-2023","14-11-2023","27-11-2023","25-12-2023",
                    "22-01-2024", "26-01-2024", "08-03-2024", "25-03-2024", "29-03-2024", "11-04-2024", "17-04-2024",
                      "01-05-2024", "20-05-2024", "17-06-2024", "17-07-2024", "15-08-2024", "02-10-2024", "01-11-2024", 
                      "15-11-2024", "25-12-2024"}
    holidays = [datetime.strptime(h, "%d-%m-%Y") for h in holidays]
    session_key = '43922262'
    api_key = '29051CA13967l00^557R178750Ho42z8'
    api_secret = '9748152O28c#42814217241s^7Y0O934'
    password = 'Sri154818'
    userID = 6301958087
    totp = 'ONSFEMDZNF3VUYKHJNGWISTWOA'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    def __init__(self,generateSession=False,getTokens=False,onlyBanknifty=False):
        #logger = logger # setup_logger('breezeclient')
        
        global breezeClient
        global session_key
        #generateSession = False
        if(generateSession and breezeClient is None):
            try:
                breezeClient = BreezeConnect(api_key=self.api_key)
                print('generate session')                
                session_key = self.autoLogin(self.api_key,self.userID,self.password,self.totp,self.api_secret)
                #breezeClient.generate_session(api_secret=self.api_secret,session_token=self.session_key)
                print(breezeClient.get_funds())
                print('generated session')
                if getTokens:
                 self.getToken(onlyBanknifty)
            except Exception as e:
                print(f"Exception occurred while generating session: {e}")  
                breezeClient = None          
        else:
           print('skip generate session')      
   
    def getBreezeClient(self):
        return breezeClient
    
    def refreshSession(self):        
        print('refresh session')
        self.autoLogin(breezeClient.api_key, breezeClient.userID, breezeClient.password, breezeClient.totp, breezeClient.api_secret)
    
    def autoLogin(self,api_key,userID,password,totp,api_secret):
        global breezeClient
        #breezeClient =  BreezeConnect(api_key=api_key)
        #return
        # Set up Chrome options for headless mode
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
        #chrome_options.binary_location = '/usr/lib/chromium-browser/chromedriver'
        browser = webdriver.Chrome(options=chrome_options)
        browser.get("https://api.icicidirect.com/apiuser/Login?api_key="+urllib.parse.quote_plus(api_key))
        browser.implicitly_wait(5)
        breezeClient =  BreezeConnect(api_key=api_key)
        username_element = browser.find_element("xpath", '/html/body/form/div[2]/div/div/div[1]/div[2]/div/div[1]/input') 
        password_element =  browser.find_element("id",'txtPass')
   
        username_element.send_keys(userID)        
       
        password_element.send_keys(password)
        #Checkbox
        browser.find_element("xpath",'/html/body/form/div[2]/div/div/div[1]/div[2]/div/div[4]/div/input').click()
        #Click Login Button
        browser.find_element("xpath",'/html/body/form/div[2]/div/div/div[1]/div[2]/div/div[5]/input[1]').click()
        sleep(2)         
        pin = browser.find_element("xpath", '/html/body/form/div[2]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div[1]/input')
        totp = TOTP(totp)
        token =  totp.now()       
        pin.send_keys(token)
        browser.find_element("xpath",'/html/body/form/div[2]/div/div/div[2]/div/div[2]/div[2]/div[4]/input[1]').click()
        sleep(1)
        retries = 5
        temp_token = None
        for _ in range(retries):
            currentUrl = browser.current_url.split('apisession=')
            if len(currentUrl) > 1:
                temp_token = currentUrl[1][:8]
                # Save in Database or text File
                print('temp_token', temp_token)
                breezeClient.generate_session(api_secret=api_secret, session_token=temp_token)
                break
            else:
                print("Session token not found, retrying...on url "+browser.current_url)
                sleep(2)  # Wait for 2 seconds before retrying

        if temp_token is None:
            print("Failed to retrieve session token from URL after retries.")
        
        browser.quit()
        return temp_token
    
    def autoLoginUsingFirefox(self, api_key, userID, password, totp, api_secret):
        global breezeClient
        # Set up Firefox options for headless mode
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")  # Run Firefox in headless mode

        # Initialize the Firefox WebDriver with options
        browser = webdriver.Firefox(options=firefox_options)
        browser.get("https://api.icicidirect.com/apiuser/Login?api_key=" + urllib.parse.quote_plus(api_key))
        browser.implicitly_wait(5)

        breezeClient = BreezeConnect(api_key=api_key)

        # Find and fill the username and password fields
        username_element = browser.find_element("xpath", '/html/body/form/div[2]/div/div/div[1]/div[2]/div/div[1]/input')
        password_element = browser.find_element("id", 'txtPass')
        username_element.send_keys(userID)
        password_element.send_keys(password)

        # Check the checkbox and click the login button
        browser.find_element("xpath", '/html/body/form/div[2]/div/div/div[1]/div[2]/div/div[4]/div/input').click()
        browser.find_element("xpath", '/html/body/form/div[2]/div/div/div[1]/div[2]/div/div[5]/input[1]').click()
        sleep(2)

        # Find the pin input and send the TOTP token
        pin = browser.find_element("xpath", '/html/body/form/div[2]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div[1]/input')
        totp = TOTP(totp)
        token = totp.now()
        pin.send_keys(token)
        browser.find_element("xpath", '/html/body/form/div[2]/div/div/div[2]/div/div[2]/div[2]/div[4]/input[1]').click()
        sleep(1)

        # Try to retrieve the session token from the URL
        retries = 5
        temp_token = None
        for _ in range(retries):
            currentUrl = browser.current_url.split('apisession=')
            if len(currentUrl) > 1:
                temp_token = currentUrl[1][:8]
                # Save in Database or text File
                print('temp_token', temp_token)
                breezeClient.generate_session(api_secret=api_secret, session_token=temp_token)
                break
            else:
                print("Session token not found, retrying...on url " + browser.current_url)
                sleep(2)  # Wait for 2 seconds before retrying

        if temp_token is None:
            print("Failed to retrieve session token from URL after retries.")

        # Quit the browser
        browser.quit()
        return temp_token

    def closeAnyTrades(self):
        print('close any trades')
        try:
            openpositions = breezeClient.get_portfolio_positions()
            print(f'open openpositions {openpositions}')            
            openpositions = openpositions['Success']
            for position in openpositions:
                print(position)
                print(position['stock_code'],position['expiry_date'],position['strike_price'],position['right'])
                order_id,order_price = self.place_order('Sell',position['strike_price'],position['right'])
                print(f'order_id {order_id} order_price {order_price}  {position["stock_code"]} {position["expiry_date"]} {position["strike_price"]} {position["right"]}')
        except Exception as e:
            print(f"Exception occurred while closing trades: {e}")
            return False
        return True

    def getToken(self,onlyBanknifty):  
        global token_df      
        zip_url = "https://directlink.icicidirect.com/NewSecurityMaster/SecurityMaster.zip"
        csv_filename = "FONSEScripMaster.txt" 
        download_dir = self.script_dir+'/SecurityMaster'
        file_path = os.path.join(download_dir, csv_filename)

        if os.path.isfile(file_path):
            print(f'File {file_path} already exists. Skipping downloading.')
            token_df = pd.read_csv(file_path)            
        else:
            print(f'File {file_path} doesn\'t exists. downloading.')
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
            zip_filepath = os.path.join(download_dir, "SecurityMaster.zip")
            response = requests.get(zip_url)
            # Download the ZIP file
            response = requests.get(zip_url)

            if response.status_code == 200:
                with open(zip_filepath, "wb") as f:
                    f.write(response.content)
                print("ZIP file downloaded successfully.")

                # Extract the ZIP file
                with zipfile.ZipFile(zip_filepath, "r") as zip_ref:
                    zip_ref.extractall(download_dir)

                print("ZIP file extracted successfully.")

                # Read the CSV file into a DataFrame
                csv_filepath = os.path.join(download_dir, csv_filename)
                token_df = pd.read_csv(csv_filepath)
                print("CSV file loaded into DataFrame successfully.")
            else:
                print("Failed to download the ZIP file.")
        
        token_df = token_df[token_df.ShortName == 'CNXBAN']
        token_df = token_df[token_df.Series=='OPTION'] # filter futures   
        token_df['StrikePrice'] = token_df['StrikePrice'].astype(int)
        token_df['ExpiryDate'] = pd.to_datetime(token_df['ExpiryDate'])  
        token_df = token_df.sort_values(by='ExpiryDate', ascending=True) 
        expiryDate = token_df.iloc[0]['ExpiryDate'].strftime('%Y-%m-%d')  #self.get_next_thursday() 
        token_df['ExpiryDate'] = token_df['ExpiryDate'].dt.strftime('%Y-%m-%d')
        token_df = token_df[token_df['ExpiryDate'].str.contains(expiryDate)]
            
        print("breeze intrument token download completed")
        return token_df    
    
    def getTrades(self,start_date,end_date,exchange_code='NFO'):        
        if isinstance(start_date, date):            
            start_date = start_date.strftime('%Y-%m-%d')            
        if isinstance(end_date, date):
            end_date = end_date.strftime('%Y-%m-%d')
        print(f'get trades {start_date} {end_date} {exchange_code}')    
        trades = breezeClient.get_trade_list(from_date=start_date,
                        to_date=end_date,
                        exchange_code=exchange_code)
        trades = trades['Success']
        trade_details_list = []
        if trades is None:
             return None
        for trade in trades:    
            order_id=trade['order_id']
            print(f'get order details {order_id}')
            orderdetails = breezeClient.get_order_detail(exchange_code=exchange_code,order_id=order_id)
            #print(orderdetails)
            orderdetails = orderdetails['Success'][0]    
            orderPrice = orderdetails['price']
            print(trade['trade_date'],trade['action'],trade['strike_price'],trade['right'],trade['average_cost'],orderPrice)              
            
            trade_date = trade['trade_date']
            action = trade['action']
            strike_price = trade['strike_price']
            right = trade['right']
            average_cost = trade['average_cost']
            
            # Append the details to the list
            trade_details_list.append({
                'Trade Date': trade_date,
                'Action': action,
                'Strike Price': strike_price,
                'Right': right,
                'Traded Price': average_cost,
                'Ordered Price': orderPrice,
                'Order ID': order_id
            })
        trade_details_df = pd.DataFrame(trade_details_list)
        # Sort the DataFrame by Order ID
        trade_details_df.sort_values(by='Order ID', inplace=True)

        grouped = trade_details_df.groupby(['Trade Date', 'Strike Price', 'Right'])
        #print(grouped)
        # Initialize a list to store PnL results
        pnl_results = []

            # Process each group
        for name, group in grouped:
            # Ensure the group is sorted by Order ID
            group = group.sort_values(by='Order ID')
            
            # Initialize a list to hold unmatched buy trades
            unmatched_buys = []

            for index, row in group.iterrows():
                if row['Action'] == 'Buy':
                    # Add buy trades to unmatched buys list
                    unmatched_buys.append(row)
                elif row['Action'] == 'Sell' and unmatched_buys:
                    # If there is a sell trade and there are unmatched buys, pair them
                    buy_trade = unmatched_buys.pop(0)
                    sell_trade = row
                    #print(buy_trade)
                    #print(sell_trade)
                    pnl = (float(sell_trade['Traded Price']) - float(buy_trade['Traded Price'])) * 15  # Adjust multiplier if needed
                    Orderedpnl = (float(sell_trade['Ordered Price']) - float(buy_trade['Ordered Price'])) * 15
                    #round to 2 decimal places
                    pnl = round(pnl, 2)
                    Orderedpnl = round(Orderedpnl, 2)                    
                    diff = pnl - Orderedpnl
                    
                    pnl_results.append({
                        'Trade Date': buy_trade['Trade Date'],
                        'Strike Price': buy_trade['Strike Price'],
                        'Right': buy_trade['Right'],
                        'Buy Order ID': buy_trade['Order ID'],
                        'Sell Order ID': sell_trade['Order ID'],
                        'Buy Price': buy_trade['Traded Price'],
                        'Sell Price': sell_trade['Traded Price'],
                        'PnL': pnl,
                        'Sell Order ID': sell_trade['Order ID'],
                        'Ordered Buy Price': buy_trade['Ordered Price'],
                        'Ordered Sell Price': sell_trade['Ordered Price'],
                        'Ordered PnL': Orderedpnl,
                        'Difference': diff
                    })

            # Convert the PnL results to a DataFrame
        pnl_df = pd.DataFrame(pnl_results)

            # Display the PnL DataFrame
        print(pnl_df)
        return pnl_df


    def get_order_details(self,order_id,exchange_code='NFO'):
        try:
            price = None
            print(f'get order details {order_id} {exchange_code}') 
            order_details = breezeClient.get_trade_detail(exchange_code=exchange_code,order_id=order_id) #get_order_detail   
            print(f'get order details response {order_details}')         
            if order_details is None or 'execution_price' not in order_details:
                sleep(1)
                order_details = breezeClient.get_trade_detail(exchange_code=exchange_code,order_id=order_id) #get_order_detail
            price = order_details['Success'][0]['execution_price']
            if price is not None:
                price = float(price)
            return price 
        except Exception as e:
            print(f"Exception occurred while getting order details: {e}")
            return None
           
    #transaction_type,strikePrice,option_type,tagname=tagname,quantity=filled_quantity
    def place_order(self,action,strike_price,right,stock_code="CNXBAN",expiry_date=None,
                    quantity=15,exchange_code="NFO",product="options",order_type="market",price=None,
                    validity="day",tagname='emi'):
        #expiry_date="2024-06-12T00:00:00.000Z" 
        expiry_date= self.nearest_expiry_date(datetime.now(),stock_code)
        print(f'place order with {stock_code} {exchange_code} {product} {action} {order_type} {quantity} {price} {validity} {expiry_date} {right} {strike_price} {tagname}')
        order_resp = breezeClient.place_order(stock_code=stock_code,exchange_code=exchange_code,
                                 product=product,action=action,
                                 order_type=order_type,quantity=quantity,price=price,
                                 validity=validity,
                                 stoploss='',
                                 expiry_date=expiry_date,right=right,strike_price=strike_price,
                                 user_remark=tagname
                                 )
        print(f'place order response {order_resp}')
        status_code = order_resp['Status']
        if status_code != 200:
            print(f"Error occurred while placing order: {order_resp['Error']}")
            if 'insufficient' in order_resp['Error']:
                return 123,None # return 123 for insufficient funds
            return None,None
        print(f"Order placed successfully: {order_resp['Success']}")
        order_id = order_resp['Success']['order_id']
        if order_id is None:
            print(f"Order ID is None")
            return None,None
        order_price = self.get_order_details(order_id,exchange_code)
        return order_id,order_price
    
    def getLTP(self,strike_price,optionType="call",stock_code="CNXBAN",exchange_code="NFO",expiry_date=None,
                 product_type="options"):
       
        logger.debug(f'get quote {stock_code} {exchange_code} {product_type} {optionType} {strike_price}')  
        if 'CE' in optionType.upper():
                optionType = 'call'
        elif 'PE' in optionType.upper():
                optionType = 'put'    
        
        try:
            response = breezeClient.get_option_chain_quotes(
                    stock_code=stock_code,
                    exchange_code=exchange_code,
                    product_type=product_type,
                    #expiry_date="2024-05-29T00:00:00.000Z",
                    right=optionType,
                    strike_price=strike_price)          
            
            data = response
            ltp = None
            # Check if 'Success' key is present and it's a non-empty list
            if 'Success' in data and isinstance(data['Success'], list) and len(data['Success']) > 0:
                first_entry = data['Success'][0]
                expiry_date = first_entry.get('expiry_date')
                ltp = first_entry.get('ltp')
                print(f'ltp {ltp} for {strike_price} {optionType} {stock_code} {exchange_code} {product_type}  ')                
            else:
                print(f"API response does not contain 'Success' key with valid data for {stock_code} {exchange_code} {product_type} {optionType} {strike_price}")
                print(response)
                
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {stock_code} {exchange_code} {product_type} {optionType} {strike_price} {e} ")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {stock_code} {exchange_code} {product_type} {optionType} {strike_price} {e}")
        return ltp

        '''
         if expiry_date is None:
            expiry_date = self.nearest_expiry_date_icici(datetime.now(),stock_code)    
            #%Y-%m-%dT06:00:00.000Z    
            expiry_date = datetime.strptime(expiry_date, '%d-%b-%Y').strftime('%Y-%m-%dT%H:%M:%S.000Z')
        
            
        quote = breezeClient.get_quotes(
                    stock_code=stock_code,
                    exchange_code=exchange_code,
                    expiry_date=expiry_date,
                    product_type=product_type,
                    right=optionType,
                    strike_price=strike_price)
        
        opchaing = breezeClient.get_option_chain_quotes(stock_code="CNXBAN",
                    exchange_code="NFO",
                    product_type="options",
                    #expiry_date="2024-05-29T00:00:00.000Z",
                    right="call",
                    strike_price="48900")
        print(opchaing)

        quote1 = breezeClient.get_quotes(
                    stock_code="CNXBAN",
                    exchange_code="NFO",
                    expiry_date='2024-05-29T00:00:00.000Z',
                    product_type="options",
                    right="call",
                    strike_price="48900")
        print(quote1)
        opchaing = breezeClient.get_option_chain_quotes(stock_code="CNXBAN",
                    exchange_code="NFO",
                    product_type="options",
                    expiry_date="2024-05-29T00:00:00.000Z",
                    right="call",
                    strike_price="48900")
        opchaing2 = breezeClient.get_option_chain_quotes(stock_code="NIFTY",
                    exchange_code="NFO",
                    product_type="options",
                    expiry_date="2024-05-30T06:00:00.000Z",
                    right="call",
                    strike_price="20100")
        print(opchaing)
        ''' 
        
    def get_next_thursday_fromdate(self,dateinput):
        # Get the current date
        current_date = dateinput
        # Calculate the number of days to the next Thursday (Thursday is weekday 3, where Monday is 0 and Sunday is 6)
        days_until_thursday = (3 - current_date.weekday() + 7) % 7
        # Add the calculated number of days to the current date to get the next Thursday
        next_thursday = current_date + timedelta(days=days_until_thursday)
        # Format the next Thursday in ISO format
        next_thursday_iso_format = next_thursday.strftime('%Y-%m-%d')
        return next_thursday_iso_format
    
    def get_next_thursday(self):
        # Get the current date
        current_date = datetime.now()
        # Calculate the number of days to the next Thursday (Thursday is weekday 3, where Monday is 0 and Sunday is 6)
        days_until_thursday = (3 - current_date.weekday() + 7) % 7
        # Add the calculated number of days to the current date to get the next Thursday
        next_thursday = current_date + timedelta(days=days_until_thursday)
        # Format the next Thursday in ISO format
        next_thursday_iso_format = next_thursday.strftime('%Y-%m-%d')
        return next_thursday_iso_format

    
    def getNSEData(self,from_date,to_date,exchange,stock,producttype,interval):
        histdf = None
        try:
            #from_date_format = from_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            #to_date_format = to_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  
            from_date_format = from_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            to_date_format = to_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            print(f'download {stock} exchange {exchange} {from_date_format} {to_date_format} {producttype} {interval}')     
            res = breezeClient.get_historical_data_v2(interval=interval,
                                from_date= from_date_format,
                                to_date= to_date_format,
                                stock_code=stock,
                                exchange_code=exchange,
                                product_type=producttype
                                )
            #print(res)
            if res is None or res['Status'] != 200:
                    print(f'Error occurred while downloading options: {res["Error"]}')
                    print('refreshing session')
                    #self.refreshSession()
                    return histdf
            histdf = pd.DataFrame(res['Success'])       
            if histdf is not None and not histdf.empty:
                '''
                histdf.rename(columns = {'open':'Open', 'close':'Close',
                              'high':'High','low':'Low','datetime':'Datetime',
                               'volume':'Volume'
                              }, inplace = True)
                '''              
                histdf['datetime'] = pd.to_datetime(histdf['datetime'])             
        except Exception as e:
                print(f"Exception occurred {stock} : {from_date} {to_date}  {e}")     
        return histdf
    
    def getNSEorOptionsDataWithForDate(self,given_date,exchange,stock,optionType,strikePrice,expiryDate,producttype,interval):  
               
        total_data = pd.DataFrame()
        if isinstance(given_date, str):
            given_date = datetime.strptime(given_date, '%Y-%m-%d')       
        if isinstance(given_date, date) and not isinstance(given_date, datetime):
            given_date = datetime.combine(given_date, time())
       
        startdate = given_date.replace(hour=9, minute=00, second=00)
        enddate = given_date.replace(hour=16, minute=00, second=00) 
                
     
        df_list = []
        nextStart = None
        #"Interval should be either '1second','1minute', '5minute', '30minute', or '1day'" for breeze
        if interval == "1sec":
            interval = "1second"
            time_delta = timedelta(seconds=1*1000)
            nextStart = 1
        elif interval == "1min":
            interval = "1minute"
            time_delta = timedelta(minutes=1*1000)
            nextStart = 60
        elif interval == "5min":
            interval = "5minute"
            time_delta = timedelta(minutes=5*1000)
            nextStart = 5*60
        elif interval == "30min":
            interval = "30minute"
            time_delta = timedelta(minutes=30*1000)
            nextStart = 30*60
        elif interval == "1day":
            interval = "1day"
            time_delta = timedelta(days=1*1000)
            nextStart = 24*60*60
        else:
            raise ValueError("Invalid interval")            
        
        while startdate <= enddate:                
                end_of_interval  = startdate + time_delta
                # Adjust end_of_interval not to exceed enddate
                end_of_interval = min(end_of_interval, enddate)
                histdf = []
                if optionType is None or optionType.strip() == '':
                    histdf = self.getNSEData(startdate,end_of_interval,'NSE',stock,'cash',interval)
                else:
                    #ovverite the expiry date with the given date as from input date range may fall on different expiry dates
                    expiry = self.nearest_expiry_date(given_date,stock) 
                    histdf = self.getOptionsHistoryData(exchange,stock,optionType,expiry,strikePrice,startdate,end_of_interval,producttype,interval)    
                if histdf is not None and not histdf.empty:
                  df_list.append(histdf) 
                startdate = end_of_interval  + timedelta(seconds=nextStart) 
        
        if df_list is not None and len(df_list) > 0:
            #print(df_list.head(2))
            total_data = pd.concat(df_list, ignore_index=True)
        
            
            #total_data.to_excel(file_path,index=False)                                         
        return total_data

    
    def getNSEorOptionsDataWithInDates(self,from_date,to_date,symbol,optionType,strikePrice,interval):  
        total_data = pd.DataFrame()
        if isinstance(from_date, str):
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
        if isinstance(to_date, str):
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
        if isinstance(from_date, date) and not isinstance(from_date, datetime):
            from_date = datetime.combine(from_date, time())
        if isinstance(to_date, date) and not isinstance(to_date, datetime):
            to_date = datetime.combine(to_date, time())    

        if to_date is not None and not isinstance(to_date, datetime):
            to_date = to_date.replace(hour=23, minute=59, second=59)
       
        startdate = from_date
        enddate = to_date  
        df_list = []
        nextStart = None
        #"Interval should be either '1second','1minute', '5minute', '30minute', or '1day'" for breeze
        if interval == "1sec":
            interval = "1second"
            time_delta = timedelta(seconds=1*1000)
            nextStart = 1
        elif interval == "1min":
            interval = "1minute"
            time_delta = timedelta(minutes=1*1000)
            nextStart = 60
        elif interval == "5min":
            interval = "5minute"
            time_delta = timedelta(minutes=5*1000)
            nextStart = 5*60
        elif interval == "30min":
            interval = "30minute"
            time_delta = timedelta(minutes=30*1000)
            nextStart = 30*60
        elif interval == "1day":
            interval = "1day"
            time_delta = timedelta(days=1*1000)
            nextStart = 24*60*60
        else:
            raise ValueError("Invalid interval")            
        
        while startdate <= enddate:                
                end_of_interval  = startdate + time_delta
                # Adjust end_of_interval not to exceed enddate
                end_of_interval = min(end_of_interval, enddate)
                histdf = []
                if optionType is None or optionType.strip() == '':
                    #from_date,to_date,exchange,stock,producttype,interval
                    histdf = self.getNSEData(startdate,end_of_interval,'NSE','CNXBAN','cash',interval)
                else:
                    expiry = self.nearest_expiry_date(startdate,'CNXBAN')
                    histdf = self.getOptionsHistoryData('NFO','CNXBAN',optionType,expiry,strikePrice,from_date,end_of_interval,'options',interval)    
                    tempHist = pd.DataFrame(histdf)
                    print(tempHist.tail(2))
                df_list.append(histdf) 
                startdate = end_of_interval  + timedelta(seconds=nextStart) 
        
        if df_list is not None and len(df_list) > 0:
            #print(df_list.head(2))            
            total_data = pd.concat(df_list, ignore_index=True)
        
            
            #total_data.to_excel(file_path,index=False)                                         
        return total_data
    
     #stock,optionType,expiry,strikePrice,startdate,end_of_interval,interval
     #strikePrice,option_type,expiryDate,from_date,to_date,interval= '1second',stock_code="CNXBAN",  exchange='NFO'
     #'NSE','CNXBAN',optionType,expiry,strikePrice,from_date,end_of_interval,'options',interval
    def getOptionsHistoryData(self,exchange,stock,option_type,expiry,strikePrice,from_date,to_date,producttype,interval):
        histdf = None      
        try:     
                if 'CE' in option_type:
                    option_type = 'call'
                elif 'PE' in option_type:
                    option_type = 'put' 

                if isinstance(from_date, str):
                    from_date = datetime.strptime(from_date, '%Y-%m-%d')
                if isinstance(to_date, str):
                    to_date = datetime.strptime(to_date, '%Y-%m-%d')           
                from_date_format = from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                to_date_format = to_date.strftime("%Y-%m-%dT%H:%M:%S.000Z") 
                if isinstance(expiry, str):
                    date_object = datetime.strptime(expiry, "%d-%b-%Y")
                    expiryDate_format = date_object.strftime('%Y-%m-%d')  
                if isinstance(expiry, datetime):                    
                    expiryDate_format = expiry.strftime('%Y-%m-%d')      
                  
                strike_price_str = str(int(strikePrice))   
                print(f'downloading options data {strike_price_str} {option_type} {from_date_format} {to_date_format} expiry {expiryDate_format}')
                res = breezeClient.get_historical_data_v2(interval=interval,
                                    from_date= from_date_format,
                                    to_date= to_date_format,
                                    stock_code=stock,
                                    exchange_code=exchange,
                                    product_type=producttype,
                                    expiry_date=expiryDate_format,
                                    right = option_type,
                                    strike_price=strike_price_str)
                if res is None or res['Status'] != 200:
                    print(f'Error occurred while downloading options: {res["Error"]}')
                    return histdf
                histdf = pd.DataFrame(res['Success'])    
                if histdf is not None and not histdf.empty:
                    print(f'downloaded options data {strike_price_str} {option_type} {from_date_format} {to_date_format} expiry {expiryDate_format}')
                    histdf.drop_duplicates(subset='datetime', inplace=True)
                    print(f"after deleting duplicates options data  {from_date_format} {to_date_format} length: {len(histdf)}")
                    return histdf           
        except Exception as e:
                print(f"Exception occurred while downloading options: {e}")
                return histdf
    
    def getHistoricalAPI(self,strikePrice,option_type,stock_code="CNXBAN",historyInDays=1,exchange='NFO',interval= '5minute'):
        to_date= datetime.now()
        to_date = to_date - timedelta(days=4)
        from_date = to_date - timedelta(days=historyInDays)
        from_date_format = from_date.isoformat()
        to_date_format = to_date.isoformat()
        expiryDate = self.get_next_thursday()
        res = breezeClient.get_historical_data_v2(interval=interval,
                            from_date= from_date_format,
                            to_date= to_date_format,
                            stock_code=stock_code,
                            exchange_code=exchange,
                            product_type="options",
                            expiry_date=expiryDate,
                            right = option_type,
                            strike_price=strikePrice)
        histdf = pd.DataFrame(res['Success'])
        return histdf
    
    def downloadOptionsHistoricalAPIWithExpiryDate(self,strikePrice,option_type,expiryDate,interval,                                     
                                     stock_code="CNXBAN",                                
                                    exchange='NFO'):
                
        total_data = []        
        date_obj = datetime.strptime(expiryDate, "%d-%b-%Y")
        start_time = datetime.now() - timedelta(days=7)
        start_time_format = start_time.strftime("%m-%d")
        strike_price_str = str(int(strikePrice))
        file_name = f'{expiryDate}_{strike_price_str}_{option_type}_{start_time_format}.xlsx'
        folder_path = self.script_dir+ '/optionsData/'+interval        
        if not os.path.exists(folder_path):           
            os.makedirs(folder_path)
        
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            print(f'File {file_name} already exists. Skipping downloading.')
            #total_data = pd.read_excel(file_path)            
        else:
            print(f'downloading options data {file_name}')
            try:
                expiryDate_format = date_obj.strftime('%Y-%m-%d')   
                   
                # Set the initial startdate to the start_time
                startdate = start_time

                # Initialize an empty list to store DataFrames
                df_list = []
                end_time = datetime.now()  # Define end_time

                # Loop until startdate reaches or exceeds end_time
                while startdate <= end_time:
                    # Calculate the enddate as startdate + 1000 seconds
                    enddate = startdate + timedelta(seconds=1000)
                    from_date_format = startdate.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                    to_date_format = enddate.strftime("%Y-%m-%dT%H:%M:%S.000Z") 
                    
                    print(f'downloading {file_name} {from_date_format} {to_date_format}')
                    # Call your history API method with startdate and enddate
                    res = breezeClient.get_historical_data_v2(interval=interval,
                                    from_date= from_date_format,
                                    to_date= to_date_format,
                                    stock_code=stock_code,
                                    exchange_code=exchange,
                                    product_type="options",
                                    expiry_date=expiryDate_format,
                                    right = option_type,
                                    strike_price=strike_price_str)
                    histdf = pd.DataFrame(res['Success'])                    
                    df_list.append(histdf)                    
                    # Increment startdate by 1000 seconds for the next iteration
                    startdate += timedelta(seconds=1000)

                # Concatenate all the accumulated DataFrames
                total_data = pd.concat(df_list, ignore_index=True)    
                total_data.to_excel(file_path)      
            except Exception as e:
                print(f"Exception occurred: {e}")
        return file_path
    
    def downloadOptionsHistoricalAPIWithInDates(self,strikePrice,option_type,expiryDate,start_time,end_time,interval,
                                     indicatorname,
                                     signalTime=None,
                                     stock_code="CNXBAN",                                
                                    exchange='NFO'):
        total_data = []        
        date_obj = datetime.strptime(expiryDate, "%d-%b-%Y")
        start_time_format = start_time.strftime("%m-%d")
        strike_price_str = str(int(strikePrice))
        file_name = f'{expiryDate}_{strike_price_str}_{option_type}_{start_time_format}.xlsx'
        folder_path = self.script_dir+ '/optionsData/'+interval        
        if not os.path.exists(folder_path):           
            os.makedirs(folder_path)
        
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            print(f'File {file_name} already exists. Skipping downloading.')
            #total_data = pd.read_excel(file_path)            
        else:
            print(f'downloading options data {file_name}')
            try:
                expiryDate_format = date_obj.strftime('%Y-%m-%d')   
                   
                # Set the initial startdate to the start_time
                startdate = start_time

                # Initialize an empty list to store DataFrames
                df_list = []

                # Loop until startdate reaches or exceeds end_time
                while startdate <= end_time:
                    # Calculate the enddate as startdate + 1000 seconds
                    enddate = startdate + timedelta(seconds=1000)
                    from_date_format = startdate.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                    to_date_format = enddate.strftime("%Y-%m-%dT%H:%M:%S.000Z") 
                    
                    print(f'downloading {file_name} {from_date_format} {to_date_format}')
                    # Call your history API method with startdate and enddate
                    res = breezeClient.get_historical_data_v2(interval=interval,
                                    from_date= from_date_format,
                                    to_date= to_date_format,
                                    stock_code=stock_code,
                                    exchange_code=exchange,
                                    product_type="options",
                                    expiry_date=expiryDate_format,
                                    right = option_type,
                                    strike_price=strike_price_str)
                    histdf = pd.DataFrame(res['Success'])                    
                    df_list.append(histdf)                    
                    # Increment startdate by 1000 seconds for the next iteration
                    startdate += timedelta(seconds=1000)

                # Concatenate all the accumulated DataFrames
                total_data = pd.concat(df_list, ignore_index=True)    
                total_data.to_excel(file_path)      
            except Exception as e:
                print(f"Exception occurred: {e}")
        return file_path
    
    
    
    def getBNHistoricalAPI(self,historyInDays=1,interval= '5minute'):
            to_date= datetime.now()
            #to_date = to_date - timedelta(days=2)
            from_date = to_date - timedelta(days=historyInDays)
            from_date_format = from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            to_date_format = to_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            print(f'get data from {from_date_format} to {to_date_format} ')
            expiryDate = self.get_next_thursday()
            res = breezeClient.get_historical_data_v2(interval=interval,
                                #from_date= '2023-06-26T07:35:00+0530',
                                #to_date= '2023-07-21T16:05:00+0530',
                                #from_date= "2023-05-01T07:00:00.000Z",
                                #to_date= "2023-07-30T07:00:00.000Z",
                                from_date= from_date_format,
                                to_date= to_date_format,                                
                                stock_code='CNXBAN',
                                exchange_code='NSE',
                                product_type="cash"
                                )

            histdf = pd.DataFrame(res['Success'])
            histdf['datetime'] = pd.to_datetime(histdf['datetime'], format='%Y-%m-%d %H:%M:%S')
            # Define the time range
            #start_time = pd.to_datetime('09:15:00', format='%H:%M:%S').time()
            #end_time = pd.to_datetime('15:25:00', format='%H:%M:%S').time()
            # Filter the DataFrame within the time range
            #filtered_df = histdf[(histdf['datetime'].dt.time >= start_time) & (histdf['datetime'].dt.time <= end_time)]
            print(histdf)
            return histdf

    def getBNExpirtyDates(self,fromdate,todate):
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
            "Upgrade-Insecure-Requests": "1", "DNT": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip, deflate, br"}
        
        #https://www.nseindia.com/api/historical/foCPV/expireDts?instrument=OPTIDX&symbol=BANKNIFTY&year=2024
        URL1 = "https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY"
        BNIFTY_URL = f'https://www.nseindia.com/api/historical/fo/derivatives/meta?&from={fromdate}&to={todate}&instrumentType=OPTIDX&symbol=BANKNIFTY'

        homeRes = requests.get(URL1, headers=head)
        d = requests.get(BNIFTY_URL, headers=head, cookies=homeRes.cookies).json()
        expiryDates = d["data"][2]
        return expiryDates
    
    def downloadOptionsChainDataUsingExpiryDay(self,expiryDate,callType):
        df = pd.DataFrame()
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
            "Upgrade-Insecure-Requests": "1", "DNT": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip, deflate, br"}


        if 'call' in callType:
            callType = 'CE'
        elif 'put' in callType:
            callType = 'PE'    

        URL1 = "https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY"        
        homeRes = requests.get(URL1, headers=head)
        date_object = datetime.strptime(expiryDate, "%d-%b-%Y")   
        fromdateObj = date_object - timedelta(days=7)    
        fromformated_date = fromdateObj.strftime("%d-%m-%Y")    
        toformated_date = date_object.strftime("%d-%m-%Y")     
        formatted_date = fromdateObj.strftime("%d-%m-%Y")
        BNIFTY_URL = f'https://www.nseindia.com/api/historical/foCPV?from={fromformated_date}&to={toformated_date}&expiryDate={expiryDate}&instrumentType=OPTIDX&symbol=BANKNIFTY&year=2024&optionType={callType}' 
        #f'https://www.nseindia.com/api/historical/fo/derivatives?&optionType=CE&from={fromdate}&to={todate}&expiryDate={expiryDate}&instrumentType=OPTIDX&symbol=BANKNIFTY'
        print(f'downloading options data {BNIFTY_URL}')
        response = requests.get(BNIFTY_URL, headers=head, cookies=homeRes.cookies)            
        error = False
        if response.status_code == 200:
            d = response.json()
        else:
            date_object = datetime.strptime(expiryDate, "%d-%b-%Y")
            formatted_date = '05-10-2023'#date_object.strftime("%d-%m-%Y")
            BNIFTY_URL = f'https://www.nseindia.com/api/historical/fo/derivatives?from={formatted_date}&to={formatted_date}&expiryDate={expiryDate}&instrumentType=OPTIDX&symbol=BANKNIFTY&year=2024&optionType={callType}' 
            response = requests.get(BNIFTY_URL, headers=head, cookies=homeRes.cookies)
            if response.status_code == 200:
                d = response.json()
            else: 
                error = True
        if error:
            print(f'error while downloading optionchain data {response.json()}')
        else:
            df = pd.DataFrame(d['data'])
            
        return df     

    def downloadOptionsChainData(self,fromdate,todate):
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
            "Upgrade-Insecure-Requests": "1", "DNT": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip, deflate, br"}

        URL1 = "https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY"
        
        homeRes = requests.get(URL1, headers=head)
        expiryDates = self.getBNExpirtyDates(fromdate,todate)
        # Convert date strings to datetime objects
        date_objects = [datetime.strptime(date_str, "%d-%b-%Y") for date_str in expiryDates]
        current_date = datetime.now()
        # Filter out future dates
        past_dates = [date_obj for date_obj in date_objects if date_obj <= current_date]
        date_strings = [date_obj.strftime("%d-%b-%Y") for date_obj in past_dates]

        print('getBNExpirtyDates from nse option chain site')
        print(date_strings)
        for expiryDate in expiryDates:
            file_name = f'{expiryDate}.xlsx'        
            file_path = os.path.join(self.script_dir+'/optionChainData', file_name)
            if os.path.isfile(file_path):
                print(f'File {file_path} already exists. Skipping downloading.')                            
            else:
                print('download data for {file_path} ')
                BNIFTY_URL = f'https://www.nseindia.com/api/historical/foCPV?from={fromdate}&to={todate}&expiryDate={expiryDate}&instrumentType=OPTIDX&symbol=BANKNIFTY&year=2023&optionType=CE' 
                #f'https://www.nseindia.com/api/historical/fo/derivatives?&optionType=CE&from={fromdate}&to={todate}&expiryDate={expiryDate}&instrumentType=OPTIDX&symbol=BANKNIFTY'
                d = requests.get(BNIFTY_URL, headers=head, cookies=homeRes.cookies).json()
                df = pd.DataFrame(d['data'])
                df.to_excel(file_path, index=False)
                print(df)
            
                  
            
    def addEMAGapIndicator(self,df,optiontype,gapdifference=5,signalName='TotalSignal'): 
        df['close'] = pd.to_numeric(df['close'])
        df["EMA8"] = ta.ema(df.close, length=8)
        df["EMA21"] = ta.ema(df.close, length=21)
        df[signalName]=0
        if 'call' in optiontype:
            df['8Crossover21']=ta.cross(df["EMA8"],df["EMA21"])
            df['EMA8_EMA21_Diff'] = df['EMA8'] - df['EMA21']
            crossover_indices = df[df['8Crossover21'] == 1].index  # Indices of all crossovers
            #print("Contents of crossover_indices:\n%s", crossover_indices.to_string())
            for i in range(len(crossover_indices)):
                crossover_index = crossover_indices[i]
                if i < len(crossover_indices) - 1:
                    next_crossover_index = crossover_indices[i + 1]
                else:
                    next_crossover_index = len(df)
                print(f'crossover_index {crossover_index} next_crossover_index {next_crossover_index}')
                for j in range(crossover_index, next_crossover_index):
                    if df['EMA8_EMA21_Diff'][j] > gapdifference:
                        df[signalName][j] = 1
                        break;
        else:
            df['21Crossover8']=ta.cross(df["EMA21"],df["EMA8"])     
            df['EMA21_EMA8_Diff'] = df['EMA21'] - df['EMA8']
            crossover_indices = df[df['21Crossover8'] == 1].index  # Indices of all crossovers
            for i in range(len(crossover_indices)):
                crossover_index = crossover_indices[i]
                if i < len(crossover_indices) - 1:
                    next_crossover_index = crossover_indices[i + 1]
                else:
                    next_crossover_index = len(df)
                print(f'crossover_index {crossover_index} next_crossover_index {next_crossover_index}')
                for j in range(crossover_index, next_crossover_index):
                    if df['EMA21_EMA8_Diff'][j] > gapdifference:
                        df[signalName][j] = 1
                        break;        
        return df    
            
     
    def addEMAIndicator(self,optiontype,historyInDays=30):
        df = self.getBNHistoricalAPI(historyInDays)
        df['close'] = pd.to_numeric(df['close'])
        df["EMA8"] = ta.ema(df.close, length=8)
        df["EMA21"] = ta.ema(df.close, length=21)
        df['TotSignal']=0
        if 'call' in optiontype:
            df['TotSignal']=ta.cross(df["EMA8"],df["EMA21"])
        else:
            df['TotSignal']=ta.cross(df["EMA21"],df["EMA8"])     

        #filter_datetime = pd.to_datetime('2023-07-21 13:05:00', format='%Y-%m-%d %H:%M:%S')
        #filtered_df = df[df['datetime'] == filter_datetime]
        #print(filtered_df[['datetime','close', 'EMA8','EMA21']])

        file_name = f'tradedata-BNnifty-{optiontype}.xlsx'        
        file_path = os.path.join(self.script_dir, file_name)

        df.to_excel(file_path, index=False)  
        print(len(df))
        return df
    

    # Function to get the next Thursday from a given date
    def get_thursdayDate(self,date_str):
        date_obj = date_str#datetime.strptime(date_str, '%Y-%m-%d')
        days_until_thursday = (2 - date_obj.weekday()) % 7
        if days_until_thursday == 0:
            # If it's already Thursday, return the same date
            return date_str.strftime('%d-%b-%Y')
        else:
            # Otherwise, get the next Thursday
            next_thursday = date_obj + timedelta(days=days_until_thursday)
            return next_thursday.strftime('%d-%b-%Y')
        
    # Function to get the next Thursday from a given date
    def get_expiryDate(self,date_obj):
        #date_obj = date_str#datetime.strptime(date_str, '%Y-%m-%d')
        target_date = date(2023, 9, 5)
        if date_obj > target_date:
           #wednesday expiry
           days_until_expiry = (2 - date_obj.weekday()) % 7
        else:
           #thursday expiry
           days_until_expiry = (3 - date_obj.weekday()) % 7    
        if days_until_expiry == 0:
            # If it's already Thursday, return the same date
            return date_obj.strftime('%d-%b-%Y')
        else:
            # Otherwise, get the next Thursday
            next_thursday = date_obj + timedelta(days=days_until_expiry)
            return next_thursday.strftime('%d-%b-%Y')

    

    def getExpiryDatesOfSignals(self,df):
        filtered_df = df[df['TotSignal']==1]
        print(f'signals count { len(filtered_df)}')
        # Convert the 'datetime' column to datetime data type
        filtered_df['datetime'] = pd.to_datetime(filtered_df['datetime'])        
        unique_dates = filtered_df['datetime'].dt.date.unique()
        # Get the next Thursday for each date in the list
        next_expiriesdays_list = set(self.get_expiryDate(date_str) for date_str in unique_dates)    
        print('next_expiriesdays_list')    
        print(next_expiriesdays_list.to_string())
        return next_expiriesdays_list

    def getStrikePrices(self,expiryDate):
        self.downloadOptionsChainDataUsingExpiryDay(expiryDate)
        file_name = f'{expiryDate}.xlsx'        
        file_path = os.path.join(self.script_dir+'/optionChainData', file_name)            
        data = pd.read_excel(file_path)
        return data    
        
    def filterStrikePrices(self,optionChaindata,signalPrice,DeltaList):      
        
        optionChaindata['FH_STRIKE_PRICE'] = optionChaindata['FH_STRIKE_PRICE'].astype(float)

        optionChaindata['FH_STRIKE_PRICE'] = optionChaindata['FH_STRIKE_PRICE'].astype(int)

        

        # Create a new DataFrame to store the filtered rows
        filtered_data = pd.DataFrame()

        # Filter rows where FH_STRIKE_PRICE is between the price range for each price in PriceList  
        signalPrice = (signalPrice // 100) * 100      
        for delta in DeltaList:
            lower_bound = signalPrice - delta
            upper_bound = signalPrice + delta
            filtered_rows = optionChaindata[
                (optionChaindata['FH_STRIKE_PRICE'] >= lower_bound) &
                (optionChaindata['FH_STRIKE_PRICE'] <= upper_bound)
            ]
            filtered_data = pd.concat([filtered_data, filtered_rows])

        # Drop duplicates and sort the final filtered DataFrame
        filtered_data = filtered_data.drop_duplicates().sort_values(by='FH_STRIKE_PRICE')
        print(f'signalPrice {signalPrice} len {len(filtered_data)}')
        #print(filtered_data)
        return filtered_data

    def allStikesData(self,optionChainDataSignals,interval):
      for index,row in optionChainDataSignals.iterrows():
            self.downloadOptionsHistoricalAPI(expiryDate=row['FH_EXPIRY_DT'],
                                 option_type='call',strikePrice=row['FH_STRIKE_PRICE'],interval=interval)
    
    def getAllStikePriceDataForSignalDate(self,signalDatetime,stock,signalPrice,optiontype,DeltaList):        
        expiryDate = self.nearest_expiry_date(signalDatetime,stock)    #'11-Oct-2023' 
        optionChainDataSignals = self.downloadOptionsChainDataUsingExpiryDay(expiryDate,optiontype)   
        if optionChainDataSignals is None or len(optionChainDataSignals) == 0:
           return None
        optionChainDataSignals = self.filterStrikePrices(optionChainDataSignals,signalPrice,DeltaList) 
        return optionChainDataSignals

    def get_expiry_from_json(self,input_date):
        expiries = ["05-Jan-2023","12-Jan-2023","19-Jan-2023","25-Jan-2023","02-Feb-2023","09-Feb-2023","16-Feb-2023","23-Feb-2023",
                    "02-Mar-2023",
                    "09-Mar-2023","16-Mar-2023","23-Mar-2023","29-Mar-2023","06-Apr-2023","13-Apr-2023","20-Apr-2023","27-Apr-2023","04-May-2023",
                    "11-May-2023","18-May-2023","25-May-2023","01-Jun-2023","08-Jun-2023","15-Jun-2023","22-Jun-2023","28-Jun-2023",
                    "29-Jun-2023","06-Jul-2023","13-Jul-2023","20-Jul-2023","27-Jul-2023","03-Aug-2023","10-Aug-2023","17-Aug-2023",
                    "24-Aug-2023","31-Aug-2023","06-Sep-2023","07-Sep-2023","13-Sep-2023","14-Sep-2023","20-Sep-2023","21-Sep-2023",
                    "28-Sep-2023","04-Oct-2023","05-Oct-2023","11-Oct-2023","18-Oct-2023","26-Oct-2023","01-Nov-2023","08-Nov-2023",
                    "15-Nov-2023","22-Nov-2023","30-Nov-2023","06-Dec-2023","13-Dec-2023","20-Dec-2023","28-Dec-2023","03-Jan-2024",
                    "10-Jan-2024","17-Jan-2024","25-Jan-2024","31-Jan-2024","07-Feb-2024","14-Feb-2024","21-Feb-2024","29-Feb-2024",
                    "06-Mar-2024","13-Mar-2024","20-Mar-2024","27-Mar-2024","03-Apr-2024","25-Apr-2024",
                    "27-Jun-2024","26-Sep-2024","26-Dec-2024"
    ]
        date_objects = [datetime.strptime(date, "%d-%b-%Y") for date in expiries]        
        date_objects = [date.date() for date in date_objects]
        if isinstance(input_date, datetime):
            input_date = input_date.date()
        nearest_next_date = None
        for current_date in sorted(date_objects):
            #current_date = datetime.strptime(date, "%d-%b-%Y")
            if current_date >= input_date:
                nearest_next_date = current_date
                break
        return nearest_next_date.strftime("%d-%b-%Y") if nearest_next_date else None
    
    def nearest_expiry_date(self, input_date, index_name):
        #return '16-Jul-2024'
        expiry_rules = {
            "NIFTY": {"weekly": 3},  # Thursday
           # "CNXBAN": {"weekly": 2, "monthly": "last_thursday"},
           "CNXBAN": {"weekly": 2},
            "NIFFIN": {"weekly": 1},  # Tuesday
            "NIFSEL": {"weekly": 0}  # Monday
        }
        
        # Convert the date to a datetime object if it's not already
        if isinstance(input_date, datetime):
            input_date = input_date.date()

        # Extract the year and month
        year = input_date.year
        month = input_date.month

        # Get the expiry rules for the given index
        index_expiry_rules = expiry_rules.get(index_name)

        if index_expiry_rules is None:
            return None  # Index not found in rules

        nearest_expiry = None

        if "weekly" in index_expiry_rules:
            # Calculate the nearest weekly expiry date
            weekly_expiry_day = index_expiry_rules["weekly"]
            nearest_expiry = input_date + timedelta((weekly_expiry_day - input_date.weekday()) % 7)

        monthly_expiry = None
        if "monthly" in index_expiry_rules:
            monthly_expiry_rule = index_expiry_rules["monthly"]
            if monthly_expiry_rule == "last_thursday":
                # Calculate the last Thursday of the month. Handle the case where month is December
                if month == 12:
                    next_month = 1
                    next_year = year + 1
                else:
                    next_month = month + 1
                    next_year = year
                last_day_of_month = datetime(next_year, next_month, 1) - timedelta(days=1)
                while last_day_of_month.weekday() != 3:  # Thursday
                    last_day_of_month -= timedelta(days=1)
                monthly_expiry = last_day_of_month.date()

        # Check if it's the last week of the month and index is BankNifty
        #if index_name == "CNXBAN" and input_date.month != (input_date + timedelta(days=7)).month:
        #    nearest_expiry = monthly_expiry

        if nearest_expiry not in self.holidays:
            return nearest_expiry.strftime("%d-%b-%Y")
        else:
            adjusted_expiry_date = nearest_expiry - timedelta(days=1)
            while adjusted_expiry_date in self.holidays:
                adjusted_expiry_date -= timedelta(days=1)
            return adjusted_expiry_date.strftime("%d-%b-%Y")   

    def nearest_expiry_date_icici(self,input_date,index_name):
        
        expiry_rules = {
                "NIFTY": {"weekly": 3},  # Thursday
                "CNXBAN": {"weekly": 2, "monthly": 2},
                "NIFFIN": {"weekly": 1},  # Tuesday   
                 "NIFSEL": {"weekly": 0}  # Monday          
                 }
        # Convert the date to a datetime object if it's not already
        if isinstance(input_date, datetime):
            input_date = input_date.date()

        # Extract the year and month
        year = input_date.year
        month = input_date.month

        # Get the expiry rules for the given index
        index_expiry_rules = expiry_rules.get(index_name)

        if index_expiry_rules is None:
            return None  # Index not found in rules

        if "weekly" in index_expiry_rules:
            # Calculate the nearest weekly expiry date
            weekly_expiry_day = index_expiry_rules["weekly"]
            nearest_expiry = input_date + timedelta((weekly_expiry_day - input_date.weekday()) % 7)

        monthly_expiry = None
        if "monthly" in index_expiry_rules:
            monthly_expiry_rule = index_expiry_rules["monthly"]
            if monthly_expiry_rule == "last_thursday":
                # Calculate the last Thursday of the month
                last_day_of_month = datetime(year, month + 1, 1) - timedelta(days=1)
                while last_day_of_month.weekday() != 3:  # Thursday
                    last_day_of_month -= timedelta(days=1)
                monthly_expiry = last_day_of_month

        # Check if it's the last week of the month and index is BankNifty
        if index_name == "CNXBAN" and monthly_expiry and input_date.month != (input_date + timedelta(days=7)).month:
            nearest_expiry = monthly_expiry
  
        if nearest_expiry not in self.holidays:
            return nearest_expiry.strftime("%d-%b-%Y")
        else: 
            adjusted_expiry_date = nearest_expiry - timedelta(days=1)
            while adjusted_expiry_date in self.holidays:
                adjusted_expiry_date -= timedelta(days=1)
            return adjusted_expiry_date.strftime("%d-%b-%Y")  
    
    def allStikesDataForSignalDate(self,df,interval,optiontype,historyIndays,indicatorname,DeltaList):     
      DeltaList = [100,200] 
      filtered_df = df[df['TotSignal']==1]
      filtered_df['datetime'] = pd.to_datetime(filtered_df['datetime']) 
      # Sort the DataFrame by the 'Datetime' column
      filtered_df.sort_values(by='datetime', inplace=True)
      filtered_df = filtered_df[filtered_df['datetime'] >= filtered_df['datetime'].max() - pd.DateOffset(days=historyIndays)]      
      for index,signalrow in filtered_df.iterrows(): 
        # Get the next Thursday for each date in the list
        start_time =   signalrow['datetime']
        expiryDate = self.get_thursdayDate(start_time)    #'11-Oct-2023' 
        optionChainDataSignals = self.downloadOptionsChainDataUsingExpiryDay(expiryDate,optiontype)   
        if len(optionChainDataSignals) >1:
            #print('optionChainDataSignals')
            #print(optionChainDataSignals)
            signalPrice = signalrow['high']    
            optionChainDataSignals = self.filterStrikePrices(optionChainDataSignals,signalPrice,DeltaList)  
            print(f'strikes {len(optionChainDataSignals)} for signal {start_time}')
            for index,row in optionChainDataSignals.iterrows():        
                    
                            
                    desired_time = time(9, 15)
                    # Create a new datetime object with the same date but the desired time
                    desired_datetime = datetime.combine(start_time.date(), desired_time)
                    end_time = desired_datetime + timedelta(hours=7)
                    fullFilePath = self.downloadOptionsHistoricalAPIWithInDates(start_time=desired_datetime,end_time=end_time,
                        expiryDate=row['FH_EXPIRY_DT'],
                                        option_type=optiontype,strikePrice=row['FH_STRIKE_PRICE'],interval=interval,indicatorname=indicatorname,signalTime=start_time)
        else:
            print(f'no optionchain data with expiry date {expiryDate}')        
                
            
                    
    def applyEMA8_EMA21Signals(self, bankniftyIndexfile, indicatorname):
        file_path = os.path.join(self.script_dir, bankniftyIndexfile)
        data = pd.read_excel(file_path)
        filtered_df = data[data['TotSignal'] == 1] 
        filtered_df['datetime'] = pd.to_datetime(filtered_df['datetime'])              
        print(f'Total Signals count {len(filtered_df)}')

        folder_path = os.path.join(self.script_dir, 'optionsData/1second')
        files = os.listdir(folder_path)
        
        # Get a list of datetime values where TotSignal is 1
        datetime_list = filtered_df[filtered_df['TotSignal'] == 1]['datetime'].tolist()

        # Group datetime_list by date
        date_grouped_signals = {}
        for signal_datetime in datetime_list:
            date = signal_datetime.date()
            if date not in date_grouped_signals:
                date_grouped_signals[date] = []
            date_grouped_signals[date].append(signal_datetime)
        
        threadCount = len(date_grouped_signals)
        print(f'Signals count group by date {threadCount}')

        def process_signals_on_date(date, signal_datetimes):
            print(f"processing date {date} {len(signal_datetimes)}") 
            try:                
                signalDateTimeObj = pd.to_datetime(date)
                expiryDateForSignal = '11-Oct-2023'#self.get_thursdayDate(signalDateTimeObj)
                for file in files:
                    if date.strftime('%m-%d') in file and expiryDateForSignal in file:
                        print(f'reading file {file} for signal date {date} ')
                        full_file_path = os.path.join(folder_path, file)
                        option_data = pd.read_excel(full_file_path)

                        if len(option_data) > 2:
                            
                            option_data['datetime'] = pd.to_datetime(option_data['datetime'], errors='coerce')
                            # Drop rows with 'NaT' values in the 'datetime' column
                            option_data.dropna(subset=['datetime'], inplace=True)

                            if indicatorname not in option_data.columns:
                                option_data[indicatorname] = 0
                            
                            updateExists = False
                            # Update the signal for all signal_datetimes on the specific date
                            # Define your time range for matching in seconds
                            time_range = 3

                            # Assuming 'option_data' is your DataFrame
                            for signal_datetime in signal_datetimes:
                                condition = (option_data['datetime'] == signal_datetime)
                                # Check if any rows exactly match the signal_datetime
                                exact_match = (option_data['datetime'] == signal_datetime).any()

                                if exact_match:
                                    # Exact match found
                                    condition = (option_data['datetime'] == signal_datetime)
                                    option_data.loc[condition, indicatorname] = 1
                                    updateExists = True
                                else:
                                    # No exact match, look for the next match within 3 seconds
                                    tolerance = timedelta(seconds=time_range)
                                    match_datetime = signal_datetime

                                    # Iterate through the DataFrame
                                    for i in range(len(option_data)):
                                        current_datetime = option_data['datetime'].iloc[i]

                                        # Check if the current row's datetime is within the tolerance of the signal_datetime
                                        if abs(current_datetime - match_datetime) <= tolerance:
                                            # Match found within 3 seconds, update the indicator
                                            option_data.loc[i, indicatorname] = 1
                                            updateExists = True
                                            print(f'match found at other time {current_datetime} for file {file}')
                                            break  # Stop searching for additional matches
                            if updateExists:
                                option_data.to_excel(full_file_path, index=False)
                                print(f'Done updating file {file}')
                            else:
                                # Log no match
                                print(f"No record exists for the signal {signal_datetime} in file {full_file_path}")
                                
                    else:
                       print(f'not updating file {file} for date {date}')            
            except Exception as e:
                print(f"Exception occurred for date {date} : {e}")  
                print(f'excetpion while updating signal  {traceback.format_exc()}')	 
        try:
          # Use ThreadPoolExecutor to process signals in parallel
            with ThreadPoolExecutor(max_workers=5) as executor:
                for date, signal_datetimes in date_grouped_signals.items():
                    print(f'updating for date {date}')
                    executor.submit(process_signals_on_date, date, signal_datetimes)
        except Exception as e:
           print(f"Exception while using ThreadPoolExecutor: {e}") 
        #time.sleep(30)   

def downloadOptionsData(expiryDate,strikePrice,option_type,interval):
    client = BreezeClient()    
    end_time= datetime.strptime('2023-10-03T15:25:00.000Z', '%Y-%m-%dT%H:%M:%S.000Z')  #datetime.now()
    start_time  = end_time - timedelta(hours=7) #datetime.strptime('2023-10-03T09:15:00.000Z', '%Y-%m-%dT%H:%M:%S.000Z').date()
    client.downloadOptionsHistoricalAPIWithInDates(strikePrice,option_type,expiryDate,start_time,end_time,interval,indicatorname=None,
                                     signalTime=None,
                                     stock_code="CNXBAN",                                
                                    exchange='NFO')
    #client.downloadOptionsHistoricalAPI(strikePrice,option_type,expiryDate,stock_code="CNXBAN",
    #                            historyInDays=30,
    #                            exchange='NFO',interval= interval)

def ema5PlL():
        DeltaList = [200]
        client = BreezeClient()
        optiontype = ['call','put']       
        justdownloaddatafirst = False
        
        # emas may be accurate for more than 8 days data
          #so downalod file first. delete some data if req and test few data
        for type in optiontype:
            client.print(f'running for option type {type}')
            file_name = f'tradedata-BNnifty-{type}.xlsx'
            file_path = os.path.join(client.script_dir, file_name)
            if justdownloaddatafirst:
                df = client.addEMAGapIndicator(type,historyInDays=30,gapdifference=10)                         
            else:   
                if 'call' in type:
                    indicatorname  = 'ema8-ema21'
                else:
                    indicatorname  = 'ema21-ema8'
                #df = client.addEMAGapIndicator(type,historyInDays=30,gapdifference=10)
                df = pd.read_excel(file_path)
                client.allStikesDataForSignalDate(df,'1second',type,historyIndays=8,indicatorname=indicatorname,DeltaList=DeltaList)
                client.applyEMA8_EMA21Signals(file_name,indicatorname)
        print('done')
        

        


def testfilter(df,signalPrice):
        DeltaList = [100, 200] 
        filtered_data = pd.DataFrame()

        # Filter rows where strikes is between the price range for each price in DeltaList   
        # DeltaList = [100,200]      
        for delta in DeltaList:
            lower_bound = signalPrice - delta
            upper_bound = signalPrice + delta
            filtered_rows = df[
                (df['StrikePrice'] >= lower_bound) &
                (df['StrikePrice'] <= upper_bound)
            ]
            filtered_data = filtered_data.append(filtered_rows, ignore_index=True)

        # Drop duplicates and sort the final filtered DataFrame
        filtered_data = filtered_data.drop_duplicates().sort_values(by='StrikePrice')
        print('signalPrice ',signalPrice)
        print(filtered_data)



def getNseData():
    client = BreezeClient(True)
    to_date = pd.Timestamp.now()
    from_date = to_date - pd.Timedelta(days=3)
    #from_date=2024-07-30 09:44:00, to_date=2024-07-30 09:54:00
    from_date =  "2024-07-30 09:44:00"
    to_date =  "2024-07-30 09:54:00"
    from_date = datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')
    to_date = datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')
    #df = client.getNSEData(from_date,to_date,'NSE','CNXBAN','cash','5minute')
    #print(df)
    breezeClient = BreezeClient(True)      
    data = breezeClient.getNSEorOptionsDataWithInDates(from_date,to_date,'CNXBAN',None,None,'1min') 
    data.to_excel('nseData.xlsx',index=False)
    print(data)

getNseData()    

#print(df)
#downloadOptionsData('11-Oct-2023','44200','call','1second')
#ema5PlL()
#client = BreezeClient(True)
#to_date = pd.Timestamp.now()
#from_date = to_date - pd.Timedelta(days=3)
#df = client.getNSEData(from_date,to_date,'NSE','CNXBAN','cash','5minute')

#print(df)
#df = client.getToken(True)
#print(df)
#testfilter(df,44600)

#df = client.getBNHistoricalAPI(historyInDays=3)
#folder_path = os.path.dirname(os.path.abspath(__file__))
#file_name = 'tradedata-BNnifty-ema8-ema21-test.xlsx'              
#file_path = os.path.join(folder_path, file_name) 
#print(df.tail())
#df.to_excel(file_path,index=False)
#client = BreezeClient()
#alldf = pd.DataFrame()
#for expiry in expiries:
#    df = client.downloadOptionsChainDataUsingExpiryDay(expiry,'CE')
#    alldf = pd.concat([alldf, df])

#alldf.to_excel('allcalls.xlsx',index=False)

#client = BreezeClient(True)
#orderdeta = client.place_order(action='BUY',strike_price=40000,right='put')
#print(orderdeta)
#quotes = client.getLTP(strike_price="48900")
#print(quotes)
    