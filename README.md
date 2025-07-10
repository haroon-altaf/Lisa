## Lisp
A program to scrape and manipulate some leading economic indicators, market data, and stock data from various sources online. This web-scraping program is intended to be part of a larger "web-application".


### The goal of the web-app will be: 
- To display a monthly timeseries of leading economic indicators for the US, Europe, and to a lesser extent China.
- Trend analyses of economic data, particularly highlighting the growth/contraction in various industry sectors and ranking based on bullish/bearish sentiment.
- Fetching, displaying, and exporting stock and industry level data from Finviz (eliminating the need of a paid Finviz subscription).


### To accomplish this, broadly 3 steps are to be carried out:
1. Write a program that can reliably and consistently obtain (scrape) data from different online sources; clean transform data as necessary.
2. Design a database that stores scraped data; write a program that safely loads scraped data into this database, at a defined frequency.
3. Build a web application that will query and display data from the database; scope of this is TBC.


### Currently:
Step 1 has been completed, i.e., the latest releases of selected economic data can be obtained using the program. Step 2 is underway.

The program currently consists of 4 files. 
1. "static.py" contains some static data; 
2. "utility.py" contains some functions and a class for managing HTTP requests, used throughout the code;
3. "loggers.py" is used to configure logging of traceback errors into a txt file.
4. **"Scrapers.py" is where the majority of the web-scraping logic and functionality is written.** 


## Usage
See example usage of code in this [**jupyer notebook (via nbviewer)**](https://nbviewer.org/github/haroon-altaf/lisp/blob/main/Notebook.ipynb)

## Setup
**Python version: 3.13.3**

1. Cloning the repository
   ```bash
   cd [path where you want to clone the repository]
   git clone https://github.com/haroon-altaf/lisp
   cd lisp
2. Create virtual environment and activate
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
3. Install required packages into environemnt
   ```bash
   pip install -r requirements.txt
4. Run code

   Create new python file or jupyter notebook; alternatively adapt Notebook.ipynb which contains some examples. 
