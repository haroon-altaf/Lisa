from __future__ import annotations  
from bs4 import BeautifulSoup
import io    
import numpy as np                                                                                   
import pandas as pd
from static import DB_STRUCTURE, URL, FINVIZ_CONST
import sqlalchemy as db
from sqlalchemy import select, update, case, delete, exists
from typing import List, Dict
from utility import WebSession, DBTransaction, TemplateLogger

logger = TemplateLogger(__name__).logger

class Finviz:
    """
    A class to provide class and static methods for obtaining Finviz data. 
    The FinvizScreener subclass represents the stock screener pages; the FinvizIndustries subclass represents the Finviz industry-level data.
    
    Methods:
        download_stocks: Downloads the stock screener data from Finviz and returns a processed DataFrame; handles pagination.
        download_industries: Downloads the industry-level data from Finviz and returns a processed DataFrame.
        load: Uploads Finviz stocks and industries data to the database.
        _process_df: Processes Pandas DataFrames containing data from Finviz.
        _get_GICS_groups: Retrieves the GICS sector and industry information from the database.
        _validate_incoming_GICS: Checks whether incoming sector-industry mappings match those in the database.
        stock_description: Returns the description of a stock based on its ticker symbol.
    """
    @classmethod
    def download_stocks(
        cls,
        num_rows: int = FINVIZ_CONST.max_rows,
        view_col_nums: List[int] = FINVIZ_CONST.screener_columns
    ) -> FinvizScreener | None:
      
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
        url = URL.finviz_screen + (',').join([str(i) for i in view_col_nums])

        # Fetch the Finviz Stock Screener data
        with WebSession() as session:
            df_list = []
            custom_na_values = pd._libs.parsers.STR_NA_VALUES.copy()
            custom_na_values.discard('NA')
            for count in range(1, num_rows, FINVIZ_CONST.rows_per_page): 
                url = url + "&r=" + str(count)  # Finviz shows 20 rows per page; update url to navigate through pages 
                response = session.get(url)
                if not response:
                    break
                
                try:
                    df_i = pd.read_html(io.StringIO(response.text), keep_default_na=False, na_values=custom_na_values)[-2]
                except (ValueError, TypeError, pd.errors.ParserError):
                    logger.exception(f"Error in reading html table for Finviz stock screener: {url}")
                    break
                
                df_list.append(df_i)
                if len(df_i) < FINVIZ_CONST.rows_per_page: 
                    break # Less than 20 rows in table indicate last page of the screener

        if not df_list:
            return None
        df = pd.concat(df_list, ignore_index=True)
        data = cls._process_df(df)
        data = data.iloc[:num_rows]
        return FinvizScreener(data)
    
    @classmethod
    def download_industries(cls) -> FinvizIndustries | None:

        url = URL.finviz_indu
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

        return FinvizIndustries(data)
    
    def load(self) -> None:
        column_map = DB_STRUCTURE[self.__class__.__name__]['table']['map']
        table_name = DB_STRUCTURE[self.__class__.__name__]['table']['name']
        df = self._prep_table()
        df_cols = df.columns

        new_cols = set(df_cols) - column_map.keys()
        if new_cols:
            raise ValueError(f"No column mapping exists for:\n{new_cols}")
        
        data_rows = df.rename(columns=column_map).to_dict(orient='records')
        with DBTransaction() as conn:
            conn.upsert_rows(table_name=table_name, data_rows=data_rows, delete_first=True)
            
    def _prep_table(self) -> pd.DataFrame:
        df = self.table.copy()
        GICS_map = self._get_GICS_groups()
        self._validate_incoming_GICS(df, GICS_map)
        if 'Industry' in df.columns:
            df['Industry'] = df['Industry'].map({ind: d['id'] for ind, d in GICS_map.items()})
        if 'Sector' in df.columns:
            df['Sector'] = df['Sector'].map({d['sector']: d['sector_id'] for d in GICS_map.values()})
        return df
    
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
    
    @staticmethod
    def _get_GICS_groups() -> Dict[str, Dict[str, str | int]]:
        with DBTransaction() as conn:
            industries_table = db.Table('GICS_Industries', conn._metadata, autoload_with=conn._engine)
            sectors_table = db.Table('GICS_Sectors', conn._metadata, autoload_with=conn._engine)
            stmt = select(industries_table, sectors_table.columns.sector)\
                .join(sectors_table, industries_table.columns.sector_id == sectors_table.columns.id)
            result = conn._connection.execute(stmt).fetchall()

        return {ind: {'id': ind_id, 'sector': sec, 'sector_id': sec_id} for (ind_id, ind, sec_id, sec) in result}
    
    @staticmethod
    def _validate_incoming_GICS(df: pd.DataFrame, GICS_map: Dict[str, Dict[str, str | int]]) -> None:
        
        new_industries = set(df['Industry']) - set(GICS_map.keys())
        if new_industries:
            raise KeyError(f"These industries are not in the database:\n{sorted(list(new_industries))}")
            
        if 'Sector' in df.columns:
            new_sectors = set(df['Sector']) - set(d['sector'] for d in GICS_map.values())
            if new_sectors:
                raise KeyError(f"These sectors are not in the database:\n{sorted(list(new_sectors))}")

            industries_sector_map = {ind: d['sector'] for ind, d in GICS_map.items()}
            matches = (df['Industry'].str.strip().map(industries_sector_map) == df['Sector'].str.strip()).fillna(False)
            if not matches.all():
                mismatches = df[~matches][['Industry', 'Sector']].drop_duplicates()
                raise ValueError(f"Received industry-sectors mapping does not match mapping in database:\n{mismatches}")

