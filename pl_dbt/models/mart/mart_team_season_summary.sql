with
season_match_detail
as (
    select
      mtch.id                                 as match_id
      ,home_id
      ,away_id
      ,home_team.name                         as home_name
      ,away_team.name                         as away_name
      ,home_score
      ,away_score
      ,season

    from {{ ref('stg_match') }} mtch
    left outer join {{ ref('stg_team') }} home_team on mtch.home_id = home_team.id
    left outer join {{ ref('stg_team') }} away_team on mtch.away_id = away_team.id
),

season_summary_home
as (
  select
    team.id                                                                     as team_id
    ,team.name                                                                  as team_name
    ,smd_home.season
    ,count(*)                                                                   as home_matches_played
    ,sum(case
       when (smd_home.home_score > smd_home.away_score) then 1
       else 0
     end)                                                                       as home_wins
    ,sum(case
       when (smd_home.home_score = smd_home.away_score) then 1
       else 0
     end)                                                                       as home_draws
    ,sum(case
       when (smd_home.home_score < smd_home.away_score) then 1
       else 0
     end)                                                                       as home_losses
    ,sum(smd_home.home_score)                                                   as home_goals_for
    ,sum(smd_home.away_score)                                                   as home_goals_against
    ,sum(smd_home.home_score) -  sum(smd_home.away_score)                       as home_goal_difference
    ,sum(case
       when (smd_home.home_score > smd_home.away_score) then 3
       when (smd_home.home_score = smd_home.away_score) then 1
       else 0
     end)                                                                       as home_points

  from  {{ ref('stg_team') }} team
  left outer join season_match_detail smd_home on smd_home.home_id = team.id
  group by
    team.id,
    team.name,
    smd_home.season

),

season_summary_away
as (
  select
    team.id                                                                     as team_id
    ,team.name                                                                  as team_name
    ,smd_away.season
    ,count(*)                                                                   as away_matches_played
    ,sum(case
       when (smd_away.away_score > smd_away.home_score) then 1
       else 0
     end)                                                                       as away_wins
    ,sum(case
       when (smd_away.home_score = smd_away.away_score) then 1
       else 0
     end)                                                                       as away_draws
    ,sum(case
       when (smd_away.home_score > smd_away.away_score) then 1
       else 0
     end)                                                                       as away_losses
    ,sum(smd_away.away_score)                                                   as away_goals_for
    ,sum(smd_away.home_score)                                                   as away_goals_against
    ,sum(smd_away.away_score) -  sum(smd_away.home_score)                       as away_goal_difference
    ,sum(case
       when (smd_away.away_score > smd_away.home_score) then 3
       when (smd_away.home_score = smd_away.away_score) then 1
       else 0
     end)                                                                       as away_points

  from {{ ref('stg_team') }} team
  left outer join season_match_detail smd_away on smd_away.away_id = team.id
  group by
    team.id,
    team.name,
    smd_away.season

),

season_summary
as (
  select
    summary_home.season
    ,summary_home.team_id
    ,summary_home.team_name
    ,summary_home.home_matches_played + summary_away.away_matches_played                                  as matches_played
    ,summary_home.home_wins + summary_away.away_wins                                                      as wins
    ,summary_home.home_draws + summary_away.away_draws                                                    as draws
    ,summary_home.home_losses + summary_away.away_losses                                                  as losses
    ,summary_home.home_goals_for + summary_away.away_goals_for                                            as goals_for
    ,summary_home.home_goals_against + summary_away.away_goals_against                                    as goals_against
    ,summary_home.home_goal_difference                              
       + summary_away.away_goal_difference                                                                as goal_difference
    ,summary_home.home_points + summary_away.away_points                                                  as points
    ,round(((summary_home.home_wins + summary_away.away_wins) * 100)::numeric             
      / (summary_home.home_matches_played + summary_away.away_matches_played), 2)::numeric(5, 2)          as win_percentage
    ,round((summary_home.home_wins * 100)::numeric 
      /  summary_home.home_matches_played, 2)::numeric(5, 2)                                              as home_win_percentage
    ,round((summary_away.away_wins * 100)::numeric 
      /  summary_away.away_matches_played, 2)::numeric(5, 2)                                              as away_win_percentage

  from season_summary_home summary_home
  left outer join season_summary_away summary_away on summary_home.team_id = summary_away.team_id
    and summary_home.season = summary_away.season
)

select
  season
  ,team_id
  ,team_name
  ,matches_played
  ,wins
  ,draws
  ,losses
  ,goals_for
  ,goals_against
  ,goal_difference
  ,points
  ,win_percentage
  ,home_win_percentage
  ,away_win_percentage

from season_summary
order by
  season,
  points desc