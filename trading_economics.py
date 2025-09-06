from __future__ import annotations  
import io                                                                          
import pandas as pd
import re
from static import DB_STRUCTURE, URL
from typing import List, Dict
from utility import WebSession, DBTransaction, TemplateLogger, set_private_attr, set_class_prop

logger = TemplateLogger(__name__).logger

class TradingEconomics:
    """
    A class that holds methods for generating subclasses - each of which represents the data for a specific asset class.
    
    Methods:
        download_commodities: Fetches commodities data from Trading Economics and returns a Commodities object.
        download_stocks: Fetches stocks data from Trading Economics and returns a Stocks object.
        download_bonds: Fetches bonds data from Trading Economics and returns a Bonds object.
        download_currencies: Fetches currencies data from Trading Economics and returns a Currencies object.
        download_crypto: Fetches crypto data from Trading Economics and returns a Crypto object.
        _main: Sends GET request to Trading Economics; returns a dictionary of DataFrames using _clean_df and _split_units.
        load: Uploads data to the database.
        _clean_df: Returns a cleaned DataFrame.
        _split_units: For the "commodities" table which has units in the first column, it splits the units out into a separate column.
        _combine_dfs: Concatenates DataFrames.
        
    """   

    @classmethod
    def download_commodities(cls) -> Commodities | None:
        data_dict = cls._main(url=URL.commodities)
        return Commodities(data_dict) if data_dict else None
    
    @classmethod
    def download_stocks(cls) -> Stocks | None:
        data_dict = cls._main(url=URL.stocks)
        return Stocks(data_dict) if data_dict else None
    
    @classmethod
    def download_bonds(cls) -> Bonds | None:
        data_dict = cls._main(url=URL.bonds)
        return Bonds(data_dict) if data_dict else None
    
    @classmethod
    def download_currencies(cls) -> Currencies | None:
        data_dict = cls._main(url=URL.currencies)
        return Currencies(data_dict) if data_dict else None
    
    @classmethod
    def download_crypto(cls) -> Crypto | None:
        data_dict = cls._main(url=URL.crypto)
        return Crypto(data_dict) if data_dict else None

    @classmethod
    def _main(cls, url: str) -> Dict[str, pd.DataFrame] | None:
        with WebSession() as session:
            response = session.get(url)
        if not response:
            return None
        
        try:
            dfs = pd.read_html(io.StringIO(response.text))
        except (ValueError, TypeError, pd.errors.ParserError):
            logger.exception(f"Error in reading html tables for {url}")
            return None
        
        clean_dfs = []
        for df in dfs:
            cdf = cls._clean_df(df)
            if 'commodities' in url:
                cdf = cls._split_units(cdf)
            if cdf is None: return None
            clean_dfs.append(cdf)

        category_dict = {}
        for df in clean_dfs:
            category_name = df.columns[0].lower().strip()
            category_dict[category_name] = df
        category_dict['table'] = cls._combine_dfs(clean_dfs)

        return category_dict

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
            conn.upsert_rows(table_name=table_name, data_rows=data_rows, delete_first=True)

    @staticmethod
    def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Drop empty columns
        df = df.dropna(axis=1, how='all')

        # Eliminate %, $, commas, and M suffixes
        pattern = {r'[%,$]': '', r'(?<=[0-9])M': ''}
        df = df.replace(pattern, regex=True)

        # Drop Day column
        df = df.drop(columns=['Day'], errors='ignore')

        # Replace empty cells with NaN
        df = df.replace('', pd.NA)
        
        # Rename columns, ignored if column not present in DataFrame
        df = df.rename(columns={'%': 'Day %', 'Weekly': 'Weekly %', 'Monthly': 'Monthly %', 'YTD': 'YTD %', 
                                          'YoY': 'YoY %', 'MarketCap': 'Market Cap (m USD)'})
        
        # Convert columns to float or string
        for col in df.columns:
            try:
                df[col] = df[col].astype('Float64')
            except ValueError:
                df[col] = df[col].astype('string')
    
        return df
    
    @staticmethod
    def _split_units(df: pd.DataFrame) -> pd.DataFrame:
        
        pattern1 = r'([A-Za-z]{3}\s*/.+)'
        pattern2 = r'(Index )?Points$'
        pattern3 = r'(USD$|EUR$|GBP$)'
        
        df = df.copy()
        first_col = df.iloc[:, 0].astype('string')
        
        matches = first_col.apply(lambda x: re.search(f'{pattern1}|{pattern2}|{pattern3}', str(x)))
        units = matches.apply(lambda x: x.group(0) if x else pd.NA)
        if units.isna().all():
            logger.error("No units found in commodities table.")
            return None

        first_col = first_col.apply(lambda x: re.sub(f'{pattern1}|{pattern2}|{pattern3}', '', str(x)))
        df.iloc[:, 0] = first_col
        df.insert(1, "Unit", units)

        return df
    
    @staticmethod
    def _combine_dfs(df: List[pd.DataFrame]) -> pd.DataFrame:
        dfs = [df.copy() for df in df]

        # Add category column and rename first column
        for df in dfs:
            df.insert(1, 'Category', df.columns[0])
            df.columns = ['Item'] + list(df.columns[1:])

        # Concatenate DataFrames
        df_combined = pd.concat(dfs, axis=0, ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset=['Item'],keep='first', ignore_index=True)

        return df_combined 

class Commodities(TradingEconomics):
    """Represents commodities data from Trading Economics. Each attribute has a DataFrame as value, unpacked from a dictionary."""
    def __init__(self, data: Dict) -> None:
        set_private_attr(self, data)
        set_class_prop(self, data)

class Stocks(TradingEconomics):
    """Represents stocks data from Trading Economics. Each attribute has a DataFrame as value, unpacked from a dictionary."""
    def __init__(self, data: Dict) -> None:
        set_private_attr(self, data)
        set_class_prop(self, data)

class Bonds(TradingEconomics):
    """Represents bonds data from Trading Economics. Each attribute has a DataFrame as value, unpacked from a dictionary."""
    def __init__(self, data: Dict) -> None:
        set_private_attr(self, data)
        set_class_prop(self, data)

class Currencies(TradingEconomics):
    """Represents currencies data from Trading Economics. Each attribute has a DataFrame as value, unpacked from a dictionary."""
    def __init__(self, data: Dict) -> None:
        set_private_attr(self, data)
        set_class_prop(self, data)

class Crypto(TradingEconomics):
    """Represents crypto data from Trading Economics. Each attribute has a DataFrame as value, unpacked from a dictionary."""
    def __init__(self, data: Dict) -> None:
        set_private_attr(self, data)
        set_class_prop(self, data)