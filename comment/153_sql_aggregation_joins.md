# N153 · SQL聚合、连接与计数语义 —— 说人话详解

> 对应 notebook：`notebooks/19_specialized_tracks/153_sql_aggregation_joins.ipynb`

## 一、这章要解决什么问题？（问题描述）

上一章我们只对一张表做过滤；这一章要把多张表（甚至一张表跟它自己）拼在一起，再数数、求和、分组。连接和聚合各有一个经典大坑，本章的目标就是绕开它们：

1. **组合两张信息表**：`Person` 存着人（firstName、lastName），`Address` 存着地址（city、state），一个人可能没登记地址。要输出"每个人的姓名 + 他的城市州名"，没地址的人也得出现在结果里（城市州那两格留空）。
2. **员工和经理比工资**：员工表里有一列 `managerId` 指向另一个员工的 `id`。要找出"工资比自己经理高"的员工名字。
3. **数下属**：找出"直接下属至少 5 个"的经理名字。

用 cell3 的真实数据给个具体例子：Employee 表 7 行里，`Boss`（工资 100）有 5 个直接下属——E2(120)、E3(80)、E4(工资是 NULL)、E5(90)、E6(110)。问"谁的工资比经理高"→ 输出 `{E2, E6}` → 为什么：E2 的 120 > Boss 的 100，E6 的 110 > 100，入选；E3、E5 工资更低落选；E4 的工资是 NULL，`NULL > 100` 算不出真假（UNKNOWN），过不了 WHERE，**不能**算入选。问"谁有至少 5 个下属"→ 输出 `{Boss}` → 为什么：数的是**行数**（COUNT(*) = 5），E4 虽然工资是 NULL 但他这个"人/行"是真实存在的下属；要是用 COUNT(salary) 数非空工资，只会数出 4，Boss 就被冤枉地刷掉了——这就是本章标题里"计数语义"四个字的分量。

## 二、关键概念（定义）

- **JOIN（连接）**：按一个匹配条件把两张表的行配成对，拼成更宽的行。`ON a.personId = p.personId` 就是配对规则。要紧的是：**连接会改变行数**——一对多匹配时左表的一行会被复制成多行。
- **INNER JOIN（内连接，写 `JOIN` 就是它）**：只保留两表都配上的行。配不上的（比如 `managerId` 为 NULL 的员工、没有下属的经理）直接消失。
- **LEFT JOIN（左连接）**：左表的行**全保留**；右表配不上的，右表的列用 NULL 补齐。它专治"没有地址的人也不能丢"这类需求。
- **一对多与行数放大**：一个人有两个地址时，LEFT JOIN 会让这个人出现两行（每个地址一行）。连接结果不保证"还是一人一行"，做 SUM/COUNT 前必须先想清楚行数被放大了没有。
- **别名（AS p / AS a）**：给表起短名。自连接时同一张表要扮演两个角色，必须用两个不同别名（`e` 员工视角、`m` 经理视角）才能区分"e 的工资"和"m 的工资"。
- **自连接（SELF JOIN）**：一张表和自己连接，靠别名分裂出两个视角，常用于"上下级""同班同学"这类表内关系。
- **GROUP BY（分组）**：按指定列的值把行归堆，之后每一堆产出一条结果。`GROUP BY m.id, m.name` 就是"每个经理一堆"。把 id 和 name 一起分组还能区分"两个同名经理"——只按 name 分会把两个人错误合并成一堆。
- **HAVING（分组后过滤）**：对**分好组、算完聚合**的结果再筛。WHERE 在分组**前**逐行筛，HAVING 在分组**后**按聚合值筛——"下属数 ≥ 5"这种条件必须写 HAVING，因为数数之前单行上根本没有"下属数"可言。
- **COUNT(*) 与 COUNT(col) 的区别**：COUNT(*) 数**行**，一行算一个，NULL 也算人头；COUNT(col) 只数**该列非 NULL** 的行。选错口径，E4 这种"工资未知但人存在"的下属就会被漏数。
- **NULL 比较不出真假**：延续上一章的三值逻辑——`NULL > 100` 是 UNKNOWN，WHERE 只留 TRUE，所以 NULL 工资的员工自动不算"高过经理"，也不会报错，就是安静落选。

