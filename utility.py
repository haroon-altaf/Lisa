from __future__ import annotations                                                                                        
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import pandas as pd
from pathlib import Path
import random
import requests
from requests.adapters import HTTPAdapter
from static import LOGGING_CONST, GET_REQ_CONST, DB_CONST
import sqlalchemy as db
from sqlalchemy.dialects.sqlite import insert
from typing import List, Dict, Any, Set, Iterable, Tuple
from urllib3.util.retry import Retry

class JSONFormatter(logging.Formatter):
    """
    Class for specifying JSON logging format.
    """
    def format(self, record, datefmt='%Y-%m-%d %H:%M:%S') -> str:
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "filename": record.filename,
            "lineno": record.lineno,
            "funcName": record.funcName,
            "message": record.getMessage()
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)
    
class TemplateLogger:
    """
    Class for generating standard loggers for use in multiple modules.
    """
    def __init__(
        self,
        name: str,
        log_path: str = LOGGING_CONST.file_path,
        encoding: str = LOGGING_CONST.encoding,
        rotation_when: str = LOGGING_CONST.rotation_when,
        rotation_interval: int = LOGGING_CONST.rotation_interval,
        rotation_backups: int = LOGGING_CONST.rotation_backups,
        file_level: int = LOGGING_CONST.file_level,
        file_format: logging.Formatter = JSONFormatter(),
        console_level: int = LOGGING_CONST.console_level,
        console_format: logging.Formatter = logging.Formatter(LOGGING_CONST.console_formatter, datefmt='%Y-%m-%d %H:%M:%S'),
    ) -> None:

        self.logger = logging.getLogger(name)
        self.logger.setLevel(10)
        self.logger.propagate = False

        if not self.logger.handlers:
            file_handler = TimedRotatingFileHandler(log_path, encoding=encoding, when=rotation_when, interval=rotation_interval, backupCount=rotation_backups)
            file_handler.setLevel(file_level)
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(console_level)
            console_handler.setFormatter(console_format)
            self.logger.addHandler(console_handler)

logger = TemplateLogger(__name__).logger

