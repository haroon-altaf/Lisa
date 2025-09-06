from __future__ import annotations  
from functools import reduce
import io                                                                             
import pandas as pd
from static import DB_STRUCTURE, URL
from utility import WebSession, DBTransaction, TemplateLogger

logger = TemplateLogger(__name__).logger

class ConstructionSurvey:
    """
    A class to represent the US Census Bureau Construction Survey data.

    Attributes:
        table: pd.DataFrame
        A Pandas DataFrame containing Year, Month, Permits, Authorized, Starts, Under Construction, and Completions.

    Methods:
        download: Downloads the US Census Bureau Construction Survey data; reads Excel files into DataFrames; returns a processed DataFrame.
        load: Loads the US Census Bureau Construction Survey data into a database table.
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
            response_permit = session.get(URL.us_buil_permit)
            response_auth = session.get(URL.us_buil_auth)
            response_start = session.get(URL.us_buil_start)
            response_construct = session.get(URL.us_buil_construct)
            response_complete = session.get(URL.us_buil_complete)
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
    
    def load(self) -> None:
        column_map = DB_STRUCTURE[self.__class__.__name__]['table']['map']
        table_name = DB_STRUCTURE[self.__class__.__name__]['table']['name']
        df = self.table
        df_cols = df.columns

        new_cols = set(df_cols) - column_map.keys()
        if new_cols:
            raise ValueError(f"No column mapping exists for:\n{new_cols}")
        
        data_rows = df.rename(columns=column_map).to_dict(orient='records')
        with DBTransaction() as conn:
            conn.upsert_rows(table_name=table_name, data_rows=data_rows)
        
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
            df = df.astype({'Year': 'Int64', 'Month': 'Int64', 'Total': 'Int64'})
        except ValueError:
            logger.exception(f"Unexpected data types in one or more columns.\n{df.head()}")
            return None

        return df