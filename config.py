import os
import datetime 
from dotenv import load_dotenv

load_dotenv()

mySecret = os.environ.get('MySecret')
SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = os.getenv("SERVER_PORT")
LOG_PATH = os.environ.get('LOG_PATH')
GCP_CREDENTIAL = os.environ.get('GCP_CREDENTIAL')
SCHEDULER_URL = os.environ.get('SCHEDULER_URL')

BASE_DIR_NAME = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
BASE_DIR = os.path.join(os.environ.get('DATA_PATH', '.'), BASE_DIR_NAME)
os.environ['BASE_DIR'] = BASE_DIR