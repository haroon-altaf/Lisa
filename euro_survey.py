#%%
from __future__ import annotations  
from bs4 import BeautifulSoup
import io
import logging    
import numpy as np                                                                                   
import pandas as pd
from static import LOGGING_PARAMS, URL
from utility import WebSession
import zipfile

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
class EuroSurvey:
    """
    A class to represent the EU Economic Survey data.
    
    Attributes:
        table: pd.DataFrame
        A Pandas DataFrame containing Year, Month, and various economic indicators per country.
    
    Methods:
        download: Downloads the EU Economic Survey data; reads the Excel file into a DataFrame; returns a processed DataFrame.
        _process_df: Processes the raw DataFrame, adding Year and Month columns.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._table = data.copy(deep=True)

    @property
    def table(self) -> pd.DataFrame:
        return self._table.copy(deep=True)
    
    @classmethod
    def download(cls) -> EuroSurvey | None:
        
        # Fetch the EU Economic Survey data
        url = URL.EURO.value
        with WebSession() as session:
            response = session.get(url)
            if not response:
                return None
            
            try:
                soup = BeautifulSoup(response.content, "html.parser")
                file_link = soup.find('td').find_next_sibling().find().get('href')
            except AttributeError:
                logger.exception(f"Error in finding Excel file link from: {url}")
                return None
            
            response = session.get(file_link)
            if not response:
                return None
        
        # Wrap response content in file-like object to extract from zip file and process the excel file
        try:
            zip_bytes = io.BytesIO(response.content)   
            with zipfile.ZipFile(zip_bytes) as z:
                file = z.filelist[0]
                with z.open(file) as f:
                    df = pd.read_excel(f, sheet_name=2)
        except Exception:
            logger.exception(f"Error opening or reading Excel file from: {response.url}")
            return None

        data = cls._process_df(df)

        return cls(data) if data is not None else None
        
    @staticmethod
    def _process_df(df: pd.DataFrame) -> pd.DataFrame:
        
        # Rename first column to Date
        df.columns.values[0] = "Date"

        # Add year and month columns
        try:
            df.insert(1, "Year", df["Date"].dt.year)
            df["Year"] = df["Year"].astype('Int64')
            df.insert(2, "Month", df["Date"].dt.month)
            df["Month"] = df["Month"].astype('Int64')
        except AttributeError:
            logger.exception(f"Error processing date column of dataframe.\n{df.head()}")
            return None

        # Drop "unnamed" and "date" columns
        df = df.loc[:, ~df.columns.str.contains('unnamed', case=False)]
        df = df.drop(columns=["Date"])

        # Set all numerical columns to float type; replacing np.nan with pd.NA just for consistency
        [df[c].astype('Float64') for c in df.columns if c not in ['Year', 'Month']]
        df = df.replace(np.nan, pd.NA)

        return df