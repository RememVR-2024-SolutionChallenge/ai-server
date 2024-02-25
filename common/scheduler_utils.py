import requests
from config import SCHEDULER_URL

def trigger_scheduler():
    url = SCHEDULER_URL + "/engine-trigger"
    response = requests.post(url)
