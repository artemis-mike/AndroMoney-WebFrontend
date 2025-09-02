import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

EXPENSES_CSV = os.path.join(BASE_DIR, 'data', 'expenses.csv')
#INCOME_JSON = os.path.join(BASE_DIR, 'income.json')

# Secret key for flash messages
SECRET_KEY = os.environ.get('FLASH_SECRET_KEY', 'fallback-key-for-dev')
