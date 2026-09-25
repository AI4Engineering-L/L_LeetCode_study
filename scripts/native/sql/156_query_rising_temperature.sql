SELECT today.id
FROM Weather AS today JOIN Weather AS yesterday
ON yesterday.recordDate = DATE(today.recordDate, '-1 day')
WHERE today.temperature > yesterday.temperature;
