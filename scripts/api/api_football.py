from dotenv import load_dotenv
import os
import requests

load_dotenv()

API_KEY = os.getenv("API_KEY")

if API_KEY is None:
    raise RuntimeError("API_KEY environment variable is not set.")

HEADERS = {
    "x-apisports-key": API_KEY
}

from consts import API_FOOTBALL_URL


def api_football_get(endpoint, params=None):
    """
    Execute a GET request against API Football.
    """

    response = requests.get(
        f"{API_FOOTBALL_URL}/{endpoint}",
        headers=HEADERS,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    return response