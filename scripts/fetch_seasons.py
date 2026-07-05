import requests
from utils.logging_config import get_logger
from api.api_football import api_football_get

logger = get_logger(__name__)


def fetch_seasons():
    """Fetch available football seasons from the API."""

    try:
        response = api_football_get(endpoint="/leagues/seasons")

        data = response.json()

        seasons = sorted(data["response"])

        logger.info("Fetched %d seasons.", len(seasons))

        return seasons

    except requests.exceptions.RequestException:
        logger.exception("Failed to fetch seasons from API.")
        raise

if __name__ == '__main__':
    fetch_seasons()