import time
import pandas as pd
import requests
from db_int import DB
from fetch_seasons import fetch_seasons
from utils.logging_config import get_logger
from api.api_football import api_football_get, wait_for_rate_limit

logger = get_logger(__name__)

def fetch_existing_match_ids():
    """
    Fetch all existing match IDs from the database.

    Returns
    -------
    set
        Existing match IDs for fast membership checks.
    """
    db = DB()

    return set(db.fetch_match_ids())


def fetch_matches_for_season(league_id, season):
    """
    Fetch raw fixture data from API Football.
    """
    try:
        params={
            "league": league_id,
            "season": season,
        }

        response = api_football_get(endpoint="fixtures", params=params)

        data = response.json()

        logger.info(
            "Fetched %d fixtures for season %s.",
            len(data["response"]),
            season,
        )

        return data["response"]

    except requests.exceptions.RequestException:
        logger.exception(
            "Failed to fetch fixtures for league %s season %s.",
            league_id,
            season,
        )
        raise


def transform_matches(matches, season, existing_match_ids, league_id):
    """
    Transform raw API data into a DataFrame.
    """

    records = []

    for match in matches:

        match_id = match["fixture"]["id"]

        if match_id in existing_match_ids:
            continue

        records.append(
            {
                "id": match_id,
                "league_id": league_id,
                "date": match["fixture"]["date"],
                "home_id": match["teams"]["home"]["id"],
                "away_id": match["teams"]["away"]["id"],
                "season": season,
                "home_score": match["goals"]["home"],
                "away_score": match["goals"]["away"],
                "round": match["league"]["round"],
            }
        )

    df = pd.DataFrame(records)

    logger.info(
        "Prepared %d new matches for season %s.",
        len(df),
        season,
    )

    return df


def save_matches(df):
    """
    Save matches to the database.
    """

    if df.empty:
        logger.info("No new matches to save.")
        return

    try:
        db = DB()

        db.save_dataframe_to_table(
            df,
            table_name="match",
            if_exists="append",
        )

        logger.info(
            "Saved %d matches to database.",
            len(df),
        )

    except Exception:
        logger.exception("Failed to save matches.")
        raise


def run():
    """
    Execute the complete match ingestion pipeline.
    """

    db = DB()

    league_ids = db.fetch_league_ids()

    seasons = fetch_seasons()

    existing_match_ids = fetch_existing_match_ids()

    first_request = True

    for league_id, league_description in league_ids.items():

        logger.info("Fetching %s teams", league_description)

        for season in seasons:

            logger.info("Processing season %s.", season)

            if not first_request:
                logger.info("Waiting 30 seconds for API rate limit.")

            first_request = wait_for_rate_limit(first_request)

            matches = fetch_matches_for_season(
                league_id,
                season,
            )

            df = transform_matches(
                matches,
                season,
                existing_match_ids,
                league_id
            )

            records = df.shape[0]

            save_matches(df)
            
            if records > 0:
                existing_match_ids.update(df["id"])
            else:
                first_request = True


if __name__ == "__main__":

    try:
        run()

    except Exception:
        logger.exception("Match ingestion pipeline failed.")