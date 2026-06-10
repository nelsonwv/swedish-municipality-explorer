select *
from {{ ref('fct_opportunity_scores') }}
where income_score < 0 or income_score > 100
   or employment_score < 0 or employment_score > 100
   or education_score < 0 or education_score > 100
   or mobility_score < 0 or mobility_score > 100
