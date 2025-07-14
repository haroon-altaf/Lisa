#%%
from __future__ import annotations  
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet
from collections import namedtuple
from datetime import datetime
from enum import Enum, IntEnum
from functools import reduce
import io
from loggers import web_scraping_logger      
import numpy as np                                                                                   
import pandas as pd
import re
from static import Man_Pmi_Structure, Serv_Pmi_Structure, GICS_sector_industry_map, Ism_Man_Sectors, Ism_Serv_Sectors
from typing import List, Dict, NamedTuple, Tuple
from utility import find_content, p_to_str, custom_table_to_df, WebSession
import zipfile

class MONTHS(IntEnum):
    JANUARY, JAN = 1, 1
    FEBRUARY, FEB = 2, 2
    MARCH, MAR = 3, 3
    APRIL, APR = 4, 4
    MAY = 5
    JUNE, JUN = 6, 6
    JULY, JUL = 7, 7
    AUGUST, AUG = 8, 8
    SEPTEMBER, SEP = 9, 9
    OCTOBER, OCT = 10, 10    
    NOVEMBER, NOV = 11, 11
    DECEMBER, DEC = 12, 12

class Url(Enum):
    US_MAN_PMI = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/pmi/"
    US_SER_PMI = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/services/"
    US_CONS_INDEX = "https://www.sca.isr.umich.edu/files/tbcics.csv"
    US_CONS_COMP = "https://www.sca.isr.umich.edu/files/tbciccice.csv"
    US_BUIL_PERMIT = "https://www.census.gov/construction/nrc/xls/permits_cust.xlsx"
    US_BUIL_AUTH = "https://www.census.gov/construction/nrc/xls/authnot_cust.xlsx"
    US_BUIL_START = "https://www.census.gov/construction/nrc/xls/starts_cust.xlsx"
    US_BUIL_CONSTRUCT = "https://www.census.gov/construction/nrc/xls/under_cust.xlsx"
    US_BUIL_COMPLETE = "https://www.census.gov/construction/nrc/xls/comps_cust.xlsx"
    EURO = "https://economy-finance.ec.europa.eu/economic-forecast-and-surveys/business-and-consumer-surveys/download-business-and-consumer-survey-data/time-series_en"
    CAIXIN_MAN_PMI = "https://tradingeconomics.com/china/manufacturing-pmi"
    CAIXIN_SER_PMI = "https://tradingeconomics.com/china/services-pmi"
    FINVIZ_SCREEN = "https://finviz.com/screener.ashx?v=151&f=ind_stocksonly&o=ticker&c="
    FINVIZ_INDU = "https://finviz.com/groups.ashx?g=industry&v=152&o=name&c=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26"
    COMMODITIES = "https://tradingeconomics.com/commodities"
    STOCKS = "https://tradingeconomics.com/stocks"
    BONDS = "https://tradingeconomics.com/bonds"
    CURRENCIES = "https://tradingeconomics.com/currencies"
    CRYPTO = "https://tradingeconomics.com/crypto"

