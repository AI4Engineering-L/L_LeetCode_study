WITH eligible AS (
    SELECT *, id - ROW_NUMBER() OVER (ORDER BY id) AS run_id
    FROM Stadium WHERE people >= 100
), long_runs AS (
    SELECT run_id FROM eligible GROUP BY run_id HAVING COUNT(*) >= 3
)
SELECT e.id, e.visit_date, e.people
FROM eligible AS e JOIN long_runs AS r ON e.run_id = r.run_id
ORDER BY e.visit_date;
