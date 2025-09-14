from __future__ import annotations
from bs4 import BeautifulSoup
from common import WebSession, DBConnection, TemplateLogger
from database_model import Commodities as Commodities_Table, Stock_Indices, Bonds as Bonds_Table, Currencies as Currencies_Table, Crypto as Crypto_Table
import io                                                                          
import pandas as pd
import re
from typing import List, Dict
from .utils import set_private_attr, set_class_prop

URL_COMMODITIES = "https://tradingeconomics.com/commodities"
URL_STOCKS = "https://tradingeconomics.com/stocks"
URL_BONDS = "https://tradingeconomics.com/bonds"
URL_CURRENCIES = "https://tradingeconomics.com/currencies"
URL_CRYPTO = "https://tradingeconomics.com/crypto"

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
        data_dict = cls._main(url=URL_COMMODITIES)
        return Commodities(data_dict) if data_dict else None
    
    @classmethod
    def download_stocks(cls) -> Stocks | None:
        data_dict = cls._main(url=URL_STOCKS)
        return Stocks(data_dict) if data_dict else None
    
    @classmethod
    def download_bonds(cls) -> Bonds | None:
        data_dict = cls._main(url=URL_BONDS)
        return Bonds(data_dict) if data_dict else None
    
    @classmethod
    def download_currencies(cls) -> Currencies | None:
        data_dict = cls._main(url=URL_CURRENCIES)
        return Currencies(data_dict) if data_dict else None
    
    @classmethod
    def download_crypto(cls) -> Crypto | None:
        data_dict = cls._main(url=URL_CRYPTO)
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
        
        clean_dfs = [cls._clean_df(df) for df in dfs]
        if 'commodities' in url:
            clean_dfs = cls._split_units(clean_dfs, response.text)

        category_dict = {df.columns[0].lower().strip(): df for df in clean_dfs}
        category_dict['table'] = cls._combine_dfs(clean_dfs)

        return category_dict

    def load(self) -> None:
        if isinstance(self, Commodities):
            column_map = Commodities_Table.column_map()
            table_name = Commodities_Table.name()

        elif isinstance(self, Stocks):
            column_map = Stock_Indices.column_map()
            table_name = Stock_Indices.name()

        elif isinstance(self, Bonds):
            column_map = Bonds_Table.column_map()
            table_name = Bonds_Table.name()

        elif isinstance(self, Currencies):
            column_map = Currencies_Table.column_map()
            table_name = Currencies_Table.name()

        elif isinstance(self, Crypto):
            column_map = Crypto_Table.column_map()
            table_name = Crypto_Table.name()

        df = self.table
        df_cols = df.columns

        new_cols = set(df_cols) - column_map.keys()
        if new_cols:
            raise ValueError(f"No column mapping exists for:\n{new_cols}")
        
        data_rows = df.rename(columns=column_map).to_dict(orient='records')
        with DBConnection() as conn:
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
    def _split_units(df_list: List[pd.DataFrame], response_text: str) -> List[pd.DataFrame]:
        
        soup = BeautifulSoup(response_text, 'html.parser')
        rows = soup.find_all('tr')
        cells = [row.find_all('td') for row in rows]

        item_unit_pairs = [(cell[0].findChild('b').get_text().strip(), cell[0].findChild('div').get_text().strip()) for cell in cells if cell]
        items_map = {f'{item} {unit}': item for item, unit in item_unit_pairs}
        units_map = {f'{item} {unit}': unit for item, unit in item_unit_pairs}

        for df in df_list:
            items = df.iloc[:, 0].map(items_map)
            units = df.iloc[:, 0].map(units_map)
            df.iloc[:, 0] = items
            df.insert(1, "Unit", units)
            
        return df_list
    
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