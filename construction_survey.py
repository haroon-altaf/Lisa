#%%
from __future__ import annotations  
from functools import reduce
import io
import logging                                                                               
import pandas as pd
from static import LOGGING_PARAMS, URL
from utility import WebSession

#%%
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(LOGGING_PARAMS['filepath'], mode='a')
file_handler.setFormatter(logging.Formatter(LOGGING_PARAMS['fileformatter']))
file_handler.setLevel(logging.ERROR)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOGGING_PARAMS['consoleformatter']))
console_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

#%%
class ConstructionSurvey:
    """
    A class to represent the US Census Bureau Construction Survey data.

    Attributes:
        table: pd.DataFrame
        A Pandas DataFrame containing Year, Month, Permits, Authorized, Starts, Under Construction, and Completions.

    Methods:
        download: Downloads the US Census Bureau Construction Survey data; reads Excel files into DataFrames; returns a processed DataFrame.
        _process_df: Processes the raw DataFrames, merging them into one.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._table = data.copy(deep=True)

    @property
    def table(self) -> pd.DataFrame:
        return self._table.copy(deep=True)
    
    @classmethod
    def download(cls) -> ConstructionSurvey | None:
        
        # Fetch the US Census Bureau Construction Survey data
        with WebSession() as session:
            response_permit = session.get(URL.US_BUIL_PERMIT.value)
            response_auth = session.get(URL.US_BUIL_AUTH.value)
            response_start = session.get(URL.US_BUIL_START.value)
            response_construct = session.get(URL.US_BUIL_CONSTRUCT.value)
            response_complete = session.get(URL.US_BUIL_COMPLETE.value)
        if not all([response_permit, response_auth, response_start, response_construct, response_complete]):
            return None
        
        xl_list = []
        for response in [response_permit, response_auth, response_start, response_construct, response_complete]:
            try:
                xl_list.append(pd.ExcelFile(io.BytesIO(response.content)))
            except ValueError:
                logger.exception(f"Error processing Excel file from: {response.url}")
                return None
        
        df_list = []
        for xl in xl_list:
            df = cls._process_df(xl)
            if df is None: return None
            df_list.append(df)

        df_list = [df.rename(columns={'Total': colname})
                for df, colname in zip(df_list, ['Permits', 'Authorized', 'Starts', 'Under Construction', 'Completions'])]
        merged_df = reduce(lambda left, right: pd.merge(left, right, on=['Year', 'Month'], how='outer'), df_list)
        merged_df = merged_df.sort_values(by=['Year', 'Month']).reset_index(drop=True)
        return cls(merged_df)
        
    @staticmethod
    def _process_df(xl: pd.ExcelFile) -> pd.DataFrame:
        if not 'Seasonally Adjusted' in xl.sheet_names:
            logger.error(f"Required tab not found in Excel file.\n{xl.sheet_names}")
            return None
        df = xl.parse(sheet_name='Seasonally Adjusted', header=5, usecols='A:B')        
        df = df.dropna(axis=0, how='any')
        df.columns = ['Date', 'Total']

        try:
            df['Date'] = pd.to_datetime(df['Date'])
        except ValueError:
            logger.exception(f"Error processing date column of dataframe.\n{df.head()}")
            return None
        
        df.insert(0, 'Month', df['Date'].dt.month)
        df.insert(0, 'Year', df['Date'].dt.year)
        df = df.drop(columns=['Date'])

        try:
            df = df.astype({'Year': 'Int64', 'Month': 'Int64', 'Total': 'Float64'})
        except ValueError:
            logger.exception(f"Unexpected data types in one or more columns.\n{df.head()}")
            return None

        return df