from dataclasses import dataclass
from types import MappingProxyType

"""
This module is a dictionary that contains information on how to navigate to the relevant sections of the HTML contents of ISM Manufacturing and Services PMI reports.
"""

@dataclass(frozen=True)
class bs4_args:
    method: str = str()
    name: str = str()
    id: str = str()
    string: str = str()
    class_: str = str()

ISM_MAN_REPORT_STRUCTURE = MappingProxyType({
    'headline': (
        bs4_args(method='find', name='h1'),
	),

    'title': (
        bs4_args(method='find', name='h1'),
        bs4_args(method='find_next_sibling', name='h1')
	),

    'highlights': (
        bs4_args(method='find', name='h3', class_='text-center'),
    ),

    'overview': (
        bs4_args(method='find', name='h3', class_='text-center'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'comments': (
        bs4_args(method='find', name='h3', id='respondentsSay'),
        bs4_args(method='find_next_siblings', name='ul')
    ),

    'full_pmi_table': (
        bs4_args(method='find', name='h3', id='respondentsSay'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'comm_price_up': (
        bs4_args(method='find', name='h3', id='commodities'),
        bs4_args(method='find_next_sibling', name='div'),
        bs4_args(method='findChild', name='p')        
    ),
   
    'comm_price_down': (
        bs4_args(method='find', name='h3', id='commodities'),
        bs4_args(method='find_next_sibling', name='div'),
        bs4_args(method='find_next_sibling', name='div'),
        bs4_args(method='findChild', name='p')        
    ),

    'comm_supply_short': (
        bs4_args(method='find', name='h3', id='commodities'),
        bs4_args(method='find_next_sibling', name='p')
    ),
    
    'index_summary': (    
        bs4_args(method='find', name='h3', id='manIndexSumm'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'new_orders_text': (
        bs4_args(method='find', name='h3', string='New Orders'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'new_orders_table': (
        bs4_args(method='find', name='h3', string='New Orders'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'production_text': (
        bs4_args(method='find', name='h3', id='production'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'production_table': (
        bs4_args(method='find', name='h3', id='production'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'employment_text': (
        bs4_args(method='find', name='h3', id='employment'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'employment_table': (
        bs4_args(method='find', name='h3', id='employment'),
        bs4_args(method='find_next_siblings', name='table')
    ),
    
    'supplier_deliveries_text': (
        bs4_args(method='find', name='h3', id='supplierDeliveries'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'supplier_deliveries_table': (
        bs4_args(method='find', name='h3', id='supplierDeliveries'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'inventories_text': (
        bs4_args(method='find', name='h3', id='inventories'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'inventories_table': (
        bs4_args(method='find', name='h3', id='inventories'),
        bs4_args(method='find_next_siblings', name='table')
    ),
    
    'customer_inventories_text': (
        bs4_args(method='find', name='h3', id='customersInventories'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'customer_inventories_table': (
        bs4_args(method='find', name='h3', id='customersInventories'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'prices_text': (
        bs4_args(method='find', name='h3', id='prices'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'prices_table': (
        bs4_args(method='find', name='h3', id='prices'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'backlog_orders_text': (
        bs4_args(method='find', name='h3', id='backlogOrders'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'backlog_orders_table': (
        bs4_args(method='find', name='h3', id='backlogOrders'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'export_orders_text': (
        bs4_args(method='find', name='h3', id='newExportOrders'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'export_orders_table': (
        bs4_args(method='find', name='h3', id='newExportOrders'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'imports_text': (
        bs4_args(method='find', name='h3', id='imports'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'imports_table': (
        bs4_args(method='find', name='h3', id='imports'),
        bs4_args(method='find_next_siblings', name='table')
    ),
    
    'buying_policy_text': (
        bs4_args(method='find', name='h3', id='buyingPolicy'),
        bs4_args(method='find_parent', name='div'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'buying_policy_table': (
        bs4_args(method='find', name='h3', id='buyingPolicy'),
        bs4_args(method='find_parent', name='div'),
        bs4_args(method='find_next_siblings', name='table') 
    )
})

ISM_SER_REPORT_STRUCTURE = MappingProxyType({
    'headline': (
        bs4_args(method='find', name='h1'),
    ),

    'title': (
        bs4_args(method='find', name='h1'),
        bs4_args(method='find_next_sibling', name='h1')
    ),
    
    'highlights': (
        bs4_args(method='find', name='h3', class_='text-center'),
    ),
    
    'overview': (
        bs4_args(method='find', name='h3', class_='text-center'),
        bs4_args(method='find_next_siblings', name='p', class_=None)
    ),
    
    'comments': (
        bs4_args(method='find', name='h3', id='respondentsSay'),
        bs4_args(method='find_next_siblings', name='ul')
    ),
    
    'full_pmi_table': (
        bs4_args(method='find', name='h3', id='respondentsSay'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'comm_price_up': (
        bs4_args(method='find', name='h3', id='commodities'),
        bs4_args(method='find_next_sibling', name='div'),
        bs4_args(method='findChild', name='p')
    ),
    
    'comm_price_down': (
        bs4_args(method='find', name='h3', id='commodities'),
        bs4_args(method='find_next_sibling', name='div'),
        bs4_args(method='find_next_sibling', name='div'),
        bs4_args(method='findChild', name='p')
    ),

    'comm_supply_short': (
        bs4_args(method='find', name='h3', id='commodities'),
        bs4_args(method='find_next_sibling', name='p')
    ),

    'index_summary': (
        bs4_args(method='find', name='h3', string=lambda text: text and 'SERVICES INDEX SUMMARIES' in text),
        bs4_args(method='find_parent', name='div'),
        bs4_args(method='find_next_sibling', name='div'),
        bs4_args(method='findChildren', name='p')
    ),

    'business_activity_text': (
        bs4_args(method='find', name='h3', id='businessActivity'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'business_activity_table': (
        bs4_args(method='find', name='h3', id='businessActivity'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'new_orders_text': (
        bs4_args(method='find', name='h3', string='New Orders'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'new_orders_table': (
        bs4_args(method='find', name='h3', string='New Orders'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'employment_text': (
        bs4_args(method='find', name='h3', string='Employment'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'employment_table': (
        bs4_args(method='find', name='h3', string='Employment'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'supplier_deliveries_text': (
        bs4_args(method='find', name='h3', string='Supplier Deliveries'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'supplier_deliveries_table': (
        bs4_args(method='find', name='h3', string='Supplier Deliveries'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'inventories_text': (
        bs4_args(method='find', name='h3', string='Inventories'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'inventories_table': (
        bs4_args(method='find', name='h3', string='Inventories'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'prices_text': (
        bs4_args(method='find', name='h3', string='Prices'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'prices_table': (
        bs4_args(method='find', name='h3', string='Prices'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'backlog_orders_text': (
        bs4_args(method='find', name='h3', string='Backlog of Orders'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'backlog_orders_table': (
        bs4_args(method='find', name='h3', string='Backlog of Orders'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'export_orders_text': (
        bs4_args(method='find', name='h3', string='New Export Orders'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'export_orders_table': (
        bs4_args(method='find', name='h3', string='New Export Orders'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'inventory_sentiment_text': (
        bs4_args(method='find', name='h3', id='inventorySentiment'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'inventory_sentiment_table': (
        bs4_args(method='find', name='h3', id='inventorySentiment'),
        bs4_args(method='find_next_siblings', name='table')
    ),

    'imports_text': (
        bs4_args(method='find', name='h3', string='Imports'),
        bs4_args(method='find_next_siblings', name='p')
    ),

    'imports_table': (
        bs4_args(method='find', name='h3', string='Imports'),
        bs4_args(method='find_next_siblings', name='table')
    )
})