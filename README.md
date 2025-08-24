## Lisp
A program to scrape and transform some leading economic indicators and stock market data from various sources online.

The program currently consists of 4 files. 
1. static.py - contains some static data; 
2. utility.py - contains some functions and a class for managing HTTP requests, used throughout the code;
3. loggers.py - is used to configure logging of traceback errors into a txt file.
4. **scrapers.py -  is where the majority of the web-scraping and data-trasformation logic is written.** 

## Usage
See example usage of code in this [**jupyer notebook (via nbviewer)**](https://nbviewer.org/github/haroon-altaf/lisp/blob/4851898373171fa4f017c4f06bfc72e7756ee518/notebook.ipynb)

## Next Steps
- Write data obtained from online sources into a database (SQLite or MySQL) to build a historical series over time.
- Read data from database and add trend analyses/graphing features.

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

   Create new python file or jupyter notebook; alternatively adapt notebook.ipynb which contains some examples. 
