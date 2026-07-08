import fetch_leagues 
import fetch_teams
import fetch_matches
from utils.logging_config import get_logger


def run_pipeline():
    logger = get_logger(__name__)
    logger.info("Pipeline started")
    try:
        fetch_leagues.run()
        fetch_teams.run()
        fetch_matches.run()
    except Exception as e:
        logger.error(e)
        raise
    logger.info("Pipeline completed successfully")


if __name__ == '__main__':
    run_pipeline()