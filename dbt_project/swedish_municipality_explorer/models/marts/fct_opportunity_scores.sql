with profiles as (

    select
        municipality_code,
        median_income,
        pct_post_secondary,
        out_commute_rate,
        year
    from {{ ref('int_municipality_profiles') }}

),

-- Income, education, and mobility are not broken down by region_of_birth
-- in the source data, so these scores are computed once per municipality
-- and repeated across all region_of_birth rows below.
base_scores as (

    select
        municipality_code,
        year,
        (median_income - min(median_income) over ())
            / nullif(
                max(median_income) over () - min(median_income) over (), 0
            ) * 100 as income_score,
        (pct_post_secondary - min(pct_post_secondary) over ())
            / nullif(
                max(pct_post_secondary) over () - min(pct_post_secondary) over (), 0
            ) * 100 as education_score,
        -- mobility_score is the inverse of out_commute_rate: lower
        -- commuting = higher score.
        (max(out_commute_rate) over () - out_commute_rate)
            / nullif(
                max(out_commute_rate) over () - min(out_commute_rate) over (), 0
            ) * 100 as mobility_score
    from profiles

),

-- Employment rate is broken down by region_of_birth ('total',
-- 'born_in_sweden', 'born_abroad'), so employment_score is normalized
-- separately within each region_of_birth group.
employment_scores as (

    select
        municipality_code,
        region_of_birth,
        year,
        (value - min(value) over (partition by region_of_birth))
            / nullif(
                max(value) over (partition by region_of_birth)
                - min(value) over (partition by region_of_birth), 0
            ) * 100 as employment_score
    from {{ ref('stg_employment') }}

)

select
    employment_scores.municipality_code,
    employment_scores.region_of_birth,
    base_scores.income_score,
    employment_scores.employment_score,
    base_scores.education_score,
    base_scores.mobility_score,
    employment_scores.year
from employment_scores
inner join base_scores
    on employment_scores.municipality_code = base_scores.municipality_code
    and employment_scores.year = base_scores.year
