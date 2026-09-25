from course_builder import add

def sql_code(queries,fixture):
    entries='\n'.join(f"    {name!r}: r'''{query.strip()}'''," for name,query in queries.items())
    return "import sqlite3\n\nSQL_QUERIES = {\n"+entries+"\n}\n\ndef create_sqlite_fixture():\n    connection=sqlite3.connect(':memory:')\n    connection.executescript(r'''"+fixture+"''')\n    return connection\n\ndef query_rows(connection,name):\n    return connection.execute(SQL_QUERIES[name]).fetchall()\n"

SQL152={
'query_recyclable_products.sql':'''SELECT product_id
FROM Products
WHERE low_fats = 'Y' AND recyclable = 'Y';''',
'query_big_countries.sql':'''SELECT name, population, area
FROM World
WHERE area >= 3000000 OR population >= 25000000;''',
'query_customer_referee.sql':'''SELECT name
FROM Customer
WHERE referee_id IS NULL OR referee_id <> 2;'''}
FIX152='''
CREATE TABLE Products(product_id INTEGER PRIMARY KEY,low_fats TEXT,recyclable TEXT);
INSERT INTO Products VALUES (0,'Y','N'),(1,'Y','Y'),(2,'N','Y'),(3,'Y','Y');
CREATE TABLE World(name TEXT PRIMARY KEY,area INTEGER,population INTEGER,gdp INTEGER);
INSERT INTO World VALUES ('AreaBoundary',3000000,1,0),('PopulationBoundary',1,25000000,0),('Small',2999999,24999999,0);
CREATE TABLE Customer(id INTEGER PRIMARY KEY,name TEXT,referee_id INTEGER);
INSERT INTO Customer VALUES (1,'Alice',NULL),(2,'Bob',2),(3,'Cara',1),(4,'Dan',NULL);
'''
add(152,'SQL表达的是集合/多重集筛选，不是逐行修改变量。WHERE只保留谓词为TRUE的行；与NULL比较得到UNKNOWN，不能用referee_id<>2保留未知推荐人，必须另写IS NULL。边界面积/人口条件采用OR；不带ORDER BY的结果不承诺顺序。',sql_code(SQL152,FIX152),
'''db=create_sqlite_fixture()
for name in SQL_QUERIES:
    cursor=db.execute(SQL_QUERIES[name]); print(name); show_table([x[0] for x in cursor.description],cursor.fetchall())
db.close()''',
'''db=create_sqlite_fixture()
assert set(query_rows(db,'query_recyclable_products.sql'))=={(1,),(3,)}
assert {row[0] for row in query_rows(db,'query_big_countries.sql')}=={'AreaBoundary','PopulationBoundary'}
assert set(query_rows(db,'query_customer_referee.sql'))=={('Alice',),('Cara',),('Dan',)}
assert db.execute('SELECT NULL <> 2, NULL = NULL, NULL IS NULL').fetchone()==(None,None,1)
db.executescript('DELETE FROM Products; DELETE FROM World; DELETE FROM Customer;')
assert all(query_rows(db,name)==[] for name in SQL_QUERIES)
db.close()''',
'AND要求两个条件同时为TRUE，OR要求至少一个为TRUE；NULL不是某个普通值，因此需使用IS NULL谓词。查询明确只选题目要求的列，不用SELECT *导致列契约漂移。测试按集合验证无排序要求的结果，同时保留NULL语义检查。',
'无额外索引时这些过滤查询扫描O(行数)，实际执行计划由数据库决定。本章在真实SQLite内存库执行；SQL文本以.sql名称映射保存在SQL_QUERIES中。其他数据库方言未在本轮执行。')

