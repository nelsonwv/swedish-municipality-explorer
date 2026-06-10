with population as (

    select
        municipality_code,
        municipality_name,
        year,
        value as population_total
    from {{ ref('stg_population') }}
    where sex = 'total' and region_of_birth = 'total'

),

income as (

    select
        municipality_code,
        value as median_income
    from {{ ref('stg_income') }}
    where sex = 'total' and region_of_birth = 'total'

),

employment_total as (

    select
        municipality_code,
        value as employment_rate_total
    from {{ ref('stg_employment') }}
    where region_of_birth = 'total'

),

employment_foreign_born as (

    select
        municipality_code,
        value as employment_rate_foreign_born
    from {{ ref('stg_employment') }}
    where region_of_birth = 'born_abroad'

),

education as (

    select
        municipality_code,
        value as post_secondary_pop
    from {{ ref('stg_education') }}
    where sex = 'total' and region_of_birth = 'total'

),

commuting as (

    select
        municipality_code,
        value as commuters_out
    from {{ ref('stg_commuting') }}
    where sex = 'total' and region_of_birth = 'total'

)

select
    population.municipality_code,
    population.municipality_name,
    left(population.municipality_code, 2) as county_code,
    population.population_total,
    income.median_income,
    employment_total.employment_rate_total,
    employment_foreign_born.employment_rate_foreign_born,
    employment_total.employment_rate_total
        - employment_foreign_born.employment_rate_foreign_born as employment_gap,
    education.post_secondary_pop
        / nullif(population.population_total, 0) * 100 as pct_post_secondary,
    commuting.commuters_out
        / nullif(
            population.population_total * employment_total.employment_rate_total / 100, 0
        ) * 100 as out_commute_rate,
    case
        when population.population_total < 20000 then 'small'
        when population.population_total < 100000 then 'medium'
        else 'large'
    end as population_category,
    population.year
from population
left join income on population.municipality_code = income.municipality_code
left join employment_total on population.municipality_code = employment_total.municipality_code
left join employment_foreign_born
    on population.municipality_code = employment_foreign_born.municipality_code
left join education on population.municipality_code = education.municipality_code
left join commuting on population.municipality_code = commuting.municipality_code
