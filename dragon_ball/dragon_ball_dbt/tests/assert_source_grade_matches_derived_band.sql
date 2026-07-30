-- The source FinalGrade column appears to be a deterministic function of
-- ExamScore. This test asserts that rule still holds on every refresh: if
-- upstream ever changes its banding, this fails loudly instead of silently
-- disagreeing with seed_grade_band.

select
    student_observation_key,
    exam_score,
    source_grade_code,
    derived_grade_code
from {{ ref('fct_student_performance') }}
where source_grade_code != derived_grade_code
