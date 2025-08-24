#%%
from __future__ import annotations  
from bs4 import BeautifulSoup
import logging                                                                               
import pandas as pd
import re
from static import LOGGING_PARAMS, URL, MONTHS
from typing import Tuple
from utility import WebSession

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
       man_data = cls._main(URL.CAIXIN_MAN_PMI.value)
       ser_data = cls._main(URL.CAIXIN_SER_PMI.value)
       if man_data is None or ser_data is None:
           return None
       return cls(man_data, ser_data)
       
    @classmethod
    def _main(cls, url: str) -> pd.DataFrame | None:
        
        with WebSession() as session:
            response = session.get(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tags = soup.find_all(class_="comment more")
        if not tags:
            logger.error(f"Failed to find HTML tags containing relevant text.")
            return None
        
        try:
            texts = [tag.text for tag in tags]
        except AttributeError:
            logger.exception(f"Failed to extract text from one or more HTML tags.\n{tags}")
            return None
        
        table_data = [cls._parse_text(text) for text in texts]
        if not all(table_data):
            return None

        col_name = "Manufacturing PMI" if url == URL.CAIXIN_MAN_PMI.value else "Services PMI"
        df = pd.DataFrame(table_data, columns=["Year", "Month", col_name])
        df = df.astype({"Year": 'Int64', "Month": 'Int64', col_name: 'Float64'})
        df = df.sort_values(by=['Year', 'Month'], ignore_index=True)
        return df
        
    @staticmethod
    def _parse_text(text: str) -> Tuple[int, int, float] | None:
        match = re.findall(r"(\d{2}(?:\.\d{1,2})?) in ([A-Za-z]+) (\d{4})", text)
        
        if not match:
            logger.error(f"Failed to parse text.\n{text}")
            return None
        else:
            index, month, year = match[0]

        try:
            index = float(index)
            year = int(year)
            month = int(MONTHS[month.upper().strip()].value)
        except (ValueError, KeyError):
            logger.exception(f"Unexpected data or data types obtained.\nYear: {year}\nMonth: {month}\nIndex: {index}")
            return None
        
        return (year, month, index)