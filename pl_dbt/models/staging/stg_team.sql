with
ranked_team
as (
    select
       id                                           as id
       ,coalesce(country, 'n/a')                    as country
       ,coalesce(name, 'n/a')                       as name
       ,national                                    as national
       ,row_number() over (partition by id)         as rn

    from {{ source('pl_data', 'team') }}
)

select
  id
  ,country
  ,name
  ,national

from ranked_team
where
  rn = 1