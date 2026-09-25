WITH first_login AS (
    SELECT player_id, MIN(event_date) AS first_date FROM Activity GROUP BY player_id
)
SELECT ROUND(COALESCE(1.0 * SUM(EXISTS (
    SELECT 1 FROM Activity AS a
    WHERE a.player_id = f.player_id AND a.event_date = DATE(f.first_date, '+1 day')
)) / COUNT(*), 0.0), 2) AS fraction
FROM first_login AS f;
