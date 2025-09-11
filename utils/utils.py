from IPython.display import display, Markdown
import json
import pandas as pd
from pathlib import Path
import re

def logs_to_df() -> pd.DataFrame | None:
    """
    Converts log files to a Pandas DataFrame.

    Args:
        startswith: str
        The name of the log file to convert. (default: Path(LOGGING_CONST.file_path).name)

    Returns:
        df: pd.DataFrame
        A Pandas DataFrame containing the log data.
    """
    log_files = Path(__file__).resolve().parent.parent.rglob('*.log')
    json_rows = []
    for log_file in log_files:
        with log_file.open("r", encoding="utf-8") as f:
            lines = [line for line in f.readlines() if line]
            json_rows += [json.loads(line) for line in lines]
    
    if json_rows:
        df = pd.DataFrame(json_rows)
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S,%f", errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")
            df = df.sort_values("time")
        return df
    
def MarkDownDisplay(obj: str | pd.DataFrame, bold: bool=False, italic: bool=False, block: bool=False, align: str='left', index: bool=False):
    """
    Creates a Markdown-formatted string and for displaying text and DataFrames in the Jupyter notebook.

    Args:
        obj: str | pd.DataFrame
        The text or DataFrame to display.

        bold: bool=False
        If True, the text or DataFrame index/header will be displayed in bold.

        italic: bool=False
        If True, the text or DataFrame index/header will be displayed in italics.

        block: bool=False
        If True, the text or DataFrame will be displayed in a block element.

        align: str='left'
        The alignment of the text or DataFrame.

        index: bool=False
        If True, the DataFrame will display index column.
    """
    if type(obj) not in (str, pd.DataFrame): 
        raise TypeError('Function only prints strings and DataFrames.')
    
    if type(obj) == str:
        text = obj
        text = re.sub(r'(?<!\n)\n(?!\n)', '<br><br>', text)
        if italic: text = f'<i>{text}</i>'
        if bold: text = f'<b>{text}</b>'
        text = f'<p style="text-align: {align}";>{text}</p>'
        if block: text = f'>{text}'
        display(Markdown(text))
    
    elif type(obj) == pd.DataFrame:
        html = obj.to_html(index=index, na_rep='&nbsp;', border=1)
        if italic: html = re.sub(r'(<th>)(.*)(</th>)', '\\1<i>\\2</i>\\3', html)
        if bold: html = re.sub(r'(<th>)(.*)(</th>)', '\\1<b>\\2</b>\\3', html)
        html = f'<div align="{align}">{html}</div>'
        if block: html = f'>{html}'
        display(Markdown(html))