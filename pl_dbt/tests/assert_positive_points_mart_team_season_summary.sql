select
  *

from {{ ref('mart_team_season_summary') }}
where
  points < 0