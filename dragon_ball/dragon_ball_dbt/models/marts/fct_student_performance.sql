-- Gold layer: grain-level fact. One row per student observation, with every
-- code resolved to a human-readable label and business rules applied.
--
-- Note this mart is NOT aggregated — a fact table at native grain is still a
-- mart. What makes it gold is that it is safe for a BI tool to query directly.

with obs as (

    select * from {{ ref('stg_student_performance') }}

),

grade_band as (
    select * from {{ ref('seed_grade_band') }}
),

learning_style as (
    select * from {{ ref('seed_learning_style') }}
),

gender as (
    select * from {{ ref('seed_gender') }}
),

resources as (
    select * from {{ ref('seed_ordinal_level') }}
),

motivation as (
    select * from {{ ref('seed_ordinal_level') }}
),

stress as (
    select * from {{ ref('seed_ordinal_level') }}
),

joined as (

    select
        obs.student_observation_key,

        -- decoded dimensions
        gender.gender,
        learning_style.learning_style,
        resources.level_label            as resource_access_level,
        motivation.level_label           as motivation_level,
        stress.level_label               as stress_level,
        grade_band.grade_letter,
        grade_band.is_passing,

        -- ordinal ranks, for ORDER BY in a BI tool
        resources.level_rank             as resource_access_rank,
        motivation.level_rank            as motivation_rank,
        stress.level_rank                as stress_rank,

        -- measures
        obs.age,
        obs.study_hours_per_week,
        obs.attendance_pct,
        obs.assignment_completion_pct,
        obs.exam_score,
        obs.online_courses_taken,

        -- flags
        obs.has_extracurricular,
        obs.has_internet_access,
        obs.participates_in_discussions,
        obs.uses_edu_tech,

        -- Business rule: FinalGrade in the source is fully derived from
        -- ExamScore (85-100=A, 70-84=B, 55-69=C, 40-54=D). We recompute it
        -- from the seed and assert agreement in a test, so the rule lives in
        -- version control rather than being trusted blindly from upstream.
        obs.grade_code                   as source_grade_code,
        grade_band.grade_code            as derived_grade_code

    from obs
    left join grade_band
        on obs.exam_score between grade_band.min_exam_score
                              and grade_band.max_exam_score
    left join learning_style
        on obs.learning_style_code = learning_style.learning_style_code
    left join gender
        on obs.gender_code = gender.gender_code
    left join resources
        on obs.resources_code = resources.level_code
    left join motivation
        on obs.motivation_code = motivation.level_code
    left join stress
        on obs.stress_level_code = stress.level_code

)

select * from joined