## 三、解决思路（一步步推导）

- **Step 1（组合两表）**：题目要求"无论有没有地址都要列出人"——这决定了用 LEFT JOIN 而不是 INNER JOIN（内连接会把没地址的 Ben 直接吞掉）。左表放 Person（人全保留），右表放 Address，配不上补 NULL。
- **Step 2（右表条件放哪）**：如果题目还要求"只要 StateA 州的地址"，条件不能随手写进 WHERE——Ben 那行 state 是 NULL，`state='StateA'` 对它是 UNKNOWN，WHERE 一筛这行又被排掉了，LEFT JOIN 白做。正确写法是把右表条件并进 `ON` 子句（或者对 NULL 再 OR 一次）。本章查询没这个条件，但 cell1 特意警告了这件事。
- **Step 3（员工比经理）**：把 Employee 当两张表用——`e` 是员工视角，`m` 是经理视角，配对条件 `e.managerId = m.id` 把每个员工和他的经理拼成一行，然后 `e.salary > m.salary` 逐行判断。内连接自动把 NoManager（没有 managerId，配不上任何经理）排除。
- **Step 4（数下属）**：还是同一个自连接，这次以经理为中心归堆：`GROUP BY m.id, m.name` 后每堆就是"该经理的全部直接下属行"，`HAVING COUNT(*) >= 5` 只留下堆里行数达标的经理。数行用 COUNT(*)，因为下属行哪怕工资是 NULL，人也是真的。

**手算演示 1（左连接，cell6 的表）**。Person 有 Ann(personId=1)、Ben(personId=2)；Address 只有一行 `(1,'CityA','StateA')`。

| firstName | lastName | city | state | 怎么来的 |
|---|---|---|---|---|
| Ann | A | CityA | StateA | personId=1 配上了地址 |
| Ben | B | NULL | None | personId=2 没地址，右列补 NULL，**人还在** |

如果是 INNER JOIN，第二行就没了——这就是选 LEFT JOIN 的全部理由。

**手算演示 2（自连接比工资）**。配对后每行长这样，逐行判断 `e.salary > m.salary`：

| 员工 | 工资 | 经理 | 经理工资 | 结果 |
|---|---|---|---|---|
| E2 | 120 | Boss | 100 | TRUE，入选 |
| E3 | 80 | Boss | 100 | FALSE |
| E4 | NULL | Boss | 100 | UNKNOWN，落选（不报错，也不算数） |
| E5 | 90 | Boss | 100 | FALSE |
| E6 | 110 | Boss | 100 | TRUE，入选 |
| NoManager | 200 | 配不上 | — | 内连接直接不产生这行 |
| Boss | 100 | 没有经理 | — | 同上 |

最终输出 `{E2, E6}`，和 cell8 的断言一致。

**手算演示 3（分组数数）**。自连接后的 5 行（E2–E6）按经理归堆：Boss 一堆正好 5 行（E4 那行工资是 NULL 但行在），`COUNT(*)=5` 达标，Boss 入选。cell6 还专门跑了一个对比实验：全表 `COUNT(*)=7` 行，`COUNT(salary)=6` 个——E4 的 NULL 工资让两个口径差了 1，放在经理题里就是"5 个下属"和"4 个下属"的天壤之别。

## 四、代码逐段讲解

cell3 的三个查询 + 建库脚本。

**查询 1：组合两表（175）**

```sql
SELECT p.firstName, p.lastName, a.city, a.state
FROM Person AS p LEFT JOIN Address AS a ON a.personId = p.personId;
```

