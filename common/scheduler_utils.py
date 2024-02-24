import requests

# url must combinate with environments' SCHEDULER_URL
def trigger_scheduler():
    url = SCHEDULER_URL + "/engine-trigger"
    response = requests.post(url)