SQL153={
'query_people_addresses.sql':'''SELECT p.firstName, p.lastName, a.city, a.state
FROM Person AS p LEFT JOIN Address AS a ON a.personId = p.personId;''',
'query_employees_gt_manager.sql':'''SELECT e.name AS Employee
FROM Employee AS e JOIN Employee AS m ON e.managerId = m.id
WHERE e.salary > m.salary;''',
'query_managers.sql':'''SELECT m.name
FROM Employee AS e JOIN Employee AS m ON e.managerId = m.id
GROUP BY m.id, m.name
HAVING COUNT(*) >= 5;'''}
FIX153='''
CREATE TABLE Person(personId INTEGER PRIMARY KEY,firstName TEXT,lastName TEXT);
CREATE TABLE Address(addressId INTEGER PRIMARY KEY,personId INTEGER,city TEXT,state TEXT);
INSERT INTO Person VALUES (1,'Ann','A'),(2,'Ben','B');
INSERT INTO Address VALUES (1,1,'CityA','StateA');
CREATE TABLE Employee(id INTEGER PRIMARY KEY,name TEXT,salary INTEGER,managerId INTEGER);
INSERT INTO Employee VALUES (1,'Boss',100,NULL),(2,'E2',120,1),(3,'E3',80,1),(4,'E4',NULL,1),(5,'E5',90,1),(6,'E6',110,1),(7,'NoManager',200,NULL);
'''
add(153,'连接会改变行数。LEFT JOIN保留没有地址的人，但若把右表条件写进WHERE，可能又排除NULL行。自连接要用不同别名区分员工与经理。聚合时COUNT(*)计算行，COUNT(col)忽略NULL；经理是否有五个下属不能按非空工资数计。',sql_code(SQL153,FIX153),
'''db=create_sqlite_fixture(); cursor=db.execute(SQL_QUERIES['query_people_addresses.sql'])
show_table([x[0] for x in cursor.description],cursor.fetchall())
show_table(['员工行数','非空工资数'],db.execute('SELECT COUNT(*), COUNT(salary) FROM Employee').fetchall())
db.close()''',
'''db=create_sqlite_fixture()
assert set(query_rows(db,'query_people_addresses.sql'))=={('Ann','A','CityA','StateA'),('Ben','B',None,None)}
assert set(query_rows(db,'query_employees_gt_manager.sql'))=={('E2',),('E6',)}
assert query_rows(db,'query_managers.sql')==[('Boss',)]
assert db.execute('SELECT COUNT(*), COUNT(salary) FROM Employee WHERE managerId=1').fetchone()==(5,4)
db.execute('DELETE FROM Employee WHERE id=6'); assert query_rows(db,'query_managers.sql')==[]
db.execute("INSERT INTO Address VALUES (2,1,'CityB','StateB')")
assert len(query_rows(db,'query_people_addresses.sql'))==3
db.close()''',
'左连接为每个左行枚举匹配右行，无匹配时补NULL；一对多连接会复制左行，不能默认输出仍是一人一行。GROUP BY以经理ID区分同名经理，HAVING在分组之后筛选，COUNT(*)恰计下属记录。工资为NULL的大小关系不为TRUE，不会误判为高薪员工。',
'连接代价依索引与查询计划变化；不把SQL短就当作O(1)。无索引嵌套连接可达O(NM)。本地测试使用SQLite、明确主键和重复地址的一对多边界。')

