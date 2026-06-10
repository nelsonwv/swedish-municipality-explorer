with source as (

    select *
    from {{ source('raw', 'raw_commuting') }}
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
    coalesce(region_of_birth_text, 'total') as region_of_birth,
    -- NOTE: value is a COUNT of commuters leaving the municipality, not
    -- yet a rate. It is converted to out_commute_rate in
    -- int_municipality_profiles. See docs/agents/agent3_dbt.md status log.
    try_cast(value as float) as value
from source
