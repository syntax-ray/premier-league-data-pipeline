import requests
from utils.logging_config import get_logger
from api.api_football import api_football_get

logger = get_logger(__name__)


def get_api_info():
    """
    Fetch information about the current API-Football subscription.
    """
    try:
        response = api_football_get(endpoint='status')

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