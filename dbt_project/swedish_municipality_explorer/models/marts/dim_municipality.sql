select
    municipality_code,
    municipality_name,
    county_code,
    {{ county_name('county_code') }} as county_name,
    population_total as population,
    population_category,
    year
from {{ ref('int_municipality_profiles') }}
