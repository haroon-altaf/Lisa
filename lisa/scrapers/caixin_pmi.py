from __future__ import annotations

import re

import pandas as pd
from bs4 import BeautifulSoup

from lisa.common import DBConnection, TemplateLogger, WebSession
from lisa.database_model import Caixin_PMI

from .utils import MONTHS

URL_MAN = "https://tradingeconomics.com/china/manufacturing-pmi"
URL_SER = "https://tradingeconomics.com/china/services-pmi"

logger = TemplateLogger(__name__).logger


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
        load: Uploads the Caixin Manufacturing and Services PMI data to the database.
        _parse_text: Parses webpage text to extract PMI index, month, and year.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self._table = data.copy(deep=True)

    @property
    def table(self) -> pd.DataFrame:
        return self._table.copy(deep=True)

    @classmethod
    def download(cls) -> CaixinPmi | None:
        man_data = cls._main(URL_MAN)
        ser_data = cls._main(URL_SER)
        if man_data is None or ser_data is None:
            return None
        data = man_data.merge(ser_data, how="outer", on=["Year", "Month"])
        data = data.astype(
            {"Year": "Int64", "Month": "Int64", "Manufacturing PMI": "Float64", "Services PMI": "Float64"}
        )
        return cls(data)

    @classmethod
    def _main(cls, url: str) -> pd.DataFrame | None:
        with WebSession() as session:
            response = session.get(url)
        if not response:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        tags = soup.find_all(class_="comment more")
        if not tags:
            logger.error("Failed to find HTML tags containing relevant text.")
            return None

        try:
            texts = [tag.text for tag in tags]
        except AttributeError:
            logger.exception(f"Failed to extract text from one or more HTML tags.\n{tags}")
            return None

        table_data = [cls._parse_text(text) for text in texts]
        if not all(table_data):
            return None

        col_name = "Manufacturing PMI" if url == URL_MAN else "Services PMI"
        df = pd.DataFrame(table_data, columns=["Year", "Month", col_name])
        df = df.sort_values(by=["Year", "Month"], ignore_index=True)
        return df

    def load(self) -> None:
        column_map = Caixin_PMI.column_map()
        table_name = Caixin_PMI.name()
        df = self.table
        df_cols = df.columns

        new_cols = set(df_cols) - column_map.keys()
        if new_cols:
            raise ValueError(f"No column mapping exists for:\n{new_cols}")

        data_rows = df.rename(columns=column_map).to_dict(orient="records")
        with DBConnection() as conn:
            conn.upsert_rows(table_name=table_name, data_rows=data_rows)

    @staticmethod
    def _parse_text(text: str) -> tuple[int, int, float] | None:
        match = re.findall(r"(\d{2}(?:\.\d{1,2})?) in ([A-Za-z]+) (\d{4})", text)

        if not match:
            logger.error(f"Failed to parse text.\n{text}")
            return None
        else:
            index, month, year = match[0]

        try:
            index = float(index)
            year = int(year)
            month = MONTHS[month.upper().strip()].value
        except (ValueError, KeyError):
            logger.exception(f"Unexpected data or data types obtained.\nYear: {year}\nMonth: {month}\nIndex: {index}")
            return None

        return (year, month, index)