SQL154={
'query_customers_without_orders.sql':'''SELECT c.name AS Customers
FROM Customers AS c
WHERE NOT EXISTS (SELECT 1 FROM Orders AS o WHERE o.customerId = c.id);''',
'query_department_max.sql':'''WITH maximum AS (
    SELECT departmentId, MAX(salary) AS highest
    FROM Employee GROUP BY departmentId
)
SELECT d.name AS Department, e.name AS Employee, e.salary AS Salary
FROM Employee AS e
JOIN maximum AS m ON m.departmentId = e.departmentId AND e.salary = m.highest
JOIN Department AS d ON d.id = e.departmentId;''',
'query_bought_all.sql':'''SELECT DISTINCT c.customer_id
FROM Customer AS c
WHERE NOT EXISTS (
    SELECT 1 FROM Product AS p
    WHERE NOT EXISTS (
        SELECT 1 FROM Customer AS bought
        WHERE bought.customer_id = c.customer_id AND bought.product_key = p.product_key
    )
);'''}
FIX154='''
CREATE TABLE Customers(id INTEGER PRIMARY KEY,name TEXT);
CREATE TABLE Orders(id INTEGER PRIMARY KEY,customerId INTEGER);
INSERT INTO Customers VALUES (1,'A'),(2,'B'),(3,'C');
INSERT INTO Orders VALUES (1,1),(2,NULL),(3,1);
CREATE TABLE Department(id INTEGER PRIMARY KEY,name TEXT);
CREATE TABLE Employee(id INTEGER PRIMARY KEY,name TEXT,salary INTEGER,departmentId INTEGER);
INSERT INTO Department VALUES (1,'R&D'),(2,'Sales');
INSERT INTO Employee VALUES (1,'Ada',100,1),(2,'Ben',100,1),(3,'Cal',90,1),(4,'Dee',80,2);
CREATE TABLE Product(product_key INTEGER PRIMARY KEY);
CREATE TABLE Customer(customer_id INTEGER,product_key INTEGER);
INSERT INTO Product VALUES (1),(2);
INSERT INTO Customer VALUES (1,1),(1,1),(1,2),(2,1),(2,1),(3,2);
'''
add(154,'反连接描述“找不到关联记录”。NOT IN遇到子查询中的NULL会产生UNKNOWN，因此NOT EXISTS更直接表达逐行不存在。部门最高薪要保留全部并列者，不是每组随便取一行。买齐所有产品可用双重NOT EXISTS表达“没有任何缺失产品”，自然处理重复购买。',sql_code(SQL154,FIX154),
'''db=create_sqlite_fixture()
show_table(['反连接方式','实际结果'],[('NOT EXISTS',query_rows(db,'query_customers_without_orders.sql')),('含NULL的NOT IN',db.execute('SELECT name FROM Customers WHERE id NOT IN (SELECT customerId FROM Orders)').fetchall())])
for name in ['query_department_max.sql','query_bought_all.sql']:
    cursor=db.execute(SQL_QUERIES[name]); print(name); show_table([x[0] for x in cursor.description],cursor.fetchall())
db.close()''',
'''db=create_sqlite_fixture()
assert set(query_rows(db,'query_customers_without_orders.sql'))=={('B',),('C',)}
assert set(query_rows(db,'query_department_max.sql'))=={('R&D','Ada',100),('R&D','Ben',100),('Sales','Dee',80)}
assert query_rows(db,'query_bought_all.sql')==[(1,)]
db.execute('DELETE FROM Orders'); assert len(query_rows(db,'query_customers_without_orders.sql'))==3
db.execute('DELETE FROM Product'); assert set(query_rows(db,'query_bought_all.sql'))=={(1,),(2,),(3,)}
db.close()''',
'NOT EXISTS只测试是否存在至少一条匹配，不受无关NULL和重复订单影响。聚合最高薪再按部门与工资双键连接，恰保留该部门所有达到最大值的行。双重否定等价于对每个产品都存在购买记录；产品表为空时条件真，返回购买表中可识别的所有客户ID，不凭空创造客户全集。',
'相关子查询在无索引时可能重复扫描，数据库可优化为连接。教学重点是逻辑语义正确；需要规模优化时为关联键建立索引并查看计划，而不是以CTE语法本身声称更快。')

