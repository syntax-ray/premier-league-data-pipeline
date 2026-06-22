# premier-league-data-pipeline

End-to-end data pipeline built using: Python, and SQL

API: https://www.api-football.com/


# Current progress

1. Fetched leagues data from API and saved it to db.
2. Fetched premier league team data from API for the available seasons and saved it to db
3. Fetched premier league match data from API for the available seasons and saved it to db
4. Added dbt to the project and connected the premier league data as a data source
5. Added a staging layer to the dbt project where naming uniformity and duplicate checks were handled
6. Added a marts layer to the dbt project
7. Added a team_season_summary mart script that breaks down team performance per season