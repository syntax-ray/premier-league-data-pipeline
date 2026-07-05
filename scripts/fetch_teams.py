import time
import pandas as pd
import requests
from db_int import DB
from fetch_api_info import get_api_info
from fetch_seasons import fetch_seasons
from utils.logging_config import get_logger
from api.api_football import api_football_get, wait_for_rate_limit

logger = get_logger(__name__)

def fetch_league_ids():
    """
    Fetch the league IDs to process.

    Currently restricted to the English Premier League due to API limits.
    """
    db = DB()

    league_ids = db.fetch_league_ids()

    prem = league_ids.loc[
        (league_ids["name"] == "Premier League")
        & (league_ids["country"] == "England")
    ]

    if prem.empty:
        raise ValueError("Premier League could not be found.")

    return [prem.iloc[0]["league_id"]]


def fetch_existing_team_ids():
    """
    Fetch existing team IDs from the database.

    Returns
    -------
    set
        Existing team IDs.
    """
    db = DB()

    return set(db.fetch_team_ids())


def fetch_teams_for_season(league_id, season):
    """
    Fetch raw team data for a league and season.
    """
    try:
        params={
            "league": league_id,
            "season": season,
        }

        response = api_football_get(endpoint='teams', params=params)

        data = response.json()

        logger.info(
            "Fetched %d teams for season %s.",
            len(data["response"]),
            season,
        )

        return data["response"]

    except requests.exceptions.RequestException:
        logger.exception(
            "Failed to fetch teams for league %s season %s.",
            league_id,
            season,
        )
        raise


def transform_teams(teams, existing_team_ids):
    """
    Transform API team data into a DataFrame.
    """

    records = []

    for team in teams:

        team_id = team["team"]["id"]

        if team_id in existing_team_ids:
            continue

        records.append(
            {
                "id": team_id,
                "name": team["team"]["name"],
                "country": team["team"]["country"],
                "national": team["team"]["national"],
            }
        )

    df = pd.DataFrame(records)

    logger.info(
        "Prepared %d new teams.",
        len(df),
    )

    return df


def save_teams(df):
    """
    Save teams to the database.
    """

    if df.empty:
        logger.info("No new teams to save.")
        return

    try:
        db = DB()

        db.save_dataframe_to_table(
            df,
            table_name="team",
            if_exists="append",
        )

        logger.info(
            "Saved %d teams.",
            len(df),
        )

    except Exception:
        logger.exception("Failed to save teams.")
        raise


def run():
    """
    Execute the team ingestion pipeline.
    """

    league_ids = fetch_league_ids()

    seasons = fetch_seasons()

    existing_team_ids = fetch_existing_team_ids()

    first_request = True

    for league_id in league_ids:

        for season in seasons:

            logger.info("Processing season %s.", season)

            if not first_request:
                logger.info("Waiting 30 seconds for API rate limit.")
            
            first_request = wait_for_rate_limit(first_request)

            teams = fetch_teams_for_season(
                league_id,
                season,
            )

            df = transform_teams(
                teams,
                existing_team_ids,
            )

            save_teams(df)

            if df.shape[0] > 0:
                existing_team_ids.update(df["id"])


if __name__ == "__main__":

    current_api_status, _ = get_api_info()
    logger.info(current_api_status)

    try:
        run()

    except Exception:
        logger.exception("Team ingestion pipeline failed.")