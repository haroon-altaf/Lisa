#%%
from __future__ import annotations                                                                                        
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet
from concurrent.futures import ThreadPoolExecutor, as_completed
from loggers import web_scraping_logger    
import pandas as pd
import random
import requests
from requests.adapters import HTTPAdapter
import threading
from typing import List, Dict
from urllib3.util.retry import Retry

"""A module containing utility functions and classes for web scraping tasks."""

#%%
class WebSession:
    """
    A thread-safe, high-performance web session client that manages concurrent requests using an internal thread pool.

    This class handles automatic retries, user-agent rotation, and session renewal. It is designed to be used as a context manager.

    Example:
        urls = ["http://example.com"] * 10
        with ConcurrentWebSession(max_workers=5) as session:
            results = session.get_many(urls)
            for url, response in results.items():
                if response:
                    print(f"Got {url} with status {response.status_code}")
    """

    def __init__(
        self,
        timeout: int = 10,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        session_renewal_interval: int = 1000,
        ua_list: list[str] = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1"
        ]
    ):
        """
        Initializes the WebSession.

        Args:
            max_workers (int): The number of concurrent threads to use for requests.
            timeout (int): Default timeout for each web request in seconds.
            max_retries (int): Maximum number of retries for failed requests.
            backoff_factor (float): Factor to determine sleep time between retries.
            ua_rotation_interval (int): Rotate user-agent after this many successful requests.
            session_renewal_interval (int): Renew the entire session after this many requests.
            ua_list (list[str]): A list of user-agent strings to rotate through. Defaults to a built-in list.
        """
        self.timeout = timeout
        self.session_renewal_interval = session_renewal_interval
        self.ua_list = ua_list

        self._retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        self._lock = threading.Lock()
        self._session = self._init_session()
        self.success_count = 0

    def _init_session(self) -> requests.Session:
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=self._retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            "User-Agent": random.choice(self.ua_list),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Connection": "keep-alive"
        })
        return session        

    def get(self, url: str) -> requests.Response | None:
        """
        Makes a single, thread-safe GET request. This method handles all underlying rotation/renewal logic and is safe 
        to be called from multiple threads.

        Args:
            url (str): The URL to request.

        Returns:
            A requests.Response object on success, otherwise None.
        """

        try:
            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Lock acquired only for quick state changes
            with self._lock:
                self.success_count += 1
                current_count = self.success_count
                if current_count % self.session_renewal_interval == 0:
                    self._session.close()
                    self._session = self._init_session()

            return response

        except requests.exceptions.RequestException as e:
            web_scraping_logger.error(f"Request failed for {url}: {e}")
            return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

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