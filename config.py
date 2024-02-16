import os
import datetime 
from dotenv import load_dotenv

load_dotenv()

mySecret = os.environ.get('MySecret')

current_date = datetime.date.today()
FORMAT_DATE = current_date.strftime("%Y-%m-%d")

API_BASE_URL = os.environ.get('API_BASE_URL')
LOG_PATH = os.environ.get('LOG_PATH')
PRESET_DIR = os.environ.get('PRESET_DIR')
GCP_CREDENTIAL = os.environ.get('GCP_CREDENTIAL')
DATA_PATH = os.environ.get('DATA_PATH')
CHECKPOINT_PATH = os.environ.get('CHECKPOINT_PATH')