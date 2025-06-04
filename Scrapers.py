#%%
from __future__ import annotations  
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet
from collections import namedtuple
from datetime import datetime
from helpers import parse_html, p_to_str, custom_table_to_df, WebSession
import io
from ism_pmi_report_structures import Man_Pmi_Structure, Serv_Pmi_Structure
from loggers import web_scraping_logger      
import numpy as np                                                                                   
import pandas as pd
import re
from typing import List, Dict, NamedTuple, Tuple
import zipfile
# TODO: Replace pandas inplace methods; add docstrings
#%%
class ManufacturingPmi:

    """
    Represents an ISM Manufacturing PMI report.
    """

    sectors = ["Apparel, Leather & Allied Products", "Chemical Products", "Computer & Electronic Products", "Electrical Equipment, Appliances & Components",
               "Fabricated Metal Products", "Food, Beverage & Tobacco Products", "Furniture & Related Products", "Machinery", "Miscellaneous Manufacturing",
               "Nonmetallic Mineral Products", "Paper Products", "Petroleum & Coal Products", "Plastics & Rubber Products", "Primary Metals",
               "Printing & Related Support Activities", "Textile Mills", "Transportation Equipment", "Wood Products"]

    def __init__(self, html_content: str, html_sections: NamedTuple, sections: NamedTuple) -> None:

        """
        Initializes a ManufacturingPmi object. Attributes are private, accessible through getter methods, to prevent assignment. Attributes are of immutable types to prevent modification.
        Args:
            url (str): The url of the webpage from which the report is obtained.
            access_date (datetime): The date and time when the report was accessed.
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
    
    @classmethod
    def web_extract(cls, url: str | None = None) -> ManufacturingPmi | None:

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
                url = f"https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/pmi/{month}/"
                
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
            web_scraping_logger.exception(f"Failed to fetch the ISM Manufacturing PMI webpage: {url}\nError: {e}\n\n")
            return None

    @classmethod
    def _parse_html(cls, html_content: str) -> Dict[str, Tag | ResultSet]:

        """
        Parses the webpage HTML using BeautifulSoup. Locates and stores the HTML of relevant report sections in a dictionary.
        The relevant sections and how to locate them in the HTML are defined in the ism_pmi_report_structures module.
        Args:
            html_content (str): The HTML of the webpage.
        Returns:
            dict[str, Tag | ResultSet]: A dictionary containing the BeautifulSoup objects for relevant report sections:
        """

        soup = BeautifulSoup(html_content, 'html.parser')
        html_sections = {}

        for segment, search_formula in Man_Pmi_Structure.items():
                search_tag = search_formula['tag']
                search_attrs = search_formula['attrs']
                search_methods = search_formula['methods']

                try:
                    chunk = parse_html(soup, search_tag, search_attrs, search_methods)
                    if type(chunk) not in [Tag, ResultSet]:
                        raise Exception(f"No content could be retrieved for '{segment}' using provided search parameters.")
                except Exception as e:
                    web_scraping_logger.exception(f"Error in parsing webpage: {e}\n\n")
                else:
                    html_sections[segment] = chunk

        return html_sections

    @classmethod
    def _transform_sections(cls, html_sections: Dict[str, Tag | ResultSet]) -> Dict[str, str | List[pd.DataFrame]]:

        """
        Converts BeautifulSoup objects into strings (from <p> tags) and Pandas DataFrames (from <table> tags), and stores the results in a dictionary.
        Args:
            html_sections: (dict[str, Tag | ResultSet]): A dictionary containing the BeautifulSoup objects of the relevant report sections.
        Returns:
            dict[str, str | list[pd.DataFrame]]: A dictionary containing the content of relevant report sections in string or Pandas DataFrame formats.
        """

        transformed_sections = {}

        for key, value in html_sections.items():
            if isinstance(value, ResultSet) and all([t.name == 'table' for t in value]):
                transformed_sections[key] = custom_table_to_df(value)
            else:
                transformed_sections[key] = p_to_str(value)
        
        transformed_sections['industry_rankings'] = cls._rankings(transformed_sections['overview'], transformed_sections['new_orders_text'])
        transformed_sections['respondents'] = cls._respondents_say(transformed_sections['comments'])

        return transformed_sections
    
    @classmethod
    def _rankings(cls, overview: str, new_orders_text: str) -> pd.DataFrame:

        """
        Ranks the sectors based on the growth/contraction in the PMI and new orders.
        Args:
            overview (str): The report overview which contains a list of growing and contracting sectors.
            new_orders_text (str): The text under the "new orders" section which contains a list of growing and contracting sectors.
        Returns:
            pd.DataFrame: A Pandas DataFrame containing the PMI and new orders rankings for each sector.
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
    """

    sectors = ["Accommodation & Food Services", "Agriculture, Forestry, Fishing & Hunting", "Arts, Entertainment & Recreation", "Construction",
               "Educational Services", "Finance & Insurance", "Health Care & Social Assistance", "Information", "Management of Companies & Support Services",
               "Mining", "Other Services", "Professional, Scientific & Technical Services", "Public Administration", "Real Estate, Rental & Leasing", "Retail Trade",
               "Transportation & Warehousing", "Utilities", "Wholesale Trade"]

    def __init__(self, html_content: str, html_sections: NamedTuple, sections: NamedTuple) -> None:

        """
        Initializes a ServicesPmi object. Attributes are private, accessible through getter methods, to prevent assignment. Attributes are of immutable types to prevent modification.
        Args:
            url (str): The url of the webpage from which the report is obtained.
            access_date (datetime): The date and time when the report was accessed.
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
    
    @classmethod
    def web_extract(cls, url: str | None = None) -> ServicesPmi | None:

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
                url = f"https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/services/{month}/"
                
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
            web_scraping_logger.exception(f"Failed to fetch the ISM Services PMI webpage: {url}\nError: {e}\n\n")
            return None

    @classmethod
    def _parse_html(cls, html_content: str) -> Dict[str, Tag | ResultSet]:

        """
        Parses the webpage HTML using BeautifulSoup. Locates and stores the HTML of relevant report sections in a dictionary.
        The relevant sections and how to locate them in the HTML are defined in the ism_pmi_report_structures module.
        Args:
            html_content (str): The HTML of the webpage.
        Returns:
            dict[str, Tag | ResultSet]: A dictionary containing the BeautifulSoup objects for relevant report sections:
        """

        soup = BeautifulSoup(html_content, 'html.parser')
        html_sections = {}

        for segment, search_formula in Serv_Pmi_Structure.items():
                search_tag = search_formula['tag']
                search_attrs = search_formula['attrs']
                search_methods = search_formula['methods']
                
                try:
                    chunk = parse_html(soup, search_tag, search_attrs, search_methods)
                    if type(chunk) not in [Tag, ResultSet]:
                        raise Exception(f"No content could be retrieved for '{segment}' using provided search parameters.")
                except Exception as e:
                    web_scraping_logger.exception(f"Error in parsing webpage: {e}\n\n")
                else:
                    html_sections[segment] = chunk

        return html_sections

    @classmethod
    def _transform_sections(cls, html_sections: Dict[str, Tag | ResultSet]) -> Dict[str, str | List[pd.DataFrame]]:

        """
        Converts BeautifulSoup objects into strings (from <p> tags) and Pandas DataFrames (from <table> tags), and stores the results in a dictionary.
        Args:
            html_sections: (dict[str, Tag | ResultSet]): A dictionary containing the BeautifulSoup objects of the relevant report sections.
        Returns:
            dict[str, str | list[pd.DataFrame]]: A dictionary containing the content of relevant report sections in string or Pandas DataFrame formats.
        """

        transformed_sections = {}
        
        for key, value in html_sections.items():
            if isinstance(value, ResultSet) and all([t.name == 'table' for t in value]):
                transformed_sections[key] = custom_table_to_df(value)
            
            else:
                transformed_sections[key] = p_to_str(value)
        
        transformed_sections['industry_rankings'] = cls._rankings(transformed_sections['overview'], transformed_sections['business_activity_text'])
        transformed_sections['respondents'] = cls._respondents_say(transformed_sections['comments'])

        return transformed_sections
    
    @classmethod
    def _rankings(cls, overview: str, business_activity_text: str) -> pd.DataFrame:
        
        """
        Ranks the sectors based on the growth/contraction in the PMI and business activity.
        Args:
            overview (str): The report overview which contains a list of growing and contracting sectors.
            business_activity_text (str): The text under the "business activity" section which contains a list of growing and contracting sectors.
        Returns:
            pd.DataFrame: A Pandas DataFrame containing the PMI and business activity rankings for each sector.
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
    A class to represent the US Michigan Consumer Survey.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data.copy(deep=True)

    @property
    def data(self) -> pd.DataFrame:
        return self._data.copy(deep=True)
    
    @classmethod
    def web_extract(cls) -> ConsumerSurvey | None:
        
        # Fetch the US Michigan Consumer Index, and the Current and Expected Components
        index_url = "https://www.sca.isr.umich.edu/files/tbcics.csv"
        components_url = "https://www.sca.isr.umich.edu/files/tbciccice.csv"

        with WebSession() as session:
            response_index = session.get(index_url)
            response_components = session.get(components_url)
        
        try:
            assert response_index and response_components
            # Wrap response string in file-like object for read_csv
            df1 = pd.read_csv(io.StringIO(response_index.text), sep=",", skiprows=4)
            df2 = pd.read_csv(io.StringIO(response_components.text), sep=",", skiprows=4)
            data = cls._process_df(df1, df2)

            return cls(data)
        
        except Exception as e:
            web_scraping_logger.exception(f'Failed to fetch the Consumer Survey data from: {index_url or components_url}{" and " + (components_url or index_url) if (index_url and components_url) else ""}\nError: {e}\n\n')
            return None
    
    @classmethod
    def _process_df(cls, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        # Drop empty columns and rows; define column names and data types
        df1.dropna(axis=1, how='all', inplace=True)
        df1.dropna(axis=0, how='all', inplace=True)
        df1.columns = ["Month", "Year", "Index"]
        df1 = df1.astype({"Month": 'string', "Year": int, "Index": 'Float64'})
        
        df2.dropna(axis=1, how='all', inplace=True)
        df2.dropna(axis=0, how='all', inplace=True)
        df2.columns = ["Month", "Year", "Current Index", "Expected Index"]
        df2 = df2.astype({"Month": 'string', "Year": int, "Current Index": 'Float64', "Expected Index": 'Float64'})

        # Merge the two dataframes and re-order columns
        df = df1.merge(df2)
        df = df[["Year", "Month", "Index", "Current Index", "Expected Index"]]
        
        return df

#%%
class ConstructionSurvey:

    """
    A class to represent the US Census Bureau Construction Survey.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data.copy(deep=True)

    @property
    def data(self) -> pd.DataFrame:
        return self._data.copy(deep=True)
    
    @classmethod
    def web_extract(cls) -> ConstructionSurvey | None:
        
        # Fetch the US Census Bureau Construction Survey data
        url = "https://www.census.gov/construction/nrc/xls/newresconst.xlsx"

        with WebSession() as session:
            response = session.get(url)

        try:
            assert response
            # Wrap response content in file-like object to process the excel file
            xl = pd.ExcelFile(io.BytesIO(response.content))  
            data = cls._process_df(xl)
            return cls(data)
        
        except Exception as e:
            web_scraping_logger.exception(f"Failed to fetch the Construction Survey data from: {url}\nError: {e}\n\n")
            return None
        
    @classmethod
    def _process_df(cls, xl: pd.ExcelFile) -> pd.DataFrame:
        # Parse first sheet to extract months
        df = xl.parse(0)
        first_col = df.iloc[:, 0].astype('string')

        # Get prev year and current year from first column
        pattern = r'^([0-9]{4})'
        years = first_col.str.extract(pattern).dropna()[0:2]
        prev_year = int(years.squeeze().iloc[0])
        curr_year = int(years.squeeze().iloc[1])

        # Get month names from first column
        pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)'
        months = first_col.str.extract(pattern).dropna()[0:13]
        months.reset_index(drop=True, inplace=True)

        # Create dataframe
        df = pd.DataFrame(months).astype('string')
        df.columns = ["Month"]

        # Add year column; detect where year changes (December -> January)
        year_change_bool = (df["Month"] == "December") & (df["Month"].shift(-1) == "January")
        year_change_idx = year_change_bool[year_change_bool].index[0]
        year_col = [prev_year for i in range(0, year_change_idx + 1)] + [curr_year for i in range(year_change_idx + 1, len(df))]
        df.insert(0, "Year", year_col)
        df["Year"] = df["Year"].astype(int)

        # Copy dataframe; extract data columns from other sheets and add to dataframe
        data = df.copy()
        for name in xl.sheet_names:
            df = xl.parse(name)
            df.dropna(inplace=True)
            df.reset_index(drop=True, inplace=True)
            data_series = df.iloc[0:13, 1].astype('Float64')
            data[f"Total {name.split(' - ')[1]}"] = data_series

        return data
    
