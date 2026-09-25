WITH maximum AS (
    SELECT departmentId, MAX(salary) AS highest
    FROM Employee GROUP BY departmentId
)
SELECT d.name AS Department, e.name AS Employee, e.salary AS Salary
FROM Employee AS e
JOIN maximum AS m ON m.departmentId = e.departmentId AND e.salary = m.highest
JOIN Department AS d ON d.id = e.departmentId;
