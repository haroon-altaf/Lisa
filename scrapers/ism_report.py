from __future__ import annotations  
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet
from common import WebSession, DBConnection, TemplateLogger
from database_model import US_Man_Pmi_Report, US_Ser_Pmi_Report, US_Man_Industry_Ranking, US_Ser_Industry_Ranking
from datetime import datetime
from .html_dictionary import ISM_MAN_REPORT_STRUCTURE, ISM_SER_REPORT_STRUCTURE
import io                                                                               
import pandas as pd
import re
from typing import List, Dict, Tuple
from urllib.parse import urlparse
from .utils import MONTHS, find_content, p_to_str, custom_table_to_df, set_private_attr, set_class_prop

URL_MAN = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/pmi/"
URL_SER = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/services/"
MAN_SECTORS = (
    "Apparel, Leather & Allied Products",
    "Chemical Products",
    "Computer & Electronic Products",
    "Electrical Equipment, Appliances & Components",
    "Fabricated Metal Products",
    "Food, Beverage & Tobacco Products",
    "Furniture & Related Products",
    "Machinery",
    "Miscellaneous Manufacturing",
    "Nonmetallic Mineral Products",
    "Paper Products",
    "Petroleum & Coal Products",
    "Plastics & Rubber Products",
    "Primary Metals",
    "Printing & Related Support Activities",
    "Textile Mills",
    "Transportation Equipment",
    "Wood Products"
)
SERV_SECTORS = (
    "Accommodation & Food Services",
    "Agriculture, Forestry, Fishing & Hunting",
    "Arts, Entertainment & Recreation",
    "Construction",
    "Educational Services",
    "Finance & Insurance",
    "Health Care & Social Assistance",
    "Information",
    "Management of Companies & Support Services",
    "Mining",
    "Other Services",
    "Professional, Scientific & Technical Services",
    "Public Administration",
    "Real Estate, Rental & Leasing",
    "Retail Trade",
    "Transportation & Warehousing",
    "Utilities",
    "Wholesale Trade"
)