#%%
class IsmReport:
    """ 
    Parent class for the ManufacturingPmi and ServicesPmi classes.
    Methods that are common to  both ManufacturingPmi and ServicesPmi are defined here.
    
    Attributes:
        _report_type: str
        The type of report to be downloaded ('m' for Manufacturing report and 's' for Services report).

    Methods:
        manufacturing: Calls the _main method and constructs a ManufacturingPmi object from the returned NamedTuple.
        services: Calls the _main method and constructs a ServicesPmi object from the returned NamedTuple.
        _main: Determines the report url; calls the _parse_html method _transform_sections method to extract report setions.
        _parse_html: Parses and extracts relevant report sections from webpage HTML.
        _transform_sections: Transforms extracted HTML content into strings (text) and Pandas DataFrames (tables); derives "rankings" and "comments".
        _rankings: Ranks the industry sectors based on their growth/contraction.
        _respondents_say: Extracts comments from respondents and stores them in a Pandas DataFrame.
    """

    @classmethod
    def download_manufacturing(cls, url: str | None = None) -> ManufacturingPmi | None:
        cls._report_type = 'm'
        sections_nt = cls._main(url)
        if sections_nt:
            return ManufacturingPmi(sections_nt)
        else:
            return None
    
    @classmethod
    def download_services(cls, url: str | None = None) -> ServicesPmi | None:
        cls._report_type = 's'
        sections_nt = cls._main(url)
        if sections_nt:
            return ServicesPmi(sections_nt)
        else:
            return None

    @classmethod
    def _main(cls, url: str | None = None) -> NamedTuple | None:
        """
        Extracts HTML content for each report section, transforms them into text and tables, and stores them in a NamedTuple.
        
        Args:
            url: str | None
            The url of the webpage from which the report is obtained. By default, the latest report is downloaded.
        
        Returns:
            sections_nt: NamedTuple | None
            A NamedTuple containing report sections. None is returned in case of an error.
        """

        if not url:
            base_url = Url.US_MAN_PMI.value if cls._report_type == 'm' else Url.US_SER_PMI.value
            prev_month = datetime.now().month - 1

            for i in range(3):
                month = datetime(1900, prev_month - i, 1).strftime("%B").lower()
                url = f"{base_url}{month}/"
                
                with WebSession() as session:
                    response = session.get(url)

                if response:
                    break
        else:
            try:
                assert type(url) == str
                with WebSession() as session:
                    response = session.get(url)
            except AssertionError:
                raise TypeError("URL must be a string.")

        try:
            assert response
            html_content = response.text
            html_sections = cls._parse_html(html_content)
            sections = cls._transform_sections(html_sections)
            sections_nt = namedtuple('sections', sections.keys())(**sections)
            return sections_nt
        
        except Exception as e:
            web_scraping_logger.exception(f"\n\nFailed to fetch the ISM report from: {url}\nError: {e}")
            return None

    @classmethod
    def _parse_html(cls, html_content: str) -> Dict[str, Tag | ResultSet | None]:
        """
        Parses the webpage HTML using BeautifulSoup. Extracts and stores the HTML of relevant sections in a dictionary.
        The relevant sections and how to locate them in the HTML structure are defined in the "static" module.
        
        Args:
            html_content: str
            The HTML of the webpage as text.

        Returns:
            html_sections: Dict[str, Tag | ResultSet | None]
            A dictionary containing the BeautifulSoup objects for relevant report sections.
        """

        soup = BeautifulSoup(html_content, 'html.parser')
        html_sections = {}

        scheme = Man_Pmi_Structure if cls._report_type == 'm' else Serv_Pmi_Structure

        for section_name, search_formula in scheme.items():
                search_tag = search_formula['tag']
                search_attrs = search_formula['attrs']
                search_methods = search_formula['methods']

                try:
                    section_content = find_content(soup, search_tag, search_attrs, search_methods)
                    assert type(section_content) in [Tag, ResultSet]
                except AssertionError:
                    web_scraping_logger.exception(f"\n\nUnexpected content retrieved for '{section_name}' using provided search parameters.\nContent: {section_content}")
                    html_sections[section_name] = None
                else:
                    html_sections[section_name] = section_content

        return html_sections

    @classmethod
    def _transform_sections(cls, html_sections: Dict[str, Tag | ResultSet | None]) -> Dict[str, str | List[pd.DataFrame] | None]:
        """
        Converts <p> tags to text and <table> tags to Pandas DataFrames, and stores the results in a dictionary.
        
        Args:
            html_sections: Dict[str, Tag | ResultSet | None]
            A dictionary containing the BeautifulSoup objects of the relevant report sections.

        Returns:
            transformed_sections: Dict[str, str | List[pd.DataFrame] | None]
            A dictionary containing the content of relevant report sections in string or Pandas DataFrame formats.
        """

        transformed_sections = {}

        for key, value in html_sections.items():
            if not value:
                transformed_sections[key] = None
                continue
            
            try:
                if 'table' in key:
                    #df_list = custom_table_to_df(value)

                    # Some table processing steps based on key (report section) name
                    if key == 'full_pmi_table':
                        df_list = custom_table_to_df(value)
                        df = df_list[0]

                    elif key == 'buying_policy_table':
                        df_list = pd.read_html(io.StringIO(str(value)))
                        for df in df_list:
                            category_name = df.columns[0]
                            dates = pd.to_datetime(df.iloc[:, 0], format='%b %Y')
                            df.insert(0, 'Category', df.columns[0])
                            df.insert(0, 'Month', dates.dt.month)
                            df.insert(0, 'Year', dates.dt.year)
                        df = pd.concat(df_list)
                        df = df.dropna(axis=1, how ='any')

                    else:
                        df_list = pd.read_html(io.StringIO(str(value)))
                        for df in df_list:
                            dates = pd.to_datetime(df.iloc[:, 0], format='%b %Y')
                            df.insert(0, 'Month', dates.dt.month)
                            df.insert(0, 'Year', dates.dt.year)
                        df = pd.concat(df_list)                  
                    
                    transformed_sections[key] = df

                else:
                    transformed_sections[key] = p_to_str(value)

            except Exception as e:
                web_scraping_logger.exception(f"\n\nFailed to transform report section: {key}\nError: {e}")
                transformed_sections[key] = None
        
        rank_by = 'new_orders_text' if cls._report_type == 'm' else 'business_activity_text'
        if 'overview' in transformed_sections and rank_by in transformed_sections:
            transformed_sections['industry_rankings'] = cls._rankings(transformed_sections['overview'], transformed_sections[rank_by])
        else:
            transformed_sections['industry_rankings'] = None
        
        if 'comments' in transformed_sections:
            transformed_sections['respondents'] = cls._respondents_say(transformed_sections['comments'])
        else:
            transformed_sections['respondents'] = None

        return transformed_sections
    
    @classmethod
    def _rankings(cls, overview: str, new_orders_text: str) -> pd.DataFrame | None:
        """
        Ranks industry sectors based on the growth/contraction in the PMI and "New Orders" (for manufacturing) or "Business Activity" (for services).
        
        Args:
            overview: str
            Text from report overview section, containing a list of growing/contracting sectors.
            
            rank_by: str
            Text from "New Orders" or "Business Activity" sections, containing a list of growing/contracting sectors.
        
        Returns:
            df: pd.DataFrame | None
            A Pandas DataFrame containing the PMI and new-orders/business-activity rankings for each sector.
        """

        if cls._report_type == 'm':
            sectors = Ism_Man_Sectors
            col_name = "New Orders Rankings"
        else:
            sectors = Ism_Serv_Sectors
            col_name = "Business Activity Rankings"

        # Initiate empty dataframe with sectors as index
        df = pd.DataFrame({"Sectors": sectors, "PMI Rankings": [0] * len(sectors), f"{col_name}": [0] * len(sectors)}).set_index('Sectors')

        try:
            # Get list of growing and contracting sectors (overall)
            txt = overview.split('\n')[-1]
            lines = txt.split('.')

            growth_sectors = lines[0].split(':')[1].split(';')
            growth_sectors[-1] = growth_sectors[-1].replace("and ","")

            contract_sectors = lines[1].split(':')[1].split(';')
            contract_sectors[-1] = contract_sectors[-1].replace("and ","")

            # Rank sectors (overall)
            for index, item in enumerate(growth_sectors):
                df.loc[item, "PMI Rankings"] = len(growth_sectors) - index

            for index, item in enumerate(contract_sectors):
                df.loc[item, "PMI Rankings"] = -(len(contract_sectors) - index)

            # Get list of growing and contracting sectors (based on New Orders or Business Activity)
            txt = new_orders_text.split('\n')[-1]
            lines = txt.split('.')

            growth_sectors = lines[0].split(':')[1].split(';')
            growth_sectors[-1] = growth_sectors[-1].replace("and ","")

            contract_sectors = lines[1].split(':')[1].split(';')
            contract_sectors[-1] = contract_sectors[-1].replace("and ","")

            # Rank sectors (based on New Orders or Business Activity)
            for index, item in enumerate(growth_sectors):
                df.loc[item, col_name] = len(growth_sectors) - index

            for index, item in enumerate(contract_sectors):
                df.loc[item, col_name] = -(len(contract_sectors) - index)

            return df

        except Exception as e:
            web_scraping_logger.exception(f"\n\nFailed to rank sectors\nError: {e}")
            return None
    
    @classmethod
    def _respondents_say(cls, comments: str) -> pd.DataFrame | None:  
        """
        Extracts the respondent comments for different sectors and stores them in a Pandas DataFrame.
        
        Args:
            comments: str
            The text under the "respondents say" section which contains a list of comments.

        Returns:
            df: pd.DataFrame | None
            A Pandas DataFrame containing the respondents' comments for different sectors.
        """

        sectors = Ism_Man_Sectors if cls._report_type == 'm' else Ism_Serv_Sectors

        # Initiate empty dataframe with sectors as index
        df = pd.DataFrame({"Sectors": sectors, "Respondent Comments": [''] * len(sectors)}).set_index('Sectors')

        try:
            # Split comments block into sentences
            txt = comments.split('\n')[1:-1]

            # For each comment, extract the sector and quote; store in dataframe
            for comment in txt:
                quote, sector = comment.split('[')
                quote = quote[1:-2]
                sector = sector[:-1]
                df.loc[sector, "Respondent Comments"] = quote

            return df

        except Exception as e:
            web_scraping_logger.exception(f"\n\nFailed to extract respondent comments\nError: {e}")
            return None

