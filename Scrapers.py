#%%
from __future__ import annotations  
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet
from collections import namedtuple
from datetime import datetime
from enum import Enum
from functools import reduce
from utility import find_content, p_to_str, custom_table_to_df, WebSession
import io
from loggers import web_scraping_logger      
import numpy as np                                                                                   
import pandas as pd
import re
from static import Man_Pmi_Structure, Serv_Pmi_Structure, GICS_sector_industry_map
from typing import List, Dict, NamedTuple, Tuple
import zipfile

"""A module containing classes to scrape and process economic reports and indicators from various sources."""

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
class ManufacturingPmi:
    """
    Represents an ISM Manufacturing PMI report.

    Attributes:
        sectors: A list of manufacturing sectors.
        _html_content: The HTML content of the webpage as string.
        _html_sections: A namedtuple containing the BeautifulSoup objects for relevant report sections.
        _sections: A namedtuple containing the relevant report sections in str or Pandas DataFrame formats.
    
    Methods:
        download: Downloads the Manufacturing PMI report from the ISM website. Defaults to the latest report.
        _parse_html: Parses the HTML content of the Manufacturing PMI report and extracts relevant sections.
        _transform_sections: Transforms the extracted HTML sections into strings (text) and Pandas DataFrames (tables).
        _rankings: Ranks the manufacturing sectors based on the growth or contraction.
        _respondents_say: Extracts the comments from the respondents and stores them in a Pandas DataFrame.
    """

    sectors = ["Apparel, Leather & Allied Products", "Chemical Products", "Computer & Electronic Products", "Electrical Equipment, Appliances & Components",
               "Fabricated Metal Products", "Food, Beverage & Tobacco Products", "Furniture & Related Products", "Machinery", "Miscellaneous Manufacturing",
               "Nonmetallic Mineral Products", "Paper Products", "Petroleum & Coal Products", "Plastics & Rubber Products", "Primary Metals",
               "Printing & Related Support Activities", "Textile Mills", "Transportation Equipment", "Wood Products"]

    def __init__(self, html_content: str, html_sections: NamedTuple, sections: NamedTuple) -> None:
        """
        Initializes a ManufacturingPmi object. Attributes are private, accessible through getter methods, to prevent assignment.
        Args:
            html_content (str): The HTML of the webpage.
            html_sections (namedtuple): A namedtuple containing the HTML for relevant report sections.
            sections (namedtuple): A namedtuple containing the relevant report sections in str or Pandas DataFrame formats (derived from processing html_sections).
        """

        self._html_content = html_content
        self._html_sections = html_sections
        self._sections = sections

    @property
    def html_content(self) -> str:
        return self._html_content

    @property   
    def html_sections(self) -> NamedTuple:
        return self._html_sections

    @property
    def sections(self) -> NamedTuple:
        return self._sections
    
    @property
    def data(self) -> NamedTuple:
        return self._sections
    
    @classmethod
    def download(cls, url: str | None = None) -> ManufacturingPmi | None:
        """
        Extracts and transforms HTML from a webpage, and calls the constructor to create a ManufacturingPmi object.
        Args:
            url (str): The url of the webpage from which the report is obtained.
        Returns:
            ManufacturingPmi: A ManufacturingPmi object is created by calling the constructor.
        """

        if not url:
            prev_month = datetime.now().month - 1

            for i in range(3):
                month = datetime(1900, prev_month - i, 1).strftime("%B").lower()
                url = f"{Url.US_MAN_PMI.value}{month}/"
                
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
            html_sections_nt = namedtuple('html_sections', html_sections.keys())(**html_sections) # Convert dictionaries into namedtuples for immutability
            sections_nt = namedtuple('sections', sections.keys())(**sections)
            return cls(html_content, html_sections_nt, sections_nt)
        
        except Exception as e:
            web_scraping_logger.exception(f"\n\nFailed to fetch the ISM Manufacturing data from: {url}\nError: {e}")
            return None

    @classmethod
    def _parse_html(cls, html_content: str) -> Dict[str, Tag | ResultSet | None]:
        """
        Parses the webpage HTML using BeautifulSoup. Locates and stores the HTML of relevant sections in a dictionary.
        The relevant sections and how to locate them in the HTML are defined in the ism_pmi_report_structures module.
        Args:
            html_content (str): The HTML of the webpage.
        Returns:
            dict[str, Tag | ResultSet]: A dictionary containing the BeautifulSoup objects for relevant report sections.
        """

        soup = BeautifulSoup(html_content, 'html.parser')
        html_sections = {}

        for segment, search_formula in Man_Pmi_Structure.items():
                search_tag = search_formula['tag']
                search_attrs = search_formula['attrs']
                search_methods = search_formula['methods']

                try:
                    section_content = find_content(soup, search_tag, search_attrs, search_methods)
                    assert type(section_content) in [Tag, ResultSet]
                except AssertionError:
                    web_scraping_logger.exception(f"\n\nNo content could be retrieved for '{segment}' using provided search parameters.")
                    html_sections[segment] = None
                else:
                    html_sections[segment] = section_content

        return html_sections

    @classmethod
    def _transform_sections(cls, html_sections: Dict[str, Tag | ResultSet | None]) -> Dict[str, str | pd.DataFrame | None]:
        """
        Converts BeautifulSoup objects into strings (from <p> tags) and Pandas DataFrames (from <table> tags), and stores the results in a dictionary.
        Args:
            html_sections: (dict[str, Tag | ResultSet]): A dictionary containing the BeautifulSoup objects of the relevant report sections.
        Returns:
            dict[str, str | list[pd.DataFrame]]: A dictionary containing the content of relevant report sections in string or Pandas DataFrame formats.
        """

        transformed_sections = {}

        for key, value in html_sections.items():
            if not value:
                transformed_sections[key] = None
                continue
            
            if 'table' in key:
                df_list = custom_table_to_df(value)

                # No processing on main overview table
                if key == 'full_pmi_table':
                    df = df_list[0]

                # Process other tables to add Year and Month columns; combine multiple tables per section into one
                else:
                    for df in df_list:
                        if key == 'buying_policy_table': df.insert(0, 'Category', df.index.name)
                        dates = pd.to_datetime(df.index, format='%b %Y').to_series()
                        df.insert(0, 'Month', dates.dt.month_name())
                        df.insert(0, 'Year', dates.dt.year)
                        df = df.reset_index(drop=True)
                    df = pd.concat(df_list)                     
                
                transformed_sections[key] = df

            else:
                transformed_sections[key] = p_to_str(value)
        
        if 'overview' in transformed_sections and 'new_orders_text' in transformed_sections:
            transformed_sections['industry_rankings'] = cls._rankings(transformed_sections['overview'], transformed_sections['new_orders_text'])
        else:
            transformed_sections['industry_rankings'] = None
        
        if 'comments' in transformed_sections:
            transformed_sections['respondents'] = cls._respondents_say(transformed_sections['comments'])
        else:
            transformed_sections['respondents'] = None

        return transformed_sections
    
    @classmethod
    def _rankings(cls, overview: str, new_orders_text: str) -> pd.DataFrame:
        """
        Ranks the sectors based on the growth/contraction in the PMI and new-orders.
        Args:
            overview (str): The report overview which contains a list of growing and contracting sectors.
            new_orders_text (str): The text under the "new orders" section which contains a list of growing and contracting sectors.
        Returns:
            pd.DataFrame: A Pandas DataFrame containing the PMI and new-orders rankings for each sector.
        """

        # Initiate empty dataframe with sectors as index
        df = pd.DataFrame({"Sectors": cls.sectors, "PMI Rankings": [0] * len(cls.sectors), "New Orders Rankings": [0] * len(cls.sectors)}).set_index('Sectors')

        # Get the growth/contraction text from the last line of "overview"; split into sentences.
        txt = overview.split('\n')[-1]
        lines = txt.split('.')

        # Extract list of growing sectors and rank them
        grow = list(map(str.strip,lines[0].split(':')[1].split(';')))
        grow[-1] = grow[-1].replace("and ","")
        for index, item in enumerate(grow):
           df.loc[item, "PMI Rankings"] = len(grow) - index

        # Extract list of contracting sectors and rank them
        contract = list(map(str.strip,lines[1].split(':')[1].split(';')))
        contract[-1] = contract[-1].replace("and ","")
        for index, item in enumerate(contract):
            df.loc[item, "PMI Rankings"] = -(len(contract) - index)

        # Get the growth/contraction text from the last line of "new orders"; split into sentences.
        txt = new_orders_text.split('\n')[-1]
        lines = txt.split('.')

        # Extract list of growing sectors and rank them
        grow = list(map(str.strip,lines[0].split(':')[1].split(';')))
        grow[-1] = grow[-1].replace("and ","")
        for index, item in enumerate(grow):
            df.loc[item, "New Orders Rankings"] = len(grow) - index

        # Extract list of contracting sectors and rank them
        contract = list(map(str.strip,lines[1].split(':')[1].split(';')))
        contract[-1] = contract[-1].replace("and ","")       
        for index, item in enumerate(contract):
            df.loc[item, "New Orders Rankings"] = -(len(contract) - index)

        return df
    
    @classmethod
    def _respondents_say(cls, comments: str) -> pd.DataFrame:  
        """
        Extracts the comments from the respondents and stores them in a Pandas DataFrame.
        Args:
            comments (str): The text under the "respondents say" section which contains a list of comments.
        Returns:
            pd.DataFrame: A Pandas DataFrame containing the respondents' comments from different sectors.
        """

        # Initiate empty dataframe with sectors as index
        df = pd.DataFrame({"Sectors": cls.sectors, "Respondent Comments": [''] * len(cls.sectors)}).set_index('Sectors')

        # Split comments block into sentences
        txt = comments.split('\n')[1:-1]

        # For each comment, extract the sector and quote; store in dataframe
        for comment in txt:
            sector = comment.split('[')[1][:-1]
            quote = comment.split('[')[0][1:-2]
            df.loc[sector, "Respondent Comments"] = quote

        return df
    
