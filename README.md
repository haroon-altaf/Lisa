## Lisp
A program to extract, manipulate, store, and visualize various leading economic indicators and stock market data from online sources.


## Usage
See example usage of code in this notebook via [**Github**](https://github.com/haroon-altaf/lisp/blob/main/notebook.ipynb) or [**via nbviewer**](https://nbviewer.org/github/haroon-altaf/lisp/blob/7391183c43533c146a7bbb46c4600f57bf3f2931/notebook.ipynb)


## Next Steps
- Write classes/functions to perform trend analysis and visualise economic data loaded into database.
- Produce Streamlit app to provide analysis and KPI dashboards


## Setup
**Python version: 3.13.3**

1. Cloning the repository
   ```cmd
   cd [your path]
   git clone https://github.com/haroon-altaf/lisp
2. Create virtual environment and activate
   ```cmd
   cd lisp
   python -m venv venv
   .\venv\Scripts\activate
3. Install required packages into environemnt
   ```cmd
   pip install -r requirements.txt
4. Run code

   Create new python file or jupyter notebook; alternatively, adapt notebook.ipynb which contains some sample code.

## File Structure
   ```text
    lisp/
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
   ├─ notebook.ipynb                     # Jupyter notebook with examples of code usage
   |
   ├─ .gitignore                         # Git ignore rules
   ├─ requirements.txt                   # Python dependencies
   └─ README.md                          # Project overview
   ```