class ManufacturingPmi(IsmReport):
    """ Represents a Manufacturing PMI report from ISM.
        Each section of the report is unpacked from a NamedTuple and stored as a private attribute.
        Each private attribute is then exposed to public using class properties (@property).
    """

    def __init__(self, sections: NamedTuple) -> None:
        
        sections_dict = sections._asdict()

        # Set private attributes
        for field_name, field_value in sections_dict.items():
            setattr(self, f'_{field_name}', field_value)

        # Set properties for public access
        for field_name in sections_dict.keys():
            get_fn = lambda self, field_name=field_name: getattr(self, f'_{field_name}')
            setattr(self.__class__, field_name, property(get_fn))

class ServicesPmi(IsmReport):
    """ Represents a Services PMI report from ISM.
        Each section of the report is unpacked from a NamedTuple and stored as a private attribute.
        Each private attribute is then exposed to public using class properties (@property).
    """

    def __init__(self, sections: NamedTuple) -> None:
        
        sections_dict = sections._asdict()

        # Set private attributes
        for field_name, field_value in sections_dict.items():
            setattr(self, f'_{field_name}', field_value)

        # Set properties for public access
        for field_name in sections_dict.keys():
            get_fn = lambda self, field_name=field_name: getattr(self, f'_{field_name}')
            setattr(self.__class__, field_name, property(get_fn))

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
            response_index = session.get(Url.US_CONS_INDEX.value)
            response_components = session.get(Url.US_CONS_COMP.value)
        
        try:
            assert response_index
            assert response_components
            # Wrap response string in file-like object for read_csv
            df1 = pd.read_csv(io.StringIO(response_index.text), sep=",", skiprows=4)
            df2 = pd.read_csv(io.StringIO(response_components.text), sep=",", skiprows=4)
            data = cls._process_df(df1, df2)

            return cls(data)
        
        except Exception as e:
            web_scraping_logger.exception(f'\n\nFailed to fetch the Consumer Survey data.\nError: {e}')
            return None
    
    @staticmethod
    def _process_df(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:

        # Drop empty columns and rows; define column names and data types
        df1 = df1.dropna(axis=1, how='all')
        df1 = df1.dropna(axis=0, how='all')
        df1.columns = ["Month", "Year", "Index"]
        
        df2 = df2.dropna(axis=1, how='all')
        df2 = df2.dropna(axis=0, how='all')
        df2.columns = ["Month", "Year", "Current Index", "Expected Index"]

        # Some months have "(P)" in the month column; remove it
        pattern = r'\s*\([A-z]\)\s*'
        df1["Month"] = df1["Month"].str.replace(pattern, "", regex=True)
        df2["Month"] = df2["Month"].str.replace(pattern, "", regex=True)

        # Map month names to month numbers
        df1['Month'] = df1['Month'].map(lambda x: MONTHS[x.upper()])
        df2['Month'] = df2['Month'].map(lambda x: MONTHS[x.upper()])

        # Convert data types
        df1 = df1.astype({"Month": 'Int64', "Year": 'Int64', "Index": 'Float64'})
        df2 = df2.astype({"Month": 'Int64', "Year": 'Int64', "Current Index": 'Float64', "Expected Index": 'Float64'})

        # Merge the two dataframes and re-order columns
        df = df1.merge(df2)
        df = df[["Year", "Month", "Index", "Current Index", "Expected Index"]]
        
        return df

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
            response_permit = session.get(Url.US_BUIL_PERMIT.value)
            response_auth = session.get(Url.US_BUIL_AUTH.value)
            response_start = session.get(Url.US_BUIL_START.value)
            response_construct = session.get(Url.US_BUIL_CONSTRUCT.value)
            response_complete = session.get(Url.US_BUIL_COMPLETE.value)

        try:
            assert response_permit
            assert response_auth
            assert response_start
            assert response_construct
            assert response_complete

            response_list = [response_permit, response_auth, response_start, response_construct, response_complete]
            xl_list = [pd.ExcelFile(io.BytesIO(response.content)) for response in response_list]
            df_list = [cls._process_df(xl) for xl in xl_list]
            
            df_list = [df.rename(columns={'Total': f'Total_{i+1}'}) for i, df in enumerate(df_list)]
            merged_df = reduce(lambda left, right: pd.merge(left, right, on=['Year', 'Month'], how='outer'), df_list)
            merged_df.columns = ['Year', 'Month', 'Permits', 'Authorized', 'Starts', 'Under Construction', 'Completions']
            merged_df = merged_df.sort_values(by=['Year', 'Month']).reset_index(drop=True)
            
            return cls(merged_df)
        
        except Exception as e:
            web_scraping_logger.exception(f"\n\nFailed to fetch the Construction Survey data.\nError: {e}")
            return None
        
    @staticmethod
    def _process_df(xl: pd.ExcelFile) -> pd.DataFrame:
        df = xl.parse(sheet_name='Seasonally Adjusted', header=5, usecols='A:B')
        df = df.dropna(axis=0, how='any')
        df.columns = ['Date', 'Total']
        df['Date'] = pd.to_datetime(df['Date'])
        df.insert(0, 'Month', df['Date'].dt.month)
        df.insert(0, 'Year', df['Date'].dt.year)
        df = df.drop(columns=['Date'])
        df = df.astype({'Year': 'Int64', 'Month': 'Int64', 'Total': 'Float64'})

        return df
    
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
        url = Url.EURO.value
        try:
            with WebSession() as session:
                response = session.get(url)
                assert response
                soup = BeautifulSoup(response.content, "html.parser")
                file_link = soup.find('td').find_next_sibling().find().get('href')
                response = session.get(file_link)
            
            assert response
            
            # Wrap response content in file-like object to extract from zip file and process the excel file
            zip_bytes = io.BytesIO(response.content)   
            with zipfile.ZipFile(zip_bytes) as z:
                file = z.filelist[0]
                with z.open(file) as f:
                    df = pd.read_excel(f, sheet_name=2)

            data = cls._process_df(df)

            return cls(data)
        
        except Exception as e:
            web_scraping_logger.exception(f"\n\nFailed to fetch the EU Economic Survey data from:{url}\nError: {e}")
            return None
        
    @staticmethod
    def _process_df(df: pd.DataFrame) -> pd.DataFrame:
        
        # Rename first column to Date
        df.columns.values[0] = "Date"

        # Add year and month columns
        df.insert(1, "Year", df["Date"].dt.year)
        df["Year"] = df["Year"].astype('Int64')

        df.insert(2, "Month", df["Date"].dt.month)
        df["Month"] = df["Month"].astype('Int64')

        # Drop "unnamed" and "date" columns
        df = df.loc[:, ~df.columns.str.contains('unnamed', case=False)]
        df = df.drop(columns=["Date"])

        # Set all numerical columns to float type; replacing np.nan with pd.NA just for consistency
        [df[c].astype('Float64') for c in df.columns if c not in ['Year', 'Month']]
        df = df.replace(np.nan, pd.NA)

        return df

#%%
class CaixinPmi:
    """
    A class to represent the Caixin Manufacturing and Services PMI data from Trading Economics.
    
    Attributes:
        _manufacturing_table: pd.DataFrame
        A Pandas DataFrame containing the Caixin Manufacturing PMI data.
        
        _services_table: pd.DataFrame
        A Pandas DataFrame containing the Caixin Services PMI data.
    
    Methods:
        download: Overarching method exposed to public; obatins outputs from _main and calls __init__.
        _main: Downloads the Manufacturing and Services PMI data from Trading Economics.
        _parse_text: Parses webpage text to extract PMI index, month, and year.
    """

    def __init__(self, man_data: pd.DataFrame, ser_data: pd.DataFrame) -> None:
        self._manufacturing_table = man_data.copy(deep=True)
        self._services_table = ser_data.copy(deep=True)

    @property
    def manufacturing_table(self) -> pd.DataFrame:
        return self._manufacturing_table.copy(deep=True)
    
    @property
    def services_table(self) -> pd.DataFrame:
        return self._services_table.copy(deep=True)
    
    @classmethod
    def download(cls) -> CaixinPmi | None:
       man_data, ser_data = [cls._main(url) for url in [Url.CAIXIN_MAN_PMI.value, Url.CAIXIN_SER_PMI.value]]
       if man_data is not None and ser_data is not None:
           return cls(man_data, ser_data)
       else:
           return None
    
    @classmethod
    def _main(cls, url: str) -> pd.DataFrame | None:
        
        with WebSession() as session:
            response = session.get(url)

        try:
            assert response
            texts = [tag.text for tag in BeautifulSoup(response.text, 'html.parser').find_all(class_="comment more")]
            col_name = "Manufacturing PMI" if url == Url.CAIXIN_MAN_PMI.value else "Services PMI"
            df = pd.DataFrame([cls._parse_text(text) for text in texts], columns=["Year", "Month", col_name])
            df['Month'] = df['Month'].apply(lambda x: MONTHS[x.upper()].value)
            df = df.astype({"Year": 'Int64', "Month": 'Int64', col_name: 'Float64'})
            df = df.sort_values(by=['Year', 'Month'], ignore_index=True)
            return df
        
        except Exception as e:
            web_scraping_logger.exception(f'\n\nFailed to fetch the Caixin Manufacturing PMI data from: {url}\nError: {e}')
            return None
        
    @staticmethod
    def _parse_text(text: str) -> Tuple[str, str, str]:
        index, month, year = re.findall(r"(\d{2}(?:\.\d{1,2})?) in ([A-Za-z]+) (\d{4})", text)[0]
        return (year, month, index)

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
        url=f"https://finviz.com/quote.ashx?t={ticker}&p=d"
        response = WebSession().get(url)
        try:
            assert response
            soup = BeautifulSoup(response.content, "html.parser")
            desc = soup.find('div', attrs={"class":"quote_profile-bio"}).get_text()
            return desc
        
        except:
            return pd.NA
    
    @staticmethod
    def _process_df(df: pd.DataFrame) -> pd.DataFrame:
        
        # Convert all columns to string
        df = df.astype('string')

        # Track df column names and name updates
        updated_cols = list(df.columns)

        #Drop duplicate rows
        df = df.drop_duplicates()

        # Detect cols with real number followed by M, B, or K suffixes
        pattern = r'(?<=\d\.\d{2})[MBK]'
        suffix_cols = [c for c in df.columns if df[c].str.contains(pattern, regex=True, na=False).any()]

        # Detect cols with real number followed by % symbol
        pattern = r'(?<=\d\.\d{2})[%]'
        pct_cols = [c for c in df.columns if df[c].str.contains(pattern, regex=True, na=False).any()]

        # Detect cols with dates
        pattern = r'\d{1,2}/\d{1,2}/\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}'
        date_cols = [c for c in df.columns if df[c].str.contains(pattern, regex=True, na=False).any()]

        # Detect cols with floats
        pattern = r'^\d+\.{1}\d+$'
        float_cols = [c for c in df.columns if df[c].str.contains(pattern, regex=True, na=False).any()]

        # Detect cols with ints
        pattern = r'^\d+$'
        int_cols = [c for c in df.columns if df[c].str.contains(pattern, regex=True, na=False).any()]

        # Treat each col with M/B/K suffixes
        for col in suffix_cols:

            # Get scale factor for conversion to millions
            arr = df[col].to_numpy().astype(str)
            scale = np.where(np.char.find(arr, 'B') != -1, 1000, np.where(np.char.find(arr, 'K') != -1, 0.001, 1))

            # Eliminate suffixes, empty strings, and "non-float characters"
            pattern = {r'(?<=\d\.\d{2})[MBK]': '', r'[^0-9eE\.\+\-]': '', r'^(-)?$': pd.NA}
            df[col] = df[col].replace(pattern, regex=True)

            # Convert to float and multiply by scale factor
            df[col] = df[col].astype('Float64') * scale

            # Adjust column names
            updated_cols[updated_cols.index(col)] = col + ' (m USD)'

        # Treat each col with % symbols
        for col in pct_cols:

            # Eliminate empty strings, and "non-float characters"
            pattern = {r'[^0-9eE\.\+\-]': '', r'^(-)?$': pd.NA}
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
            pattern = {r'/[ab]': '', r'^(-)?$': pd.NA}
            df[col] = df[col].replace(pattern, regex=True)

            # Convert to datetime
            if col == "Earnings":
                df[col] = pd.to_datetime(df[col] + f' {pd.Timestamp.today().year}', format='%b %d %Y').dt.strftime('%d/%m/%Y') # NOTE:Test Dec-Jan cases
            else:
                df[col] = pd.to_datetime(df[col], format='%m/%d/%Y').dt.strftime('%d/%m/%Y')

        # Treat each col wih float types
        for col in float_cols:
    
            # Eliminate empty strings, and "non-float characters"
            pattern = {r'[^0-9eE\.\+\-]': '', r'^(-)?$': pd.NA}
            df[col] = df[col].replace(pattern, regex=True)

            # Convert to float
            df[col] = df[col].astype('Float64')

        # Treat each col wih int types
        for col in int_cols:
    
            # Eliminate empty strings, and "non-int characters"
            pattern = {r'[^0-9\+\-]': '', r'^(-)?$': pd.NA}
            df[col] = df[col].replace(pattern, regex=True)

            # Convert to float
            df[col] = df[col].astype('Int64')

        # Eliminate empty strings and hyphens from remaining (string type) columns
        pattern = {r'^(-)?$': pd.NA}
        df = df.replace(pattern, regex=True)

        # Update column names
        df.columns = updated_cols

        return df

    @classmethod
    def download_stocks(cls, num_rows: int = 10000, view_col_nums: None | List[int] = None) -> FinvizSreener | None:
      
        # Set default values and check input types
        try:
            num_rows = int(num_rows)
        except ValueError:
            raise ValueError("Number of rows must be an integer.")
            
        if not view_col_nums:
            view_col_nums = [1, 2, 79, 3, 4, 5, 129, 6, 7, 8, 9, 10, 11, 12, 13, 73, 74, 75, 14, 130, 131, 15, 16, 77, 17, 18, 19, 20,
                    21, 23, 22, 132, 133, 82, 78, 127, 128, 24, 25, 85, 26, 27, 28, 29, 30, 31, 84, 32, 33, 34, 35, 36, 37, 38,
                    39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 134, 125, 126, 59, 68, 70, 80,
                    83, 76, 60, 61, 62, 63, 64, 67, 69, 81, 86, 87, 88, 65, 66]
        else:
            try:
                view_col_nums = [int(i) for i in view_col_nums]
            except ValueError:
                raise ValueError("Column numbers must be input as a list of integers.")
            
        # Define url for viewing all columns; all downloaded and later filtered to show only selected columns
        url = Url.FINVIZ_SCREEN.value + (',').join([str(i) for i in view_col_nums])

        # Fetch the Finviz Stock Screener data
        with WebSession() as session:
            
            # Finviz shows 20 rows per page; update url (increase r by steps of 20) to navigate through pages 
            df = pd.DataFrame()
            for count in range(1, num_rows, 20):
                try:
                    url = url + "&r=" + str(count)
                    response = session.get(url)
                    assert response
                    df_i = pd.read_html(io.StringIO(response.text))[-2]
                    df = pd.concat([df, df_i], ignore_index=True)
                    if len(df_i) < 20: break # Less than 20 rows in table indicate last page of the screener

                except Exception as e:
                    web_scraping_logger.exception(f'\n\nFailed to fetch the Finviz Stock Screener data from: {url}\nError: {e}')
                    return None

        try:
            # Process dataframe to ensure correct types and handling missing values
            data = cls._process_df(df)
            data = data.iloc[:num_rows]
            return FinvizSreener(data)

        except Exception as e:
            web_scraping_logger.exception(f"\n\nFailed to fetch the Finviz Stock Screener data from: {url}\nError: {e}")
            return None
    
    @classmethod
    def download_industries(cls) -> FinvizIndustries | None:

        url = Url.FINVIZ_INDU.value
        with WebSession() as session:
            response = session.get(url)

        try:
            assert response
            df = pd.read_html(io.StringIO(response.text))[-2]
            data = cls._process_df(df)
            data = data.rename(columns={'Name': 'Industry'})
            GICS_sector_industry_map_inverse = {industry: sector for sector, industries in GICS_sector_industry_map.items() for industry in industries}
            data.insert(1, "Sector", data['Industry'].map(GICS_sector_industry_map_inverse))
            return FinvizIndustries(data)

        except Exception as e:
            web_scraping_logger.exception(f'\n\nFailed to fetch the Finviz industry-level data from: {url}\nError: {e}')
            return None 

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
        
    
#%%
class MarketData:
    """
    A class to represent market data from Trading Economics, including commodities, stocks, bonds, currencies, and cryptocurrencies.
    
    Attributes:
        commodities: NamedTuple
        stocks: NamedTuple
        bonds: NamedTuple
        currencies: NamedTuple
        crypto: NamedTuple

    Methods:
        download: Downloads market data from Trading Economics for commodities, stocks, bonds, currencies, and cryptocurrencies; returns constructed sub-classes to MarketData constructor
        _main: Fetches the HTML tables from Trading Economics and processes them into a dictionary of Pandas DataFrames.
        _clean_df: Cleans a DataFrame by dropping unwanted/empty columns, removing unwanted characters, converting data types and renaming columns.
        _split_units: For commodities only; splits the first column of the DataFrames into separate "item" and "units" columns.
        _combine_dfs: Combines a list of DataFrames into a single DataFrame.
    """

    def __init__(self, all_namedtuples: List) -> None:
        self._commodities, self._stocks, self._bonds, self._currencies, self._crypto = all_namedtuples

    @property
    def commodities(self) -> NamedTuple:
        return self._commodities

    @property
    def stocks(self) -> NamedTuple:
        return self._stocks

    @property
    def bonds(self) -> NamedTuple:
        return self._bonds

    @property
    def currencies(self) -> NamedTuple:
        return self._currencies

    @property
    def crypto(self) -> NamedTuple:
        return self._crypto        

    @classmethod
    def download(cls) -> MarketData | None:
        
        # Commodities
        data_dict = cls._main(url=Url.COMMODITIES.value)
        commodities = namedtuple('commodities', data_dict.keys())(**data_dict) if data_dict else None

        # Stocks
        data_dict = cls._main(url=Url.STOCKS.value)
        stocks = namedtuple('stocks', data_dict.keys())(**data_dict) if data_dict else None

        # Bonds
        data_dict = cls._main(url=Url.BONDS.value)
        bonds = namedtuple('bonds', data_dict.keys())(**data_dict) if data_dict else None

        # Currencies
        data_dict = cls._main(url=Url.CURRENCIES.value)
        currencies = namedtuple('currencies', data_dict.keys())(**data_dict) if data_dict else None

        # Crypto
        data_dict = cls._main(url=Url.CRYPTO.value)
        crypto = namedtuple('crypto', data_dict.keys())(**data_dict) if data_dict else None

        # All Data
        all_namedtuples = [commodities, stocks, bonds, currencies, crypto]
        
        if any(all_namedtuples):
            return cls(all_namedtuples)
        else:
            return None

    @classmethod
    def _main(cls, url: str) -> Dict[str, pd.DataFrame] | None:
        with WebSession() as session:
            response = session.get(url)
            
        try:
            assert response
            dfs = pd.read_html(io.StringIO(response.text))
            clean_dfs = [cls._clean_df(df) for df in dfs]
            if 'commodities' in url:
                clean_dfs = [cls._split_units(df) for df in clean_dfs]
            
            category_dict = {}
            for df in clean_dfs:
                if not df.empty or not df.columns:
                    category_name = df.columns[0].lower().strip()
                    category_dict[category_name] = df
            category_dict['all'] = cls._combine_dfs(clean_dfs)

            return category_dict

        except Exception as e:
            web_scraping_logger.exception(f"\n\nFailed to fetch data from Trading Economics: {url}\nError: {e}")
            return None

    @staticmethod
    def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
        df_copy = df.copy()

        # Drop empty columns
        df_copy = df_copy.dropna(axis=1, how='all')

        # Eliminate %, $, commas and M suffixes
        pattern = {r'[%,$]': '', r'(?<=[0-9])M': ''}
        df_copy = df_copy.replace(pattern, regex=True)

        # Drop Day column
        df_copy = df_copy.drop(columns=['Day'], errors='ignore')
        
        # Rename columns, ignored if column not present in DataFrame
        df_copy = df_copy.rename(columns={'%': 'Day %', 'Weekly': 'Weekly %', 'Monthly': 'Monthly %', 'YTD': 'YTD %', 
                                          'YoY': 'YoY %', 'MarketCap': 'Market Cap (m USD)'})
        
        # Convert columns to float or string
        for col in df_copy.columns:
            try:
                df_copy[col] = df_copy[col].astype('Float64')
            except ValueError:
                df_copy[col] = df_copy[col].astype('string')
    
        return df_copy
    
    @staticmethod
    def _split_units(clean_df: pd.DataFrame) -> pd.DataFrame:
        
        pattern1 = r'([A-Za-z]{3}\s*/.+)'
        pattern2 = r'(Index )?Points$'
        pattern3 = r'(USD$|EUR$|GBP$)'
        
        clean_df_copy = clean_df.copy()
        first_col = clean_df_copy.iloc[:, 0].astype('string')
        
        matches = first_col.apply(lambda x: re.search(f'{pattern1}|{pattern2}|{pattern3}', str(x)))
        units = matches.apply(lambda x: x.group(0) if x else None)
        first_col = first_col.apply(lambda x: re.sub(f'{pattern1}|{pattern2}|{pattern3}', '', str(x)))

        clean_df_copy.iloc[:, 0] = first_col
        clean_df_copy.insert(1, "Unit", units)

        return clean_df_copy
    
    @staticmethod
    def _combine_dfs(dfs: List[pd.DataFrame]) -> pd.DataFrame:
        dfs_copy = [df.copy(deep=True) for df in dfs]

        # Add category column and rename first column
        for df in dfs_copy:
            df.insert(1, 'Category', df.columns[0])
            df.columns = ['Item'] + list(df.columns[1:])

        # Concatenate DataFrames
        df_combined = pd.concat(dfs_copy, axis=0, ignore_index=True)

        return df_combined