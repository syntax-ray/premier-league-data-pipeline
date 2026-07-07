import fetch_leagues 
import fetch_teams
import fetch_matches


def run_pipeline():
    fetch_leagues.run()
    fetch_teams.run()
    fetch_matches.run()


if __name__ == '__main__':
    run_pipeline()