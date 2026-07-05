from dotenv import load_dotenv
import logging
import os
import time

import pandas as pd
import requests

from consts import API_FOOTBALL_URL, LOGGING_FILE
from db_int import DB
from fetch_seasons import fetch_seasons
from utils.logging_config import get_logger

logger = get_logger(__name__)

load_dotenv()

API_KEY = os.getenv("API_KEY")

if API_KEY is None:
    raise RuntimeError("API_KEY environment variable is not set.")

HEADERS = {
    "x-apisports-key": API_KEY
}


def fetch_league_ids():
    """
    Fetch the league IDs that should be processed.

    Currently restricted to the English Premier League due to API constraints.
    """
    db = DB()

    league_ids = db.fetch_league_ids()

    prem = league_ids.loc[
        (league_ids["name"] == "Premier League")
        & (league_ids["country"] == "England")
    ]

    if prem.empty:
        raise ValueError("Premier League could not be found in the database.")

    return [prem.iloc[0]["league_id"]]


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
        response = requests.get(
            f"{API_FOOTBALL_URL}/fixtures",
            params={
                "league": league_id,
                "season": season,
            },
            headers=HEADERS,
            timeout=10,
        )

        response.raise_for_status()

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


def transform_matches(matches, season, existing_match_ids):
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


def wait_for_rate_limit(first_request):
    """
    Sleep between requests to respect API rate limits.

    Returns
    -------
    bool
        Always False after the first request.
    """

    if first_request:
        return False

    logger.info("Waiting 30 seconds for API rate limit.")

    time.sleep(30)

    return False


def run():
    """
    Execute the complete match ingestion pipeline.
    """

    league_ids = fetch_league_ids()

    seasons = fetch_seasons()

    existing_match_ids = fetch_existing_match_ids()

    first_request = True

    for league_id in league_ids:

        for season in seasons:

            logger.info("Processing season %s.", season)

            first_request = wait_for_rate_limit(first_request)

            matches = fetch_matches_for_season(
                league_id,
                season,
            )

            df = transform_matches(
                matches,
                season,
                existing_match_ids,
            )

            records = df.shape[0]

            save_matches(df)
            
            if records > 0:
                existing_match_ids.update(df["id"])


if __name__ == "__main__":

    try:
        run()

    except Exception:
        logger.exception("Match ingestion pipeline failed.")