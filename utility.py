#%%
from __future__ import annotations                                                                                        
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet
from loggers import web_scraping_logger    
import pandas as pd
import random
import requests
from requests.adapters import HTTPAdapter
from typing import List, Dict
from urllib3.util.retry import Retry

"""A module containing utility functions and classes for web scraping tasks."""

#%%
"""
WebSession class for managing web requests with user-agent rotation and session renewal.

Attributes:
    timeout (int): Timeout for requests in seconds.
    ua_rotation_interval (int): Number of successful requests before rotating the user-agent.
    session_renewal_interval (int): Number of successful requests before renewing the session.
    success_count (int): Counter for successful requests.
    prev_url (str): Previous URL to use as a referer.
    user_agent (str): Current user-agent string.
    retry_strategy (Retry): Retry strategy for handling request failures.
    session (requests.Session): The session object for making requests.

Methods:
    __enter__(): Returns the WebSession object for use in a context manager.
    __exit__(exc_type, exc_val, exc_tb): Closes the session when exiting the context manager.
    __init__(timeout, max_retries, backoff_factor, ua_rotation_interval, session_renewal_interval, ua_list): Initializes the WebSession object.
    _init_session(): Initializes a requests.session with retry strategy.
    _rotateuser_agent(): Rotates the user-agent string.
    _renew_session(): Renews the session by closing and reinitializing it.
    get(url): Makes a GET request to the specified URL with appropriate headers and handles retries. Exposed as a public method.

"""
class WebSession:

    def __init__(
        self,
        timeout: int = 10,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        ua_rotation_interval: int = 500,
        session_renewal_interval: int = 1000,
        ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", 
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"
        ]
    ):
        self.timeout = timeout
        self.ua_rotation_interval = ua_rotation_interval
        self.session_renewal_interval = session_renewal_interval
        self.success_count = 0
        self.prev_url = "https://google.com"
        self.ua_list = ua_list
        self.user_agent = random.choice(ua_list)

        self.retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            raise_on_status=False
        )
        self._init_session()

    def _init_session(self):
        self.session = requests.Session()
        self.session.headers.update({"Accept-Language": "en-US,en;q=0.9", "User-Agent": self.user_agent})
        adapter = HTTPAdapter(max_retries=self.retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _rotate_user_agent(self):
        self.user_agent = random.choice(self.ua_list)
        self.session.headers.update({"User-Agent": self.user_agent})

    def _renew_session(self):
        self.session.close()
        self._init_session()

    def get(self, url: str) -> requests.Response | None:
        
        """
        Makes a GET request to the specified URL with appropriate headers and handles retries.
        Args:
            url (str): The URL to make the GET request to.
        Returns:
            requests.Response | None: The response object if the request is successful, None otherwise.
        """

        if self.success_count and self.success_count % self.ua_rotation_interval == 0:
            self._rotate_user_agent()

        if self.success_count and self.success_count % self.session_renewal_interval == 0:
            self._renew_session()

        headers = {
            "User-Agent": self.user_agent,
            "Referer": self.prev_url
        }

        try:
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            self.prev_url = url
            self.success_count += 1
            return response
        
        except requests.exceptions.RequestException as e:
            web_scraping_logger.exception(f"Request to {url} failed: {e}")
            return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

#%%
def find_content(html_content: BeautifulSoup, search_tag: str, search_attrs: Dict[str, str] = {}, methods: List[Dict[str, str | Dict[str, str]]] = []) -> Tag | ResultSet:

    """
    Extracts, from the full HTML content of a webpage obtained using BeautifulSoup, the HTML content of the relevant report sections.
    First the find() method is applied to the html_content using the specified search_tag and search_attrs.
    Then, further methods in the methods list are applied to the object returned by find(), sequentially, to navigate in the HTML tree.

    Args:
        html_content (BeautifulSoup): The full HTML content of the webpage as a BeautifulSoup object.
        search_tag (str): The HTML tag to search for using the find() method.
        search_attrs (Dict): A dictionary of attributes to search for using the find() method.
        methods (List): A list of dictionaries, each containing the: 
                        (i) method to use, e.g., 'find_next_sibling' or 'find_parent'
                        (ii) the HTML tag to search for using this method, e.g., 'p' or 'table'
                        (iii) a dictionary of attribute: value pairs to search for using this method, e.g., {'class_': 'text-center'}

    Returns:
        Tag | ResultSet: The HTML content of a relevant section of the report, returned as a Tag or ResultSet (list of Tags) object.
    """

    target = html_content.find(search_tag, **search_attrs)
    if methods:
        for method in methods:
            method_name = method['name']
            method_tag = method['tag']
            method_attrs = method['attrs']
            target = getattr(target, method_name)(method_tag, **method_attrs)
    return target   

#%%
def p_to_str(html: Tag | ResultSet) -> str:

    """
    Converts a BeautifulSoup Tag or ResultSet object with <p> tags to a string.
    ResultSet elements are joined with newlines; nested <br> tags are translated to newlines.
    "*" characters are removed.

    Args:
        html (Tag | ResultSet): The beautifulsoup object to convert.

    Returns:
        str: The text within Tag/ResultSet elements processed as strings.
    """

    if isinstance(html, Tag):
        nested_tags = list(html.children)
        any_br_tags = any([t.name == 'br' for t in nested_tags])
        if any_br_tags:
            return "\n".join(list(html.stripped_strings)).replace('*', '')
        
        else:
            return html.get_text().replace('*', '')
    
    elif isinstance(html, ResultSet): 
        return "\n".join([t.get_text() for t in html]).replace('*', '')

 #%%   
def custom_table_to_df(table_list: ResultSet) -> List[pd.DataFrame]:
        
        """
        Converts a BeautifulSoup ResultSet object with <Table> tags to a list of Pandas DataFrame objects.
        "*" characters are removed from table axes and numerical values are converted to floats where valid.
        This function is used instead of pandas.read_html() to handle complex tables with dual headers and merged cells.

        Args:
            table_list (ResultSet): The Beautifulsoup ResultSet object to convert. This is iterable and accessible as a list.

        Returns:
            list[pd.DataFrame]: A list of Pandas DataFrame onjects.
        """

        extracted_tables = []
        for table in table_list:
            table_data = []
            rows = table.find_all('tr')

            # Check for dual headers
            cells = rows[0].find_all(['th', 'td'])
            any_merged_cells = any([cell.has_attr('colspan') for cell in cells])
            num_headers = 2 if any_merged_cells else 1

            # Extract one or all headers
            multi_index_arrays = []
            for row_idx in range(num_headers):
                cells = rows[row_idx].find_all(['th', 'td'])
                col_names = [cell.get_text(strip=True).replace('*', '') for cell in cells]
                col_spans = [int(cell.get('colspan', 1))  for cell in cells]
                header = []
                for name, span in zip(col_names, col_spans): header += [name] * span
                multi_index_arrays.append(header)
            multi_index = pd.MultiIndex.from_arrays(multi_index_arrays)

            # Extract table rows
            for row in rows[row_idx + 1:]:
                cells = row.find_all(['th', 'td'])
                merged_cells = int(cells[0].get('colspan', 1)) - 1
                row_data = [cells[0].get_text(strip=True)] + [None] * merged_cells + [cell.get_text(strip=True) for cell in cells[1:]]
                row_data = [cell.replace('*', '') if cell else '' for cell in row_data]
                for index, value in enumerate(row_data):
                    try:
                        row_data[index] = float(value)
                    except ValueError:
                        pass
                table_data.append(row_data)

            # Convert to DataFrame
            df = pd.DataFrame(table_data)
            df.columns = multi_index
            df = df.set_index(df.columns[0])
            if isinstance(df.index.name, tuple):
                df.index.name = df.index.name[-1]
            df = df.fillna('')
            extracted_tables.append(df)
        
        return extracted_tables