class FinvizScreener(Finviz):
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
    
    @classmethod
    def load_stock_descriptions(cls) -> None:
        with DBTransaction() as conn:
            # Create table objects
            table = DB_STRUCTURE[cls.__name__]['table']['name']
            finviz_stocks = db.Table(table, conn._metadata, autoload_with=conn._engine)
            table_desc = DB_STRUCTURE[cls.__name__]['table_description']['name']
            stocks_desc = db.Table(table_desc, conn._metadata, autoload_with=conn._engine)

            # Delete orphan rows (tickers) from description table that are not in stocks table
            delete_stmt = (
                delete(stocks_desc)
                .where(~exists().where(finviz_stocks.c.ticker == stocks_desc.c.ticker))
            )
            conn._connection.execute(delete_stmt)

            # Add rows (tickers) from stocks table that are not in description table
            insert_stmt = stocks_desc.insert().from_select(
                [stocks_desc.c.ticker],
                select(finviz_stocks.c.ticker).where(
                    ~exists().where(stocks_desc.c.ticker == finviz_stocks.c.ticker)
                )
            )
            conn._connection.execute(insert_stmt)
            
            # Find tickers with missing descriptions (NULL)
            select_stmt = select(stocks_desc.columns.ticker).where(stocks_desc.columns.description.is_(None))
            result = conn._connection.execute(select_stmt).fetchall()
            null_description_tickers = [ticker for ticker, *_ in result]

            # Download and update missing descriptions
            if null_description_tickers:
                ticker_desc_map = cls.stock_description(null_description_tickers)
                if not ticker_desc_map:
                    return
                case_stmt = case(ticker_desc_map, value=stocks_desc.c.ticker)
                stmt = update(stocks_desc).where(stocks_desc.c.ticker.in_(ticker_desc_map.keys())).values(description=case_stmt)
                conn._connection.execute(stmt)

    @staticmethod
    def stock_description(tickers: List[str]) -> Dict[str, str | None]:
        
        result = {}
        with WebSession() as session:
            for ticker in tickers:
                url = URL.finviz_stock + f"?t={ticker}&p=d"
                response = session.get(url)
                if not response:
                    continue
                
                soup = BeautifulSoup(response.content, "html.parser")
                try:
                    desc = soup.find('div', attrs={"class":"quote_profile-bio"}).get_text()
                except AttributeError:
                    logger.warning(f"Failed to find description for ticker: {ticker}")
                    continue

                result[ticker] = desc
        
        return result
    
    
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