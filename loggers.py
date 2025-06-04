import logging
import os

path = os.path.join(os.path.dirname(__file__), 'errors.log')
file_handler = logging.FileHandler(path)
file_handler.setFormatter(logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s'))

web_scraping_logger = logging.getLogger('web_scraping_errors')
web_scraping_logger.addHandler(file_handler)
web_scraping_logger.setLevel(logging.ERROR)

database_logger = logging.getLogger('database_errors')
database_logger.addHandler(file_handler)
database_logger.setLevel(logging.ERROR)