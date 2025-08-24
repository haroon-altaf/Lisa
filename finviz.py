#%%
from __future__ import annotations  
from bs4 import BeautifulSoup
import io
import logging     
import numpy as np                                                                                   
import pandas as pd
from static import LOGGING_PARAMS, URL, FINVIZ_PARAMS, GICS_MAP
from typing import List
from utility import WebSession

#%%
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(LOGGING_PARAMS['filepath'], mode='a')
file_handler.setFormatter(logging.Formatter(LOGGING_PARAMS['fileformatter']))
file_handler.setLevel(logging.WARNING)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOGGING_PARAMS['consoleformatter']))
console_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

#%%
class Finviz:
    """
    A class to provide class and static methods for obtaining Finviz data. 
    The FinvizScreener subclass represents the stock screener pages; the FinvizIndustries subclass represents the Finviz industry-level data.
    
    Methods:
        stock_description: Returns the description of a stock based on its ticker symbol.
        _process_df: Processes Pandas DataFrames containing data from Finviz.
        download_stocks: Downloads the stock screener data from Finviz and returns a processed DataFrame; handles pagination.
        download_industries: Downloads the industry-level data from Finviz and returns a processed DataFrame.
    """

    @staticmethod
    def stock_description(ticker: str) -> str:
        url = URL.FINVIZ_STOCK.value + f"?t={ticker}&p=d"

        response = WebSession().get(url)
        if not response:
            return None
   
        soup = BeautifulSoup(response.content, "html.parser")

        try:
            desc = soup.find('div', attrs={"class":"quote_profile-bio"}).get_text()
        except AttributeError:
            logger.exception(f"Failed to find description for ticker: {ticker}")
            return None
        
        return desc
    
    @staticmethod
    def _process_df(df: pd.DataFrame) -> pd.DataFrame:
        
        # Convert all columns to string
        df = df.astype('string')

        # Track df column names and name updates
        updated_cols = list(df.columns)

        #Drop duplicate rows
        df = df.drop_duplicates()

        # Define regex patterns
        suffix_pattern = r'(?<=\d\.\d{2})[MBK]'
        pct_pattern = r'(?<=\d\.\d{2})[%]'
        date_pattern = r'\d{1,2}/\d{1,2}/\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}'
        float_pattern = r'^\d+\.{1}\d+$'
        int_pattern = r'^\d+$'
        non_numeric_pattern = r'[^0-9eE\.\+\-]'
        empty_pattern = r'^(-)?$'

        # Detect cols with respective patterns
        suffix_cols = [c for c in df.columns if df[c].str.contains(suffix_pattern, regex=True, na=False).any()]
        pct_cols = [c for c in df.columns if df[c].str.contains(pct_pattern, regex=True, na=False).any()]
        date_cols = [c for c in df.columns if df[c].str.contains(date_pattern, regex=True, na=False).any()]
        float_cols = [c for c in df.columns if df[c].str.contains(float_pattern, regex=True, na=False).any()]
        int_cols = [c for c in df.columns if df[c].str.contains(int_pattern, regex=True, na=False).any()]

        # Treat each col with M/B/K suffixes
        for col in suffix_cols:

            # Get scale factor for conversion to millions
            arr = df[col].to_numpy().astype(str)
            scale = np.where(np.char.find(arr, 'B') != -1, 1000, np.where(np.char.find(arr, 'K') != -1, 0.001, 1))

            # Eliminate suffixes, empty strings, and "non-float characters"
            pattern = {suffix_pattern: '', non_numeric_pattern: '', empty_pattern: pd.NA}
            df[col] = df[col].replace(pattern, regex=True)

            # Convert to float and multiply by scale factor
            df[col] = df[col].astype('Float64') * scale

            # Adjust column names
            updated_cols[updated_cols.index(col)] = col + ' (m USD)'

        # Treat each col with % symbols
        for col in pct_cols:

            # Eliminate empty strings, and "non-float characters"
            pattern = {non_numeric_pattern: '', empty_pattern: pd.NA}
            df[col] = df[col].replace(pattern, regex=True)

            # Convert to float
            df[col] = df[col].astype('Float64')

            # Adjust column names
            if not "%" in col:
                if "Dividend.1" in col:
                    updated_cols[updated_cols.index(col)] = 'Dividend (%)'
                else:
                    updated_cols[updated_cols.index(col)] = col + ' (%)'

        # Treat each col wih dates
        for col in date_cols:
    
            # Eliminate /a and /b symbols; eliminate empty strings and hyphens
            pattern = {r'/[ab]': '', empty_pattern: pd.NA}
            df[col] = df[col].replace(pattern, regex=True)

            # Convert to datetime
            try:
                if col == "Earnings":
                    df[col] = pd.to_datetime(df[col] + f' {pd.Timestamp.today().year}', format='%b %d %Y').dt.strftime('%d/%m/%Y') # NOTE:Test Dec-Jan cases
                else:
                    df[col] = pd.to_datetime(df[col], format='%m/%d/%Y').dt.strftime('%d/%m/%Y')
            except ValueError:
                logger.warning(f"Failed to convert column to datetime; {col}")

        # Treat each col wih float types
        for col in float_cols:
    
            # Eliminate empty strings, and "non-float characters"
            pattern = {non_numeric_pattern: '', empty_pattern: pd.NA}
            df[col] = df[col].replace(pattern, regex=True)

            # Convert to float
            df[col] = df[col].astype('Float64')

        # Treat each col wih int types
        for col in int_cols:
    
            # Eliminate empty strings, and "non-int characters"
            pattern = {non_numeric_pattern: '', empty_pattern: pd.NA}
            df[col] = df[col].replace(pattern, regex=True)

            # Convert to float
            df[col] = df[col].astype('Int64')

        # Eliminate empty strings and hyphens from remaining (string type) columns
        pattern = {empty_pattern: pd.NA}
        df = df.replace(empty_pattern, regex=True)

        # Update column names
        df.columns = updated_cols

        return df

    @classmethod
    def download_stocks(
        cls,
        num_rows: int = FINVIZ_PARAMS['max_rows'],
        view_col_nums: List[int] = FINVIZ_PARAMS['screener_columns']
    ) -> FinvizSreener | None:
      
        # Set default values and check input types
        try:
            num_rows = int(num_rows)
            assert num_rows > 0
        except (ValueError, AssertionError):
            raise ValueError("Number of rows must be a positive integer.")
            
        try:
            view_col_nums = [int(i) for i in view_col_nums]
            assert len(view_col_nums) > 0
            assert min(view_col_nums) > 0
        except (ValueError, AssertionError):
            raise ValueError("Column numbers must be input as a list of positive integer(s).")
            
        # Define url for viewing all columns; all downloaded and later filtered to show only selected columns
        url = URL.FINVIZ_SCREEN.value + (',').join([str(i) for i in view_col_nums])

        # Fetch the Finviz Stock Screener data
        with WebSession() as session:
            df_list = []
            for count in range(1, num_rows, FINVIZ_PARAMS['rows_per_page']): 
                url = url + "&r=" + str(count)  # Finviz shows 20 rows per page; update url to navigate through pages 
                response = session.get(url)
                if not response:
                    break
                
                try:
                    df_i = pd.read_html(io.StringIO(response.text))[-2]
                except (ValueError, TypeError, pd.errors.ParserError):
                    logger.exception(f"Error in reading html table for Finviz stock screener: {url}")
                    break
                
                df_list.append(df_i)
                if len(df_i) < FINVIZ_PARAMS['rows_per_page']: 
                    break # Less than 20 rows in table indicate last page of the screener

        if not df_list:
            return None
        df = pd.concat(df_list, ignore_index=True)
        data = cls._process_df(df)
        data = data.iloc[:num_rows]
        return FinvizSreener(data)
    
    @classmethod
    def download_industries(cls) -> FinvizIndustries | None:

        url = URL.FINVIZ_INDU.value
        with WebSession() as session:
            response = session.get(url)
        if not response:
            return None

        try:
            df = pd.read_html(io.StringIO(response.text))[-2]
        except (ValueError, TypeError, pd.errors.ParserError):
            logger.exception(f"Error in reading html table for Finviz industries: {url}")
            return None
        
        data = cls._process_df(df)
        data = data.rename(columns={'Name': 'Industry'})
        GICS_MAP_INV = {industry: sector for sector, industries in GICS_MAP.items() for industry in industries}
        data.insert(1, "Sector", data['Industry'].map(GICS_MAP_INV))
        return FinvizIndustries(data)

class FinvizSreener(Finviz):
    """
    A class to represent the Finviz Stock Screener.

    Attributes:
        table: pd.DataFrame
        A Pandas DataFrame containing the stock screener data with various financial metrics.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._table = data.copy(deep=True)

    @property
    def table(self) -> pd.DataFrame:
        return self._table.copy(deep=True)
    
    
class FinvizIndustries(Finviz):
    """
    A class to represent the Finviz industries performance page.

    Attributes:
        table: pd.DataFrame
        A Pandas DataFrame containing the industry performance data.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._table = data.copy(deep=True)

    @property
    def table(self) -> pd.DataFrame:
        return self._table.copy(deep=True)