#%%
class ServicesPmi:
    """
    Represents an ISM Services PMI report.

    Attributes:
        sectors: A list of services sectors.
        _html_content: The HTML content of the webpage as string.
        _html_sections: A namedtuple containing the BeautifulSoup objects for relevant report sections.
        _sections: A namedtuple containing the relevant report sections in str or Pandas DataFrame formats.
    
    Methods:
        download: Downloads the Services PMI report from the ISM website. Defaults to the latest report.
        _parse_html: Parses the HTML content of the Manufacturing PMI report and extracts relevant sections.
        _transform_sections: Transforms the extracted HTML sections into strings (text) and Pandas DataFrames (tables).
        _rankings: Ranks the manufacturing sectors based on the growth or contraction.
        _respondents_say: Extracts the comments from the respondents and stores them in a Pandas DataFrame.
    """

    sectors = ["Accommodation & Food Services", "Agriculture, Forestry, Fishing & Hunting", "Arts, Entertainment & Recreation", "Construction",
               "Educational Services", "Finance & Insurance", "Health Care & Social Assistance", "Information", "Management of Companies & Support Services",
               "Mining", "Other Services", "Professional, Scientific & Technical Services", "Public Administration", "Real Estate, Rental & Leasing", "Retail Trade",
               "Transportation & Warehousing", "Utilities", "Wholesale Trade"]

    def __init__(self, html_content: str, html_sections: NamedTuple, sections: NamedTuple) -> None:
        """
        Initializes a ServicesPmi object. Attributes are private, accessible through getter methods, to prevent assignment.
        Args:
            html_content (str): The HTML content of the webpage.
            html_sections (namedtuple): A namedtuple containing the HTML for relevant report sections.
            sections (namedtuple): A namedtuple containing the relevant report sections in str or Pandas DataFrame formats (derived from processing html_sections).
        """

        self._html_content = html_content
        self._html_sections = html_sections
        self._sections = sections

    @property
    def html_content(self) -> str:
        return self._html_content

    @property   
    def html_sections(self) -> NamedTuple:
        return self._html_sections

    @property
    def sections(self) -> NamedTuple:
        return self._sections
    
    @property
    def data(self) -> NamedTuple:
        return self._sections
    
    @classmethod
    def download(cls, url: str | None = None) -> ServicesPmi | None:
        """
        Extracts and transforms HTML from a webpage, and calls the constructor to create a ServicesPmi object.
        Args:
            url (str): The url of the webpage from which the report is obtained.
        Returns:
            ServicesPmi: A ServicesPmi object is created by calling the constructor.
        """

        if not url:
            prev_month = datetime.now().month - 1

            for i in range(3):
                month = datetime(1900, prev_month - i, 1).strftime("%B").lower()
                url = f"{Url.US_SER_PMI.value}{month}/"
                
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
            html_sections_nt = namedtuple('html_sections', html_sections.keys())(**html_sections) # Convert dictionaries into namedtuples for immutability
            sections_nt = namedtuple('sections', sections.keys())(**sections)
            return cls(html_content, html_sections_nt, sections_nt)
        
        except Exception as e:
            web_scraping_logger.exception(f"\n\nFailed to fetch the ISM Services data from: {url}\nError: {e}")
            return None

    @classmethod
    def _parse_html(cls, html_content: str) -> Dict[str, Tag | ResultSet | None]:
        """
        Parses the webpage HTML using BeautifulSoup. Locates and stores the HTML of relevant report sections in a dictionary.
        The relevant sections and how to locate them in the HTML are defined in the ism_pmi_report_structures module.
        Args:
            html_content (str): The HTML of the webpage.
        Returns:
            dict[str, Tag | ResultSet]: A dictionary containing the BeautifulSoup objects for relevant report sections.
        """

        soup = BeautifulSoup(html_content, 'html.parser')
        html_sections = {}

        for segment, search_formula in Serv_Pmi_Structure.items():
                search_tag = search_formula['tag']
                search_attrs = search_formula['attrs']
                search_methods = search_formula['methods']
                
                try:
                    section_content = find_content(soup, search_tag, search_attrs, search_methods)
                    assert type(section_content) in [Tag, ResultSet]
                except AssertionError:
                    web_scraping_logger.exception(f"No content could be retrieved for '{segment}' using provided search parameters.")
                    html_sections[segment] = None
                else:
                    html_sections[segment] = section_content

        return html_sections

    @classmethod
    def _transform_sections(cls, html_sections: Dict[str, Tag | ResultSet | None]) -> Dict[str, str | pd.DataFrame | None]:
        """
        Converts BeautifulSoup objects into strings (from <p> tags) and Pandas DataFrames (from <table> tags), and stores the results in a dictionary.
        Args:
            html_sections: (dict[str, Tag | ResultSet]): A dictionary containing the BeautifulSoup objects of the relevant report sections.
        Returns:
            dict[str, str | list[pd.DataFrame]]: A dictionary containing the content of relevant report sections in string or Pandas DataFrame formats.
        """

        transformed_sections = {}
        
        for key, value in html_sections.items():
            if not value:
                transformed_sections[key] = None
                continue

            if 'table' in key:
                df_list = custom_table_to_df(value)

                # No processing on main overview table
                if key == 'full_pmi_table':
                    df = df_list[0]

                # Process other tables to add Year and Month columns; combine multiple tables per section into one
                else:
                    for df in df_list:
                        dates = pd.to_datetime(df.index, format='%b %Y').to_series()
                        df.insert(0, 'Month', dates.dt.month_name())
                        df.insert(0, 'Year', dates.dt.year)
                        df = df.reset_index(drop=True)
                    df = pd.concat(df_list)
                
                transformed_sections[key] = df

            else:
                transformed_sections[key] = p_to_str(value)
        
        if 'overview' in transformed_sections and 'business_activity_text' in transformed_sections:
            transformed_sections['industry_rankings'] = cls._rankings(transformed_sections['overview'], transformed_sections['business_activity_text'])
        else:
            transformed_sections['industry_rankings'] = None
        
        if 'comments' in transformed_sections:
            transformed_sections['respondents'] = cls._respondents_say(transformed_sections['comments'])
        else:
            transformed_sections['respondents'] = None

        return transformed_sections
    
    @classmethod
    def _rankings(cls, overview: str, business_activity_text: str) -> pd.DataFrame:
        """
        Ranks the sectors based on the growth/contraction in the PMI and business-activity.
        Args:
            overview (str): The report overview which contains a list of growing and contracting sectors.
            business_activity_text (str): The text under the "business activity" section which contains a list of growing and contracting sectors.
        Returns:
            pd.DataFrame: A Pandas DataFrame containing the PMI and business-activity rankings for each sector.
        """

        # Initiate empty dataframe with sectors as index
        df = pd.DataFrame({"Sectors": cls.sectors, "PMI Rankings": [0] * len(cls.sectors), "Business Activity Rankings": [0] * len(cls.sectors)}).set_index('Sectors')

        # Get the growth/contraction text from the last line of "overview"; split into sentences.
        txt = overview.split('\n')[-1]
        lines = txt.split('.')

        # Extract list of growing sectors and rank them
        grow = list(map(str.strip,lines[0].split(':')[1].split(';')))
        grow[-1] = grow[-1].replace("and ","")
        for index, item in enumerate(grow):
           df.loc[item, "PMI Rankings"] = len(grow) - index
        
        # Extract list of contracting sectors and rank them
        contract = list(map(str.strip,lines[1].split(':')[1].split(';')))
        contract[-1] = contract[-1].replace("and ","")
        for index, item in enumerate(contract):
            df.loc[item, "PMI Rankings"] = -(len(contract) - index)

        # Get the growth/contraction text from the last line of "business activity"; split into sentences.
        txt = business_activity_text.split('\n')[-1]
        lines = txt.split('.')

        # Extract list of growing sectors and rank them
        grow = list(map(str.strip,lines[0].split(':')[1].split(';')))
        grow[-1] = grow[-1].replace("and ","")
        for index, item in enumerate(grow):
            df.loc[item, "Business Activity Rankings"] = len(grow) - index

        # Extract list of contracting sectors and rank them
        contract = list(map(str.strip,lines[1].split(':')[1].split(';')))
        contract[-1] = contract[-1].replace("and ","")
        for index, item in enumerate(contract):
            df.loc[item, "Business Activity Rankings"] = -(len(contract) - index)

        return df
    
    @classmethod
    def _respondents_say(cls, comments: str) -> pd.DataFrame:
        """
        Extracts the comments from the respondents and stores them in a Pandas DataFrame.
        Args:
            comments (str): The text under the "respondents say" section which contains a list of comments.
        Returns:
            pd.DataFrame: A Pandas DataFrame containing the respondents' comments from different sectors.
        """

        # Initiate empty dataframe with sectors as index
        df = pd.DataFrame({"Sectors": cls.sectors, "Respondent Comments": [''] * len(cls.sectors)}).set_index('Sectors')

        # Split comments block into sentences
        txt = comments.split('\n')[1:-1]

        # For each comment, extract the sector and quote; store in dataframe
        for comment in txt:
            sector = comment.split('[')[1][:-1]
            quote = comment.split('[')[0][1:-2]
            df.loc[sector, "Respondent Comments"] = quote

        return df
    
    #%%
