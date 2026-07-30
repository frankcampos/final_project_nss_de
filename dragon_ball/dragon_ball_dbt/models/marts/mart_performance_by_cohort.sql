-- Gold layer: aggregated mart. One row per (learning style x resource access
-- x motivation) cohort — the "aggregation" half of the mart layer.
--
-- Honest caveat: profiling showed every source feature has ~0 correlation with
-- exam_score (all |r| < 0.04 across 14k rows), so these cohort averages are
-- expected to be flat at ~70. The flatness is the finding. This mart exists to
-- make that visible and auditable, not to imply a relationship.

with fct as (

    select * from {{ ref('fct_student_performance') }}

),

aggregated as (

    select
        learning_style,
        resource_access_level,
        motivation_level,

        count(*)                                        as student_count,

        round(avg(exam_score), 2)                       as avg_exam_score,
        min(exam_score)                                 as min_exam_score,
        max(exam_score)                                 as max_exam_score,
        round(stddev_samp(exam_score), 2)               as stddev_exam_score,

        round(avg(study_hours_per_week), 2)             as avg_study_hours,
        round(avg(attendance_pct), 2)                   as avg_attendance_pct,
        round(avg(assignment_completion_pct), 2)        as avg_assignment_completion_pct,

        round(100.0 * sum(case when is_passing then 1 else 0 end) / count(*), 2)
                                                        as pass_rate_pct,
        round(100.0 * sum(case when has_internet_access then 1 else 0 end) / count(*), 2)
                                                        as internet_access_pct

    from fct
    group by 1, 2, 3

)

select * from aggregated
order by avg_exam_score desc
