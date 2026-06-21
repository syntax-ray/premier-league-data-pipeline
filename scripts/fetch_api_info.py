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


def max_calls_per_minute():
    CONN.request('GET',"/status", headers=HEADERS)
    max_calls = CONN.getresponse().getheader('X-RateLimit-Limit')
    return max_calls


def get_api_info():
    try:
        CONN.request('GET',"/status", headers=HEADERS)
        response = CONN.getresponse().read().decode()
        status = json.loads(response)
        requests_made = status['response']['requests']['current']
        requests_limit = status['response']['requests']['limit_day']
        print(f'The current request status is {requests_made} / {requests_limit}')
    except Exception as e:
        print(f'Could not get status due to {e}')


if __name__ == '__main__':
    print(max_calls_per_minute())