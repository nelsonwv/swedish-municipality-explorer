with source as (

    select *
    from {{ source('raw', 'raw_population') }}
    where time_period = '2021'

)

select
    cast(region_code as varchar(10)) as municipality_code,
    region_text as municipality_name,
    cast(time_period as integer) as year,
    coalesce(sex_text, 'total') as sex,
    coalesce(region_of_birth_text, 'total') as region_of_birth,
    try_cast(value as float) as value
from source
