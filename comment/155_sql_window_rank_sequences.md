# N155 · SQL窗口、排名与连续段 —— 说人话详解

> 对应 notebook：`notebooks/19_specialized_tracks/155_sql_window_rank_sequences.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章解决的是四道经典的 SQL 报表题，它们有一个共同点：你既想看到**每一行明细**，又想给每行挂上一个**跨行算出来的统计值**（比如排名、上一个人的成绩、所属连续段编号）。普通 `GROUP BY` 会把多行折叠成一行，明细没了；不折叠又算不出排名。窗口函数就是为这个矛盾发明的。

给你一个具体到数字的例子。表 `Scores` 里有六个分数：`3.5, 3.65, 4.0, 3.85, 4.0, 3.65`。题目（LeetCode 178）要求按分数从高到低给每个人排名，并列的人名次相同，且**名次不能跳号**：两个 4.0 并列第 1 之后，3.85 应该是第 2（而不是第 3）。所以正确输出是：

```
4.0  → 1
4.0  → 1
3.85 → 2
3.65 → 3
3.65 → 3
3.5  → 4
```

为什么 3.85 是 2？因为"不跳号"的排名数的是**不同分数的个数**，比 3.85 大的不同分数只有 {4.0} 这一个，所以它是第 2 名。这一章还会解决"找出连续出现三次的数字"和"找出人流连续达标的日子"，思路都是"给行编号，再比较编号"。

## 二、关键概念（定义）

- **窗口函数（window function）**：一种"不合并行、给每行算一个跨行统计值"的函数，写法是 `函数名() OVER (怎么分组怎么排序)`。它和 `GROUP BY` 的区别是：`GROUP BY` 十行变一行，窗口函数十行还是十行，只是每行多了一列。
- **ROW_NUMBER**：窗口内从 1 开始的连续编号，1、2、3、4……不管并列，纯粹按顺序排。
- **RANK**：并列同名次，但并列之后**跳号**。两个第 1 名之后，下一个人是第 3 名（1、1、3）。
- **DENSE_RANK**：并列同名次，且**不跳号**。两个第 1 名之后，下一个人是第 2 名（1、1、2）。"第 N 高的工资"这类题必须用它，因为"不同值有几个"才是我们关心的。
- **PARTITION BY**：窗口函数里的"分组"。`PARTITION BY departmentId` 的意思是"在每个部门内部各自排名"，部门和部门之间互不干扰，相当于对每个分区分别开一个窗口。
- **LAG / LEAD**：取"窗口内按顺序排好的上一行 / 下一行"的值。比如 `LAG(score)` 能让你在当前行直接看到上一个人的分数，用来算环比、差分很方便。
- **窗口 frame**：`OVER` 里还能指定统计范围（如 `ROWS BETWEEN 1 PRECEDING AND CURRENT ROW`），决定"每行的窗口到底覆盖哪几行"。本章代码没显式用 frame，但练习 1 会让你体会它。
- **gaps and islands（缺口与岛屿）**：一类经典题型——把序列切成一段一段连续的"岛"，岛与岛之间被"缺口"隔开。本章的 Stadium 题就用 `id - ROW_NUMBER()` 这个差值来标记岛。
- **CTE（WITH 子句）**：`WITH 名字 AS (SELECT ...)` 给子查询起个名字，后面的查询可以像用表一样用它。本章用它把"先排名"和"再筛选"两步拆开写。

## 三、解决思路（一步步推导）

我们按四条查询的难度递进来讲。

**Step 1：用 DENSE_RANK 给分数排名。** 按 `score DESC` 开窗口，`DENSE_RANK()` 数的是"比我大的不同值有几个，加一"。手算一遍：分数从高到低是 4.0、4.0、3.85、3.65、3.65、3.5。第一个 4.0：比我大的不同值 0 个 → 第 1；第二个 4.0 同理 → 第 1；3.85：比我大的不同值只有 4.0 → 第 2；3.65 → 第 3；3.5 → 第 4。这就是第一节里的目标输出。

**Step 2：找连续出现三次的数字（Logs 表）。** 表里有 `(1,7),(2,7),(3,7),(5,9),(6,9),(8,9),(10,2),(11,2),(12,2),(13,2)`。最直白的办法是"自连接三次"：把表 `a`、`b`、`c` 各当成一份拷贝，要求 `b.id = a.id+1 且 b.num = a.num`（下一个还是同一个数），再要求 `c.id = a.id+2 且 c.num = a.num`（下下一个还是同一个数）。手算：`a=id1` 时，id2、id3 都是 7 → 7 入选；`a=id5` 时 id6 是 9 但 id7 不存在 → 9 落选；`a=id10` 时 id11、id12 都是 2 → 2 入选。最后 `DISTINCT` 去重得到 {7, 2}。注意 id=4、7、9 这些缺口是真实数据里没有的行，**缺口必须打断连续**，这正是自连接天然保证的。

**Step 3：每个部门工资前三高的所有人（Employee 表）。** 部门 D 里五个人工资是 100、90、80、80、70。先用 CTE 给每个人打上 `DENSE_RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC)`：A=1、B=2、C=3、D=3、E=4。再外层筛 `salary_rank <= 3`。为什么用 DENSE_RANK 而不是 RANK？因为题目要"前三高的**所有**员工"：两个 80 都是第三高，都得保留；如果用 RANK，它们是 3、4，D 会被 4>3 错误地筛掉。手算结果：A、B、C、D 入选，E 落选。

**Step 4：体育馆连续三天人流 ≥ 100（Stadium 题，gaps and islands）。** 这是最难的一条，核心技巧是 `id - ROW_NUMBER()`。先把不达标的行**筛掉**：数据里 id=12（90 人）被去掉，剩下 id 为 1,2,3,5,6,7,8,10,11,13。然后按 id 升序给这些幸存者编 `ROW_NUMBER()`：1,2,3,4,5,6,7,8,9,10。再算差值 `run_id = id - row_number`：

| id | 1 | 2 | 3 | 5 | 6 | 7 | 8 | 10 | 11 | 13 |
|----|---|---|---|---|---|---|---|----|----|----|
| rn | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8  | 9  | 10 |
| run_id | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 2  | 2  | 3  |

关键规律：**当 id 连续时，id 每加 1，row_number 也恰好多 1，差值不变**；一旦 id 跳了（3→5），row_number 只多 1 而 id 多了 2，差值就变了。于是同一个 `run_id` 的人天然属于同一个"连续岛"。数一数：run_id=0 有 3 行（id 1,2,3）达标；run_id=1 有 4 行（id 5,6,7,8）达标；run_id=2 只有 2 行、run_id=3 只有 1 行，不够 3 天，淘汰。最终答案是 id = 1,2,3,5,6,7,8。**必须先筛 people>=100 再编号**：如果先编号后筛，被筛掉的行就不打断连续了，id 10、11、13 会被错误地连成一个岛。

## 四、代码逐段讲解

cell3 是一段 Python 驱动代码，里面用字典装了四条真实的 SQL，然后用内存 SQLite 建表灌数据来跑这些 SQL。我们逐段看。

**第 1 段：两条"排名/连续"查询。**

```sql
SELECT score, DENSE_RANK() OVER (ORDER BY score DESC) AS rank
FROM Scores ORDER BY score DESC;
```

这条对应 Step 1：`OVER (ORDER BY score DESC)` 说明窗口按分数从高到低排，`DENSE_RANK()` 在这个窗口里算不跳号的名次，起了别名叫 `rank`；外层再 `ORDER BY score DESC` 保证输出顺序（cell4 特意强调：顺序只有在明写 ORDER BY 时才有保证）。

```sql
SELECT DISTINCT a.num AS ConsecutiveNums
FROM Logs AS a
JOIN Logs AS b ON b.id = a.id + 1 AND b.num = a.num
JOIN Logs AS c ON c.id = a.id + 2 AND c.num = a.num;
```

这条对应 Step 2：同一张 `Logs` 被起了三个别名，`JOIN` 条件直接写"下一行 id 加一且数字相同""下下行 id 加二且数字相同"。三重连接后能活下来的 `a.num` 必然连着出现三次，`DISTINCT` 把重复的数字压成一个。

**第 2 段：CTE + 窗口的两条查询。**

```sql
WITH ranked AS (
    SELECT e.*, DENSE_RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC) AS salary_rank
    FROM Employee AS e
)
SELECT d.name AS Department, r.name AS Employee, r.salary AS Salary
FROM ranked AS r JOIN Department AS d ON d.id = r.departmentId
WHERE r.salary_rank <= 3;
```

这条对应 Step 3：CTE `ranked` 先给每个员工打部门内名次（`e.*` 表示把员工表的列全带上，再追加一列 `salary_rank`）；外层再连部门表拿部门名，并筛 `salary_rank <= 3`。为什么拆成两层？因为**大多数数据库不允许在 WHERE 里直接引用窗口函数的结果**，所以必须先在一个 SELECT 里算出名次，再在外层用它过滤。

```sql
WITH eligible AS (
    SELECT *, id - ROW_NUMBER() OVER (ORDER BY id) AS run_id
    FROM Stadium WHERE people >= 100
), long_runs AS (
    SELECT run_id FROM eligible GROUP BY run_id HAVING COUNT(*) >= 3
)
SELECT e.id, e.visit_date, e.people
FROM eligible AS e JOIN long_runs AS r ON e.run_id = r.run_id
ORDER BY e.visit_date;
```

这条对应 Step 4，两个 CTE 串起来：`eligible` 先在 `WHERE people >= 100` 筛过的行上算 `id - ROW_NUMBER()`，得到岛编号 `run_id`；`long_runs` 按岛分组，`HAVING COUNT(*) >= 3` 只留人数够 3 的岛；最后把 `eligible` 和 `long_runs` 按 `run_id` 连回去，取出整段的所有行。

**第 3 段：Python 夹具和执行器。**

```python
def create_sqlite_fixture():
    connection=sqlite3.connect(':memory:')
    connection.executescript(r'''
CREATE TABLE Scores(id INTEGER PRIMARY KEY,score REAL);
INSERT INTO Scores VALUES (1,3.5),(2,3.65),(3,4.0),(4,3.85),(5,4.0),(6,3.65);
CREATE TABLE Logs(id INTEGER PRIMARY KEY,num INTEGER);
INSERT INTO Logs VALUES (1,7),(2,7),(3,7),(5,9),(6,9),(8,9),(10,2),(11,2),(12,2),(13,2);
...
''')
    return connection

