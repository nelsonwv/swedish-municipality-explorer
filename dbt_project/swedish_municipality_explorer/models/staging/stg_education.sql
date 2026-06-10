with source as (

    select *
    from {{ source('raw', 'raw_education') }}
    where time_period = '2021'

)

select
    cast(region_code as varchar(10)) as municipality_code,
    region_text as municipality_name,
    cast(time_period as integer) as year,
    coalesce(sex_text, 'total') as sex,
    coalesce(region_of_birth_text, 'total') as region_of_birth,
    -- NOTE: value is a population COUNT (residents with post-secondary
    -- education, ISCED97 levels 5-7), not yet a percentage. It is
    -- converted to pct_post_secondary in int_municipality_profiles.
    -- See docs/agents/agent3_dbt.md status log for details.
    try_cast(value as float) as value
from source
