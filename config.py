import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

mySecret = os.environ.get('MySecret')
SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = os.getenv("SERVER_PORT")
LOG_PATH = os.environ.get('LOG_PATH')
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
SCHEDULER_URL = os.environ.get('SCHEDULER_URL')
BUCKET=os.environ.get('BUCKET')
REQUEST_COLLECTION =os.environ.get('REQUEST_COLLECTION')
VR_RESOURCE_COLLECTION=os.environ.get('VR_RESOURCE_COLLECTION')

BASE_DIR_NAME = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
BASE_DIR = os.path.join(os.environ.get('DATA_PATH', '.'), BASE_DIR_NAME)
os.environ['BASE_DIR'] = BASE_DIR
