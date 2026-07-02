with
season_aggregates
as (
select
  season
  ,count(*)                                                                  as total_matches
  ,sum(home_score + away_score)                                              as total_goals_scored
  ,(sum(home_score + away_score)
    /   count(*)::numeric)::numeric(5, 2)                                    as average_goals_per_game
  ,round(sum(
     case when home_score > away_score then 1 else 0 end
   )::numeric * 100 / count(*), 2)                                           as home_win_percentage
  ,round(sum(
     case when away_score > home_score then 1 else 0 end
   )::numeric * 100 / count(*), 2)                                           as away_win_percentage
  ,round(sum(
     case when away_score = home_score then 1 else 0 end
   )::numeric * 100 / count(*), 2)                                           as draw_percentage

from {{ ref('stg_match') }}
group by
  season
)

select
   season
  ,total_matches
  ,total_goals_scored
  ,average_goals_per_game
  ,home_win_percentage
  ,away_win_percentage
  ,draw_percentage
  ,case
     when (round(home_win_percentage) + round(away_win_percentage) 
       + round(draw_percentage)) = 100 then true
     else false
   end                                                                       as percentage_validation

from season_aggregates