SQL155={
'query_dense_rank.sql':'''SELECT score, DENSE_RANK() OVER (ORDER BY score DESC) AS rank
FROM Scores ORDER BY score DESC;''',
'query_consecutive_numbers.sql':'''SELECT DISTINCT a.num AS ConsecutiveNums
FROM Logs AS a
JOIN Logs AS b ON b.id = a.id + 1 AND b.num = a.num
JOIN Logs AS c ON c.id = a.id + 2 AND c.num = a.num;''',
'query_department_top3.sql':'''WITH ranked AS (
    SELECT e.*, DENSE_RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC) AS salary_rank
    FROM Employee AS e
)
SELECT d.name AS Department, r.name AS Employee, r.salary AS Salary
FROM ranked AS r JOIN Department AS d ON d.id = r.departmentId
WHERE r.salary_rank <= 3;''',
'query_stadium.sql':'''WITH eligible AS (
    SELECT *, id - ROW_NUMBER() OVER (ORDER BY id) AS run_id
    FROM Stadium WHERE people >= 100
), long_runs AS (
    SELECT run_id FROM eligible GROUP BY run_id HAVING COUNT(*) >= 3
)
SELECT e.id, e.visit_date, e.people
FROM eligible AS e JOIN long_runs AS r ON e.run_id = r.run_id
ORDER BY e.visit_date;'''}
FIX155='''
CREATE TABLE Scores(id INTEGER PRIMARY KEY,score REAL);
INSERT INTO Scores VALUES (1,3.5),(2,3.65),(3,4.0),(4,3.85),(5,4.0),(6,3.65);
CREATE TABLE Logs(id INTEGER PRIMARY KEY,num INTEGER);
INSERT INTO Logs VALUES (1,7),(2,7),(3,7),(5,9),(6,9),(8,9),(10,2),(11,2),(12,2),(13,2);
CREATE TABLE Department(id INTEGER PRIMARY KEY,name TEXT);
CREATE TABLE Employee(id INTEGER PRIMARY KEY,name TEXT,salary INTEGER,departmentId INTEGER);
INSERT INTO Department VALUES (1,'D');
INSERT INTO Employee VALUES (1,'A',100,1),(2,'B',90,1),(3,'C',80,1),(4,'D',80,1),(5,'E',70,1);
CREATE TABLE Stadium(id INTEGER PRIMARY KEY,visit_date TEXT,people INTEGER);
INSERT INTO Stadium VALUES (1,'2021-01-01',100),(2,'2021-01-02',110),(3,'2021-01-03',120),
(5,'2021-01-05',100),(6,'2021-01-06',100),(7,'2021-01-07',100),(8,'2021-01-08',100),
(10,'2021-01-10',200),(11,'2021-01-11',200),(12,'2021-01-12',90),(13,'2021-01-13',200);
'''
add(155,'窗口函数在保留明细行的同时计算组内排序。ROW_NUMBER对每行编号，RANK并列后跳号，DENSE_RANK不跳号；前三种不同工资要用DENSE_RANK。连续段必须先定义连续的是行号、ID还是自然日期，本章Logs和Stadium按连续ID判断，ID缺口不能被忽略。',sql_code(SQL155,FIX155),
'''db=create_sqlite_fixture()
for name in ['query_dense_rank.sql','query_stadium.sql']:
    cursor=db.execute(SQL_QUERIES[name]); print(name); show_table([x[0] for x in cursor.description],cursor.fetchall())
db.close()''',
'''db=create_sqlite_fixture()
assert query_rows(db,'query_dense_rank.sql')==[(4.0,1),(4.0,1),(3.85,2),(3.65,3),(3.65,3),(3.5,4)]
assert set(query_rows(db,'query_consecutive_numbers.sql'))=={(7,),(2,)}
assert {row[1] for row in query_rows(db,'query_department_top3.sql')}=={'A','B','C','D'}
assert [row[0] for row in query_rows(db,'query_stadium.sql')]==[1,2,3,5,6,7,8]
db.execute('DELETE FROM Logs WHERE id=2'); assert set(query_rows(db,'query_consecutive_numbers.sql'))=={(2,)}
db.close()''',
'过滤后的高人流记录按ID排序，相邻ID连续时id与row_number同步加1，差值保持不变；ID断开时差值变化，从而得到连续岛。先筛选再编号使不达标记录打断连续段。工资排名按部门分区，筛rank≤3保留第三高工资的所有并列员工。',
'窗口排序通常O(n log n)，合适索引可能减少排序代价；连续三ID自连接可利用主键索引。返回顺序只在查询明写ORDER BY时保证。SQLite窗口函数真实执行通过后才记录本章成功。')