`AS p`/`AS a` 给两表起短名，后面所有列引用都带前缀（`p.firstName` 是人的名，`a.city` 是地址的城），两张表有同名列 `personId`，不带前缀就分不清。`LEFT JOIN ... ON ...` 保证左表（Person）行行都在；交付四列且逐列点名，不用 `SELECT *`。

**查询 2：员工比经理工资高（181）**

```sql
SELECT e.name AS Employee
FROM Employee AS e JOIN Employee AS m ON e.managerId = m.id
WHERE e.salary > m.salary;
```

同一张 `Employee` 表在 FROM 里出现两次，靠别名 `e`（员工视角）和 `m`（经理视角）拆成两个角色。`ON e.managerId = m.id` 把"员工那行的经理编号"对到"经理那行的员工编号"上，一行员工 + 一行经理拼成一行宽记录。`JOIN`（内连接）让没有经理的行（Boss、NoManager，managerId 为 NULL）自然消失。`WHERE e.salary > m.salary` 里两个前缀各指各的工资，绝不能混。`AS Employee` 把输出列名改成题目要求的 `Employee`。

**查询 3：至少 5 个直接下属的经理（570）**

```sql
SELECT m.name
FROM Employee AS e JOIN Employee AS m ON e.managerId = m.id
GROUP BY m.id, m.name
HAVING COUNT(*) >= 5;
```

前两行与查询 2 完全一样：还是员工配经理的宽行。区别从 `GROUP BY` 开始：按 `m.id, m.name` 把宽行按经理归堆，每堆 = 该经理的直接下属全集。`HAVING COUNT(*) >= 5` 数每堆的**行数**（就是下属人头数），只留 ≥5 的堆，输出经理名。按 `m.id` 分组而不只按 `m.name`，是为了两个同名经理不被并成一堆（id 是主键，唯一的）。

**Python 脚手架（fixture 数据是精心埋的雷）**：

```python
INSERT INTO Person VALUES (1,'Ann','A'),(2,'Ben','B');
INSERT INTO Address VALUES (1,1,'CityA','StateA');
INSERT INTO Employee VALUES (1,'Boss',100,NULL),(2,'E2',120,1),(3,'E3',80,1),(4,'E4',NULL,1),(5,'E5',90,1),(6,'E6',110,1),(7,'NoManager',200,NULL);
```

Employee Employee 这 7 行每个都有任务：Boss 当经理；E2/E6 工资高过经理（正例）；E3/E5 工资低（反例）；**E4 工资 NULL**（专测 COUNT 口径和 NULL 比较落选）；**NoManager 有 managerId=NULL**（专测内连接把它排除、他不属于任何经理的堆）；下属恰好 5 个（压着 `>= 5` 的边界）。`query_rows` 与上一章相同：按名字取 SQL 文本，在真 SQLite 上执行后 `fetchall()`。

三个查询的结构要素对个账，复习时可以按行扫一遍：

| 查询 | 连接类型 | 关键子句 | 专治的坑 |
|---|---|---|---|
| 组合两表 | LEFT JOIN | `ON` 配对 | 没地址的人被吞 |
| 比经理工资 | INNER JOIN（自连接） | 别名 e/m 分身 | NULL 工资误判 |
| 数下属 | INNER JOIN + GROUP BY | `HAVING COUNT(*)` | COUNT 口径选错、同名经理并堆 |

## 五、为什么是对的？复杂度是多少？（说人话）

**左连接为什么能保住所有人？** 它的规则是"左表每行必须出现至少一次"：右表有匹配就拼上匹配（一个匹配一行，多个匹配多行），一个都没有就拼一行全 NULL 的。所以 Ben 没地址不是消失，而是带着 NULL 地址出场。但要注意反面：一旦右表匹配多个，左行被复制，"一人一行"的直觉就破产了——给 Ann 再插第二条地址后，结果就从 2 行变 3 行（Ann 出现两次），cell8 最后一条断言验证的就是这个放大效应。

