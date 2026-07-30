-- Audit test: the dedupe must not lose rows, only collapse them.
-- sum(source_row_count) in staging must equal the raw source row count.
-- Fails if the grain changes or the dedupe starts dropping data silently.

with source_rows as (
    select count(*) as n from {{ source('raw', 'student_performance') }}
),

staged_rows as (
    select sum(source_row_count) as n from {{ ref('stg_student_performance') }}
)

select
    source_rows.n as source_row_count,
    staged_rows.n as staged_row_count
from source_rows
cross join staged_rows
where source_rows.n != staged_rows.n
