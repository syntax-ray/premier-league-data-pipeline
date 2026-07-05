from dotenv import load_dotenv
import os
import requests
import logging
from consts import LOGGING_FILE, API_FOOTBALL_URL 

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


def fetch_seasons():
    '''
        Fetches available season years from the api
    '''
    try:
        response = requests.get(f'{API_FOOTBALL_URL}/leagues/seasons', headers=HEADERS)
        logger.info('Successfully fetched seasons')
        response = response.json()
        seasons = response['response']
        seasons.sort()
        return seasons
    except Exception as e:
        logger.error('Could not fetch seasons due to %s', e)


if __name__ == '__main__':
    print(fetch_seasons())