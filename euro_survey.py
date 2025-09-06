from __future__ import annotations  
from bs4 import BeautifulSoup
import io 
import numpy as np                                                                                   
import pandas as pd
from static import DB_STRUCTURE, URL
from utility import WebSession, DBTransaction, TemplateLogger
import zipfile

logger = TemplateLogger(__name__).logger

class EuroSurvey:
    """
    A class to represent the EU Economic Survey data.
    
    Attributes:
        table: pd.DataFrame
        A Pandas DataFrame containing Year, Month, and various economic indicators per country.
    
    Methods:
        download: Downloads the EU Economic Survey data; reads the Excel file into a DataFrame; returns a processed DataFrame.
        load: Loads the EU Economic Survey data into a database table.
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
        url = URL.euro
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