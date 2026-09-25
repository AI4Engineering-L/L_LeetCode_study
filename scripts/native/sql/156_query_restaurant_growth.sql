WITH daily AS (
    SELECT visited_on, SUM(amount) AS daily_amount FROM Customer GROUP BY visited_on
), rolling AS (
    SELECT visited_on,
           SUM(daily_amount) OVER (
               ORDER BY JULIANDAY(visited_on)
               RANGE BETWEEN 6 PRECEDING AND CURRENT ROW
           ) AS amount
    FROM daily
)
SELECT visited_on, amount, ROUND(amount / 7.0, 2) AS average_amount
FROM rolling
WHERE JULIANDAY(visited_on) - (SELECT JULIANDAY(MIN(visited_on)) FROM daily) >= 6
ORDER BY visited_on;
