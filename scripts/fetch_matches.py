from dotenv import load_dotenv
import os
import http.client
import json
import pandas as pd
from db_int import DB
from fetch_seasons import fetch_seasons
import time

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
        Meant to return fetched league ids from the database but currently only returns the English premier league id due to api
        constraints
    '''
    db = DB()
    ids = []
    # league metadata + league ids
    league_ids = db.fetch_league_ids()
    # filyer for premier league
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

def fetch_matches():
    '''
        Fetch matches data for all premier league seasons in the season list.

            -> fetch matches
            -> get existing match ids()
            -> filter out matches that already exist
            -> append the rest
    '''
    db = DB()
    league_ids = fetch_league_ids()
    seasons = fetch_seasons()
    skip_sleep = False
    for id in league_ids:
        for season in seasons:
            print(f'Fetching season: ({season})')
            if not skip_sleep:
                skip_sleep = True
            else:
                time.sleep(30)
            try:
                CONN.request("GET", f"/fixtures?league={id}&season={season}", headers=HEADERS)
                print('Successfully fetched matches')
                response = CONN.getresponse().read().decode()
                matches = json.loads(response)['response']

                clean_matches = {
                    'id': [],
                    'date': [],
                    'home_id': [],
                    'away_id': [],
                    'season': [],
                    'home_score': [],
                    'away_score': [],
                    'round': []
                }

                existing_matches = db.fetch_match_ids()

                for match in matches:
                    match_id = match['fixture']['id']
                    if match_id not in existing_matches: 
                        clean_matches['id'].append(match_id)
                        clean_matches['date'].append(match['fixture']['date'])
                        clean_matches['home_id'].append(match['teams']["home"]['id'])
                        clean_matches['away_id'].append(match['teams']["away"]['id'])
                        clean_matches['season'].append(season)
                        clean_matches['home_score'].append(match['goals']['home'])
                        clean_matches['away_score'].append(match['goals']['away'])
                        clean_matches['round'].append(match['league']['round'])


                clean_matches_df = pd.DataFrame(clean_matches)
                db.save_dataframe_to_table(clean_matches_df, 'match', 'append')            
                print('Saved match data to db')
            except Exception as e:
                print(f'Could not fetch matches due to {e}')
    



if __name__ == '__main__':
    # get_api_status()
    fetch_matches()