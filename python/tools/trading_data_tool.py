import pandas as pd
import os
from datetime import datetime
from agent import Agent
from python.helpers.tool import Tool, Response
from python.helpers import files
from python.helpers.dataservice import getDataFromBreeze,getDataFromYahoo


class TradingDataTool(Tool):
    def execute(self, from_date,to_date,interval,optionType=None,strikePrice=None, **kwargs):
        try: 
            print(f"TradingDataTool: from_date={from_date}, to_date={to_date}, interval={interval}, optionType={optionType}, strikePrice={strikePrice}")  
            
            # 2024-07-30 10:04:59 convert to datetime
            if from_date is not None and to_date is not None:
                if ':' in from_date and ':' in to_date:
                    from_date = datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')
                    to_date = datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')
                else:    
                #conver from_date and to_date to datetime input is 2023-06-10
                    from_date = datetime.strptime(from_date, '%Y-%m-%d')
                    to_date = datetime.strptime(to_date, '%Y-%m-%d')

        
            data = getDataFromBreeze(from_date,to_date,'CNXBAN',optionType,strikePrice,interval)       
        
            filePrefix = 'indexData'
            if optionType is not None and optionType != '':
                filePrefix = 'optionsData_'+optionType
            
            # Save DataFrame to Excel file
            file_path = f"{filePrefix}_trading_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
            data.to_excel(file_path, index=False)
            #full_path = os.path.abspath(file_path)
            print(f"Data saved to {file_path}")
            print(data.head(2))
            return Response(message=f"Data saved to {file_path}", break_loop=False)
        except Exception as e:
            print(f'Error in TradingDataTool: {e}')
            return Response(message=f"Error in TradingDataTool {e}", break_loop=True)      
        