class ConsumerSurvey:
    """
    A class to represent the US Michigan Consumer Survey data.

    Attributes:
        data: A Pandas DataFrame containing the consumer survey data with columns for Year, Month, Index, Current Index, and Expected Index.
    
    Methods:
        download: Downloads the US Michigan Consumer Survey data; reads CSVs into DataFrames; returns a processed DataFrame.
        _process_df: Processes the raw DataFrames from the downloaded CSV files, merging them into one.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data.copy(deep=True)

    @property
    def data(self) -> pd.DataFrame:
        return self._data.copy(deep=True)
    
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
        df1 = df1.astype({"Month": 'string', "Year": int, "Index": 'Float64'})
        
        df2 = df2.dropna(axis=1, how='all')
        df2 = df2.dropna(axis=0, how='all')
        df2.columns = ["Month", "Year", "Current Index", "Expected Index"]
        df2 = df2.astype({"Month": 'string', "Year": int, "Current Index": 'Float64', "Expected Index": 'Float64'})

        # Some months have "(P)" in the month column; remove it
        pattern = r'\s*\(P\)\s*'
        df1["Month"] = df1["Month"].str.replace(pattern, "", regex=True)
        df2["Month"] = df2["Month"].str.replace(pattern, "", regex=True)

        # Merge the two dataframes and re-order columns
        df = df1.merge(df2)
        df = df[["Year", "Month", "Index", "Current Index", "Expected Index"]]
        
        return df

#%%
class ConstructionSurvey:
    """
    A class to represent the US Census Bureau Construction Survey data.

    Attributes:
        data: A Pandas DataFrame containing the construction survey data with columns for Year, Month, Permits, Authorized, Starts, Under Construction, and Completions.

    Methods:
        download: Downloads the US Census Bureau Construction Survey data; reads Excel files into DataFrames; returns a processed DataFrame.
        _process_df: Processes the raw DataFrames from the downloaded Excel files, merging them into one.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data.copy(deep=True)

    @property
    def data(self) -> pd.DataFrame:
        return self._data.copy(deep=True)
    
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
            
            merged_df['Month_num'] = pd.to_datetime(merged_df['Month'], format='%B').dt.month
            merged_df = merged_df.sort_values(by=['Year', 'Month_num']).drop(columns='Month_num').reset_index(drop=True)
            
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
        df.insert(0, 'Month', df['Date'].dt.month_name())
        df.insert(0, 'Year', df['Date'].dt.year)
        df = df.drop(columns=['Date'])
        df = df.astype({'Year': int, 'Month': 'string', 'Total': 'Float64'})

        return df
    