logger = TemplateLogger(__name__).logger

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
        load: Calls the _load_report_table and _load_rankings_table methods to upload records to the database.
        _main: Determines the report url; calls the _parse_html method _transform_sections method to extract report setions.
        _parse_html: Parses and extracts relevant report sections from webpage HTML.
        _transform_sections: Transforms extracted HTML content into strings (text) and Pandas DataFrames (tables); derives "rankings" and "comments".
        _rankings: Ranks the industry sectors based on their growth/contraction.
        _respondents_say: Extracts comments from respondents and stores them in a Pandas DataFrame.
        _load_report_table: Uploads report sections to the database.
        _load_rankings_table: Uploads sector rankings to the database.
        _prep_report_table: Prepares records from various report sections to be uploaded to the database.
        _prep_rankings_table: Prepares records from sector rankings to be uploaded to the database.
    """

    @classmethod
    def download_manufacturing(cls, url: str | None = None) -> ManufacturingPmi | None:
        cls._report_type = 'm'
        sections = cls._main(url)
        nones = [k for k, v in sections.items() if v is None]
        if nones:
            logger.error(f"Some sections of the ISM manufacturing report could not be processed correctly.\n{nones}")
        if len(nones) == len(sections):
            return None
        return ManufacturingPmi(sections)
    
    @classmethod
    def download_services(cls, url: str | None = None) -> ServicesPmi | None:
        cls._report_type = 's'
        sections = cls._main(url)
        nones = [k for k, v in sections.items() if v is None]
        if nones:
            logger.error(f"Some sections of the ISM services report could not be processed correctly.\n{nones}")
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
            if not parsed_url.scheme in ["http", "https"] or not parsed_url.netloc:
                raise ValueError("URL is not valid.")
            with WebSession() as session:
                response = session.get(url)   
        else:
            base_url = URL_MAN if cls._report_type == 'm' else URL_SER
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
        navigation_scheme = ISM_MAN_REPORT_STRUCTURE if cls._report_type == 'm' else ISM_SER_REPORT_STRUCTURE
        for section_name, navigation_steps in navigation_scheme.items():
                section_content = find_content(soup, navigation_steps)
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
        
        if transformed_sections['title']:
            words = transformed_sections['title'].split(' ')
            transformed_sections['month'] = MONTHS[words[0].upper().strip()].value
            transformed_sections['year'] = int(words[1])

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
                grow = lines[0].split(': ')[1].split(';')
                grow = [item.strip() for item in grow]
                grow[-1] = grow[-1].replace('and ','').replace('.', '')
                contract = lines[1].split(': ')[1].split(';')
                contract = [item.strip() for item in contract]
                contract[-1] = contract[-1].replace('and ','').replace('.', '')
            except Exception:
                logger.exception(f"Error in extracting sectors from text.\n{text}")
                return [None, None]
            
            if not set(grow + contract).issubset(sectors):
                logger.error(f"Unexpected sector names in text.\n{set(grow + contract) - set(sectors)}\n{text}")
                return [None, None]

            return grow, contract

        # Rank sectors (overall)
        grow, contract = sectors_from_text(overview)
        if grow is None or contract is None:
            return None
        for index, item in enumerate(grow):
            df.loc[item, "PMI Rankings"] = len(grow) - index
        for index, item in enumerate(contract):
            df.loc[item, "PMI Rankings"] = index - len(grow)

        # Rank sectors (based on New Orders or Business Activity)
        grow, contract = sectors_from_text(rank_by)
        if grow is None or contract is None:
            return None
        for index, item in enumerate(grow):
            df.loc[item, col_name] = len(grow) - index
        for index, item in enumerate(contract):
            df.loc[item, col_name] = index - len(contract)

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

        # Split comments block into sentences
        txt = comments.split('\n')[1:-1]

        # For each comment, extract the sector and quote; store in dataframe
        pattern = (
            r'[\'"‘“‟]'
            r'(?P<quote>.+?)'
            r'[\'"’”]'
            r'\s+'
            r'[\[\(]'
            r'(?P<sector>.+?)'
            r'[\]\)]$'
        )
        pairs = []
        for comment in txt:
            search_res = re.search(pattern, comment)
            if not search_res:
                logger.error(f"Error in extracting comments from text.\n{comment}")
                return None
            pairs.append((search_res.group("sector"), search_res.group("quote")))

        df = pd.DataFrame(pairs, columns=["Sector", "Respondent Comments"]).set_index("Sector")
        
        return df
    
    def load(self) -> None:
        self._load_report_table()
        self._load_rankings_table()
    
    def _load_report_table(self) -> None:
        if isinstance(self, ManufacturingPmi):
            column_map = US_Man_Pmi_Report.column_map()
            table_name = US_Man_Pmi_Report.name()
        else:
            column_map = US_Ser_Pmi_Report.column_map()
            table_name = US_Ser_Pmi_Report.name()

        df = self._prep_report_table()
        df_cols = df.columns

        new_cols = set(df_cols) - column_map.keys()
        if new_cols:
            raise ValueError(f"No column mapping exists for:\n{new_cols}")
        
        data_rows = df.rename(columns=column_map).to_dict(orient='records')
        with DBConnection() as conn:
            conn.upsert_rows(table_name=table_name, data_rows=data_rows)

    def _load_rankings_table(self) -> None:
        if isinstance(self, ManufacturingPmi):
            column_map = US_Man_Industry_Ranking.column_map()
            table_name = US_Man_Industry_Ranking.name()
        else:
            column_map = US_Ser_Industry_Ranking.column_map()
            table_name = US_Ser_Industry_Ranking.name()
        
        df = self._prep_rankings_table()
        df_cols = df.columns

        new_cols = set(df_cols) - column_map.keys()
        if new_cols:
            raise ValueError(f"No column mapping exists for:\n{new_cols}")
        
        data_rows = df.rename(columns=column_map).to_dict(orient='records')
        with DBConnection() as conn:
            conn.upsert_rows(table_name=table_name, data_rows=data_rows)

    def _prep_report_table(self) -> pd.DataFrame:
        if isinstance(self, ManufacturingPmi):
            full_pmi_table = self.full_pmi_table
            new_orders_table = self.new_orders_table
            production_table = self.production_table
            employment_table = self.employment_table
            supplier_deliveries_table = self.supplier_deliveries_table
            inventories_table = self.inventories_table
            customer_inventories_table = self.customer_inventories_table
            prices_table = self.prices_table
            backlog_orders_table = self.backlog_orders_table
            export_orders_table = self.export_orders_table
            imports_table = self.imports_table
            buying_policy_table = self.buying_policy_table[self.buying_policy_table['Month']==self.month].sort_values('Category')

            data_row = pd.DataFrame(
                index=[0],
                data={
                    'year': int(self.year),
                    'month': int(self.month),
                    'headline': str(self.headline),
                    'highlights': str(self.highlights),
                    'overview': str(self.overview),
                    'comments': str(self.comments),
                    'commodities_up': str(self.comm_price_up),
                    'commodities_down': str(self.comm_price_down),
                    'commodities_short': str(self.comm_supply_short),
                    'index_summary': str(self.index_summary),
                    'new_orders': str(self.new_orders_text),
                    'production': str(self.production_text),
                    'employment': str(self.employment_text),
                    'supplier_deliveries': str(self.supplier_deliveries_text),
                    'inventories': str(self.inventories_text),
                    'customer_inventories': str(self.customer_inventories_text),
                    'prices': str(self.prices_text),
                    'backlog_orders': str(self.backlog_orders_text),
                    'export_orders': str(self.export_orders_text),
                    'imports': str(self.imports_text),
                    'buying_policy': str(self.buying_policy_text),
                    'pmi_index_value': float(full_pmi_table.iloc[0, 0]),
                    'pmi_direction': str(full_pmi_table.iloc[0, 3]),
                    'pmi_change_rate': str(full_pmi_table.iloc[0, 4]),
                    'pmi_trend_months': int(full_pmi_table.iloc[0, 5]),
                    'new_orders_index_value': float(full_pmi_table.iloc[1, 0]),
                    'new_orders_direction': str(full_pmi_table.iloc[1, 3]),
                    'new_orders_change_rate': str(full_pmi_table.iloc[1, 4]),
                    'new_orders_trend_months': int(full_pmi_table.iloc[1, 5]),
                    'production_index_value': float(full_pmi_table.iloc[2, 0]),
                    'production_direction': str(full_pmi_table.iloc[2, 3]),
                    'production_change_rate': str(full_pmi_table.iloc[2, 4]),
                    'production_trend_months': int(full_pmi_table.iloc[2, 5]),
                    'employment_index_value': float(full_pmi_table.iloc[3, 0]),
                    'employment_direction': str(full_pmi_table.iloc[3, 3]),
                    'employment_change_rate': str(full_pmi_table.iloc[3, 4]),
                    'employment_trend_months': int(full_pmi_table.iloc[3, 5]),
                    'supplier_deliveries_index_value': float(full_pmi_table.iloc[4, 0]),
                    'supplier_deliveries_direction': str(full_pmi_table.iloc[4, 3]),
                    'supplier_deliveries_change_rate': str(full_pmi_table.iloc[4, 4]),
                    'supplier_deliveries_trend_months': int(full_pmi_table.iloc[4, 5]),
                    'inventories_index_value': float(full_pmi_table.iloc[5, 0]),
                    'inventories_direction': str(full_pmi_table.iloc[5, 3]),    
                    'inventories_change_rate': str(full_pmi_table.iloc[5, 4]),
                    'inventories_trend_months': int(full_pmi_table.iloc[5, 5]),
                    'customer_inventories_index_value': float(full_pmi_table.iloc[6, 0]),
                    'customer_inventories_direction': str(full_pmi_table.iloc[6, 3]),    
                    'customer_inventories_change_rate': str(full_pmi_table.iloc[6, 4]),
                    'customer_inventories_trend_months': int(full_pmi_table.iloc[6, 5]),
                    'prices_index_value': float(full_pmi_table.iloc[7, 0]),
                    'prices_direction': str(full_pmi_table.iloc[7, 3]),    
                    'prices_change_rate': str(full_pmi_table.iloc[7, 4]),
                    'prices_trend_months': int(full_pmi_table.iloc[7, 5]),
                    'backlog_orders_index_value': float(full_pmi_table.iloc[8, 0]),
                    'backlog_orders_direction': str(full_pmi_table.iloc[8, 3]),    
                    'backlog_orders_change_rate': str(full_pmi_table.iloc[8, 4]),
                    'backlog_orders_trend_months': int(full_pmi_table.iloc[8, 5]),
                    'export_orders_index_value': float(full_pmi_table.iloc[9, 0]),
                    'export_orders_direction': str(full_pmi_table.iloc[9, 3]),    
                    'export_orders_change_rate': str(full_pmi_table.iloc[9, 4]),
                    'export_orders_trend_months': int(full_pmi_table.iloc[9, 5]),
                    'imports_index_value': float(full_pmi_table.iloc[10, 0]),
                    'imports_direction': str(full_pmi_table.iloc[10, 3]),    
                    'imports_change_rate': str(full_pmi_table.iloc[10, 4]),
                    'imports_trend_months': int(full_pmi_table.iloc[10, 5]),
                    'overall_economy_direction': str(full_pmi_table.iloc[11, 3]),    
                    'overall_economy_change_rate': str(full_pmi_table.iloc[11, 4]),
                    'overall_economy_trend_months': int(full_pmi_table.iloc[11, 5]),
                    'manufacturing_sector_direction': str(full_pmi_table.iloc[12, 3]),    
                    'manufacturing_sector_change_rate': str(full_pmi_table.iloc[12, 4]),
                    'manufacturing_sector_trend_months': int(full_pmi_table.iloc[12, 5]),
                    'new_orders_higher_pct': float(new_orders_table.iloc[0, 3]),
                    'new_orders_same_pct': float(new_orders_table.iloc[0, 4]),
                    'new_orders_lower_pct': float(new_orders_table.iloc[0, 5]),
                    'production_higher_pct': float(production_table.iloc[0, 3]),
                    'production_same_pct': float(production_table.iloc[0, 4]),
                    'production_lower_pct': float(production_table.iloc[0, 5]),
                    'employment_higher_pct': float(employment_table.iloc[0, 3]),
                    'employment_same_pct': float(employment_table.iloc[0, 4]),
                    'employment_lower_pct': float(employment_table.iloc[0, 5]),
                    'supplier_deliveries_slower_pct': float(supplier_deliveries_table.iloc[0, 3]),
                    'supplier_deliveries_same_pct': float(supplier_deliveries_table.iloc[0, 4]),
                    'supplier_deliveries_faster_pct': float(supplier_deliveries_table.iloc[0, 5]),
                    'inventories_higher_pct': float(inventories_table.iloc[0, 3]),
                    'inventories_same_pct': float(inventories_table.iloc[0, 4]),
                    'inventories_lower_pct': float(inventories_table.iloc[0, 5]),
                    'customer_inventories_reporting_pct': float(customer_inventories_table.iloc[0, 3]),
                    'customer_inventories_too_high_pct': float(customer_inventories_table.iloc[0, 4]),
                    'customer_inventories_about_right_pct': float(customer_inventories_table.iloc[0, 5]),
                    'customer_inventories_too_low_pct': float(customer_inventories_table.iloc[0, 6]),
                    'prices_higher_pct': float(prices_table.iloc[0, 3]),
                    'prices_same_pct': float(prices_table.iloc[0, 4]),
                    'prices_lower_pct': float(prices_table.iloc[0, 5]),
                    'backlog_orders_reporting_pct': float(backlog_orders_table.iloc[0, 3]),
                    'backlog_orders_higher_pct': float(backlog_orders_table.iloc[0, 4]),
                    'backlog_orders_same_pct': float(backlog_orders_table.iloc[0, 5]),
                    'backlog_orders_lower_pct': float(backlog_orders_table.iloc[0, 6]),
                    'export_orders_reporting_pct': float(export_orders_table.iloc[0, 3]),
                    'export_orders_higher_pct': float(export_orders_table.iloc[0, 4]),
                    'export_orders_same_pct': float(export_orders_table.iloc[0, 5]),
                    'export_orders_lower_pct': float(export_orders_table.iloc[0, 6]),
                    'imports_reporting_pct': float(imports_table.iloc[0, 3]),
                    'imports_higher_pct': float(imports_table.iloc[0, 4]),
                    'imports_same_pct': float(imports_table.iloc[0, 5]),
                    'imports_lower_pct': float(imports_table.iloc[0, 6]),
                    'capex_lead_time_hand_to_mouth_pct': float(buying_policy_table.iloc[0, 3]),
                    'capex_lead_time_thirty_days_pct': float(buying_policy_table.iloc[0, 4]),
                    'capex_lead_time_sixty_days_pct': float(buying_policy_table.iloc[0, 5]),
                    'capex_lead_time_ninety_days_pct': float(buying_policy_table.iloc[0, 6]),
                    'capex_lead_time_six_months_pct': float(buying_policy_table.iloc[0, 7]),
                    'capex_lead_time_year_plus_pct': float(buying_policy_table.iloc[0, 8]),
                    'capex_lead_time_avg': int(buying_policy_table.iloc[0, 9]),
                    'production_lead_time_hand_to_mouth_pct': float(buying_policy_table.iloc[1, 3]),
                    'production_lead_time_thirty_days_pct': float(buying_policy_table.iloc[1, 4]),
                    'production_lead_time_sixty_days_pct': float(buying_policy_table.iloc[1, 5]),
                    'production_lead_time_ninety_days_pct': float(buying_policy_table.iloc[1, 6]),
                    'production_lead_time_six_months_pct': float(buying_policy_table.iloc[1, 7]),
                    'production_lead_time_year_plus_pct': float(buying_policy_table.iloc[1, 8]),
                    'production_lead_time_avg': int(buying_policy_table.iloc[1, 9]),
                    'mro_lead_time_hand_to_mouth_pct': float(buying_policy_table.iloc[2, 3]),
                    'mro_lead_time_thirty_days_pct': float(buying_policy_table.iloc[2, 4]),
                    'mro_lead_time_sixty_days_pct': float(buying_policy_table.iloc[2, 5]),
                    'mro_lead_time_ninety_days_pct': float(buying_policy_table.iloc[2, 6]),
                    'mro_lead_time_six_months_pct': float(buying_policy_table.iloc[2, 7]),
                    'mro_lead_time_year_plus_pct': float(buying_policy_table.iloc[2, 8]),
                    'mro_lead_time_avg': int(buying_policy_table.iloc[2, 9])
                }
            )
        else:
            full_pmi_table = self.full_pmi_table
            new_orders_table = self.new_orders_table
            business_activity_table = self.business_activity_table
            employment_table = self.employment_table
            supplier_deliveries_table = self.supplier_deliveries_table
            inventories_table = self.inventories_table
            inventory_sentiment_table = self.inventory_sentiment_table
            prices_table = self.prices_table
            backlog_orders_table = self.backlog_orders_table
            export_orders_table = self.export_orders_table
            imports_table = self.imports_table

            data_row = pd.DataFrame(
                index=[0],
                data={
                    'year': int(self.year),
                    'month': int(self.month),
                    'headline': str(self.headline),
                    'highlights': str(self.highlights),
                    'overview': str(self.overview),
                    'comments': str(self.comments),
                    'commodities_up': str(self.comm_price_up),
                    'commodities_down': str(self.comm_price_down),
                    'commodities_short': str(self.comm_supply_short),
                    'index_summary': str(self.index_summary),
                    'new_orders': str(self.new_orders_text),
                    'employment': str(self.employment_text),
                    'supplier_deliveries': str(self.supplier_deliveries_text),
                    'inventories': str(self.inventories_text),
                    'prices': str(self.prices_text),
                    'backlog_orders': str(self.backlog_orders_text),
                    'export_orders': str(self.export_orders_text),
                    'imports': str(self.imports_text),
                    'business_activity': str(self.business_activity_text),
                    'inventory_sentiment': str(self.inventory_sentiment_text),
                    'pmi_index_value': float(full_pmi_table.iloc[0, 0]),
                    'pmi_direction': str(full_pmi_table.iloc[0, 3]),
                    'pmi_change_rate': str(full_pmi_table.iloc[0, 4]),
                    'pmi_trend_months': int(full_pmi_table.iloc[0, 5]),
                    'business_activity_index_value': float(full_pmi_table.iloc[1, 0]),
                    'business_activity_direction': str(full_pmi_table.iloc[1, 3]),
                    'business_activity_change_rate': str(full_pmi_table.iloc[1, 4]),
                    'business_activity_trend_months': int(full_pmi_table.iloc[1, 5]),
                    'new_orders_index_value': float(full_pmi_table.iloc[2, 0]),
                    'new_orders_direction': str(full_pmi_table.iloc[2, 3]),
                    'new_orders_change_rate': str(full_pmi_table.iloc[2, 4]),
                    'new_orders_trend_months': int(full_pmi_table.iloc[2, 5]),
                    'employment_index_value': float(full_pmi_table.iloc[3, 0]),
                    'employment_direction': str(full_pmi_table.iloc[3, 3]),
                    'employment_change_rate': str(full_pmi_table.iloc[3, 4]),
                    'employment_trend_months': int(full_pmi_table.iloc[3, 5]),
                    'supplier_deliveries_index_value': float(full_pmi_table.iloc[4, 0]),
                    'supplier_deliveries_direction': str(full_pmi_table.iloc[4, 3]),
                    'supplier_deliveries_change_rate': str(full_pmi_table.iloc[4, 4]),
                    'supplier_deliveries_trend_months': int(full_pmi_table.iloc[4, 5]),
                    'inventories_index_value': float(full_pmi_table.iloc[5, 0]),
                    'inventories_direction': str(full_pmi_table.iloc[5, 3]),    
                    'inventories_change_rate': str(full_pmi_table.iloc[5, 4]),
                    'inventories_trend_months': int(full_pmi_table.iloc[5, 5]),
                    'prices_index_value': float(full_pmi_table.iloc[6, 0]),
                    'prices_direction': str(full_pmi_table.iloc[6, 3]),    
                    'prices_change_rate': str(full_pmi_table.iloc[6, 4]),
                    'prices_trend_months': int(full_pmi_table.iloc[6, 5]),
                    'backlog_orders_index_value': float(full_pmi_table.iloc[7, 0]),
                    'backlog_orders_direction': str(full_pmi_table.iloc[7, 3]),    
                    'backlog_orders_change_rate': str(full_pmi_table.iloc[7, 4]),
                    'backlog_orders_trend_months': int(full_pmi_table.iloc[7, 5]),
                    'export_orders_index_value': float(full_pmi_table.iloc[8, 0]),
                    'export_orders_direction': str(full_pmi_table.iloc[8, 3]),    
                    'export_orders_change_rate': str(full_pmi_table.iloc[8, 4]),
                    'export_orders_trend_months': int(full_pmi_table.iloc[8, 5]),
                    'imports_index_value': float(full_pmi_table.iloc[9, 0]),
                    'imports_direction': str(full_pmi_table.iloc[9, 3]),    
                    'imports_change_rate': str(full_pmi_table.iloc[9, 4]),
                    'imports_trend_months': int(full_pmi_table.iloc[9, 5]),
                    'inventory_sentiment_index_value': float(full_pmi_table.iloc[10, 0]),
                    'inventory_sentiment_direction': str(full_pmi_table.iloc[10, 3]),    
                    'inventory_sentiment_change_rate': str(full_pmi_table.iloc[10, 4]),
                    'inventory_sentiment_trend_months': int(full_pmi_table.iloc[10, 5]),
                    'overall_economy_direction': str(full_pmi_table.iloc[12, 3]),    
                    'overall_economy_change_rate': str(full_pmi_table.iloc[12, 4]),
                    'overall_economy_trend_months': int(full_pmi_table.iloc[12, 5]),
                    'services_sector_direction': str(full_pmi_table.iloc[13, 3]),    
                    'services_sector_change_rate': str(full_pmi_table.iloc[13, 4]),
                    'services_sector_trend_months': int(full_pmi_table.iloc[13, 5]),
                    'new_orders_higher_pct': float(new_orders_table.iloc[0, 3]),
                    'new_orders_same_pct': float(new_orders_table.iloc[0, 4]),
                    'new_orders_lower_pct': float(new_orders_table.iloc[0, 5]),
                    'business_activity_higher_pct': float(business_activity_table.iloc[0, 3]),
                    'business_activity_same_pct': float(business_activity_table.iloc[0, 4]),
                    'business_activity_lower_pct': float(business_activity_table.iloc[0, 5]),
                    'employment_higher_pct': float(employment_table.iloc[0, 3]),
                    'employment_same_pct': float(employment_table.iloc[0, 4]),
                    'employment_lower_pct': float(employment_table.iloc[0, 5]),
                    'supplier_deliveries_slower_pct': float(supplier_deliveries_table.iloc[0, 3]),
                    'supplier_deliveries_same_pct': float(supplier_deliveries_table.iloc[0, 4]),
                    'supplier_deliveries_faster_pct': float(supplier_deliveries_table.iloc[0, 5]),
                    'inventories_higher_pct': float(inventories_table.iloc[0, 3]),
                    'inventories_same_pct': float(inventories_table.iloc[0, 4]),
                    'inventories_lower_pct': float(inventories_table.iloc[0, 5]),
                    'inventory_sentiment_too_high_pct': float(inventory_sentiment_table.iloc[0, 4]),
                    'inventory_sentiment_about_right_pct': float(inventory_sentiment_table.iloc[0, 5]),
                    'inventory_sentiment_too_low_pct': float(inventory_sentiment_table.iloc[0, 6]),
                    'prices_higher_pct': float(prices_table.iloc[0, 3]),
                    'prices_same_pct': float(prices_table.iloc[0, 4]),
                    'prices_lower_pct': float(prices_table.iloc[0, 5]),
                    'backlog_orders_higher_pct': float(backlog_orders_table.iloc[0, 4]),
                    'backlog_orders_same_pct': float(backlog_orders_table.iloc[0, 5]),
                    'backlog_orders_lower_pct': float(backlog_orders_table.iloc[0, 6]),
                    'export_orders_higher_pct': float(export_orders_table.iloc[0, 4]),
                    'export_orders_same_pct': float(export_orders_table.iloc[0, 5]),
                    'export_orders_lower_pct': float(export_orders_table.iloc[0, 6]),
                    'imports_higher_pct': float(imports_table.iloc[0, 4]),
                    'imports_same_pct': float(imports_table.iloc[0, 5]),
                    'imports_lower_pct': float(imports_table.iloc[0, 6])
                }
            )

        if data_row.isna().any().any():
            raise ValueError("Some sections of the ISM report are missing. Cannot proceed with database update.")
        
        return data_row
    
    def _prep_rankings_table(self) -> pd.DataFrame:
        if isinstance(self, ManufacturingPmi):
            data_row = \
            pd.Series({'Year': int(self.year), 'Month': int(self.month)}).to_frame().T\
            .join(self.sector_ranking['PMI Rankings'].to_frame().T.reset_index(drop=True))\
            .join(self.sector_ranking['New Orders Rankings'].to_frame().T.reset_index(drop=True), rsuffix=' - New Orders')
        
        else:
            data_row = \
            pd.Series({'Year': int(self.year), 'Month': int(self.month)}).to_frame().T\
            .join(self.sector_ranking['PMI Rankings'].to_frame().T.reset_index(drop=True))\
            .join(self.sector_ranking['Business Activity Rankings'].to_frame().T.reset_index(drop=True), rsuffix=' - Business Activity')

        if data_row.isna().any().any():
            raise ValueError("Rankings for some sectors are missing. Cannot proceed with database update.")
    
        return data_row
        
class ManufacturingPmi(IsmReport):
    """ Represents a Manufacturing PMI report from ISM.
        Each section of the report is unpacked from a dictionary and stored as a private attribute.
        Each private attribute is then exposed to public using class properties (@property).
    """

    def __init__(self, sections: Dict) -> None:
        set_private_attr(self, sections)
        set_class_prop(self, sections)
        

class ServicesPmi(IsmReport):
    """ Represents a Services PMI report from ISM.
        Each section of the report is unpacked from a dictionary and stored as a private attribute.
        Each private attribute is then exposed to public using class properties (@property).
    """

    def __init__(self, sections: Dict) -> None:
        set_private_attr(self, sections)
        set_class_prop(self, sections)