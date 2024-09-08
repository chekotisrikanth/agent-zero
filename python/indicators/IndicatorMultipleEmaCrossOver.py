import pandas_ta as ta
import pandas as pd
import logging


import sys


class IndicatorMultipleEmaCrossOver():    
    
    signalName = None
    lineNames = []
    markers = []
    #tolerance = 10
 
    def __init__(self,optionType=None,indicatorparams=None,timeframe=None):
        self.optionType = optionType
        self.indicatorparams = indicatorparams
        self.timeframe = timeframe
        super().__init__()

    def __str__(self):
        return 'IndicatorMultipleEmaCrossOver'
    
    def addIndicator(self,df,optionType,indicatorparams):
        indicatorparams = '8,21,34,3'
        if optionType is None or optionType.strip() == '':
            optionType = 'Call'

        if optionType == 'CE':
            optionType = 'Call'
        elif optionType == 'PE':
            optionType = 'Put'

        print(f'inside addIndicator {optionType} {indicatorparams}')
        print(df.head(2))
        if df is None or df.empty:
            return df
        lowema = 8
        highema = 21
        tolerance = 3 
        if indicatorparams is not None and  ',' in indicatorparams:
                params = indicatorparams.split(',')
                lowema = int(params[0])
                highema = int(params[1])
                emagap = int(params[2])
                if len(params) > 3:
                   tolerance = int(params[3])
          
                
        self.signalName = 'Buy'
        self.markers = ['Buy','crossover_8_21_occurred']
        df[self.signalName] = None
        df['optionType'] = ''
        df['crossover_8_21_occurred'] = 0
        df['diff'] = 0
        self.lineNames = ['EMA8','EMA21','EMA34']
        #print(df.head(2))    
        #print(df.tail(2))
        #print(len(df))
        if optionType == 'Call':
            #print(f'inside call optionType {optionType} {indicatorparams} {len(df)}')
            # Calculate the EMA values
            df['EMA8'] = ta.ema(df['close'], length=8)
            df['EMA21'] = ta.ema(df['close'], length=21)
            df['EMA34'] = ta.ema(df['close'], length=34)
             
            # Initialize a flag to track the first crossover of EMA8 with EMA21
            crossover_8_21_occurred = False
            crossover_8_34_occurred = False

            # Iterate over each row in the DataFrame
            for i in range(1, len(df)):
                # Check if EMA8 crosses EMA21
                currentdatetime = df.at[i, 'datetime']
                currentema8 = df.at[i, 'EMA8']
                currentema34 = df.at[i, 'EMA34']
                if currentema8 is not None and currentema34 is not None:
                    #print(f'currentdatetime: {currentdatetime}, currentema8: {currentema8}, currentema34: {currentema34}')
                    diff = currentema8 - currentema34
                    df.at[i, 'diff'] = diff
                    #print(f'diff: {diff}')
                    #print(f'currentdatetime {currentdatetime} {currentema8} {df.at[i, "EMA21"]} {df.at[i, "EMA34"]}')
                    if (df.at[i-1, 'EMA8'] < df.at[i-1, 'EMA21']) and (df.at[i, 'EMA8'] > df.at[i, 'EMA21']):
                        #print(f'crossover_8_21_occurred at {df.at[i, "datetime"]}')
                        crossover_8_21_occurred = True  # Set the flag to True
                        df.at[i, 'crossover_8_21_occurred'] = 1
                        #print(f'crossover_8_21_occurred set to 1 at index {i}')

                    #print(f'crossover_8_21_occurred: {crossover_8_21_occurred}')
                    if crossover_8_21_occurred and df.at[i-1, 'EMA8'] < df.at[i-1, 'EMA34'] and df.at[i, 'EMA8'] > df.at[i, 'EMA34'] :
                        #print(f'crossover_8_34_occurred at {df.at[i, "datetime"]}')
                        crossover_8_34_occurred = True
                        

                    #print(f'crossover_8_34_occurred: {crossover_8_34_occurred}')
                    if crossover_8_34_occurred and diff > tolerance:
                        #print(f'Signal condition met at index {i}, datetime {currentdatetime}, diff {diff}, tolerance {tolerance}')
                        #print(f'Signal triggered at index {i}, datetime {currentdatetime}')
                        #print(f'signal triggered at index {i} len {len(df)}')
                        df.at[i, self.signalName] = 1  # Add signal = 1
                        df.at[i, 'optionType'] = optionType
                        crossover_8_34_occurred = False
                        crossover_8_21_occurred = False

        elif optionType == 'Put':
                #print(f'inside put optionType {optionType} {indicatorparams} {len(df)}')
                # Calculate the EMA values
                df['EMA8'] = ta.ema(df['close'], length=8)
                df['EMA21'] = ta.ema(df['close'], length=21)
                df['EMA34'] = ta.ema(df['close'], length=34)
                
                # Initialize a flag to track the first crossover of EMA8 with EMA21
                crossover_34_21_occurred = False
                crossover_34_8_occurred = False
                # Iterate over each row in the DataFrame
                for i in range(1, len(df)):
                    # Check if EMA8 crosses EMA21
                    currentema8 = df.at[i, 'EMA8']
                    currentema21 = df.at[i, 'EMA21']
                    diff = currentema21 - currentema8
                    df.at[i, 'diff'] = diff
                    if df.at[i-1, 'EMA34'] > df.at[i-1, 'EMA21'] and df.at[i, 'EMA34'] < df.at[i, 'EMA21'] :
                        crossover_34_21_occurred = True  # Set the flag to True
                        df.at[i, 'crossover_34_21_occurred'] = 1
                    # Check if EMA8 crosses EMA34 after the crossover of EMA8 with EMA21
                    if crossover_34_21_occurred and df.at[i-1, 'EMA34'] > df.at[i-1, 'EMA8'] and df.at[i, 'EMA34'] < df.at[i, 'EMA8']:
                        crossover_34_8_occurred = True
                    
                    if crossover_34_8_occurred and diff > tolerance:
                      df.at[i, self.signalName] = 1  # Add signal = 1
                      df.at[i, 'optionType'] = optionType
                      crossover_34_8_occurred = False
                      crossover_34_21_occurred = False

        #print(df.tail(2))
        #print(f'self.signalName {self.signalName}')
        #print(df[df[self.signalName]==1].tail())
        #print(df[df['crossover_8_21_occurred']==1].tail())
        #print(f'signals in addindicator {len(df[df[self.signalName]==1])} {self.signalName}')    
        df[self.signalName] = df[self.signalName].shift(1)
        return df 

    def addIndicator2(self,df,optionType,indicatorparams): 
        if optionType == 'CE':
            if ',' in indicatorparams:
                params = indicatorparams.split(',')
                lowema = int(params[0])
                middleema = int(params[1])
                highema = int(params[2])
            else:   
                lowema = 8
                middleema = 21
                highema = 34 
        elif optionType == 'PE':
            if ',' in indicatorparams:
                params = indicatorparams.split(',')
                lowema = int(params[1])
                middleema = int(params[0])
                highema = int(params[2])
            else:   
                lowema = 34
                middleema = 21
                highema = 8
        
        emaSName = 'EMA'+ str(lowema)
        emaMName = 'EMA'+str(middleema)      
        emaLName = 'EMA'+str(highema)      
        self.signalName = '3emacrossover' #emaSName + '-' + emaMName +'-' + str(emaLName)
        df[emaSName] = ta.ema(df.close, length=lowema)
        df[emaMName] = ta.ema(df.close, length=middleema)
        df[emaLName] = ta.ema(df.close, length=highema)
        df[self.signalName]=0
        lowmidcrossover = str(lowema) + 'Crossover' + str(middleema)
        lowhighcrossover = str(lowema) + 'Crossover' + str(highema)

        lowmidcrossoverreverse = str(middleema) + 'Crossover' + str(lowema)
        df[lowmidcrossover] = ta.cross(df[emaSName],df[emaMName])
        df[lowhighcrossover] = ta.cross(df[emaSName],df[emaLName])

        df[lowmidcrossoverreverse] = ta.cross(df[emaMName],df[emaSName])
  
        # Iterate over lowhighcrossover values        
        for lh_crossover in df[lowhighcrossover]:
            # Find the nearest lowmidcrossover and lowmidcrossoverreverse values
            nearest_lowmid = max((dt for dt in df[lowmidcrossover] if dt <= lh_crossover), default=None)
            nearest_lowmid_reverse = min((dt for dt in df[lowmidcrossoverreverse] if dt >= lh_crossover), default=None)
            
            # Check if lowhighcrossover value is between lowmidcrossover and lowmidcrossoverreverse
            if nearest_lowmid is not None and nearest_lowmid_reverse is not None:
                # Update signal column to 1
                #df.loc[(df.index >= nearest_lowmid) & (df.index <= nearest_lowmid_reverse), self.signalName] = 1
                pass
        
        if optionType == 'CE':
           crossover_condition = (df[lowhighcrossover] == 1) & (df[emaSName] > df[emaMName])
        elif optionType == 'PE':
           crossover_condition = (df[lowhighcrossover] == 1) & (df[emaSName] < df[emaMName])   

        # Add signal = 1 where the condition is met
        # Find the index of the first occurrence where the condition is met
        first_occurrence_index = df.index[crossover_condition].min()

        # Set signal = 1 only at the first occurrence
        if not pd.isnull(first_occurrence_index):
            df.at[first_occurrence_index, self.signalName] = 1

        print(f'self.signalName {self.signalName}')
        print(df[df[self.signalName]==1].tail())
        print(f'signals in addindicator {len(df[df[self.signalName]==1])} {self.signalName}')     
        return df




