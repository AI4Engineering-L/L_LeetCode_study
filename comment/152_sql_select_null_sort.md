# N152 · SQL入门、过滤与NULL —— 说人话详解

> 对应 notebook：`notebooks/19_specialized_tracks/152_sql_select_null_sort.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章是 SQL 专线第一站。我们习惯的编程是"拿着变量一格一格改"，SQL 完全是另一种思路：**你描述"我要什么样的行"，数据库替你从表里筛出来**。本章练三件最基本的事：用 `SELECT` 挑列、用 `WHERE` 写过滤条件、以及 SQL 里最容易翻车的一件事——`NULL` 的处理。

对应三道题，每道给一个具体到数字的例子（数据就是 cell3 建的测试表）：

1. **可回收低脂产品**：`Products` 表有 4 行——`(0,'Y','N'), (1,'Y','Y'), (2,'N','Y'), (3,'Y','Y')`（列是 product_id、low_fats、recyclable）。要挑"既是低脂又可回收"的产品 id。输入这 4 行 → 输出 `{1, 3}` → 为什么：只有 1 号和 3 号两列都是 'Y'；0 号可回收列是 'N'，2 号低脂列是 'N'，都被刷掉。
2. **大国**：`World` 表有三行——`('AreaBoundary', 面积 3000000, 人口 1)`、`('PopulationBoundary', 面积 1, 人口 25000000)`、`('Small', 2999999, 24999999)`。条件是"面积 ≥ 3000000 **或** 人口 ≥ 25000000"。输入这 3 行 → 输出 `{AreaBoundary, PopulationBoundary}` → 为什么：前两行各自压着边界值恰好满足一个条件（注意是"大于等于"，3000000 整好达标）；Small 两项都只差 1，双双落选。
3. **找客户推荐人**：`Customer` 表——`(1,'Alice',NULL), (2,'Bob',2), (3,'Cara',1), (4,'Dan',NULL)`。要"推荐人不是 2 号"的客户名。直觉写 `referee_id <> 2` 只会得到 `{Cara}`，正确答案是 `{Alice, Cara, Dan}`——Alice 和 Dan 的 referee_id 是 NULL（没有推荐人），会被 `<> 2` 这个条件神秘漏掉。这就是本章的核心坑，下面慢慢拆。

## 二、关键概念（定义）

- **表的行列语义**：一张表是"行的集合（更准确说多重集合）× 列的契约"。每一行是一条独立记录，行与行之间没有先后依赖；列名和类型是表结构的一部分。SQL 操作的对象是整张表，不是某一行。
- **SELECT（投影）**：从筛出来的行里挑你要的列。`SELECT product_id` 只交付一列。写成 `SELECT *` 会把所有列都带出来——cell4 特意说不用它，因为一旦表结构加了列，`SELECT *` 的输出跟着变，下游断言就"漂移"了；明确点名要哪些列才是稳的契约。
- **WHERE（过滤谓词）**：给每一行算一个条件表达式，**只保留算出来为 TRUE 的行**。注意这句黑体——FALSE 和 UNKNOWN 都出局，这就是 NULL 陷阱的根源。
- **NULL 与三值逻辑**：NULL 表示"这里没有值/未知"，它不是 0 也不是空字符串。任何值和 NULL 做比较（`= <> < >`），结果既不是 TRUE 也不是 FALSE，而是第三种状态 UNKNOWN。所以 `NULL <> 2` 不是 TRUE，是 UNKNOWN，WHERE 一看不是 TRUE，这行就被丢了。判断 NULL 只能用专门的谓词 `IS NULL` / `IS NOT NULL`。
- **AND / OR**：AND 要求两边**同时为 TRUE** 才算 TRUE；OR 要求**至少一边为 TRUE**。任何一边是 UNKNOWN 时，结果可能是 UNKNOWN（比如 `TRUE OR UNKNOWN` 是 TRUE，`UNKNOWN OR FALSE` 是 UNKNOWN）。
- **多重集合（multiset / 袋语义）**：SQL 表默认允许重复行，所以严格说是"多重集合"而不是数学集合。这也是"去重（DISTINCT）与保留重复"成为练习题的原因。
- **DISTINCT / ORDER BY / LIMIT**：DISTINCT 把结果里重复的行捏成一条；ORDER BY 指定输出顺序；LIMIT 截取前若干行。注意 cell1 的提醒：**不带 ORDER BY 时 SQL 不承诺任何顺序**，所以验证答案要按"集合"比，不能按"列表顺序"比。
- **内存 SQLite fixture**：`sqlite3.connect(':memory:')` 在内存里建一个真数据库，跑完即销毁。本章所有 SQL 都在真实的 SQLite 引擎里执行，不是纸面模拟。

## 三、解决思路（一步步推导）

- **Step 1**：把每道题翻译成"对哪张表、保留哪些行、交付哪些列"。三道题全是单表过滤，没有连接、没有分组，所以模板就是 `SELECT 列 FROM 表 WHERE 条件`。
- **Step 2**：条件里的 AND/OR 按题意选：题 1 是"同时满足两个条件"用 AND；题 2 是"满足任一即可"用 OR。边界值（3000000、25000000 这种恰好压线的）要确认题目说的是 `>=` 还是 `>`。
- **Step 3**：遇到可能为 NULL 的列，先问自己"条件对 NULL 行算出什么"。题 3 的 referee_id 有 NULL，`referee_id <> 2` 对这些行算出 UNKNOWN → 被丢 → 漏人。补救办法是把"没有推荐人"显式写成 `referee_id IS NULL`，和原条件用 OR 连起来。
- **Step 4**：验证时按集合比对结果（`set(...)`），因为我们没有写 ORDER BY，数据库返回的行序不受我们控制。

**手算演示（重点：题 3 的 NULL 是怎么漏的）**。对 `Customer` 表四行分别算 `referee_id <> 2`：

| 行 | referee_id | `referee_id <> 2` 的结果 | 只写这个条件会保留吗 |
|---|---|---|---|
| Alice | NULL | UNKNOWN（NULL 和 2 比不出真假） | 不会（WHERE 只留 TRUE） |
| Bob | 2 | FALSE（2 不满足"不等于 2"） | 不会 |
| Cara | 1 | TRUE | 会 |
| Dan | NULL | UNKNOWN | 不会 |

所以只写 `referee_id <> 2` 输出只剩 Cara，Alice、Dan 无声消失。改成 `referee_id IS NULL OR referee_id <> 2` 后再走一遍：Alice 的 `IS NULL` 是 TRUE，OR 出 TRUE，保留；Bob 两个条件都 FALSE，排除；Cara 后半 TRUE，保留；Dan 前半 TRUE，保留。输出 `{Alice, Cara, Dan}`，和 cell8 的断言一致。

**题 2 的边界演示**：AreaBoundary 的面积恰好 3000000，`area >= 3000000` 用的是"大于等于"，所以 TRUE；Small 的面积 2999999 差 1，人口 24999999 也差 1，两个条件都 FALSE，OR 完还是 FALSE，出局。压线行能不能进，完全由 `>=` 还是 `>` 决定，读题要咬文嚼字。

**结果顺序的演示**：三条查询都没写 ORDER BY，SQL 标准不保证输出顺序——今天 SQLite 先返回 Alice 再返回 Dan，明天换个版本或换个执行计划顺序可能倒过来，但**行集不变**。所以验证要按集合比（`set(...)`），要顺序就必须显式写 `ORDER BY 列`；想只要前几名再配 `LIMIT`（比如"面积最大的前 3 个国家"就是 `ORDER BY area DESC LIMIT 3`，此时 ORDER BY 与 LIMIT 缺一不可：LIMIT 单独用会"随便砍 3 行"）。

## 四、代码逐段讲解

cell3 的代码分两部分：SQL 查询文本 + Python 脚手架。

**SQL 查询（存在 `SQL_QUERIES` 字典里，键就是 `.sql` 文件名）**：

```sql
SELECT product_id
FROM Products
WHERE low_fats = 'Y' AND recyclable = 'Y';
```

题 1：从 Products 里保留 low_fats 和 recyclable **同时**为 'Y' 的行，只交付 product_id 一列。AND 意味着任何一列不是 'Y' 就整行出局。

```sql
SELECT name, population, area
FROM World
WHERE area >= 3000000 OR population >= 25000000;
```

题 2：面积、人口**至少一项**过线即保留，交付三列。注意列名按题目要求点名列出，顺序也照题目来。

```sql
SELECT name
FROM Customer
WHERE referee_id IS NULL OR referee_id <> 2;
```

题 3：本章的主角。"推荐人缺失"（`IS NULL`）或"推荐人存在且不是 2"（`<> 2`）都保留。两个条件各管一批 NULL/非 NULL 行，合起来才不漏人。`IS NULL` 是唯一能对 NULL 给出 TRUE/FALSE 的写法，普通比较符对 NULL 只会给 UNKNOWN。

**Python 脚手架**：

```python
import sqlite3

