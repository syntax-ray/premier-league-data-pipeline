with
league_match
as (
    select
       id                                           as id
       ,coalesce(date, '1700-01-01'::date)          as date
       ,coalesce(home_id, -99)                      as home_id
       ,coalesce(away_id, -99)                      as away_id
       ,coalesce(home_score, -99)                   as home_score
       ,coalesce(away_score, -99)                   as away_score
       ,coalesce(season, -99)                       as season       

    from {{ source('pl_data', 'match') }}
)

select
  *

from league_match