#%%
class EuroSurvey:

    """
    A class to represent the EU Economic Survey.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data.copy(deep=True)

    @property
    def data(self) -> pd.DataFrame:
        return self._data.copy(deep=True)
    
    @classmethod
    def web_extract(cls) -> EuroSurvey | None:
        
        # Fetch the EU Economic Survey data
        url = "https://ec.europa.eu/economy_finance/db_indicators/surveys/documents/series/nace2_ecfin_2504/main_indicators_sa_nace2.zip"

        with WebSession() as session:
            response = session.get(url)

        try:
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
            web_scraping_logger.exception(f"Failed to fetch the EU Economic Survey data from: {url}\nError: {e}\n\n")
            return None
        
    @classmethod
    def _process_df(cls, df: pd.DataFrame) -> pd.DataFrame:
        # Drop empty columns
        df.dropna(axis=1, how='all', inplace=True)

        # Rename first column to Date
        df.columns.values[0] = "Date"

        # Add year and month columns
        df.insert(1, "Year", df["Date"].dt.year)
        df["Year"] = df["Year"].astype(int)

        months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        df.insert(2, "Month", df["Date"].dt.month.apply(lambda x: months_list[x - 1]))
        df["Month"] = df["Month"].astype('string')

        # Format dates and set all numerical columns to float type
        df["Date"] = df["Date"].dt.strftime("%d-%m-%Y")
        df.iloc[:, 3:] = df.iloc[:, 3:].astype('float64')

        return df

#%%
class CaixinPmi:

    """
    A class to represent the Caixin PMI from Trading Economics.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data.copy(deep=True)

    @property
    def data(self) -> pd.DataFrame:
        return self._data.copy(deep=True)
    
    @classmethod
    def web_extract(cls) -> CaixinPmi | None:

        # Fetch the Caixin manufacturing and services PMI data
        man_url = "https://tradingeconomics.com/china/manufacturing-pmi"
        ser_url = "https://tradingeconomics.com/china/services-pmi"

        with WebSession() as session:
            response_manufacturing = session.get(man_url)
            response_services = session.get(ser_url)

        try:
            assert response_manufacturing and response_services
            # Find relevant html tags and obtain text
            man_text = BeautifulSoup(response_manufacturing.text, 'html.parser').find(id="description").text
            ser_text = BeautifulSoup(response_services.text, 'html.parser').find(id="description").text

            # Parse text to obtain current and last month's indices
            man_data = cls._parse_html(man_text)
            ser_data = cls._parse_html(ser_text)

            # Create dataframe
            data = [man_data["prev_year"], man_data["prev_month"], man_data["prev_index"], ser_data["prev_index"]], [man_data["year"], man_data["month"], man_data["index"], ser_data["index"]]
            data = pd.DataFrame(data, columns=["Year", "Month", "Manufacturing PMI", "Services PMI"])
            data = data.astype({"Year": int, "Month": 'string', "Manufacturing PMI": 'Float64', "Services PMI": 'Float64'})

            return cls(data)
        
        except Exception as e:
            web_scraping_logger.exception(f'Failed to fetch the Caixin PMI data from: {man_url or ser_url}{" and " + (ser_url or man_url) if (man_url and ser_url) else ""}\nError: {e}\n\n')
            return None
        
    @staticmethod
    def _parse_html(text: str) -> Dict[str, str | int | float]:

        # Get PMI index, current month and current year
        index, month, year  = re.findall(r"(\d{2}(?:\.\d{1,2})?) in ([A-Za-z]+) (\d{4})", text)[0]

        # Get previous index value
        pattern = (
            r"(?<!expectations of )"
            r"(?<!expectation of )"
            r"(?<!forecasts of )"
            r"(?<!forecast of )"
            r"(?<!estimates of )"
            r"(?<!estimate of )"
            r"(?<!projections of )"
            r"(?<!projection of )"
            r"(?<!predictions of )"
            r"(?<!prediction of )"
            r"(?<!\d{1})"
            r"(?<!\d{2})"
            r"(?<!January )(?<!February )(?<!March )(?<!April )"
            r"(?<!May )(?<!June )(?<!July )(?<!August )"
            r"(?<!September )(?<!October )(?<!November )(?<!December )"
            r"(\d{2}(?:\.\d{1,2})?)"
        )
        prev_index = re.findall(pattern, text)[1]

        # Get previous month and year
        months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        prev_month = months_list[months_list.index(month) - 1]
        year = int(year)
        if prev_month == "December":
            prev_year = year - 1
        else:
            prev_year = year

        return {"index": index, "month": month, "year": year, "prev_index": prev_index, "prev_month": prev_month, "prev_year": prev_year}
    
