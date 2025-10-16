## LISA - Leading Indicators Scraping and Analysis
A program to extract, transform, store, analyse and visualize various leading economic indicators and stock market data from online sources.


## Usage
See example usage of code in this notebook via [**Github**](https://github.com/haroon-altaf/lisp/blob/main/notebook.ipynb)

Run code online via [**Colab**](https://colab.research.google.com/github/haroon-altaf/LISA/blob/main/notebook.ipynb)


## Next Steps
- Create scheduler to extract, transform and load latest data at pre-determined times/intervals.
- Write classes/functions to perform trend analysis and visualise economic data loaded into database.
- Produce Streamlit app to provide analysis and KPI dashboards.


## Setup
**Python version: 3.13.3**

1. Install uv if missing
   ```cmd
   pip install uv  
2. Clone the repository
   ```cmd
   git clone https://github.com/haroon-altaf/LISA
3. Create virtual environment and install dependencies
   ```cmd
   cd LISA
   uv install
4. Run code
   Create new python file or jupyter notebook; alternatively, adapt notebook.ipynb which contains some sample code.


## File Structure (lisa)
   ```text
    lisa/
   |
   ├─ common/
   │  ├─ __init__.py
   │  ├─ db_connection.py                # Creates SQLAlchemy engine and database methods
   |  ├─ web_session.py                  # Provides context manager for requests sessions
   |  ├─ template_logger.py              # Provides template logger class for use throughout code
   |
   ├─ scrapers/
   │  ├─ __init__.py
   │  └─ ism_report.py                   # extracts, transforms and loads data from ISM business reports
   │  └─ html_dictionary.py              # contains information on navigating ISM reports' HTML
   │  └─ consumer_survey.py              # extracts, transforms and loads UoM Consumer Survey data
   │  └─ construction_survey.py          # extracts, transforms and loads US Buildings Survey data
   │  └─ euro_survey.py                  # extracts, transforms and loads EU economic sentiment data
   │  └─ caixin_pmi.py                   # extracts, transforms and loads Caixin PMI data
   │  └─ finviz.py                       # extracts, transforms and loads stocks data from Finviz
   │  └─ trading_economics.py            # extracts, transforms and loads data from Trading Economics
   |
   ├─ utils/
   │  ├─ __init__.py
   │  └─ utils.py                        # Contains miscellaneous utility functions
   | 
   ├─ database_models/                   # Contains SQLAlchemy ORM classes for each database table
   │  ├─ __init__.py
   │  └─ ...
   |
   ├─ Leading Indicators and Stocks.db   # SQLits database containing scraped data
   ```
