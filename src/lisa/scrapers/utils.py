from __future__ import annotations

from enum import Enum
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag

from lisa.common import TemplateLogger

from .html_dictionary import bs4_args

logger = TemplateLogger(__name__).logger


class MONTHS(Enum):
    """Enum for interconverting month names and numbers."""

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


def set_private_attr(obj: Any, d: dict[str, Any]) -> None:
    """
    Sets private attributes (starting with '_') for a class instance using key:value pairs.
    This distcionary unpacking is helpful when lots of attributes are being set at once.

    Args:
        obj: Any
        The instance of a class to set attributes for.

        d: dict[str, Any]
        A dictionary of key:value pairs.

    Returns:
        None
    """
    [setattr(obj, f"_{k}", v) for k, v in d.items()]


def set_class_prop(obj: Any, d: dict[str, Any]) -> None:
    """
    Sets class properties (allowing public access to private attributes) for class instance using key:value pairs.
    This is helpful when a @property is needed to provide read-only access to lots of attributes.
    For dataframes, a copy of the DataFrame is returned preventing modifications.

    Args:
        obj: Any
        The instance of a class to set attributes for.

        d: dict[str, Any]
        A dictionary of key:value pairs.

    Returns:
        None
    """
    for k in d.keys():

        def get_fn(obj, k=k):
            v = getattr(obj, f"_{k}")
            return v.copy(deep=True) if isinstance(v, pd.DataFrame) else v

        setattr(obj.__class__, k, property(get_fn))


def find_content(html_soup: BeautifulSoup, steps: tuple[bs4_args]) -> Tag | ResultSet | None:
    """
    Extracts relevant sections from BeautifulSoup objects, by chaining a sequence of BeautifulSoup methods.

    Args:
        html_soup: BeautifulSoup
        The full HTML content of the webpage as a BeautifulSoup object.

        steps: tuple[bs4_args]
        A tuple of bs4_args objects. Each bs4_args object is a dataclass containing the name of the BeautifulSoup method to use, and the key-word arguments to pass to it.

    Returns:
        target: Tag | ResultSet
        The relevant secion of the BeautifulSoup object is returned as a Tag or ResultSet (list of Tags) object.
    """
    if not html_soup or not steps:
        return None

    target = html_soup
    for args in steps:
        method = args.method
        kwargs = {k: v for k, v in args.__dict__.items() if v != "" and k != "method"}
        target = getattr(target, method)(**kwargs)

    if not target:
        logger.error(f"Failed on method: {method} with key-word arguments: {kwargs}")
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
            any_br_tags = any([t.name == "br" for t in nested_tags])
            if any_br_tags:
                return "\n".join(list(html.stripped_strings)).replace("*", "")
            else:
                return html.get_text().replace("*", "")

        elif isinstance(html, ResultSet):
            return "\n".join([t.get_text() for t in html]).replace("*", "")

    except AttributeError:
        logger.exception(f"Failed to extract text from tag.\n{html}")
        return None


def custom_table_to_df(table_list: ResultSet) -> list[pd.DataFrame]:
    """
    Converts a BeautifulSoup ResultSet object with <Table> tags to a list of Pandas DataFrame objects.
    Asterisks are removed from table axes and numerical values are converted to floats where valid.
    This function is used instead of pandas.read_html() to handle complex tables with dual headers and merged cells.

    Args:
        table_list: ResultSet
        The Beautifulsoup ResultSet object to convert. This is iterable and accessible as a list.

    Returns:
        extracted_tables: list[pd.DataFrame]
        A list of Pandas DataFrame objects.
    """
    if not isinstance(table_list, ResultSet):
        logger.error(f"Object is not a ResultSet.\n{table_list}")
        return None

    if not all([t.name == "table" for t in table_list]):
        logger.error(f"Object is not a list of <table> tags.\n{table_list}")
        return None

    extracted_tables = []
    for table in table_list:
        table_data = []
        rows = table.find_all("tr")
        if len(rows) < 1:
            logger.error(f"Empty table encountered.\n{table}")
            return None

        # Check for dual headers
        cells = rows[0].find_all(["th", "td"])
        any_merged_cells = any([cell.has_attr("colspan") for cell in cells])
        num_headers = 2 if any_merged_cells else 1

        # Extract one or all headers
        multi_index_arrays = []
        for row_idx in range(num_headers):
            cells = rows[row_idx].find_all(["th", "td"])
            col_names = [cell.get_text(strip=True).replace("*", "") for cell in cells]
            col_spans = [int(cell.get("colspan", 1)) for cell in cells]
            header = []
            for name, span in zip(col_names, col_spans):
                header += [name] * span
            multi_index_arrays.append(header)
        multi_index = pd.MultiIndex.from_arrays(multi_index_arrays)

        # Extract table rows
        for row in rows[row_idx + 1 :]:
            cells = row.find_all(["th", "td"])
            merged_cells = int(cells[0].get("colspan", 1)) - 1
            row_data = (
                [cells[0].get_text(strip=True)]
                + [None] * merged_cells
                + [cell.get_text(strip=True) for cell in cells[1:]]
            )
            row_data = [cell.replace("*", "") if cell else "" for cell in row_data]
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
        df = df.fillna("")
        extracted_tables.append(df)

    return extracted_tables[0]