#%%
class FinvizSreener:

    """
    A class to represent the Finviz Stock Screener.
    """
    _col_nums = [1, 2, 79, 3, 4, 5, 129, 6, 7, 8, 9, 10, 11, 12, 13, 73, 74, 75, 14, 130, 131, 15, 16, 77, 17, 18, 19, 20, 21, 23, 22, 132, 133, 82, 78, 127, 128,
                 24, 25, 85, 26, 27, 28, 29, 30, 31, 84, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
                 134, 125, 126, 59, 68, 70, 80, 83, 76, 60, 61, 62, 63, 64, 67, 69, 81, 86, 87, 88, 65, 66]
    _default_col_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 14 ,37, 42, 43, 44, 45, 46, 47, 48, 49, 52, 53, 68, 65]
    _default_rows = 5500
    
    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data.copy(deep=True)

    @property
    def data(self) -> pd.DataFrame:
        return self._data.copy(deep=True)
    
    @classmethod
    def web_extract(cls, num_rows: int | None = None, view_col_nums: List[int] | None = None) -> FinvizSreener | None:

        # Define url for viewing all columns
        url = "https://finviz.com/screener.ashx?v=151&f=ind_stocksonly&o=ticker&c=" + (',').join([str(i) for i in cls._col_nums])
        
        # Set default values and check input types
        if not num_rows: 
            num_rows = cls._default_rows
        else:
            try:
                num_rows = int(num_rows)
            except ValueError:
                raise ValueError("Number of rows must be an integer.")
            
        if view_col_nums == 'all':
            view_col_nums = cls._col_nums
        elif not view_col_nums or view_col_nums=='default':
            view_col_nums = cls._default_col_nums
        else:
            try:
                view_col_nums = [int(i) for i in view_col_nums]
            except ValueError:
                raise ValueError("Column numbers must be input as a list of integers.")

        # Fetch the Finviz Stock Screener data
        with WebSession() as session:
            
            # Finviz shows 20 rows per page; update url (increase r by steps of 20) to navigate through pages 
            for count in range(1, num_rows, 20):
                try:
                    if count == 1:
                        response = session.get(url)
                        assert response
                        df = pd.read_html(io.StringIO(response.text))[-2]

                    elif count > 1:
                        url = url + "&r=" + str(count)
                        response = session.get(url)
                        assert response
                        df_i = pd.read_html(io.StringIO(response.text))[-2]
                        df = pd.concat([df, df_i], ignore_index=True)

                except Exception as e:
                    web_scraping_logger.exception(f'Failed to fetch the Finviz Stock Screener data from: {url}\nError: {e}\n\n')
                    return None

        try:
            # Process dataframe to ensure correct types and handling missing values
            data = cls._process_df(df)

            # Select subset of columns to view
            num_name_dict = {num: name for num, name in zip(cls._col_nums, data.columns)}
            view_col_names = [num_name_dict[i] for i in view_col_nums]
            data = data[view_col_names]

        except Exception as e:
            web_scraping_logger.exception(f"Failed to fetch the Finviz Stock Screener data from: {url}\nError: {e}\n\n")
            return None

        return cls(data)
    
    @classmethod
    def _process_df(cls, df: pd.DataFrame) -> pd.DataFrame:
        
        # Convert all columns to string
        df = df.astype('string')

        # Track df column names and name updates
        updated_cols = list(df.columns)

        #Drop duplicate rows
        df.drop_duplicates(inplace=True)

        # Detect cols with real number followed by M, B, or K suffixes
        pattern = r'(?<=\d\.\d{2})[MBK]'
        suffix_cols = [c for c in df.columns if df[c].str.contains(pattern, regex=True, na=False).any()]

        # Detect cols with real number followed by % symbol
        pattern = r'(?<=\d\.\d{2})[%]'
        pct_cols = [c for c in df.columns if df[c].str.contains(pattern, regex=True, na=False).any()]

        # Detect cols with dates
        pattern = r'\d{1,2}/\d{1,2}/\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}'
        date_cols = [c for c in df.columns if df[c].str.contains(pattern, regex=True, na=False).any()]

        # Detect cols with no alphabets and dashes(representing columns to be convererted to float types)
        pattern = r'[A-z/]+|\s-\s'
        float_cols = [c for c in df.columns if not df[c].str.contains(pattern, regex=True, na=False).any()]

        # Treat each col with M/B/K suffixes
        for col in suffix_cols:

            # Get scale factor for conversion to millions
            arr = df[col].to_numpy().astype(str)
            scale = np.where(np.char.find(arr, 'B') != -1, 1000, np.where(np.char.find(arr, 'K') != -1, 0.001, 1))

            # Eliminate suffixes, empty strings, and "non-float characters"
            pattern = {r'(?<=\d\.\d{2})[MBK]': '', r'[^0-9eE\.\+\-]': '', r'^(-)?$': pd.NA}
            df[col].replace(pattern, regex=True, inplace=True)

            # Convert to float and multiply by scale factor
            df[col] = df[col].astype('Float64') * scale

            # Adjust column names
            updated_cols[updated_cols.index(col)] = col + ' (m USD)'

        # Treat each col with % symbols
        for col in pct_cols:

            # Eliminate empty strings, and "non-float characters"
            pattern = {r'[^0-9eE\.\+\-]': '', r'^(-)?$': pd.NA}
            df[col].replace(pattern, regex=True, inplace=True)

            # Convert to float and multiply by scale factor
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
            df[col].replace(pattern, regex=True, inplace=True)

            # Convert to datetime
            if col == "Earnings":
                df[col] = pd.to_datetime(df[col] + f' {pd.Timestamp.today().year}', format='%b %d %Y').dt.strftime('%d/%m/%Y') # Test Dec-Jan cases
            else:
                df[col] = pd.to_datetime(df[col], format='%m/%d/%Y').dt.strftime('%d/%m/%Y')

        # Treat each col wih float types
        for col in float_cols:
    
            # Eliminate empty strings, and "non-float characters"
            pattern = {r'[^0-9eE\.\+\-]': '', r'^(-)?$': pd.NA}
            df[col].replace(pattern, regex=True, inplace=True)

            # Convert to float
            df[col] = df[col].astype('Float64')

        # Eliminate empty strings and hyphens from remaining (string type)columns
        pattern = {r'^(-)?$': pd.NA}
        df.replace(pattern, regex=True, inplace=True)

        # Update column names
        df.columns = updated_cols

        return df

