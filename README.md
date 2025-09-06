## Lisp
A program to extract, manipulate, store, and visualize various leading economic indicators and stock market data from online sources.

The program currently consists of 9 files. 
1. static.py - contains static data and configurable parameters, used in multiple places
2. utility.py - contains helper functions and a class for managing HTTP requests, used in multiple places
3. ism_report.py - contains code for scraping data from ISM manufacturing and services reports (US)
4. consumer_survey.py - contains code for scraping University of Michigan's consumer sentiment data (US)
5. construction_survey.py - contains code for scraping US Census Bureau's buildings survey data (US)
6. euro_survey.py - contains code for scraping European economic sentiment data (EU)
7. caixin_pmi,py - contains code for scraping caixin PMI data (China)
8. trading_economics.py - contains code for scraping price and performance data for various asset classes
9. finviz.py - contains code for scraping data from the FinViz stock screener

## Usage
See example usage of code in this [**jupyer notebook (via nbviewer)**](https://nbviewer.org/github/haroon-altaf/lisp/blob/25b3d595d215a2299108045fe66ed71aabc24d30/notebook.ipynb)

## Next Steps
- Write classes/functions to perform trend analysis and visualise economic data loaded into database.
- Produce Streamlit app to provide analysis and KPI dashboards

## Setup
**Python version: 3.13.3**

1. Cloning the repository
   ```cmd
   cd [path where you want to clone the repository]
   git clone https://github.com/haroon-altaf/lisp
   cd lisp
2. Create virtual environment and activate
   ```cmd
   python -m venv venv
   .\venv\Scripts\activate
3. Install required packages into environemnt
   ```cmd
   pip install -r requirements.txt
4. Run code

   Create new python file or jupyter notebook; alternatively, adapt notebook.ipynb which contains some examples. 
