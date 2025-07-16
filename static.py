# > This file contains static data that is used elsewhere in the code.
#
# > Overview:
#
#   Data Structure Name         |   Type        |   Description
#   ----------------------------|---------------|-------------------------------------------------------------------------------------
#   MAN_REPORT                  |   Dictionary  |   Describes how to naviagate the ISM report HTML to extract sections
#   SER_REPORT                  |   Dictionary  |   Describes how to naviagate the ISM report HTML to extract sections
#   GICS_MAP                    |   Dictionary  |   Presents the GICS sectors and industry mapping as in Finviz
#   MAN_SECTORS                 |   List        |   List of NAIC manufacturing sectors as in the ISM industry reports
#   SERV_SECTORS                |   List        |   List of NAIC services sectors as in the ISM industry reports


# > Details on data structures (1) and (2):
#
#     The keys in the dictionary are the names of the sections in the report.
#     Each key has another dictionary as value, containing information of how to search for that section in the HTML structure.
#     Each value dictionary has three keys: tag, attrs, and methods.
#     The tag key contains the name of the HTML tag to search for using BeautifulSoup's .find() method (e.g., 'h1', 'h2', 'p').
#     The attrs key contains the attributes of this HTML tag in the form of key: value pairs where keys are attribute names and values are attribute values, e.g., {'class_': 'text-center'}.
#     The methods key contains a list of dictionaries, each dictionary containing information on what chain of methods to call after the first .find() method, in order to navigate to the target HTML content
#     Each dictionary in the method list contains the method name to call, the tags to search for, and the attributes of that tag.

#     Take the below key: value pair as an example:
#         'comm_price_up': {
#             'tag': 'h3',
#             'attrs': {'id': 'commodities'},
#             'methods': [
#                 {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
#                 {'name': 'findChild', 'tag': 'p', 'attrs': {}}
#             ]
#         }

#     This tells us that we need to find the <h3> tag with id='commodities' and then, find the next sibling with <div> tag, and then find the first child with <p> tag.
#     target_html_tag = soup.find('h3', id='commodities').find_next_sibling('div').findChild('p')

#     In the relevant module, these dictionaries are imported, and fed to a function (defined in helpers.py) that programmatically searches for the target HTML tags using the .find() and other methods from beautifulsoup.
#     If there are any changes to the ISM reports' website struture, the dictionaries will need to be updated. However, no other code would need changing.

MAN_REPORT = {
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
    'Basic Materials': {   'Agricultural Inputs',
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
                           'Steel'},
    'Communication Services': {   'Advertising Agencies',
                                  'Broadcasting',
                                  'Electronic Gaming & Multimedia',
                                  'Entertainment',
                                  'Internet Content & Information',
                                  'Publishing',
                                  'Telecom Services'},
    'Consumer Cyclical': {   'Apparel Manufacturing',
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
                             'Travel Services'},
    'Consumer Defensive': {   'Beverages - Brewers',
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
                              'Tobacco'},
    'Energy': {   'Oil & Gas Drilling',
                  'Oil & Gas E&P',
                  'Oil & Gas Equipment & Services',
                  'Oil & Gas Integrated',
                  'Oil & Gas Midstream',
                  'Oil & Gas Refining & Marketing',
                  'Thermal Coal',
                  'Uranium'},
    'Financial': {   'Asset Management',
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
                     'Shell Companies'},
    'Healthcare': {   'Biotechnology',
                      'Diagnostics & Research',
                      'Drug Manufacturers - General',
                      'Drug Manufacturers - Specialty & Generic',
                      'Health Information Services',
                      'Healthcare Plans',
                      'Medical Care Facilities',
                      'Medical Devices',
                      'Medical Distribution',
                      'Medical Instruments & Supplies',
                      'Pharmaceutical Retailers'},
    'Industrials': {   'Aerospace & Defense',
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
                       'Waste Management'},
    'Real Estate': {   'REIT - Diversified',
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
                       'Real Estate Services'},
    'Technology': {   'Communication Equipment',
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
                      'Solar'},
    'Utilities': {   'Utilities - Diversified',
                     'Utilities - Independent Power Producers',
                     'Utilities - Regulated Electric',
                     'Utilities - Regulated Gas',
                     'Utilities - Regulated Water',
                     'Utilities - Renewable'}
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