#%%
class MarketData:

    def __init__(self, commodities: Commodities | None, stocks: Stocks | None, bonds: Bonds | None, currencies: Currencies | None, crypto: Crypto | None) -> None:
        if commodities: self._commodities = commodities
        if stocks: self._stocks = stocks
        if bonds: self._bonds = bonds
        if currencies: self._currencies = currencies
        if crypto: self._crypto = crypto

    @property
    def commodities(self) -> Commodities:
        return self._commodities
    
    @property
    def stocks(self) -> Stocks:
        return self._stocks
    
    @property
    def bonds(self) -> Bonds:
        return self._bonds
    
    @property
    def currencies(self) -> Currencies:
        return self._currencies
    
    @property
    def crypto(self) -> Crypto:
        return self._crypto
        

    @classmethod
    def web_extract(cls) -> MarketData:
        
        # Commodities
        data = cls._main(url='https://tradingeconomics.com/commodities')
        if data:
            category_dict, all = data
            commodities = Commodities(category_dict, all)
        else:
            commodities = None

        # Stocks
        data = cls._main(url='https://tradingeconomics.com/stocks')
        if data:
            category_dict, all = data
            stocks = Stocks(category_dict, all)
        else:
            stocks = None

        # Bonds
        data = cls._main(url='https://tradingeconomics.com/bonds')
        if data:
            category_dict, all = data
            bonds = Bonds(category_dict, all)
        else:
            bonds = None

        # Currencies
        data = cls._main(url='https://tradingeconomics.com/currencies')
        if data:
            category_dict, all = data
            currencies = Currencies(category_dict, all)
        else:
            currencies = None

        # Crypto
        data = cls._main(url='https://tradingeconomics.com/crypto')
        if data:
            category_dict, all = data
            crypto = Crypto(category_dict, all)
        else:
            crypto = None

        return cls(commodities, stocks, bonds, currencies, crypto)

    @classmethod
    def _main(cls, url: str) -> Tuple[dict[str, pd.DataFrame], pd.DataFrame] | None:
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
            all = cls._combine_dfs(clean_dfs)

            return category_dict, all

        except Exception as e:
            web_scraping_logger.exception(f"Failed to fetch data from Trading Economics: {url}\nError: {e}\n\n")
            return None

    @classmethod
    def _clean_df(cls, df: pd.DataFrame) -> pd.DataFrame:
        df_copy = df.copy()

        # Drop empty columns
        df_copy.dropna(axis=1, how='all', inplace=True)

        # Eliminate %, $, commas and M suffixes
        pattern = {r'[%,$]': '', r'(?<=[0-9])M': ''}
        df_copy.replace(pattern, regex=True, inplace=True)

        # Drop Day column
        df_copy.drop(columns=['Day'], errors='ignore', inplace=True)
        
        # Rename columns, ignored if column not present in DataFrame
        df_copy.rename(columns={'%': 'Day %', 'Weekly': 'Weekly %', 'Monthly': 'Monthly %', 'YTD': 'YTD %', 'YoY': 'YoY %', 'MarketCap': 'Market Cap (m USD)'}, inplace=True)
        
        # Convert columns to float or string
        for col in df_copy.columns:
            try:
                df_copy[col] = df_copy[col].astype('Float64')
            except ValueError:
                df_copy[col] = df_copy[col].astype('string')
    
        return df_copy
    
    @classmethod
    def _split_units(cls, clean_df: pd.DataFrame) -> pd.DataFrame:
        
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
    
    @classmethod
    def _combine_dfs(cls, dfs: List[pd.DataFrame]) -> pd.DataFrame:
        dfs_copy = [df.copy(deep=True) for df in dfs]

        # Add category column and rename first column
        for df in dfs_copy:
            df.insert(1, 'Category', df.columns[0])
            df.columns = ['Item'] + list(df.columns[1:])

        # Concatenate DataFrames
        df_combined = pd.concat(dfs_copy, axis=0, ignore_index=True)

        return df_combined
    
