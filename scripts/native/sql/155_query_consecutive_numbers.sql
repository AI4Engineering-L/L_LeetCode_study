SELECT DISTINCT a.num AS ConsecutiveNums
FROM Logs AS a
JOIN Logs AS b ON b.id = a.id + 1 AND b.num = a.num
JOIN Logs AS c ON c.id = a.id + 2 AND c.num = a.num;