def query_rows(connection,name):
    return connection.execute(SQL_QUERIES[name]).fetchall()
```

`create_sqlite_fixture` 在内存数据库（`:memory:`，不落盘、跑完即扔）里建四张表并插入我们手算用的小数据集；`query_rows` 按查询名取出 SQL、执行、把所有行收成 Python 元组列表，方便后面 `assert` 直接比较。这就是本章的"测试"方式：不调用 LeetCode，而是用固定小数据比对整张结果表。

## 五、为什么是对的？复杂度是多少？（说人话）

**Stadium 为什么对？** 我们要证明的只有一句话：同一个岛里的行算出的 `run_id` 一定相同，不同岛的行算出的一定不同。在一个岛内部，id 每往前走一行正好加 1，而 row_number 也是每行加 1，两个同步增长的数相减，差值纹丝不动；一旦遇到缺口，id 一下子跳了不止 1，row_number 却还是老老实实加 1，差值立刻变大，从此进入新的岛。另外"先 `WHERE people >= 100` 再编号"这个顺序也很关键：不达标的行在编号之前就被扔掉了，所以它占据的 id 天然形成一个缺口，能把两段达标的日期隔开。

**Department Top 3 为什么对？** 因为 DENSE_RANK 数的是"部门内比我工资高的**不同**工资有几个"，所以第三高工资不管有几个人并列，名次都是 3，`<= 3` 就能把他们一网打尽，一个不多一个不少。

**复杂度怎么说？** 窗口函数内部要做排序，排序一般是 O(n log n)。拿 Stadium 的 13 行数据举例，log 13 ≈ 3.7，总代价大约就是 13 × 3.7 ≈ 48 次比较这个量级；哪怕体育馆记录涨到 10 万行，也不过是 10 万 × 17 ≈ 170 万次比较，毫秒级就能跑完。如果表上有合适的索引，数据库甚至可以省掉排序这一步。Logs 那条三重自连接走的是主键索引查找，每行常数代价，整体 O(n)。最后再强调一次 cell4 的提醒：SQL 返回顺序不是白给的，只有查询里明写了 `ORDER BY`，顺序才有保证。

## 六、测试用例在测什么

cell8 的验证方式是：重建内存数据库，把四条查询各跑一遍，拿 `assert` 逐条比对完整结果。

1. `assert query_rows(db,'query_dense_rank.sql')==[(4.0,1),(4.0,1),(3.85,2),(3.65,3),(3.65,3),(3.5,4)]` —— 这条测的是**正常值 + 并列值**：两个 4.0 必须都排第 1，3.85 必须是第 2（不跳号），3.5 排第 4（三个不同值之后紧跟第四个）。列表是全序比较，连行顺序一起查。
2. `assert set(query_rows(db,'query_consecutive_numbers.sql'))=={(7,), (2,)}` —— 这条测**正常段与被缺口打断的段**：7（id 1-3 连续三次）和 2（id 10-13）入选，而 9 因为 id 断成 5、6、8 两截而落选。用 `set` 比较是因为 `DISTINCT` 后两行的相对顺序我们不想依赖。
3. `assert {row[1] for row in query_rows(db,'query_department_top3.sql')}=={'A','B','C','D'}` —— 这条专门盯**并列第三**这个坑：C 和 D 都是 80 分，必须同时入选；E（70，第 4 名）必须在门外。只取 `row[1]`（员工名）比较，说明我们关心的是"谁入选"而不是输出顺序。
4. `assert [row[0] for row in query_rows(db,'query_stadium.sql')]==[1,2,3,5,6,7,8]` —— 这条测 gaps and islands 的完整答案：run_id=2（10、11 只有两天）和 run_id=3（13 只有一天）被淘汰，而且查询写了 `ORDER BY e.visit_date`，所以这里敢用有序列表精确匹配。
5. `db.execute('DELETE FROM Logs WHERE id=2'); assert set(query_rows(db,'query_consecutive_numbers.sql'))=={(2,)}` —— 这是一条**突变测试**：删掉 id=2 之后，7 的三连（1、2、3）被拆成 1 和 3 两截，7 必须从答案里消失，只剩 2。它验证的是"缺口打断连续"这个语义，而不是查询恰好背下了答案。

## 七、练习思路提示

- **练习 1（ROWS 与 RANGE 在重复排序键下的差别）**：提示——先用 `ROW_NUMBER()` 和一个带重复值的排序列（比如本章 Scores 里两个 4.0）造输入，然后分别写 `OVER (ORDER BY score ROWS BETWEEN ...)` 和 `RANGE BETWEEN ...` 的窗口求和。手算时问自己一句：RANGE 会把"排序值相同的所有行"当成一个整体拉进窗口，ROWS 只数物理行数，两个 4.0 在两种 frame 下的求和结果差在哪？把预期值写死，再用本章的 sqlite 夹具跑出来对。
- **练习 2（连续 ID 与连续日期分别建模）**：提示——Logs 的"连续"是 `id+1`，但很多业务表里真正的连续是"自然日连续"（今天、明天、后天），id 可能乱序也可能跳。想一想：日期也有个"该有的序号"（比如把日期换算成天数），套用 `日期序号 - ROW_NUMBER()` 的岛技巧时，哪一步需要换成 `date(id, '+1 day')` 或者 julianday 差？先手算一个"日期连续但 id 断裂"的 4 行小例子，预测两种模型给出不同答案，再分别跑。

## 八、对应 LeetCode 题目

- **178. Rank Scores**：练的就是 DENSE_RANK 本身——并列不跳号，输出每个分数的名次，本章第一节和 `query_dense_rank.sql` 一比一对应。
- **180. Consecutive Numbers**：练"连续出现"的判定，对应自连接写法 `query_consecutive_numbers.sql`，也可以拿它验证你写的 LAG 版本。
- **185. Department Top Three Salaries**：练 PARTITION BY 分区 + 筛 `rank <= 3` 保留并列，对应 `query_department_top3.sql`，专治"并列第三被 RANK 误杀"。
- **601. Human Traffic of Stadium**：练 gaps and islands 套路 `id - ROW_NUMBER()`，对应 `query_stadium.sql`，也是"先过滤再编号"顺序敏感性的最佳示范。
