from dotenv import load_dotenv
import os
import pandas as pd
from db_int import DB
import requests
from consts import LOGGING_FILE, API_FOOTBALL_URL
from fetch_api_info import get_api_info
import logging

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


def fetch_leagues():
    '''
        Fetches league information from api football
    '''
    try:
        response = requests.get(f'{API_FOOTBALL_URL}/leagues', headers=HEADERS)
        response = response.json()
        leagues = response['response']
        leagues_summary = {
            'id': [],
            'league_id': [],
            'name': [],
            'type': [],
            'country': []
        }
        for idx, league in enumerate(leagues):
            leagues_summary['id'].append(idx + 1)
            leagues_summary['league_id'].append(league['league']['id'])
            leagues_summary['name'].append(league['league']['name'])
            leagues_summary['type'].append(league['league']['type'])
            leagues_summary['country'].append(league['country']['name'])
        summary_df = pd.DataFrame(leagues_summary)
        db = DB()
        db.save_dataframe_to_table(summary_df, table_name='league', if_exists='replace')
    except Exception as e:
        logger.error('Could not fetch leagues due to %s', e)
    

if __name__ == '__main__':
    current_api_status, _ = get_api_info()
    logger.info(current_api_status)
    fetch_leagues()