class Commodities(MarketData):

    def __init__(self, category_dict: Dict[str, pd.DataFrame], all: pd.DataFrame) -> None:
        self._all = all
        self._category_dict = category_dict
    
    @property
    def all(self) -> pd.DataFrame:
        return self._all
    
    def __getattr__(self, name: str) -> pd.DataFrame:
        if name in self._category_dict:
            return self._category_dict[name]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}' or no such category data.")
        
class Stocks(MarketData):

    def __init__(self, category_dict: Dict[str, pd.DataFrame], all: pd.DataFrame) -> None:
        self._all = all
        self._category_dict = category_dict
    
    @property
    def all(self) -> pd.DataFrame:
        return self._all
    
    def __getattr__(self, name: str) -> pd.DataFrame:
        if name in self._category_dict:
            return self._category_dict[name]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}' or no such category data.")

class Bonds(MarketData):

    def __init__(self, category_dict: Dict[str, pd.DataFrame], all: pd.DataFrame) -> None:
        self._all = all
        self._category_dict = category_dict
    
    @property
    def all(self) -> pd.DataFrame:
        return self._all
    
    def __getattr__(self, name: str) -> pd.DataFrame:
        if name in self._category_dict:
            return self._category_dict[name]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}' or no such category data.")
        
class Currencies(MarketData):

    def __init__(self, category_dict: Dict[str, pd.DataFrame], all: pd.DataFrame) -> None:
        self._all = all
        self._category_dict = category_dict
    
    @property
    def all(self) -> pd.DataFrame:
        return self._all
    
    def __getattr__(self, name: str) -> pd.DataFrame:
        if name in self._category_dict:
            return self._category_dict[name]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}' or no such category data.")
        
class Crypto(MarketData):

    def __init__(self, category_dict: Dict[str, pd.DataFrame], all: pd.DataFrame) -> None:
        self._all = all
        self._category_dict = category_dict
    
    @property
    def all(self) -> pd.DataFrame:
        return self._all
    
    def __getattr__(self, name: str) -> pd.DataFrame:
        if name in self._category_dict:
            return self._category_dict[name]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}' or no such category data.")