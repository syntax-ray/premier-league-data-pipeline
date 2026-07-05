from dotenv import load_dotenv
import logging
import os

import requests

from consts import API_FOOTBALL_URL, LOGGING_FILE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    filename=LOGGING_FILE,
)

logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("API_KEY")
if API_KEY is None:
    raise RuntimeError("API_KEY environment variable is not set.")

HEADERS = {
    "x-apisports-key": API_KEY,
}


def get_api_info():
    """
    Fetch information about the current API-Football subscription.
    """
    try:
        response = requests.get(
            f"{API_FOOTBALL_URL}/status",
            headers=HEADERS,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        max_calls_per_minute = response.headers["X-RateLimit-Limit"]
        requests_made = data["response"]["requests"]["current"]
        requests_limit = data["response"]["requests"]["limit_day"]

        logger.info(
            "Retrieved API status: %s/%s requests used.",
            requests_made,
            requests_limit,
        )

        return (
            f"The current request status is {requests_made} / {requests_limit}",
            max_calls_per_minute,
        )

    except requests.exceptions.RequestException:
        logger.exception("Failed to retrieve API status.")
        raise

if __name__ == '__main__':
    get_api_info()