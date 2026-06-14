with
league
as (
    select
       league_id                                as id
      ,lower(coalesce(name, 'n/a'))             as name
      ,lower(coalesce(type, 'n/a'))             as type
      ,lower(coalesce(country, 'n/a'))          as country

    from {{ source('pl_data', 'league') }}
)

select
  *

from league