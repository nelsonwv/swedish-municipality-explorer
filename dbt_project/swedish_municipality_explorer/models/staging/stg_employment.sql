with source as (

    select *
    from {{ source('raw', 'raw_employment') }}
    where time_period = '2021'

)

select
    cast(region_code as varchar(10)) as municipality_code,
    region_text as municipality_name,
    cast(time_period as integer) as year,
    case
        when sex_text = 'men and women' then 'total'
        else coalesce(sex_text, 'total')
    end as sex,
    case
        when region_of_birth_text = 'born in Sweden' then 'born_in_sweden'
        when region_of_birth_text = 'foreign-born' then 'born_abroad'
        when region_of_birth_text = 'total' then 'total'
        else coalesce(region_of_birth_text, 'total')
    end as region_of_birth,
    try_cast(value as float) as value
from source