**自连接为什么不会自己配自己搞乱？** 因为配对条件写的是跨视角的 `e.managerId = m.id`：只有"员工的经理编号恰好等于某行的员工编号"时才配对。Boss 的 managerId 是 NULL，配不上任何 id，既不会给自己当经理，也不会进任何堆。

**NULL 工资为什么不会误判？** `e.salary > m.salary` 遇到 E4 的 NULL 时结果是 UNKNOWN，WHERE 的老规矩是"只留 TRUE"，UNKNOWN 落选——他既不算高过经理（不合理），也不算低过经理，就是"无法判断"地出局。同理 COUNT(*) 与 COUNT(salary) 在 E4 身上分道扬镳：人数他（行在），工资数不数他（列是 NULL）。"经理是否有 5 个下属"问的是人头，所以必须 COUNT(*)。

**为什么 NoManager 和 Boss 不会混进经理的统计？** 自连接的配对条件是 `e.managerId = m.id`：NoManager 的 managerId 是 NULL，配不上任何 id，内连接根本不产生他的宽行；Boss 的 managerId 也是 NULL，同理他不会作为"员工"出现，只作为"经理 m"接收别人的配对。于是 GROUP BY 归堆时，堆里只有"有经理的员工"行，NoManager 不属于任何堆、Boss 的堆恰好装着他的 5 个下属。配对规则本身就把不相关的人挡在了门外，不需要额外条件。

再补一个易错点：`NoManager` 工资 200 是全表最高，但"比经理工资高"的查询根本轮不到他——内连接先把他请出场，比较条件压根没机会执行。"连接筛行"发生在"WHERE 筛行"之前，这个先后次序决定了哪些行连被比较的资格都没有。

**HAVING 为什么不能用 WHERE 替代？** SQL 虽然是先写 SELECT 再写 WHERE，但实际执行顺序是另一套：`FROM`/`JOIN` 先拼出宽行 → `WHERE` 逐行筛 → `GROUP BY` 归堆 → 聚合函数（COUNT/MAX/…）对每堆算数 → `HAVING` 按算出来的数筛堆 → `SELECT` 挑列交付。到 WHERE 那一步时"每个经理有几个下属"这个数还不存在（那要归堆之后才算得出），所以聚合条件只能进 HAVING。写 SQL 时按这个执行顺序在脑子里过一遍，很多"条件该放哪"的犹豫就消失了。

**连接放大到底长什么样？** cell8 最后一条断言的场景值得展开手算一遍：给 Ann 追加第二条地址 `(2,1,'CityB','StateB')` 后，LEFT JOIN 对 Ann（personId=1）找到**两条**匹配，于是 Ann 被复制成两行——`(Ann, A, CityA, StateA)` 和 `(Ann, A, CityB, StateB)`；Ben 依旧一行 NULL 补位。结果从 2 行涨到 3 行。此时如果对连接结果做 SUM/COUNT，Ann 的任何个人信息都会被算两次——这正是练习 1 要构造的坑，也是"连接前先问基数"这条工程直觉的来源。

**复杂度是多少？** cell4 说得直白：连接的代价取决于有没有索引、数据库选什么查询计划，**SQL 写得短不等于跑得快**。最坏情况（两表都没索引、数据库用嵌套循环逐对尝试）是 O(N×M)：左表 100 万行配右表 100 万行就是万亿次比较。有索引时数据库可以走"每行只查索引命中项"的计划，代价大幅下降。分组本身还要把行按键归堆，量级和参与分组的行数成正比。写 SQL 时心里要有这杆秤：先想行数会被放大到多少，再想有没有索引可走。

## 六、测试用例在测什么

cell8 的断言逐条拆（验证方式仍是 Python assert + 真 SQLite 执行结果比对）：

