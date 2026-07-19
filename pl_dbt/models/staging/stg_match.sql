with
ranked_league_match
as (
    select
       id                                                       as id
       ,coalesce(league_id, -99)                                as league_id
       ,coalesce(date, '1700-01-01'::date)                      as date
       ,coalesce(home_id, -99)                                  as home_id
       ,coalesce(away_id, -99)                                  as away_id
       ,coalesce(home_score, -99)                               as home_score
       ,coalesce(away_score, -99)                               as away_score
       ,coalesce(season, -99)                                   as season
       ,row_number() over (partition by date, home_id, away_id) as rn       

    from {{ source('pl_data', 'match') }}
)

select
  id
  ,league_id                                                      
  ,date
  ,home_id
  ,away_id
  ,home_score
  ,away_score
  ,season

from ranked_league_match
where
  rn = 1