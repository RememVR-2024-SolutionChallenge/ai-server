import logging
from config import LOG_PATH
import os

########## @@ Logging ##########
log_dir = os.path.dirname(LOG_PATH)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(LOG_PATH, mode="a")
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
