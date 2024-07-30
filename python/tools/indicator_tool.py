import pandas as pd
import importlib.util
from python.helpers.tool import Tool, Response
from python.indicators import IndicatorMultipleEmaCrossOver
import traceback

class IndicatorTool(Tool):
    def execute(self, file_path, indicator_class_name,optionType=None, **kwargs):
        try:
            print(f'IndicatorTool execute with file_path={file_path}, optionType {optionType} indicator_class_name={indicator_class_name}, kwargs={kwargs}')
            # Read the file into a DataFrame
            df = pd.read_excel(file_path)

            # Load the indicator module
            module_name = f"python.indicators.{indicator_class_name}"
            #indicator_class = getattr(self, indicator_class_name)
            indicator_module = importlib.import_module(module_name)
            indicator_class = getattr(indicator_module, indicator_class_name)
            indicator_instance = indicator_class()
            
            print('before addIndicator')
            print(df.head(2))
            indexDatadf = indexDatadf = indicator_instance.addIndicator(df,optionType,None)
            print('after addIndicator')
            print(indexDatadf.head(2))
            signalName = indicator_instance.signalName
            print('signalName: '+signalName)
            #print('signal count: '+str(len(indexDatadf[indexDatadf[signalName]==1])))
        


            # Save the modified DataFrame back to an Excel file
            output_file_path = f"modified_{file_path}"
            indexDatadf.to_excel(output_file_path, index=False)
            return Response(message=f"Data with indicator saved to {output_file_path}", break_loop=False)
        except Exception as e:
            print(f'Error in IndicatorTool: {e}')
            traceback.print_exc()
            return Response(message=f"Error in IndicatorTool {e}", break_loop=True)

        


