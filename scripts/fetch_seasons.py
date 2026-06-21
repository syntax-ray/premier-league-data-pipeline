from dotenv import load_dotenv
import os
import http.client
import json

load_dotenv()
API_KEY = os.getenv('API_KEY')
CONN = http.client.HTTPSConnection("v3.football.api-sports.io")
TARGET_YEAR = 2024


HEADERS = {
    'x-apisports-key': API_KEY
    }


def fetch_seasons():
    '''
        Fetches available season years from the api
    '''
    try:
        CONN.request("GET", f"/leagues/seasons", headers=HEADERS)
        print('Successfully fetched seasons')
        response = CONN.getresponse().read().decode()
        seasons = json.loads(response)['response']
        seasons.sort()
        return seasons

    except Exception as e:
        print(f'Could not fetch seasons due to {e}')


if __name__ == '__main__':
    print(fetch_seasons())