SQL_QUERIES = {
    'query_recyclable_products.sql': r'''SELECT product_id ...''',
    'query_big_countries.sql': r'''SELECT name, ...''',
    'query_customer_referee.sql': r'''SELECT name ...''',
}

def create_sqlite_fixture():
    connection=sqlite3.connect(':memory:')
    connection.executescript(r'''
CREATE TABLE Products(product_id INTEGER PRIMARY KEY,low_fats TEXT,recyclable TEXT);
INSERT INTO Products VALUES (0,'Y','N'),(1,'Y','Y'),(2,'N','Y'),(3,'Y','Y');
CREATE TABLE World(name TEXT PRIMARY KEY,area INTEGER,population INTEGER,gdp INTEGER);
INSERT INTO World VALUES ('AreaBoundary',3000000,1,0),('PopulationBoundary',1,25000000,0),('Small',2999999,24999999,0);
CREATE TABLE Customer(id INTEGER PRIMARY KEY,name TEXT,referee_id INTEGER);
INSERT INTO Customer VALUES (1,'Alice',NULL),(2,'Bob',2),(3,'Cara',1),(4,'Dan',NULL);
''')
    return connection

def query_rows(connection,name):
    return connection.execute(SQL_QUERIES[name]).fetchall()
```

- `SQL_QUERIES` 用字典把三个查询按 `.sql` 文件名存好，模拟"每题一个 sql 文件"的组织方式（cell2 说的接口就是这三个名字）。查询文本用 `r'''...'''` 三引号原始字符串包起来：三引号允许 SQL 跨行书写保持可读，`r` 前缀让反斜杠不被 Python 转义，SQL 里出现特殊字符也不会出岔子。
- 看一遍 fixture 数据就能反查出它想考什么：Products 的 4 行让"AND 两边都得真"每种缺一列的情况各占一行；World 的三行是"两项压线 + 一项双差 1"；Customer 的 4 行把 referee_id 的四种形态（NULL/恰为 2/其他值/NULL）各放一行。测试数据不是随便编的，每一行都是一道小题。
- `create_sqlite_fixture()`：`sqlite3.connect(':memory:')` 建一个纯内存数据库（不落盘，关掉就没了）；`executescript` 一次执行整段建表加插数据的脚本。三张表的数据都是精心设计的：Products 里 0 号只满足 recyclable、2 号只满足 low_fats（专测 AND 必须两个都真）；World 里两行恰好压线、一行双双差 1（专测 `>=` 边界和 OR）；Customer 里两个 NULL、一个 2、一个 1（专测 NULL 语义的四种情况各占一行）。
- `query_rows(connection, name)`：按名字取出 SQL 文本，`execute` 交给 SQLite 真正执行，`fetchall()` 把所有结果行拿回来（每行是一个元组，如 `(1,)`、`('Alice',)`）。
- cell6 用 `cursor.description` 拿到结果列名当表头，把三个查询的输出逐张渲染成表格——你看到的表就是真数据库算出来的，不是手写的答案图。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么题 3 必须加 `IS NULL`？** 因为 WHERE 的规则是铁的：**只有 TRUE 能过桥**，FALSE 和 UNKNOWN 都掉河里。NULL 参与的任何比较（`=`、`<>`、`<`、`>`）结果都是 UNKNOWN，所以"值未知"的行永远过不了普通比较这一关。想要它们就必须另开一条专门通道，`IS NULL` 是 SQL 里唯一对 NULL 说人话的谓词。甚至 `NULL = NULL` 也是 UNKNOWN（两个"未知"未必相等），判断"是不是 NULL"只能用 `IS NULL`——cell8 专门有一条断言验证这件事。

**为什么 AND/OR 那样算？** AND 是"两个都得真"：一个 TRUE 一个 UNKNOWN，你没法确定两边都成立，结果是 UNKNOWN，行照样被丢——所以题 1 里如果某行的 low_fats 是 NULL，这行也进不了结果。OR 是"至少一个真"：一边已经 TRUE 了，另一边即使是 UNKNOWN 也无所谓，结果 TRUE 保留。你可以把 UNKNOWN 理解成"暂定不算数"，任何无法拍板说 TRUE 的组合都过不了 WHERE。

把三值逻辑整理成一张速查表（T=TRUE、F=FALSE、U=UNKNOWN）：

| 表达式 | 另一边是 T | 另一边是 F | 另一边是 U |
|---|---|---|---|
| `x AND y` | T | F | U |
| `x OR y` | T | F（当 x 也是 F 时） | U |

读法：AND 遇到 F 立刻判 F、遇到 U 就悬着；OR 遇到 T 立刻判 T、遇到 U 也悬着。WHERE 只放行最终的 T，悬着的 U 和确定的 F 一样出局。

**为什么不比行的顺序？** 因为这批查询都没写 ORDER BY，SQL 标准本来就不保证无 ORDER BY 时的输出顺序（cell1 明确提醒了这一点）。所以测试用 `set(...)` 把行装进集合再比——集合相等只看"有哪些行"，不看先后。这也是为什么"大国"那条断言写的是 `{row[0] for row in ...}` 而不是列表直接 `==`。

**复杂度是多少？** 这三条查询都是单表过滤，表上没建额外索引时数据库只能把每一行看一遍，代价 O(行数)。比如 World 表有 100 万行，`WHERE area >= ... OR population >= ...` 就要扫 100 万行。真实系统里可以在过滤列上建索引让数据库走别的执行计划，但那是数据库的选择，SQL 文本不变；本章用小表，扫描完全够用。另外声明一下适用范围：这些 SQL 在 SQLite 里跑过，其他数据库（MySQL/PostgreSQL）语法基本兼容，但本轮没有实际验证过。

## 六、测试用例在测什么

cell8 每条断言逐个看（本章的验证方式是：Python `assert` + 在真 SQLite 库上执行查询比对结果）：

- `set(query_rows(db,'query_recyclable_products.sql'))=={(1,),(3,)}`：正常值测试。4 行里只有 1、3 两个产品两列全是 'Y'，专测 AND 两边都得满足；0 和 2 各缺一列被淘汰。
- `{row[0] for row in query_rows(db,'query_big_countries.sql')}=={'AreaBoundary','PopulationBoundary'}`：边界值测试。AreaBoundary 面积恰好 3000000、PopulationBoundary 人口恰好 25000000，都必须入选（验证 `>=` 含等号）；Small 两项各差 1 必须落选。用集合推导比名字，体现"不承诺顺序"。
- `set(query_rows(db,'query_customer_referee.sql'))=={('Alice',),('Cara',),('Dan',)}`：NULL 语义测试。Alice、Dan 的 referee_id 是 NULL，靠 `IS NULL` 分支保留；Bob 是 2 被排除；Cara 是 1 靠 `<> 2` 保留。这条就是全章核心坑的正反面验证。
- `db.execute('SELECT NULL <> 2, NULL = NULL, NULL IS NULL').fetchone()==(None,None,1)`：三值逻辑的显微镜实验，直接让数据库回答三个问题——`NULL <> 2` 得到 NULL（Python 里显示 None），证明"未知值参与比较结果是未知"；`NULL = NULL` 也是 NULL，证明连 NULL 自己都不等于自己；只有 `NULL IS NULL` 得到 1（SQLite 用整数 1 表示真）。一条断言把 NULL 的全部反直觉行为钉死。顺带注意 Python 侧的对应关系：SQL 的 NULL 取回来就是 Python 的 None，这也是为什么前一条断言里 Ben 的地址两格是 None。
- `db.executescript('DELETE FROM Products; DELETE FROM World; DELETE FROM Customer;')` 之后 `all(query_rows(db,name)==[] for name in SQL_QUERIES)`：空表边界。把三张表清空再跑全部查询，结果必须是三个空列表——过滤条件再对，没有数据就交不出行，不能报错也不能吐出幻觉行。

## 七、练习思路提示

- **练习 1（解释 `referee_id<>2` 会漏掉 NULL）**：提示——第三节的四行手算表就是现成的讲稿骨架：逐行算出比较结果是 TRUE/FALSE/UNKNOWN，再套"WHERE 只留 TRUE"的规则，眼看着 Alice、Dan 掉出去。验证方法：临时把查询改成只含 `referee_id <> 2` 在 fixture 上跑一遍，对照 `{Cara}` 与完整版 `{Alice, Cara, Dan}` 的差别。边界再想一层：如果列里还有 0、负数、空字符串这些"看起来也像没有"的值，它们和 NULL 的待遇完全不同（普通比较对它们有效），值得各造一行试试。
- **练习 2（比较去重与保留重复行）**：提示——先给 Products 表手工再加一行 `(1,'Y','Y')`（与 1 号产品完全重复，注意 product_id 是主键所以换个思路给 Customer 加两个同名的人更方便），分别跑 `SELECT name ...` 和 `SELECT DISTINCT name ...`，数一数行数差别。想清楚"SQL 表是多重集合、允许重复行"和"题目要的是名单还是人头"这两件事：要"出现过的名字"用 DISTINCT，要"每一行记录"就不加。边界：整列全重复、全不重复两种极端。

## 八、对应 LeetCode 题目

- **1757. Recyclable and Low Fat Products**：对应题 1 的查询——练最基本的 `SELECT 列 FROM 表 WHERE 条件 AND 条件` 单表过滤。
- **595. Big Countries**：对应题 2——练 OR 条件和 `>=` 边界值的咬文嚼字，以及按题目要求点名交付列。
- **584. Find Customer Referee**：对应题 3——练本章最关键的点：NULL 三值逻辑，普通比较会漏掉 NULL 行，必须补 `IS NULL` 分支。

三道题合起来覆盖了本章知识点的三个层次：题 1 练投影与 AND、题 2 练 OR 与边界、题 3 练 NULL 语义——正好是从"会写条件"到"会写对条件"的进阶路径。
