import pandas as pd
import requests
from db_int import DB
from fetch_api_info import get_api_info
from utils.logging_config import get_logger
from api.api_football import api_football_get


logger = get_logger(__name__)


def fetch_leagues():
    """
    Fetch raw league data from the API.
    """
    try:
        response = api_football_get(endpoint='leagues')

        data = response.json()

        logger.info("Successfully fetched league data.")

        return data["response"]

    except requests.exceptions.RequestException:
        logger.exception("Failed to fetch leagues from API.")
        raise


def transform_leagues(leagues):
    """
    Transform raw API response into a pandas DataFrame.
    """

    records = [
        {
            "id": idx + 1,
            "league_id": league["league"]["id"],
            "name": league["league"]["name"],
            "type": league["league"]["type"],
            "country": league["country"]["name"],
        }
        for idx, league in enumerate(leagues)
    ]

    df = pd.DataFrame(records)

    logger.info("Successfully transformed %d leagues.", len(df))

    return df


def save_leagues(df):
    """
    Save league DataFrame to the database.
    """
    try:
        db = DB()

        db.save_dataframe_to_table(
            df,
            table_name="league",
            if_exists="replace",
        )

        logger.info("Successfully saved %d leagues.", len(df))

    except Exception:
        logger.exception("Failed to save leagues to database.")
        raise


def run():
    """
    Execute the complete ETL pipeline.
    """
    leagues = fetch_leagues()

    df = transform_leagues(leagues)

    save_leagues(df)


if __name__ == "__main__":
    current_api_status, _ = get_api_info()
    logger.info(current_api_status)

    try:
        run()
    except Exception:
        logger.exception("League ETL pipeline failed.")