class DBTransaction:
    """
    Class for handling database operations. Commit and rollback occur when context manager exits.
    """
    def __init__(self, path: str = DB_CONST.path) -> None:
        self._engine = db.create_engine(f"sqlite:///{path}")
        self._metadata = db.MetaData()
        self._connection = self._engine.connect()

    def upsert_rows(self, table_name: str, data_rows: List[Dict[str, Any]], delete_first: bool = False) -> None: 

        table = db.Table(table_name, self._metadata, autoload_with=self._engine)
        pk_columns, name_types_dict = self._table_schema(table)
        incoming_name_types_dict = {name: type(value) for name, value in data_rows[0].items()}
        self._pre_load_checks(table, incoming_name_types_dict, name_types_dict)

        if delete_first:
            self._connection.execute(table.delete())

        n_col = len(data_rows[0])
        n_rows = len(data_rows)
        chunk_size = DB_CONST.exe_limit // n_col
        n_chunks = int(n_rows/chunk_size) + (n_rows % chunk_size > 0)
        
        for i in range(n_chunks):
            data_rows_i = data_rows[i*chunk_size : (i+1)*chunk_size]
            stmt = insert(table).values(data_rows_i)
            stmt = stmt.on_conflict_do_update(
                index_elements=pk_columns, 
                set_={c.name: stmt.excluded[c.name] for c in table.columns if c.name not in pk_columns}
            )
            self._connection.execute(stmt)
       
        print(f"Successful upsert in {table_name}.")
    
    def _pre_load_checks(self, table: db.Table, incoming_name_types_dict: Dict[str, Any], name_types_dict: Dict[str, Any], ) -> None: 

        new_columns = self._new_columns(incoming_name_types_dict.keys(), name_types_dict.keys())
        if new_columns:
            raise ValueError(f"Received column names must match column names in table: {table.name}.\nNew columns not in database:\n{sorted(list(new_columns))}.")
        
        missing_columns = self._missing_columns(incoming_name_types_dict.keys(), name_types_dict.keys())
        if missing_columns:
            logger.warning(f"The following columns exist in database but are missing from received data:\n{sorted(list(missing_columns))}")
        
        type_mismatches = self._mismatching_types(incoming_name_types_dict, name_types_dict)
        if type_mismatches:
            raise ValueError(f"Received column types must match column types in table: {table.name}.\nMismatches:\n{type_mismatches}")
    
    def df_from_sql(self, table_name: str) -> pd.DataFrame:
        return pd.read_sql_table(table_name, self._engine)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._connection.commit()
        else:
            self._connection.rollback()
        self._connection.close()

    @staticmethod
    def _table_schema(table: db.Table) -> Tuple[List[str], Dict[str, Any]]:
        primary_keys = [c.name for c in table.primary_key]
        types_dict = {c.name: c.type.python_type for c in table.columns}
        return primary_keys, types_dict

    @staticmethod
    def _new_columns(incoming_columns: Iterable, expected_columns: Iterable) -> Set[str]:
        return set(incoming_columns) - set(expected_columns)
    
    @staticmethod
    def _missing_columns(incoming_columns: Iterable, expected_columns: Iterable) -> Set[str]:
        return set(expected_columns) - set(incoming_columns)
    
    @staticmethod
    def _mismatching_types(incoming_types_dict: Dict[str, Any], expected_types_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        mismatches = [
            {"Column": name, "Received type": typ, "Required type": expected_types_dict[name]}
            for name, typ in incoming_types_dict.items()
            if typ not in {
                type(None),
                expected_types_dict[name],
                int if expected_types_dict[name] is float else type(None), # relaxation: accept integers when floats expected; not vice versa
            }
        ]
        return mismatches

class WebSession:
    """
   Class to implement the resquests.get() method with automatic retries, headers, and session renewal (to avoid being blocked by sites).
   It is designed to be used as a context manager.
   """

    def __init__(
        self,
        timeout: int = GET_REQ_CONST.timeout,
        max_retries: int = GET_REQ_CONST.max_retries,
        backoff_factor: float = GET_REQ_CONST.backoff_factor,
        session_renewal_interval: int = GET_REQ_CONST.session_renewal_interval,
        ua_list: Tuple[str] = GET_REQ_CONST.ua_list
    ) -> None:
    
        self._timeout = timeout
        self._session_renewal_interval = session_renewal_interval
        self._ua_list = ua_list

        self._retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        self._session = self._init_session()
        self._success_count = 0

    def _init_session(self) -> requests.Session:
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=self._retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            "User-Agent": random.choice(self._ua_list),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Connection": "keep-alive"
        })
        return session        

    def get(self, url: str) -> requests.Response | None:
    
        try:
            response = self._session.get(url, timeout=self._timeout)
        except (requests.exceptions.RequestException, requests.exceptions.Timeout):
            logger.exception(f"GET request failed for: {url}")
            return None
        
        if not response.ok:
            logger.error(f"GET request failed for: {url}\nResponse code: {response.status_code}")
            return None
        
        self._success_count += 1
        current_count = self._success_count
        if current_count % self._session_renewal_interval == 0:
            self._session.close()
            self._session = self._init_session()
        return response


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

def find_content(
    html_content: BeautifulSoup,
    search_tag: str,
    search_attrs: Dict[str, str] = {},
    methods: List[Dict[str, str | Dict[str, str]]] = []
) -> Tag | ResultSet | None:

    """
    Extracts HTML content of the relevant report sections.
    First the find() method is applied to the html_content using the specified search_tag and search_attrs.
    Then, further methods specified in the methods list are applied to the object returned by find(), sequentially, to navigate in the HTML tree.

    Args:
        html_content: BeautifulSoup
        The full HTML content of the webpage as a BeautifulSoup object.
        
        search_tag: str
        The HTML tag to search for using the find() method.
        
        search_attrs: Dict[str, str]
        A dictionary of attributes to search for using the find() method.
        
        methods: List[Dict[str, str | Dict[str, str]]]
        A list of dictionaries, each containingfurther methods to chain onto the find() method.

    Returns:
        target: Tag | ResultSet
        The HTML content of a relevant section of the report, returned as a Tag or ResultSet (list of Tags) object.
    """

    target = html_content.find(search_tag, **search_attrs)
    if not target:
        logger.error(f"Failed to find tag: {search_tag} with attributes: {search_attrs}")
        return None
    
    if methods:
        for method in methods:
            method_name = method['name']
            method_tag = method['tag']
            method_attrs = method['attrs']
            target = getattr(target, method_name)(method_tag, **method_attrs)
            if not target:
                logger.error(f"Failed on method: {method_name} to find tag: {method_tag} with attributes: {method_attrs}")
                return None
    
    return target

