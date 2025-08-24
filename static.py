# This file contains static data and configurable parameters that are used in other program files.
#
#   Data Structure Name         |   Type        |   Description
#   ----------------------------|---------------|-------------------------------------------------------------------------------------------------------------
#   MONTHS                      |   Enum class  |   Enables conversions between month names/abbreviations and month numbers
#   URL                         |   Enum class  |   URLs for different data sources to be scraped
#   LOGGING_PARAMS              |   Dictionary  |   Common configurable parameters for logging handlers
#   REQUESTS_PARAMS             |   Dictionary  |   Configurable parameters for GET requests with retries
#   FINVIZ_PARAMS               |   Dictionary  |   Configurable parameters for scraping Finviz screener data
#   MAN_REPORT                  |   Dictionary  |   Describes how to naviagate to different sections in the HTML structure of ISM reports for manufacturing
#   SER_REPORT                  |   Dictionary  |   Describes how to naviagate to different sections in the HTML structure of ISM reports for services
#   GICS_MAP                    |   Dictionary  |   GICS sectors and industry mapping as in Finviz
#   MAN_SECTORS                 |   List        |   List of NAIC manufacturing sectors as in the ISM industry reports
#   SERV_SECTORS                |   List        |   List of NAIC services sectors as in the ISM industry reports

from enum import Enum, IntEnum
import os

class MONTHS(IntEnum):
    JANUARY, JAN = 1, 1
    FEBRUARY, FEB = 2, 2
    MARCH, MAR = 3, 3
    APRIL, APR = 4, 4
    MAY = 5
    JUNE, JUN = 6, 6
    JULY, JUL = 7, 7
    AUGUST, AUG = 8, 8
    SEPTEMBER, SEP = 9, 9
    OCTOBER, OCT = 10, 10    
    NOVEMBER, NOV = 11, 11
    DECEMBER, DEC = 12, 12

class URL(Enum):
    US_MAN_PMI = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/pmi/"
    US_SER_PMI = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/services/"
    US_CONS_INDEX = "https://www.sca.isr.umich.edu/files/tbcics.csv"
    US_CONS_COMP = "https://www.sca.isr.umich.edu/files/tbciccice.csv"
    US_BUIL_PERMIT = "https://www.census.gov/construction/nrc/xls/permits_cust.xlsx"
    US_BUIL_AUTH = "https://www.census.gov/construction/nrc/xls/authnot_cust.xlsx"
    US_BUIL_START = "https://www.census.gov/construction/nrc/xls/starts_cust.xlsx"
    US_BUIL_CONSTRUCT = "https://www.census.gov/construction/nrc/xls/under_cust.xlsx"
    US_BUIL_COMPLETE = "https://www.census.gov/construction/nrc/xls/comps_cust.xlsx"
    EURO = "https://economy-finance.ec.europa.eu/economic-forecast-and-surveys/business-and-consumer-surveys/download-business-and-consumer-survey-data/time-series_en"
    CAIXIN_MAN_PMI = "https://tradingeconomics.com/china/manufacturing-pmi"
    CAIXIN_SER_PMI = "https://tradingeconomics.com/china/services-pmi"
    FINVIZ_SCREEN = "https://finviz.com/screener.ashx?v=151&f=ind_stocksonly&o=ticker&c="
    FINVIZ_STOCK = "https://finviz.com/quote.ashx"
    FINVIZ_INDU = "https://finviz.com/groups.ashx?g=industry&v=152&o=name&c=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26"
    COMMODITIES = "https://tradingeconomics.com/commodities"
    STOCKS = "https://tradingeconomics.com/stocks"
    BONDS = "https://tradingeconomics.com/bonds"
    CURRENCIES = "https://tradingeconomics.com/currencies"
    CRYPTO = "https://tradingeconomics.com/crypto"

LOGGING_PARAMS = {
    'filepath': os.path.join(os.path.dirname(__file__), 'errors.log'),
    'fileformatter': '\n\n\n------------------------------ %(asctime)s | %(name)s | %(levelname)s ------------------------------\n\n%(message)s\n',
    'consoleformatter': '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
}

