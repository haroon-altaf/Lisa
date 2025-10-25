## LISA - Leading Indicators Scraping and Analysis
A program to extract, transform, store, analyse and visualize various leading economic indicators and stock market data from online sources.

**Motiation for project:** 
- to learn development best practices and programming design patterns via building something concrete
- to document my learning journey and demonstrate current level of competence


## Usage
See example usage of code in [this notebook](https://github.com/haroon-altaf/lisp/blob/main/notebook.ipynb).


## Next Steps
See future development plans [here](https://github.com/users/haroon-altaf/projects/2).


## Setup
**Python version: 3.13.3**

1. Install uv if missing
   ```cmd
   pip install uv  
2. Clone the repository
   ```cmd
   git clone https://github.com/haroon-altaf/LISA
   cd LISA
3. Create virtual environment; install dependencies and src files
   ```cmd
   uv sync
4. Run code
   
   To explore code, create new python file or jupyter notebook; alternatively, adapt notebook.ipynb which contains some sample code.


## Project File Structure
   ```text
   LISA/
   |
   ├─ src/
   |  └─lisa/
   |    |
   |    ├─ common/
   |    │  ├─ __init__.py
   |    │  ├─ db_connection.py             # Creates SQLAlchemy engine and database methods
   |    |  ├─ web_session.py               # Provides context manager for requests sessions
   |    |  └─ template_logger.py           # Provides template logger class for use throughout code
   |    |
   |    ├─ scrapers/
   |    │  ├─ __init__.py
   |    │  ├─ ism_report.py                # extracts, transforms and loads data from ISM business reports
   |    │  ├─ html_dictionary.py           # contains information on navigating ISM reports' HTML
   |    │  ├─ consumer_survey.py           # extracts, transforms and loads UoM Consumer Survey data
   |    │  ├─ construction_survey.py       # extracts, transforms and loads US Buildings Survey data
   |    │  ├─ euro_survey.py               # extracts, transforms and loads EU economic sentiment data
   |    │  ├─ caixin_pmi.py                # extracts, transforms and loads Caixin PMI data
   |    │  ├─ finviz.py                    # extracts, transforms and loads stocks data from Finviz
   |    │  └─ trading_economics.py         # extracts, transforms and loads data from Trading Economics
   |    |
   |    ├─ utils/
   |    │  ├─ __init__.py
   |    │  └─ utils.py                     # Contains miscellaneous utility functions
   |    | 
   |    ├─ database_models/                # Contains SQLAlchemy ORM classes for each database table
   |       ├─ __init__.py
   |       └─ ...
   |
   ├─ data/
   |  └─Leading Indicators and Stocks.db   # SQLite database containing scraped data
   |
   ├─ notebook.ipynb                       # Jupyter notebook containing example code 
   ├─ pyproject.toml
   ├─ uv.lock
   ├─ README.md
   └─ .gitignore
   ```
