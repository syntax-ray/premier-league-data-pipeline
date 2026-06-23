select
  season
  ,team_id

from {{ ref('mart_team_season_summary') }}
group by
  season, team_id having count(*) > 1