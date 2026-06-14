with
team
as (
    select
       id                                           as id
       ,coalesce(country, 'n/a')                    as country
       ,coalesce(name, 'n/a')                       as name
       ,national                                    as national

    from {{ source('pl_data', 'team') }}
)

select
  *

from team