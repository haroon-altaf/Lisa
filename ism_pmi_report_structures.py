"""
Intro:
This file contains information on how to find the relevant HTML sections in the ISM Manufactiring and Services PMI reports,
using BeautifulSoup's .find() and other methods.
The Man_Pmi_Structure dictionary contains information on navigating the manufacturing PMI reports.
The Serv_Pmi_Structure dictionary contains information on navigating the services PMI reports.
The function that uses these dictionaries is located in the helpers.py module.

Structure of each dictionary:
The keys in the dictionary are the names of the sections in the report.
Each key has another dictionary as value, containing information of how to search for that section in the HTML structure.
Each value dictionary has three keys: tag, attrs, and methods.
The tag key contains the name of the HTML tag to search for using BeautifulSoup's .find() method (e.g., 'h1', 'h2', 'p').
The attrs key contains the attributes of this HTML tag in the form of key: value pairs where keys are attribute names and values are attribute values, e.g., {'class_': 'text-center'}.
The methods key contains a list of dictionaries, each dictionary containing information on what chain of methods to call after the first .find() method, in order to navigate to the target HTML content
Each dictionary in the method list contains the method name to call, the tags to search for, and the attributes of that tag.

Take the below key: value pair as an example:
    'comm_price_up': {
        'tag': 'h3',
        'attrs': {'id': 'commodities'},
        'methods': [
            {'name': 'find_next_sibling', 'tag': 'div', 'attrs': {}},
            {'name': 'findChild', 'tag': 'p', 'attrs': {}}
        ]
    }

This tells us that we need to find the <h3> tag with id='commodities' and then, find the next sibling with <div> tag, and then find the first child with <p> tag.
target_html_tag = soup.find('h3', id='commodities').find_next_sibling('div').findChild('p')

Usage of these dictionaries:
In the relevant module, these dictionaries are imported, and fed to a function (defined in helpers.py) that programmatically searches for the target HTML tags using the .find() and other methods from beautifulsoup.
If there are any changes to the ISM reports' website struture, the dictionaries will need to be updated. However, no other code would need changing.
"""

Man_Pmi_Structure = {
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

Serv_Pmi_Structure = {
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