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


def test_fetch_match():
    CONN.request("GET", f"/fixtures?league=39&season=2012", headers=HEADERS)
    print('Successfully fetched matches')
    response = CONN.getresponse().read().decode()
    matches = json.loads(response)['response']
    print(response)
    print()
    print(matches)


def test_fetch_teams():
    CONN.request("GET", f"/teams?league=39&season=2010", headers=HEADERS)
    print('Successfully fetched teams')
    CONN.getresponse().status
    response = CONN.getresponse().read().decode()
    teams = json.loads(response)['response']
    print(response)
    print()
    print(teams)


if __name__ == '__main__':
    test_fetch_teams()