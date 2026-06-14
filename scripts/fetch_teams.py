from dotenv import load_dotenv
import os
import http.client
import json
import pandas as pd
from db_int import DB

load_dotenv()
API_KEY = os.getenv('API_KEY')
CONN = http.client.HTTPSConnection("v3.football.api-sports.io")
TARGET_YEAR = 2024


HEADERS = {
    'x-apisports-key': API_KEY
    }

def get_api_status():
    try:
        CONN.request('GET',"/status", headers=HEADERS)
        response = CONN.getresponse().read().decode()
        status = json.loads(response)
        requests_made = status['response']['requests']['current']
        requests_limit = status['response']['requests']['limit_day']
        print(f'The current request status is {requests_made} / {requests_limit}')
    except Exception as e:
        print(f'Could not get status due to {e}')


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


def fetch_seasons():
    '''
        Fetches available season years from the api
    '''
    try:
        CONN.request("GET", f"/leagues/seasons", headers=HEADERS)
        print('Successfully fetched seasons')
        response = CONN.getresponse().read().decode()
        seasons = json.loads(response)['response']
        get_api_status()
        return seasons

    except Exception as e:
        print(f'Could not fetch seasons due to {e}')

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
    seasons.sort()
    for id in league_ids:
        for season in seasons:
            try:
                CONN.request("GET", f"/teams?league={id}&season={season}", headers=HEADERS)
                print('Successfully fetched teams')
                response = CONN.getresponse().read().decode()
                teams = json.loads(response)['response']
                clean_teams = {
                    'id': [],
                    'name': [],
                    'country': [],
                    'national': []
                }
                
                existing_teams = db.fetch_team_ids()
                print(f"There were {len(existing_teams)} teams")
                for team in teams:
                    team_id = team['team']['id']
                    if team_id not in existing_teams:
                        clean_teams['id'].append(team_id)
                        clean_teams['name'].append(team['team']['name'])
                        clean_teams['country'].append(team['team']['country'])
                        clean_teams['national'].append(team['team']['national'])
                clean_teams_df = pd.DataFrame(clean_teams)
                db.save_dataframe_to_table(clean_teams_df, 'team', 'append')            
                print('Saved teams data to db')
                # get_api_status()
            except Exception as e:
                print(f'Could not fetch leagues due to {e}')
    



if __name__ == '__main__':
    get_api_status()
    fetch_teams()