SQL156={
'query_rising_temperature.sql':'''SELECT today.id
FROM Weather AS today JOIN Weather AS yesterday
ON yesterday.recordDate = DATE(today.recordDate, '-1 day')
WHERE today.temperature > yesterday.temperature;''',
'query_next_day_retention.sql':'''WITH first_login AS (
    SELECT player_id, MIN(event_date) AS first_date FROM Activity GROUP BY player_id
)
SELECT ROUND(COALESCE(1.0 * SUM(EXISTS (
    SELECT 1 FROM Activity AS a
    WHERE a.player_id = f.player_id AND a.event_date = DATE(f.first_date, '+1 day')
)) / COUNT(*), 0.0), 2) AS fraction
FROM first_login AS f;''',
'query_restaurant_growth.sql':'''WITH daily AS (
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
ORDER BY visited_on;'''}
FIX156='''
CREATE TABLE Weather(id INTEGER PRIMARY KEY,recordDate TEXT,temperature INTEGER);
INSERT INTO Weather VALUES (1,'2020-12-31',10),(2,'2021-01-01',11),(3,'2021-01-03',20);
CREATE TABLE Activity(player_id INTEGER,device_id INTEGER,event_date TEXT,games_played INTEGER);
INSERT INTO Activity VALUES (1,1,'2020-12-31',1),(1,1,'2021-01-01',1),(1,2,'2021-01-01',2),
(2,1,'2021-01-01',1),(2,1,'2021-01-03',1),(3,1,'2021-01-02',1);
CREATE TABLE Customer(customer_id INTEGER,name TEXT,visited_on TEXT,amount INTEGER);
INSERT INTO Customer VALUES (1,'A','2021-01-01',10),(2,'B','2021-01-01',20),
(3,'C','2021-01-03',30),(4,'D','2021-01-07',70),(5,'E','2021-01-08',80);
'''
add(156,'日期不是普通相邻行。昨天要求自然日期相差一天，留存分母是独立玩家而不是登录行数。餐厅报表先按日期汇总，再按自然日范围求和：缺失日期不能把七行窗口伪装成七天。本章缺失日期贡献0，只在实际有消费的日期输出已覆盖完整七天的窗口。',sql_code(SQL156,FIX156),
'''db=create_sqlite_fixture()
for name in SQL_QUERIES:
    cursor=db.execute(SQL_QUERIES[name]); print(name); show_table([x[0] for x in cursor.description],cursor.fetchall())
print('实际SQLite版本',sqlite3.sqlite_version)
db.close()''',
'''db=create_sqlite_fixture()
assert query_rows(db,'query_rising_temperature.sql')==[(2,)]
assert query_rows(db,'query_next_day_retention.sql')==[(0.33,)]
assert query_rows(db,'query_restaurant_growth.sql')==[('2021-01-07',130,18.57),('2021-01-08',180,25.71)]
# 重复同日记录不会增加玩家分母或留存次数。
db.execute("INSERT INTO Activity VALUES(1,3,'2021-01-01',99)")
assert query_rows(db,'query_next_day_retention.sql')==[(0.33,)]
db.execute('DELETE FROM Activity'); assert query_rows(db,'query_next_day_retention.sql')==[(0.0,)]
db.execute('DELETE FROM Customer'); assert query_rows(db,'query_restaurant_growth.sql')==[]
db.close()''',
'留存先按玩家求首日，再用EXISTS判断恰好次日是否出现，重复登录不重复计分。餐厅RANGE以JULIANDAY数值排序，6 PRECEDING到CURRENT ROW对应当前日及前六个自然日；与ROWS基于行数不同。分母固定7，空活动集合的0.0是本章明确的教学扩展。',
'先聚合日/玩家通常需分组与排序；窗口排序O(D log D)级，实际查询计划决定具体实现。DATE、JULIANDAY及此窗口写法已在SQLite执行，未宣称MySQL/PostgreSQL方言已测。')