#%%
class EuroSurvey:
    """
    A class to represent the EU Economic Survey data.
    
    Attributes:
        data: A Pandas DataFrame containing the EU Economic Survey data with columns for Year, Month, and various economic indicators per country.
    
    Methods:
        download: Downloads the EU Economic Survey data; reads the Excel file into a DataFrame; returns a processed DataFrame.
        _process_df: Processes the raw DataFrame from the downloaded Excel file, adding Year and Month columns.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data.copy(deep=True)

    @property
    def data(self) -> pd.DataFrame:
        return self._data.copy(deep=True)
    
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
        df["Year"] = df["Year"].astype(int)

        df.insert(2, "Month", df["Date"].dt.month_name())
        df["Month"] = df["Month"].astype('string')

        # Drop "unnamed" and "date" columns
        df = df.loc[:, ~df.columns.str.contains('unnamed', case=False)]
        df = df.drop(columns=["Date"])

        # Set all numerical columns to float type
        df.iloc[:, 3:] = df.iloc[:, 3:].astype('float64')

        return df

#%%
class CaixinManufacturingPmi:
    """
    A class to represent the Caixin Manufacturing PMI data from Trading Economics.
    
    Attributes:
        data: A Pandas DataFrame containing the Caixin Manufacturing PMI data with columns for Year, Month, and Manufacturing PMI index.
    
    Methods:
        download: Downloads the text from the Caixin Manufacturing PMI page from Trading Economics and processes it into a DataFrame.
        _parse_text: Parses the text to extract the Manufacturing PMI index, month, and year.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data.copy(deep=True)

    @property
    def data(self) -> pd.DataFrame:
        return self._data.copy(deep=True)
    
    @classmethod
    def download(cls) -> CaixinManufacturingPmi | None:

        url = Url.CAIXIN_MAN_PMI.value
        with WebSession() as session:
            response = session.get(url)

        try:
            assert response
            text = BeautifulSoup(response.text, 'html.parser').find(id="description").text

            index, month, year = cls._parse_text(text)

            df = pd.DataFrame([[year, month, index]], columns=["Year", "Month", "Manufacturing PMI"])
            df = df.astype({"Year": int, "Month": 'string', "Manufacturing PMI": 'Float64'})

            return cls(df)
        
        except Exception as e:
            web_scraping_logger.exception(f'\n\nFailed to fetch the Caixin Manufacturing PMI data from: {url}\nError: {e}')
            return None
        
    @staticmethod
    def _parse_text(text: str) -> Tuple[str, str, str]:
        return re.findall(r"(\d{2}(?:\.\d{1,2})?) in ([A-Za-z]+) (\d{4})", text)[0]