def p_to_str(html: Tag | ResultSet) -> str:

    """
    Converts a BeautifulSoup Tag or ResultSet object with <p> tags to a string.
    ResultSet elements are joined with newlines; nested <br> tags are translated to newlines; asterisks are removed.

    Args:
        html: Tag | ResultSet
        The beautifulsoup object to convert.

    Returns:
        str: The text within Tag/ResultSet elements as strings.
    """
    try:
        if isinstance(html, Tag):
            nested_tags = list(html.children)
            any_br_tags = any([t.name == 'br' for t in nested_tags])
            if any_br_tags:
                return "\n".join(list(html.stripped_strings)).replace('*', '')
            else:
                return html.get_text().replace('*', '')
        
        elif isinstance(html, ResultSet):        
            return "\n".join([t.get_text() for t in html]).replace('*', '')
        
    except AttributeError:
        logger.exception(f"Failed to extract text from tag.\n{html}")
        return None

def custom_table_to_df(table_list: ResultSet) -> List[pd.DataFrame]:
        
        """
        Converts a BeautifulSoup ResultSet object with <Table> tags to a list of Pandas DataFrame objects.
        Asterisks are removed from table axes and numerical values are converted to floats where valid.
        This function is used instead of pandas.read_html() to handle complex tables with dual headers and merged cells.

        Args:
            table_list: ResultSet
            The Beautifulsoup ResultSet object to convert. This is iterable and accessible as a list.

        Returns:
            extracted_tables: List[pd.DataFrame]
            A list of Pandas DataFrame objects.
        """

        if not isinstance(table_list, ResultSet):
            logger.error(f"Object is not a ResultSet.\n{table_list}")
            return None
        
        if not all([t.name == 'table' for t in table_list]):
            logger.error(f"Object is not a list of <table> tags.\n{table_list}")
            return None

        extracted_tables = []
        for table in table_list:
            table_data = []
            rows = table.find_all('tr')
            if len(rows) < 1:
                logger.error(f"Empty table encountered.\n{table}")
                return None

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
            if isinstance(df.index.name, tuple): df.index.name = df.index.name[-1]
            df = df.fillna('')
            extracted_tables.append(df)
        
        return extracted_tables[0]

def set_private_attr(obj: Any, d: Dict[str, Any]) -> None:
    """
    Sets private attributes (starting with '_') for a class instance using key:value pairs.
    This distcionary unpacking is helpful when lots of attributes are being set at once.

    Args:
        obj: Any
        The instance of a class to set attributes for.

        d: Dict[str, Any]
        A dictionary of key:value pairs.
    
    Returns:
        None
    """
    [setattr(obj, f'_{k}', v) for k, v in d.items()]

def set_class_prop(obj: Any, d: Dict[str, Any]) -> None:
    """
    Sets class properties (allowing public access to private attributes) for class instance using key:value pairs.
    This is helpful when a @property is needed to provide read-only access to lots of attributes.
    For dataframes, a copy of the DataFrame is returned preventing modifications.

    Args:
        obj: Any
        The instance of a class to set attributes for.

        d: Dict[str, Any]
        A dictionary of key:value pairs.
    
    Returns:
        None
    """
    for k in d.keys():
        def get_fn(obj, k=k):
            v = getattr(obj, f'_{k}')
            return v.copy(deep=True) if isinstance(v, pd.DataFrame) else v
        setattr(obj.__class__, k, property(get_fn))

def logs_to_df(startswith: str =Path(LOGGING_CONST.file_path).name) -> pd.DataFrame | None:
    """
    Converts log files to a Pandas DataFrame.

    Args:
        startswith: str
        The name of the log file to convert. (default: Path(LOGGING_CONST.file_path).name)

    Returns:
        df: pd.DataFrame
        A Pandas DataFrame containing the log data.
    """

    log_files = Path.cwd().rglob(f"{startswith}*")
    json_rows = []
    for log_file in log_files:
        with log_file.open("r", encoding="utf-8") as f:
            lines = [line for line in f.readlines() if line]
            json_rows += [json.loads(line) for line in lines]
    
    if json_rows:
        df = pd.DataFrame(json_rows)
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"], errors="coerce")
            df = df.sort_values("time")
        return df