REQUESTS_PARAMS = {
    'timeout': 10,
    'max_retries': 3,
    'backoff_factor': 1.0,
    'session_renewal_interval': 1000,
    'ua_list': [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    ]
}

FINVIZ_PARAMS = {
    'screener_columns' : [
        1, 2, 79, 3, 4, 5, 129, 6, 7, 8, 9, 10, 11, 12, 13, 73, 74, 75, 14, 130, 131, 15, 16, 77, 17, 18, 19, 20, 21, 23, 22, 132, 133, 82, 78, 127, 128, 24, 25, 85, 26, 27, 28, 29, 30, 31, 84, 32, 33,
        34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 134, 125, 126, 59, 68, 70, 80, 83, 76, 60, 61, 62, 63, 64, 67, 69, 81, 86, 87, 88, 65, 66
    ],
    'max_rows' : 10000,
    'rows_per_page' : 20
}

MAN_REPORT = {
#    The keys in the dictionary are the names of different sections in the ISM reports.
#    Each key has another dictionary as value, containing information of how to search for that section in the HTML structure.
#    This dictionary has three keys: tag, attrs, and methods.
#    The tag key contains the name of the HTML tag to search for using BeautifulSoup's .find() method (e.g., 'h1', 'h2', 'p').
#    The attrs key contains the attributes of this HTML tag in the form of key: value pairs where keys are attribute names and values are attribute values, e.g., {'class_': 'text-center'}.
#    The methods key contains a list of dictionaries, each dictionary containing information on what chain of methods to call after the first .find() method, in order to navigate to the target HTML content.
#    Each dictionary in the methods list contains the method name to call, the tags to search for, and the attributes of that tag.

#    Take the below key: value pair as an example:
#        'comm_price_up': {
#            'tag': 'h3',
#            'attrs': {'id': 'commodities'},
#            'methods': [
#                {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
#                {'name': 'findChild', 'tag': 'p', 'attrs': {}}
#            ]
#        }

#    This tells us that we need to find the <h3> tag with id='commodities' and then, find the next sibling with <div> tag, and then find the first child with <p> tag.
#    target_html_tag = soup.find('h3', id='commodities').find_next_sibling('div').findChild('p')

#    In the relevant module, these dictionaries are imported, and fed to a function (defined in helpers.py) that programmatically searches for the target HTML tags using the .find() and other beautifulsoup methods.#    If there are any changes to the ISM reports' website struture, the dictionaries will need to be updated. However, no other code would need changing.

    'headline': {
        'tag': 'h1',
        'attrs': {},
        'methods': []
    },
    'highlights': {
        'tag': 'h3',
        'attrs': {'class_': 'text-center'},
        'methods': []
    },
    'overview': {
        'tag': 'h3',
        'attrs': {'class_': 'text-center'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'comments': {
        'tag': 'h3',
        'attrs': {'id': 'respondentsSay'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'ul', 'attrs': {}}
        ]
    },
    'full_pmi_table': {
        'tag': 'h3',
        'attrs': {'id': 'respondentsSay'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'comm_price_up': {
        'tag': 'h3',
        'attrs': {'id': 'commodities'},
        'methods': [
            {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
            {'name': 'findChild', 'tag': 'p', 'attrs': {}}
        ]
    },
    'comm_price_down': {
        'tag': 'h3',
        'attrs': {'id': 'commodities'},
        'methods': [
            {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
            {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
            {'name': 'findChild', 'tag': 'p', 'attrs': {}}
        ]
    },
    'comm_supply_short': {
        'tag': 'h3',
        'attrs': {'id': 'commodities'},
        'methods': [
            {'name': 'find_next_sibling', 'tag': 'p', 'attrs': {}}
        ]
    },
    'index_summary': {
        'tag': 'h3',
        'attrs': {'id': 'manIndexSumm'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'new_orders_text': {
        'tag': 'h3',
        'attrs': {'string': 'New Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'new_orders_table': {
        'tag': 'h3',
        'attrs': {'string': 'New Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'production_text': {
        'tag': 'h3',
        'attrs': {'id': 'production'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'production_table': {
        'tag': 'h3',
        'attrs': {'id': 'production'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'employment_text': {
        'tag': 'h3',
        'attrs': {'id': 'employment'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'employment_table': {
        'tag': 'h3',
        'attrs': {'id': 'employment'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'supplier_deliveries_text': {
        'tag': 'h3',
        'attrs': {'id': 'supplierDeliveries'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'supplier_deliveries_table': {
        'tag': 'h3',
        'attrs': {'id': 'supplierDeliveries'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'inventories_text': {
        'tag': 'h3',
        'attrs': {'id': 'inventories'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'inventories_table': {
        'tag': 'h3',
        'attrs': {'id': 'inventories'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'customer_inventories_text': {
        'tag': 'h3',
        'attrs': {'id': 'customersInventories'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'customer_inventories_table': {
        'tag': 'h3',
        'attrs': {'id': 'customersInventories'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'prices_text': {
        'tag': 'h3',
        'attrs': {'id': 'prices'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'prices_table': {
        'tag': 'h3',
        'attrs': {'id': 'prices'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'backlog_orders_text': {
        'tag': 'h3',
        'attrs': {'id': 'backlogOrders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'backlog_orders_table': {
        'tag': 'h3',
        'attrs': {'id': 'backlogOrders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'export_orders_text': {
        'tag': 'h3',
        'attrs': {'id': 'newExportOrders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'export_orders_table': {
        'tag': 'h3',
        'attrs': {'id': 'newExportOrders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'imports_text': {
        'tag': 'h3',
        'attrs': {'id': 'imports'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'imports_table': {
        'tag': 'h3',
        'attrs': {'id': 'imports'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'buying_policy_text': {
        'tag': 'h3',
        'attrs': {'id': 'buyingPolicy'},
        'methods': [
            {'name': 'find_parent', 'tag': 'div', 'attrs': {}},
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'buying_policy_table': {
        'tag': 'h3',
        'attrs': {'id': 'buyingPolicy'},
        'methods': [
            {'name': 'find_parent', 'tag': 'div', 'attrs': {}},
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    }
}

SERV_REPORT = {
    'headline': {
        'tag': 'h1',
        'attrs': {},
        'methods': []
    },
    'highlights': {
        'tag': 'h3',
        'attrs': {'class_': 'text-center'},
        'methods': []
    },
    'overview': {
        'tag': 'h3',
        'attrs': {'class_': 'text-center'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {'class_': None}}
        ]
    },
    'comments': {
        'tag': 'h3',
        'attrs': {'id': 'respondentsSay'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'ul', 'attrs': {}}
        ]
    },
    'full_pmi_table': {
        'tag': 'h3',
        'attrs': {'id': 'respondentsSay'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'comm_price_up': {
        'tag': 'h3',
        'attrs': {'id': 'commodities'},
        'methods': [
            {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
            {'name': 'findChild', 'tag': 'p', 'attrs': {}}
        ]
    },
    'comm_price_down': {
        'tag': 'h3',
        'attrs': {'id': 'commodities'},
        'methods': [
            {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
            {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
            {'name': 'findChild', 'tag': 'p', 'attrs': {}}
        ]
    },
    'comm_supply_short': {
        'tag': 'h3',
        'attrs': {'id': 'commodities'},
        'methods': [
            {'name': 'find_next_sibling', 'tag': 'p', 'attrs': {}}
        ]
    },
    'index_summary': {
        'tag': 'h3',
        'attrs': {'string': lambda text: 'SERVICES INDEX SUMMARIES' in text if text else False},
        'methods': [
            {'name': 'find_parent', 'tag': 'div', 'attrs': {}},
            {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
            {'name': 'findChildren', 'tag': 'p', 'attrs': {}}
        ]
    },
    'business_activity_text': {
        'tag': 'h3',
        'attrs': {'id': 'businessActivity'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'business_activity_table': {
        'tag': 'h3',
        'attrs': {'id': 'businessActivity'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'new_orders_text': {
        'tag': 'h3',
        'attrs': {'string': 'New Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'new_orders_table': {
        'tag': 'h3',
        'attrs': {'string': 'New Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'employment_text': {
        'tag': 'h3',
        'attrs': {'string': 'Employment'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'employment_table': {
        'tag': 'h3',
        'attrs': {'string': 'Employment'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'supplier_deliveries_text': {
        'tag': 'h3',
        'attrs': {'string': 'Supplier Deliveries'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'supplier_deliveries_table': {
        'tag': 'h3',
        'attrs': {'string': 'Supplier Deliveries'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'inventories_text': {
        'tag': 'h3',
        'attrs': {'string': 'Inventories'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'inventories_table': {
        'tag': 'h3',
        'attrs': {'string': 'Inventories'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'prices_text': {
        'tag': 'h3',
        'attrs': {'string': 'Prices'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'prices_table': {
        'tag': 'h3',
        'attrs': {'string': 'Prices'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'backlog_orders_text': {
        'tag': 'h3',
        'attrs': {'string': 'Backlog of Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'backlog_orders_table': {
        'tag': 'h3',
        'attrs': {'string': 'Backlog of Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'export_orders_text': {
        'tag': 'h3',
        'attrs': {'string': 'New Export Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'export_orders_table': {
        'tag': 'h3',
        'attrs': {'string': 'New Export Orders'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    },
    'inventory_sentiment_text': {
        'tag': 'h3',
        'attrs': {'id': 'inventorySentiment'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'p', 'attrs': {}}
        ]
    },
    'inventory_sentiment_table': {
        'tag': 'h3',
        'attrs': {'id': 'inventorySentiment'},
        'methods': [
            {'name': 'find_next_siblings', 'tag': 'table', 'attrs': {}}
        ]
    }
}

GICS_MAP = {
    'Basic Materials': {   
        'Agricultural Inputs',
        'Aluminum',
        'Building Materials',
        'Chemicals',
        'Coking Coal',
        'Copper',
        'Gold',
        'Lumber & Wood Production',
        'Other Industrial Metals & Mining',
        'Other Precious Metals & Mining',
        'Paper & Paper Products',
        'Silver',
        'Specialty Chemicals',
        'Steel'
    },
    'Communication Services': {   
        'Advertising Agencies',
        'Broadcasting',
        'Electronic Gaming & Multimedia',
        'Entertainment',
        'Internet Content & Information',
        'Publishing',
        'Telecom Services'
    },
    'Consumer Cyclical': {   
        'Apparel Manufacturing',
        'Apparel Retail',
        'Auto & Truck Dealerships',
        'Auto Manufacturers',
        'Auto Parts',
        'Department Stores',
        'Footwear & Accessories',
        'Furnishings, Fixtures & Appliances',
        'Gambling',
        'Home Improvement Retail',
        'Internet Retail',
        'Leisure',
        'Lodging',
        'Luxury Goods',
        'Packaging & Containers',
        'Personal Services',
        'Recreational Vehicles',
        'Residential Construction',
        'Resorts & Casinos',
        'Restaurants',
        'Specialty Retail',
        'Textile Manufacturing',
        'Travel Services'
    },
    'Consumer Defensive': {   
        'Beverages - Brewers',
        'Beverages - Non-Alcoholic',
        'Beverages - Wineries & Distilleries',
        'Confectioners',
        'Discount Stores',
        'Education & Training Services',
        'Farm Products',
        'Food Distribution',
        'Grocery Stores',
        'Household & Personal Products',
        'Packaged Foods',
        'Tobacco'
    },
    'Energy': {   
        'Oil & Gas Drilling',
        'Oil & Gas E&P',
        'Oil & Gas Equipment & Services',
        'Oil & Gas Integrated',
        'Oil & Gas Midstream',
        'Oil & Gas Refining & Marketing',
        'Thermal Coal',
        'Uranium'
    },
    'Financial': {   
        'Asset Management',
        'Banks - Diversified',
        'Banks - Regional',
        'Capital Markets',
        'Credit Services',
        'Financial Conglomerates',
        'Financial Data & Stock Exchanges',
        'Insurance - Diversified',
        'Insurance - Life',
        'Insurance - Property & Casualty',
        'Insurance - Reinsurance',
        'Insurance - Specialty',
        'Insurance Brokers',
        'Mortgage Finance',
        'Shell Companies'
    },
    'Healthcare': {   
        'Biotechnology',
        'Diagnostics & Research',
        'Drug Manufacturers - General',
        'Drug Manufacturers - Specialty & Generic',
        'Health Information Services',
        'Healthcare Plans',
        'Medical Care Facilities',
        'Medical Devices',
        'Medical Distribution',
        'Medical Instruments & Supplies',
        'Pharmaceutical Retailers'
    },
    'Industrials': {   
        'Aerospace & Defense',
        'Airlines',
        'Airports & Air Services',
        'Building Products & Equipment',
        'Business Equipment & Supplies',
        'Conglomerates',
        'Consulting Services',
        'Electrical Equipment & Parts',
        'Engineering & Construction',
        'Farm & Heavy Construction Machinery',
        'Industrial Distribution',
        'Infrastructure Operations',
        'Integrated Freight & Logistics',
        'Marine Shipping',
        'Metal Fabrication',
        'Pollution & Treatment Controls',
        'Railroads',
        'Rental & Leasing Services',
        'Security & Protection Services',
        'Specialty Business Services',
        'Specialty Industrial Machinery',
        'Staffing & Employment Services',
        'Tools & Accessories',
        'Trucking',
        'Waste Management'
    },
    'Real Estate': {   
        'REIT - Diversified',
        'REIT - Healthcare Facilities',
        'REIT - Hotel & Motel',
        'REIT - Industrial',
        'REIT - Mortgage',
        'REIT - Office',
        'REIT - Residential',
        'REIT - Retail',
        'REIT - Specialty',
        'Real Estate - Development',
        'Real Estate - Diversified',
        'Real Estate Services'
    },
    'Technology': {   
        'Communication Equipment',
        'Computer Hardware',
        'Consumer Electronics',
        'Electronic Components',
        'Electronics & Computer Distribution',
        'Information Technology Services',
        'Scientific & Technical Instruments',
        'Semiconductor Equipment & Materials',
        'Semiconductors',
        'Software - Application',
        'Software - Infrastructure',
        'Solar'
    },
    'Utilities': {   
        'Utilities - Diversified',
        'Utilities - Independent Power Producers',
        'Utilities - Regulated Electric',
        'Utilities - Regulated Gas',
        'Utilities - Regulated Water',
        'Utilities - Renewable'
    }
}

MAN_SECTORS = [
    "Apparel, Leather & Allied Products",
    "Chemical Products",
    "Computer & Electronic Products",
    "Electrical Equipment, Appliances & Components",
    "Fabricated Metal Products",
    "Food, Beverage & Tobacco Products",
    "Furniture & Related Products",
    "Machinery",
    "Miscellaneous Manufacturing",
    "Nonmetallic Mineral Products",
    "Paper Products",
    "Petroleum & Coal Products",
    "Plastics & Rubber Products",
    "Primary Metals",
    "Printing & Related Support Activities",
    "Textile Mills",
    "Transportation Equipment",
    "Wood Products"
]

SERV_SECTORS = [
    "Accommodation & Food Services",
    "Agriculture, Forestry, Fishing & Hunting",
    "Arts, Entertainment & Recreation",
    "Construction",
    "Educational Services",
    "Finance & Insurance",
    "Health Care & Social Assistance",
    "Information",
    "Management of Companies & Support Services",
    "Mining",
    "Other Services",
    "Professional, Scientific & Technical Services",
    "Public Administration",
    "Real Estate, Rental & Leasing",
    "Retail Trade",
    "Transportation & Warehousing",
    "Utilities",
    "Wholesale Trade"
]