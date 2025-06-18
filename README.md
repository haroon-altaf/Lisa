# lisp
A program to scrape and manipulate some leading economic indicators, market data, and stock data from various sources online.
This web-scraping program will be part of a larger "web-application".


## The goal of the web-app will be: 
To allow anyone to visualise a monthly timeseries of "leading" economic indicators for the US, Europe, and to a lesser extent China.
In addition to simply visualising historical data, there will be some analyses of trends, particularly highlighting the growth/contraction in various manufacturing and services sectors;
this highlights which sectors look "bullish" in the near term, and which to avoid.


## To accomplish this, broadly 3 steps are to be carried out:
1. Write a program that can reliably and consistently obtain (scrape) data from different online sources; and apply transformations to the data where needed to get the correct format and derived quantities.
2. Set up a lightweight database (Sqlite) that stores the scraped and transformed data on a monthly basis, building a history. Write a program that safely loads data into this database.
3. Build a front-end web application that will display data retrieved from this database. TBC what this will look like and how it will be interacted with.


## Currently:
Only step 1 has been completed, i.e., the latest releases of selected economic data can be obtained using the program. Step 2 is underway, where the scraped data will be safely loaded into a database.


## Structure of the scraping program (lisp) files:
The program currently consists of 4 files. "static.py" contains some static data; "utility.py" contains some functions and a class for managing HTTP requests, used throughout the code; **"Scrapers.py" is where the majority of the web-scraping logic and functionality is written** - a web scraping class is created for each online source from which data is to be obtained. The "loggers.py" file is used to configure logging of traceback errors into a txt file (the program itself fails safely by returning None and does not - or should not - throw exceptions).


## Usage of the scraping program (lisp):
[work in progress]
