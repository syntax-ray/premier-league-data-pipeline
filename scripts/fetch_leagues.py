from dotenv import load_dotenv
import os
import http.client
import json
import pandas as pd
from db_int import DB

load_dotenv()
API_KEY = os.getenv('API_KEY')
CONN = http.client.HTTPSConnection("v3.football.api-sports.io")
LEAGUES_SAVE_PATH = os.path.join(os.getcwd(), 'data', 'leagues.json')
LEAGUES_SUMMARY_SAVE_PATH = os.path.join(os.getcwd(), 'data', 'leagues_summary.csv')

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

def fetch_leagues():
    try:
        CONN.request("GET", "/leagues", headers=HEADERS)
        print('Successfully fetched leagues')
        response = CONN.getresponse().read().decode()
        leagues = json.loads(response)['response']
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
        print(f'Could not fetch leagues due to {e}')
    

if __name__ == '__main__':
    get_api_status()
    fetch_leagues()