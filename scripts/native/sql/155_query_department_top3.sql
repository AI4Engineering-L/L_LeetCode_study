WITH ranked AS (
    SELECT e.*, DENSE_RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC) AS salary_rank
    FROM Employee AS e
)
SELECT d.name AS Department, r.name AS Employee, r.salary AS Salary
FROM ranked AS r JOIN Department AS d ON d.id = r.departmentId
WHERE r.salary_rank <= 3;