#%%
class CaixinServicesPmi:
    """
    A class to represent the Caixin Services PMI data from Trading Economics.
    
    Attributes:
        data: A Pandas DataFrame containing the Caixin Services PMI data with columns for Year, Month, and Services PMI index.
    
    Methods:
        download: Downloads the text from the Caixin Services PMI page from Trading Economics and processes it into a DataFrame.
        _parse_text: Parses the text to extract the Services PMI index, month, and year.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data.copy(deep=True)

    @property
    def data(self) -> pd.DataFrame:
        return self._data.copy(deep=True)
    
    @classmethod
    def download(cls) -> CaixinServicesPmi | None:

        url = Url.CAIXIN_SER_PMI.value
        with WebSession() as session:
            response = session.get(url)

        try:
            assert response
            text = BeautifulSoup(response.text, 'html.parser').find(id="description").text

            index, month, year = cls._parse_text(text)

            df = pd.DataFrame([[year, month, index]], columns=["Year", "Month", "Services PMI"])
            df = df.astype({"Year": int, "Month": 'string', "Services PMI": 'Float64'})

            return cls(df)
        
        except Exception as e:
            web_scraping_logger.exception(f'\n\nFailed to fetch the Caixin Services PMI data from: {url}\nError: {e}')
            return None
        
    @staticmethod
    def _parse_text(text: str) -> Tuple[str, str, str]:
        return re.findall(r"(\d{2}(?:\.\d{1,2})?) in ([A-Za-z]+) (\d{4})", text)[0]
    
#%%
class Finviz:

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
                df[col] = pd.to_datetime(df[col] + f' {pd.Timestamp.today().year}', format='%b %d %Y').dt.strftime('%d/%m/%Y') # Test Dec-Jan cases
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

class FinvizSreener(Finviz):
    """
    A class to represent the Finviz Stock Screener.

    Attributes:
        data: A Pandas DataFrame containing the stock screener data with various columns for financial metrics.

    Methods:
        download: Downloads tabular data and processes it into a DataFrame.
        _process_df: Processes the raw DataFrame from the downloaded HTML, converting columns to appropriate types and handling numerical suffixes.
    """

    _col_nums = [1, 2, 79, 3, 4, 5, 129, 6, 7, 8, 9, 10, 11, 12, 13, 73, 74, 75, 14, 130, 131, 15, 16, 77, 17, 18, 19, 20, 21, 23, 22, 132, 133, 82, 78, 127, 128,
                 24, 25, 85, 26, 27, 28, 29, 30, 31, 84, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
                 134, 125, 126, 59, 68, 70, 80, 83, 76, 60, 61, 62, 63, 64, 67, 69, 81, 86, 87, 88, 65, 66]
    _default_col_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 14 ,37, 42, 43, 44, 45, 46, 47, 48, 49, 52, 53, 68, 65]
    
    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data.copy(deep=True)

    @property
    def data(self) -> pd.DataFrame:
        return self._data.copy(deep=True)
    
    @classmethod
    def download(cls, num_rows: int = 5500, view_col_nums: str | List[int] = "default") -> FinvizSreener | None:

        # Define url for viewing all columns; all downloaded and later filtered to show only selected columns
        url = Url.FINVIZ_SCREEN.value + (',').join([str(i) for i in cls._col_nums])
        
        # Set default values and check input types
        try:
            num_rows = int(num_rows)
        except ValueError:
            raise ValueError("Number of rows must be an integer.")
            
        if view_col_nums == 'default':
            view_col_nums = cls._default_col_nums
        elif view_col_nums=='all':
            view_col_nums = cls._col_nums
        else:
            try:
                view_col_nums = [int(i) for i in view_col_nums]
            except ValueError:
                raise ValueError("Column numbers must be input as a list of integers.")

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

                except Exception as e:
                    web_scraping_logger.exception(f'\n\nFailed to fetch the Finviz Stock Screener data from: {url}\nError: {e}')
                    return None

        try:
            # Process dataframe to ensure correct types and handling missing values
            data = cls._process_df(df)
            
            # Select subset of columns to view
            num_name_dict = {num: name for num, name in zip(cls._col_nums, data.columns)}
            view_col_names = [num_name_dict[i] for i in view_col_nums]
            data = data[view_col_names]

            return cls(data)

        except Exception as e:
            web_scraping_logger.exception(f"\n\nFailed to fetch the Finviz Stock Screener data from: {url}\nError: {e}")
            return None
    
class FinvizIndustries(Finviz):
    """
    A class to represent the Finviz industries performance page.

    Attributes:
        data: A Pandas DataFrame containing the industry performance data.

    Methods:
        download: Downloads tabular data and processes it into a DataFrame.
        _process_df: Processes the raw DataFrame from the downloaded HTML, converting columns to appropriate types and handling numerical suffixes.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data.copy(deep=True)

    @property
    def data(self) -> pd.DataFrame:
        return self._data.copy(deep=True)
    
    @classmethod
    def download(cls) -> FinvizSreener | None:

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
            return cls(data)

        except Exception as e:
            web_scraping_logger.exception(f'\n\nFailed to fetch the Finviz industry-level data from: {url}\nError: {e}')
            return None     
    
#%%
class MarketData:
    """
    A class to represent market data from Trading Economics, including commodities, stocks, bonds, currencies, and cryptocurrencies.
    
    Attributes:
        data: A namedtuple with 5 other namedtuples as values: commodities, stocks, bonds, currencies, crypto.

    Methods:
        download: Downloads market data from Trading Economics for commodities, stocks, bonds, currencies, and cryptocurrencies; returns constructed sub-classes to MarketData constructor
        _main: Fetches the HTML tables from Trading Economics and processes them into a dictionary of Pandas DataFrames.
        _clean_df: Cleans a DataFrame by dropping unwanted/empty columns, removing unwanted characters, converting data types and renaming columns.
        _split_units: For commodities only; splits the first column of the DataFrames into separate "item" and "units" columns.
        _combine_dfs: Combines a list of DataFrames into a single DataFrame.
    """

    def __init__(self, data: NamedTuple) -> None:
        self._data = data

    @property
    def data(self) -> NamedTuple:
        return self._data        

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
        data_dict = {"commodities": commodities, "stocks": stocks, "bonds": bonds, "currencies": currencies, "crypto": crypto}
        data = namedtuple('data', data_dict.keys())(**data_dict)
        
        if any([i for i in data]):
            return cls(data)
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