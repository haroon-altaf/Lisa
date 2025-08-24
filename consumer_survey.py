#%%
from __future__ import annotations  
import io
import logging                                                                              
import pandas as pd
from static import LOGGING_PARAMS, URL, MONTHS
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
class ConsumerSurvey:
    """
    A class to represent the US Michigan Consumer Survey data.

    Attributes:
        table: pd.DataFrame
        A Pandas DataFrame containing Year, Month, Index, Current Index, and Expected Index.
    
    Methods:
        download: Downloads the US Michigan Consumer Survey data; reads CSVs into DataFrames; returns a processed DataFrame.
        _process_df: Processes the raw DataFrames, merging them into one.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._table = data.copy(deep=True)

    @property
    def table(self) -> pd.DataFrame:
        return self._table.copy(deep=True)
    
    @classmethod
    def download(cls) -> ConsumerSurvey | None:
        
        # Fetch the US Michigan Consumer Index, and the Current and Expected Components
        with WebSession() as session:
            response_index = session.get(URL.US_CONS_INDEX.value)
            response_components = session.get(URL.US_CONS_COMP.value)
        if not all([response_index, response_components]):
            return None
        
        # Wrap response string in file-like object for read_csv
        df1 = pd.read_csv(io.StringIO(response_index.text), sep=",", skiprows=4)
        df2 = pd.read_csv(io.StringIO(response_components.text), sep=",", skiprows=4)
        data = cls._process_df(df1, df2)
        return None if data is None else cls(data)
    
    @staticmethod
    def _process_df(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:

        # Drop empty columns and rows; define column names and data types  
        df1 = df1.dropna(axis=1, how='all')
        df1 = df1.dropna(axis=0, how='all')
        if not df1.shape[1] == 3:
            logger.error(f"Unexpected number of columns in dataframe; strictly 3 expected.\n{df1.head()}")
            return None
        
        df2 = df2.dropna(axis=1, how='all')
        df2 = df2.dropna(axis=0, how='all')
        if not df2.shape[1] == 4:
            logger.error(f"Unexpected number of columns in dataframe; strictly 4 expected.\n{df2.head()}")
            return None
        
        df1.columns = ["Month", "Year", "Index"]
        df2.columns = ["Month", "Year", "Current Index", "Expected Index"]

        # Some months have "(P)" in the month column; remove it
        try:
            pattern = r'\s*\([A-z]\)\s*'
            df1["Month"] = df1["Month"].str.replace(pattern, "", regex=True)
            df2["Month"] = df2["Month"].str.replace(pattern, "", regex=True)
        except AttributeError:
            logger.exception(f"Unexpected data type in one or more Month columns.\n{df1.head()}\n{df2.head()}")
            return None
        
        # Map month names to month numbers
        try:
            df1['Month'] = df1['Month'].map(lambda x: MONTHS[x.upper().strip()])
            df2['Month'] = df2['Month'].map(lambda x: MONTHS[x.upper().strip()])
        except KeyError:
            logger.exception(f"Month name could not be converted to number for one or more columns.\n{df1.head()}\n{df2.head()}")
            return None

        # Convert data types
        try:
            df1 = df1.astype({"Month": 'Int64', "Year": 'Int64', "Index": 'Float64'})
            df2 = df2.astype({"Month": 'Int64', "Year": 'Int64', "Current Index": 'Float64', "Expected Index": 'Float64'})
        except ValueError:
            logger.exception(f"Unexpected data type in one or more columns.\n{df1.head()}\n{df2.head()}")
            return None

        # Merge the two dataframes and re-order columns
        df = df1.merge(df2)
        df = df[["Year", "Month", "Index", "Current Index", "Expected Index"]]
        
        return df