- `set(...) == {('Ann','A','CityA','StateA'),('Ben','B',None,None)}`：**左连接语义**。Ben 没有 address 但必须以 NULL 补位行出现——这条专抓"手滑写成 INNER JOIN 把 Ben 弄丢"的错误。用 set 比对，因为没写 ORDER BY 不承诺顺序（None 就是 SQL 的 NULL 在 Python 侧的样子）。
- `set(...) == {('E2',),('E6',)}`：**自连接 + NULL 比较语义**。正常正例 E2/E6 要中；隐含的陷阱行 E4（NULL 工资，不许入选）和 NoManager（无经理，内连接必须排除）都被这个结果覆盖到了。
- `query_rows(db,'query_managers.sql') == [('Boss',)]`：**分组计数语义**。Boss 恰好 5 个下属压线达标（`>= 5` 的边界）。结果只有一个经理，直接按列表比也没有顺序问题。
- `db.execute('SELECT COUNT(*), COUNT(salary) FROM Employee WHERE managerId=1').fetchone()==(5,4)`：**两个 COUNT 口径的直接对照实验**。Boss 名下 5 行下属（COUNT(*)=5），但只有 4 个填了工资（COUNT(salary)=4，E4 的 NULL 被忽略）。这条断言把"数人头还是数非空值"的差别钉在数字上——查询 3 若误用 COUNT(salary)，Boss 的堆只有 4，会被 `>=5` 错杀。
- `DELETE FROM Employee WHERE id=6` 后 `query_rows(...) == []`：**边界变动测试**。删掉 E6，Boss 的下属从 5 变 4，跌破门槛，查询必须立刻什么都查不出来。防止实现里把"恰好 5"错写成"> 5"或"永远返回 Boss"。
- `INSERT INTO Address VALUES (2,1,'CityB','StateB')` 后 `len(...) == 3`：**一对多放大测试**。给 Ann（personId=1）加第二条地址，左连接结果从 2 行涨到 3 行——Ann 出现两次。这条专治"以为连接还是一人一行"的错觉，也预告了练习 1 里 SUM 被放大的坑。

## 七、练习思路提示

- **练习 1（构造一对多连接使 SUM 重复）**：提示——复用 cell8 最后那条断言的场景再往前走一步：Person 里给 Ann 存一个"账户余额"之类的数值列，让她连上 2 条地址后对余额求 SUM，观察 SUM 变成两倍（100 的余额连出 3000000 行内是 200）。手算示例：余额 100 × 匹配 2 条地址 = SUM 200。修复方向：先在子查询/分组里把右表归并成"一人一条"再连接（下一章的 GROUP BY 子查询正好用得上）。边界：右表零匹配（SUM 该算原值一次）和右表全部重复。
- **练习 2（区分 WHERE 和 HAVING）**：提示——拿查询 3 做实验田：把 `HAVING COUNT(*) >= 5` 挪到 WHERE 里数据库会直接报错（WHERE 阶段还没有聚合值），这本身就是一个值得展示的现象。再对比"先 WHERE e.salary > 0 再分组"和"先分组再 HAVING"两种写法在 E4（NULL 工资）身上的差别：WHERE 先把 E4 那行筛掉，Boss 的 COUNT(*) 就从 5 变 4——同一条筛选写在两个阶段，结果可以完全不同。手算示例就用这个 5→4 的变化。边界：筛选条件里只涉及原始列（两个阶段可互换但语义要对齐）与涉及聚合值（只能 HAVING）两类。

## 八、对应 LeetCode 题目

- **175. Combine Two Tables**：对应查询 1——练 LEFT JOIN 保左行、NULL 补位，以及"必须保留无匹配行"这个需求信号怎么读出来。
- **181. Employees Earning More Than Their Managers**：对应查询 2——练自连接的别名分身术，顺带体会 NULL 工资/无经理行在内连接与比较中的安静落选。
- **570. Managers with at Least 5 Direct Reports**：对应查询 3——练 GROUP BY + HAVING 的分组后筛选，以及 COUNT(*)（数人头）与 COUNT(col)（数非空值）的口径选择。
