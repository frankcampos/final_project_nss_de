-- Silver layer: one row per distinct student observation.
--
-- Responsibilities kept deliberately narrow: dedupe, rename to snake_case,
-- cast booleans, mint a surrogate key. No joins, no business logic — those
-- belong in marts.

with source as (

    select * from {{ source('raw', 'student_performance') }}

),

deduped as (

    -- The source ships genuine duplicate rows: 1,334 distinct row-values
    -- repeat, some up to 5x. Tested against chance: using the actual marginal
    -- distributions, P(two rows identical) = 3.9e-13, so 14k rows should yield
    -- 0.0000038 duplicate pairs. We observe 1,758. These are artifacts of how
    -- the dataset was assembled, not coincidence, so collapsing them is safe.
    --
    -- GROUP BY rather than SELECT DISTINCT: same rows out, but it preserves
    -- the multiplicity in source_row_count instead of discarding it. That
    -- keeps the collapse auditable — sum(source_row_count) reconciles back to
    -- the source row count.
    select
        *,
        count(*) as source_row_count
    from source
    group by all

),

renamed as (

    select
        -- The source has no natural key (no student_id), so the full attribute
        -- set IS the identity. Post-dedupe this is unique by construction.
        md5(concat_ws('|',
            StudyHours, Attendance, Resources, Extracurricular, Motivation,
            Internet, Gender, Age, LearningStyle, OnlineCourses, Discussions,
            AssignmentCompletion, ExamScore, EduTech, StressLevel, FinalGrade
        )) as student_observation_key,

        -- measures
        StudyHours              as study_hours_per_week,
        Attendance              as attendance_pct,
        AssignmentCompletion    as assignment_completion_pct,
        ExamScore               as exam_score,
        OnlineCourses           as online_courses_taken,
        Age                     as age,

        -- categorical codes, decoded in the mart layer via seed joins
        Resources               as resources_code,
        Motivation              as motivation_code,
        StressLevel             as stress_level_code,
        LearningStyle           as learning_style_code,
        Gender                  as gender_code,
        FinalGrade              as grade_code,

        -- 0/1 integers are booleans in disguise; make that explicit
        Extracurricular = 1     as has_extracurricular,
        Internet = 1            as has_internet_access,
        Discussions = 1         as participates_in_discussions,
        EduTech = 1             as uses_edu_tech,

        -- How many times this exact combination appeared in the source.
        -- 1 for most rows, up to 5 for the repeated ones.
        source_row_count

    from deduped

)

select * from renamed
