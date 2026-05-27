from dotenv import load_dotenv
import os
import http.client
import json
import pandas as pd

load_dotenv()
API_KEY = os.getenv('API_KEY')
CONN = http.client.HTTPSConnection("v3.football.api-sports.io")
AVALABLE_LEAGUES_SAVE_PATH = os.path.join(os.getcwd(), 'data', 'leagues.json')
AVAILABLE_LEAGUES_SUMMARY_SAVE_PATH = os.path.join(os.getcwd(), 'data', 'leagues_summary.csv')

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
        print(f'The current status is {requests_made} / {requests_limit}')
    except Exception as e:
        print(f'Could not get status due to {e}')

def fetch_available_leagues():
    try:
        CONN.request("GET", "/leagues", headers=HEADERS)
        print('Successfully fetched leagues')
        response = CONN.getresponse().read().decode()
        leagues = json.loads(response)['response']
        with open(AVALABLE_LEAGUES_SAVE_PATH, 'w') as f:
            json.dump(leagues, f)
        print('Saved leagues data to file')
        get_api_status()
    except Exception as e:
        print(f'Could not fetch leagues due to {e}')
    
def available_leagues_to_summary_csv():
    leagues = None
    with open(AVALABLE_LEAGUES_SAVE_PATH, 'r') as f:
        leagues = json.load(f)
    summary = {
        'id': [],
        'league_id': [],
        'name': [],
        'type': [],
        'country': []
    }
    for idx, league in enumerate(leagues):
        summary['id'].append(idx + 1)
        summary['league_id'].append(league['league']['id'])
        summary['name'].append(league['league']['name'])
        summary['type'].append(league['league']['type'])
        summary['country'].append(league['country']['name'])

    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(path_or_buf=AVAILABLE_LEAGUES_SUMMARY_SAVE_PATH, index=False)


if __name__ == '__main__':
    get_api_status()
    if not os.path.exists(AVALABLE_LEAGUES_SAVE_PATH):
        fetch_available_leagues ()
        available_leagues_to_summary_csv()
    if not os.path.exists(AVAILABLE_LEAGUES_SUMMARY_SAVE_PATH):
        available_leagues_to_summary_csv()
    