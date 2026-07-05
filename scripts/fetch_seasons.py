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
    "x-apisports-key": API_KEY
}


def fetch_seasons():
    """Fetch available football seasons from the API."""

    try:
        response = requests.get(
            f"{API_FOOTBALL_URL}/leagues/seasons",
            headers=HEADERS,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        seasons = sorted(data["response"])

        logger.info("Fetched %d seasons.", len(seasons))

        return seasons

    except requests.exceptions.RequestException:
        logger.exception("Failed to fetch seasons from API.")
        raise

if __name__ == '__main__':
    fetch_seasons()