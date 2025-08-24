#%%
from __future__ import annotations  
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet
from datetime import datetime
import io
import logging                                                                                
import pandas as pd
from static import LOGGING_PARAMS, URL, MAN_REPORT, SERV_REPORT, MAN_SECTORS, SERV_SECTORS
from typing import List, Dict, Tuple
from urllib.parse import urlparse
from utility import WebSession, find_content, p_to_str, custom_table_to_df, set_private_attr, set_class_prop

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
class IsmReport:
    """ 
    Parent class for the ManufacturingPmi and ServicesPmi classes.
    Methods that are common to  both ManufacturingPmi and ServicesPmi are defined here.
    
    Attributes:
        _report_type: str
        The type of report to be downloaded ('m' for Manufacturing report and 's' for Services report).

    Methods:
        download_manufacturing: Calls the _main method and constructs a ManufacturingPmi object from the returned dictionary.
        download_services: Calls the _main method and constructs a ServicesPmi object from the returned dictionary.
        _main: Determines the report url; calls the _parse_html method _transform_sections method to extract report setions.
        _parse_html: Parses and extracts relevant report sections from webpage HTML.
        _transform_sections: Transforms extracted HTML content into strings (text) and Pandas DataFrames (tables); derives "rankings" and "comments".
        _rankings: Ranks the industry sectors based on their growth/contraction.
        _respondents_say: Extracts comments from respondents and stores them in a Pandas DataFrame.
    """

    @classmethod
    def download_manufacturing(cls, url: str | None = None) -> ManufacturingPmi | None:
        cls._report_type = 'm'
        sections = cls._main(url)
        nones = [k for k, v in sections.items() if v is None]
        if nones:
            logger.error(f"Some secctions of the ISM manufacturing report could not be processed correctly.\n{nones}")
        if len(nones) == len(sections):
            return None
        return ManufacturingPmi(sections)
    
    @classmethod
    def download_services(cls, url: str | None = None) -> ServicesPmi | None:
        cls._report_type = 's'
        sections = cls._main(url)
        nones = [k for k, v in sections.items() if v is None]
        if nones:
            logger.error(f"Some secctions of the ISM services report could not be processed correctly.\n{nones}")
        if len(nones) == len(sections):
            return None
        return ServicesPmi(sections)

    @classmethod
    def _main(cls, url: str | None = None) -> Dict[str, str | List[pd.DataFrame] | None]:
        """
        Extracts HTML content for each report section, transforms them into text and tables, and stores them in a NamedTuple.
        
        Args:
            url: str | None
            The url of the webpage from which the report is obtained. By default, the latest report is downloaded.
        
        Returns:
            sections: Dict[str, str | List[pd.DataFrame] | None]
            A dictionary containing report sections.
        """

        if url:
            if not isinstance(url, str):
                raise TypeError("URL must be a string")
            parsed_url = urlparse(url)
            if not parsed_url.scheme in ("http", "https") or bool(parsed_url.netloc):
                raise ValueError("URL is not valid.")
            with WebSession() as session:
                response = session.get(url)   
        else:
            base_url = URL.US_MAN_PMI.value if cls._report_type == 'm' else URL.US_SER_PMI.value
            prev_month = datetime.now().month - 1
            for i in range(2):
                month = datetime(1900, prev_month - i, 1).strftime("%B").lower()
                url = f"{base_url}{month}/"
                with WebSession() as session:
                    response = session.get(url)
                if response:
                    break
            
        if not response:
            return None
        
        html_content = response.text
        html_sections = cls._parse_html(html_content)
        sections = cls._transform_sections(html_sections)
        return sections

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
        scheme = MAN_REPORT if cls._report_type == 'm' else SERV_REPORT
        for section_name, search_formula in scheme.items():
                search_tag = search_formula['tag']
                search_attrs = search_formula['attrs']
                search_methods = search_formula['methods']
                section_content = find_content(soup, search_tag, search_attrs, search_methods)
                if not type(section_content) in [Tag, ResultSet]:
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
            
            if not 'table' in key:
                transformed_sections[key] = p_to_str(value)
            
            else:
                # Some table processing steps based on report section names (keys)
                if key == 'full_pmi_table':
                    df_list = custom_table_to_df(value)
                    transformed_sections[key] = df_list
                
                elif key == 'buying_policy_table':
                    try:
                        df_list = pd.read_html(io.StringIO(str(value)))
                    except (ValueError, TypeError, pd.errors.ParserError):
                        logger.exception(f"Error in reading html for section: {key}\n{value}")
                        transformed_sections[key] = None    
                    for df in df_list:
                        try:
                            dates = pd.to_datetime(df.iloc[:, 0], format='%b %Y')
                        except (ValueError, TypeError):
                            logger.exception(f"Error converting first column to datetime for section: {key}\n{df.head()}")
                            transformed_sections[key] = None
                        df.insert(0, 'Category', df.columns[0])
                        df.insert(0, 'Month', dates.dt.month)
                        df.insert(0, 'Year', dates.dt.year)
                    df = pd.concat(df_list)
                    df = df.dropna(axis=1, how ='any')
                    transformed_sections[key] = df
                
                else:
                    try:
                        df_list = pd.read_html(io.StringIO(str(value)))
                    except (ValueError, TypeError, pd.errors.ParserError):
                        logger.exception(f"Error in reading html for section: {key}\n{value}")
                        transformed_sections[key] = None
                    for df in df_list:
                        try:
                            dates = pd.to_datetime(df.iloc[:, 0], format='%b %Y')
                        except (ValueError, TypeError):
                            logger.exception(f"Error converting first column to datetime for section: {key}\n{df.head()}")
                            transformed_sections[key] = None
                        df.insert(0, 'Month', dates.dt.month)
                        df.insert(0, 'Year', dates.dt.year)
                    df = pd.concat(df_list) 
                    transformed_sections[key] = df
        
        rank_by = 'new_orders_text' if cls._report_type == 'm' else 'business_activity_text'
        if transformed_sections['overview'] and transformed_sections[rank_by]:
            transformed_sections['sector_ranking'] = cls._rankings(transformed_sections['overview'], transformed_sections[rank_by])
        else:
            transformed_sections['sector_ranking'] = None
        
        if transformed_sections['comments']:
            transformed_sections['respondents'] = cls._respondents_say(transformed_sections['comments'])
        else:
            transformed_sections['respondents'] = None

        return transformed_sections
    
    @classmethod
    def _rankings(cls, overview: str, rank_by: str) -> pd.DataFrame | None:
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
            sectors = MAN_SECTORS
            col_name = "New Orders Rankings"
        else:
            sectors = SERV_SECTORS
            col_name = "Business Activity Rankings"

        # Initiate empty dataframe with sectors as index
        df = pd.DataFrame({"Sectors": sectors, "PMI Rankings": [0] * len(sectors), f"{col_name}": [0] * len(sectors)}).set_index('Sectors')

        def sectors_from_text(text: str) -> Tuple[List[str] | None, List[str] | None]:
            try:
                lines = text.split('\n')[-1].split('. ')
                grow = lines[0].split(':')[1].split(';')
                grow = [item.strip() for item in grow]
                grow[-1] = grow[-1].replace('and ','').replace('.', '')
                contract = lines[1].split(':')[1].split(';')
                contract = [item.strip() for item in contract]
                contract[-1] = contract[-1].replace('and ','').replace('.', '')
                return grow, contract
            except Exception:
                logger.exception(f"Error in extracting sectors from text.\n{text}")
                return [None, None]

        # Rank sectors (overall)
        grow, contract = sectors_from_text(overview)
        if not grow or not contract:
            return None
        for index, item in enumerate(grow):
            df.loc[item, "PMI Rankings"] = len(grow) - index
        for index, item in enumerate(contract):
            df.loc[item, "PMI Rankings"] = -(len(contract) - index)

        # Rank sectors (based on New Orders or Business Activity)
        grow, contract = sectors_from_text(rank_by)
        if not grow or not contract:
            return None
        for index, item in enumerate(grow):
            df.loc[item, col_name] = len(grow) - index
        for index, item in enumerate(contract):
            df.loc[item, col_name] = -(len(contract) - index)

        return df

    
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

        # Initiate empty dataframe with sectors as index
        df = pd.DataFrame(columns=["Sectors", "Respondent Comments"]).set_index('Sectors')

        try:
            # Split comments block into sentences
            txt = comments.split('\n')[1:-1]

            # For each comment, extract the sector and quote; store in dataframe
            for comment in txt:
                quote, sector = comment.split('[')
                quote = quote[1:-2].strip()
                sector = sector[:-1].strip()
                df.loc[sector, "Respondent Comments"] = quote

        except Exception:
            logger.exception(f"Error in extracting comments from text.\n{comments}")
            return None

        return df
 
        
class ManufacturingPmi(IsmReport):
    """ Represents a Manufacturing PMI report from ISM.
        Each section of the report is unpacked from a dictionary and stored as a private attribute.
        Each private attribute is then exposed to public using class properties (@property).
    """

    def __init__(self, sections: Dict) -> None:

        # Set private attributes
        set_private_attr(self, sections)

        # Set properties for public access
        set_class_prop(self, sections)
        

class ServicesPmi(IsmReport):
    """ Represents a Services PMI report from ISM.
        Each section of the report is unpacked from a dictionary and stored as a private attribute.
        Each private attribute is then exposed to public using class properties (@property).
    """

    def __init__(self, sections: Dict) -> None:

        # Set private attributes
        set_private_attr(self, sections)

        # Set properties for public access
        set_class_prop(self, sections)