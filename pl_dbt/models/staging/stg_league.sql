with
ranked_league
as (
    select
       league_id                                  as id
      ,lower(coalesce(name, 'n/a'))               as name
      ,lower(coalesce(type, 'n/a'))               as type
      ,lower(coalesce(country, 'n/a'))            as country
      ,row_number() over (partition by league_id) as rn

    from {{ source('pl_data', 'league') }}
)

select
  id
  ,name
  ,type
  ,country

from ranked_league
where
  rn = 1