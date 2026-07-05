from dotenv import load_dotenv
import os
import pandas as pd
from db_int import DB
from fetch_seasons import fetch_seasons
import time
import logging
import requests
from fetch_api_info import get_api_info
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


def fetch_league_ids():
    '''
        Fetch English Premier League league id. Returns a list incase the scope expands
    '''
    db = DB()
    ids = []
    # league ids with league data
    league_ids = db.fetch_league_ids()
    prem_id_series = ((league_ids.loc[ (league_ids['name'] == 'Premier League') &  (league_ids['country'] == 'England')])['league_id'])
    prem_id = prem_id_series.iloc[0]
    ids.append(prem_id)
    return ids


def fetch_teams():
    '''
        Fetch teams data from api based on seasons
            -> fetch teams
            -> get existing team ids()
            -> filter out teams that already exist
            -> append the rest
    '''
    db = DB()
    league_ids = fetch_league_ids()
    seasons = fetch_seasons()
    skip_sleep = False

    for id in league_ids:
        for season in seasons:
            logger.info('Fetching teams for season: (%s)', season)
            if not skip_sleep:
                skip_sleep = True
            else:
                time.sleep(30)

            try:
                response = requests.get(f"{API_FOOTBALL_URL}/teams?league={id}&season={season}", headers=HEADERS)
                response = response.json()
                teams = response['response']
                clean_teams = {
                    'id': [],
                    'name': [],
                    'country': [],
                    'national': []
                }
                
                existing_teams = db.fetch_team_ids()
                for team in teams:
                    team_id = team['team']['id']
                    if team_id not in existing_teams:
                        clean_teams['id'].append(team_id)
                        clean_teams['name'].append(team['team']['name'])
                        clean_teams['country'].append(team['team']['country'])
                        clean_teams['national'].append(team['team']['national'])
                clean_teams_df = pd.DataFrame(clean_teams)
                db.save_dataframe_to_table(clean_teams_df, 'team', 'append')            
            except Exception as e:
                logger.error('Could not fetch leagues due to %s', e)
    



if __name__ == '__main__':
    current_api_status, _ = get_api_info()
    logger.info(current_api_status)
    fetch_teams()