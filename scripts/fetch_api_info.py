from dotenv import load_dotenv
import os
import json
import logging
from consts import LOGGING_FILE, API_FOOTBALL_URL
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    filename=LOGGING_FILE
)

logger = logging.getLogger(__name__)


load_dotenv()
API_KEY = os.getenv('API_KEY')
HEADERS = {
    'x-apisports-key': API_KEY
}
    

def get_api_info():
    '''
        Fetches information about api-football api on the current plan
    '''
    try:
        response = requests.get(
            f"{API_FOOTBALL_URL}/status",
            headers=HEADERS
        )
        max_calls_per_minute = response.headers["X-RateLimit-Limit"]
        response = response.json()
        requests_made = response['response']['requests']['current']
        requests_limit = response['response']['requests']['limit_day']
        return f'The current request status is {requests_made} / {requests_limit}', max_calls_per_minute
    except Exception as e:
        logger.error(f'Could not get status due to {e}')


if __name__ == '__main__':
    print(get_api_info())