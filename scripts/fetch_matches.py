from dotenv import load_dotenv
import os
import http.client
import json

load_dotenv()
API_KEY = os.getenv('API_KEY')
CONN = http.client.HTTPSConnection("v3.football.api-sports.io")

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

def fetch_leagues():
    try:
        CONN.request("GET", "/leagues", headers=HEADERS)
        print('Successfully fetched leagues')
        response = CONN.getresponse().read().decode()
        leagues = json.loads(response)['response']
        leagues_save_path = os.path.join(os.getcwd(), 'data', 'leagues.json')
        with open(leagues_save_path, 'w') as f:
            json.dump(leagues, f)
        print('Saved leagues data to file')
        get_api_status()
    except Exception as e:
        print(f'Could not fetch leagues due to {e}')
    


if __name__ == '__main__':
    get_api_status()
    fetch_leagues()
    