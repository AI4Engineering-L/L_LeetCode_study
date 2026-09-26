# N158 · Pandas连接、聚合与宽长变换 —— 说人话详解

> 对应 notebook：`notebooks/19_specialized_tracks/158_pandas_aggregation_merge_reshape.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章解决"表的形状变换和表的连接"四件事：把两张同结构的表上下摞成一张（拼接）；把"行式"记录转成"交叉表"（透视 pivot）；把宽表转回长表（melt）；找出从没下过单的客户（反连接）。共同的主题是：**每次变换前先问清楚——连接键是什么？键唯一吗？输出会变成几行几列？**

给你两个具体到数字的例子。第一个是宽转长（cell6 真实数据）：

```
宽表（2 行 5 列）：                长表（8 行 3 列）：
product  q1  q2  q3  q4          product  quarter     sales
A        1   2   3   4    →      A        quarter_1  1
B        5   6   7   8          B        quarter_1  5
                                  A        quarter_2  2
                                  ...（共 4×2 = 8 行）
```

为什么是 8 行？因为宽表里每个 `(product, quarter)` 组合各占一个格子，2 个产品 × 4 个季度 = 8 个格子，melt 就是把每个格子立成一行。第二个是反连接（LeetCode 183）：客户 `id=[1,2,3]` 名字 `a,b,c`，订单表 customerId 是 `[1, 1, None]`。没下过单的是谁？客户 1 下过（两次，但"下过"只算一次），None 订单不指向任何客户，所以答案是 `b, c`——而且结果里 b、c 各出现一次，不因为客户 1 下两单就被复制。

## 二、关键概念（定义）

- **concat（纵向拼接）**：把两张表首尾相接摞成一张长表。它**不做任何匹配**，只是摞，所以要求两张表列结构一致（本章契约连列的**顺序**都要求一致）。
- **merge（连接）**：按某列的键把两张表左右拼起来，等价于 SQL 的 JOIN。危险在于行数会变：一对多时左表一行会被右表多行"复制"，多对多甚至会膨胀成笛卡尔积，所以 cell1 第一句就是"连接不一定保持行数"。
- **groupby / agg / transform**：分组三兄弟。`groupby('city')` 把同城市的行归为一组；`agg` 把每组折叠成一个统计值（如 sum，输出行数 = 组数）；`transform` 也算组内统计但**结果对齐回每一行**（输出行数 = 原行数）。本章代码没直接用它们，但它们是"聚合折叠"和"窗口保留"这对概念的 pandas 版本。
- **pivot（透视）**：把长表的三列（行键、列键、值）展开成交叉表：行键做索引、列键做列名、值填格子。它是纯搬格子，**不做任何聚合**——同一个 `(行键, 列键)` 出现两次（格子该填哪个值说不清）它就报错。
- **pivot_table**：pivot 的"会聚合"版本，格子冲突时会按你指定的函数（默认平均）把多个值压成一个。本章的教学立场是：数据契约没说可以平均时，**重复就是错误**，所以选了 pivot 并手工把关。
- **melt（宽转长）**：pivot 的反向操作。`id_vars` 指定"保持不动的列"，`value_vars` 指定"要被立成行的列"，原来的列名落进 `var_name` 列、格子值落进 `value_name` 列。
- **反连接（anti-join）**：SQL 里 `NOT EXISTS` 的 pandas 等价写法——"留下在另一张表里**找不到匹配**的行"。用 `isin`（成员判断）加取反 `~` 实现。
- **多对多（many-to-many）**：两表的连接键在两边都有重复，连接结果行数等于匹配对的乘积，是最容易把表撑爆的场景，所以先检查键的唯一性再决定怎么连。判断口诀可以记成三句话：

- 左键唯一、右键重复 → 一对多，左行会被复制（行数变多）。
- 两边都重复 → 多对多，行数相乘式膨胀，十有八九是口径错了。
- 只想问"匹配上没有" → 别用 merge，用 `isin` 做集合判断，行数不变。

## 三、解决思路（一步步推导）

**Step 1：拼接前先验契约。** 拿 `a`（列 x,y）和 `b`（列 y,x，顺序反了）来说：先比较 `list(df1.columns) != list(df2.columns)`，列名或顺序不一致直接抛 ValueError，一致才 `pd.concat([...], ignore_index=True)` 摞起来并把行号重排成 0..n-1。为什么要管顺序？因为 concat 是按**位置**对齐列的，x 对到 y 上数据就串列了。

**Step 2：pivot 前先查键唯一。** 拿 weather（city、month、temperature 三列）来说：先 `duplicated(['city','month']).any()` 检查"同一城市同一月份是否出现两次"，出现就报错；然后 `pivot(index='month', columns='city', values='temperature')` 生成"月份 × 城市"的温度交叉表，再 `sort_index()` 和 `sort_index(axis=1)` 把行列都排好序。手算一遍 cell6 的数据（Seoul/Paris × Jan/Feb，温度 0,5,2,7）：

| month \ city | Paris | Seoul |
|---|---|---|
| Feb | 7 | 2 |
| Jan | 5 | 0 |

注意 Feb 排在 Jan 前面——`sort_index()` 按字符串排，'Feb' < 'Jan'，这正是"输出顺序也要讲清楚"的一个小陷阱。

**Step 3：melt 把每格立成一行。** `id_vars=['product']` 表示产品列不动；`value_vars=四个季度列` 表示这四列全部"熔化"；`var_name='quarter'` 接住原列名，`value_name='sales'` 接住格子值。手算产品 A：它在四列里的值是 1,2,3,4，所以贡献 4 行 `(A, quarter_1..4, 1..4)`；产品 B 同理贡献 4 行；共 8 行，行数恰好 = 4 × 原行数。cell6 专门打了一张"形状对照表"记录这次变换：

| 表示 | 行数 | 列 |
|------|------|-----|
| wide（宽表） | 2 | product, quarter_1, quarter_2, quarter_3, quarter_4 |
| long（长表） | 8 | product, quarter, sales |

2 行变 8 行、5 列变 3 列，行列一增一减，但信息一个没丢——宽表的每个格子都能用长表的 `(product, quarter)` 定位回去。反过来，如果原表是每个 `(product, quarter)` 唯一的，melt 之后还能唯一还原——这就是 cell4 说的"可以逆变换"。

**Step 4：反连接找未下单客户。** 先从订单表取 `customerId` 并 `dropna()`——None 不指向任何客户，相当于 SQL 里 NULL 不参与相等匹配；再对客户表逐行判断 `~customers['id'].isin(ordered_ids)`（我的 id 不在"下过单的 id 集合"里），命中就取 name 列、改名叫 Customers、重排索引。手算：ordered_ids = {1,1}→{1}；客户 1 在集合里 → 排除；客户 2、3 不在 → 留下，答案 `b, c`。两个不变量都成立：客户 1 的**两笔**订单不会把任何人复制两份（isin 只管"在不在"）；None 订单不会误伤（dropna 掉了）。

## 四、代码逐段讲解

cell3 一共四个函数，逐个看。

```python
def concatenate_tables(df1, df2):
    if list(df1.columns) != list(df2.columns):
        raise ValueError('Both tables must have the same ordered schema')
    return pd.concat([df1, df2], ignore_index=True)
```

第一行就是本章的"形状契约"检查：列名列表（含顺序）必须完全相等，否则抛错——宁可失败也不悄悄按位置错位对齐。`pd.concat` 纵向摞表；`ignore_index=True` 丢弃两张表各自的旧行号，重新从 0 编号，避免出现 [0,1,0] 这种重复索引。

```python
def pivot_weather(weather):
    """One measurement per (city, month); duplicates are errors, not averages."""
    if weather.duplicated(['city', 'month']).any():
        raise ValueError('Duplicate (city, month) measurement')
    return weather.pivot(index='month', columns='city', values='temperature').sort_index().sort_index(axis=1)
```

`duplicated(['city','month'])` 标出 (city, month) 重复的行，`.any()` 问"有没有至少一个"；有就抛错——docstring 明说"重复是错误，不是平均值"。`pivot` 三个参数分别是行键、列键、要填的值；两个 `sort_index` 分别按索引（月份）和按列（城市，`axis=1`）排序，让输出确定、可比较。

```python
def melt_sales(report):
    quarters = ['quarter_1','quarter_2','quarter_3','quarter_4']
    return report.melt(id_vars=['product'], value_vars=quarters,
                       var_name='quarter', value_name='sales').reset_index(drop=True)
```

把四个季度列名写死在 `value_vars` 里，明确"只有这四列被熔化"；`id_vars=['product']` 保持产品列；熔化后行序可能乱（pandas 默认按"原列"分组输出），`reset_index(drop=True)` 把索引压平成 0..7，让输出和手算表一一对应。

```python
def customers_without_orders(customers, orders):
    # NULL customerId does not match a real customer, just as with SQL NOT EXISTS.
    ordered_ids = orders['customerId'].dropna()
    return customers.loc[~customers['id'].isin(ordered_ids), ['name']].rename(
        columns={'name':'Customers'}).reset_index(drop=True)
```

三步走：`dropna()` 先把 NULL 订单扔掉（注释点明这和 SQL NOT EXISTS 的 NULL 语义一致）；`~isin` 是"成员关系取反"，即反连接的核；`loc[行筛子, ['name']]` 一步完成"筛行 + 取列"——注意 `loc` 的第一个位置放布尔序列是"按条件选行"、第二个位置放列表是"按标签选列"，一次方括号同时干两件事。最后 `rename` 把列名改成题目要的 Customers。注意整条链里没有任何 merge——**判存在性用集合就够了，不需要真的连接**，这就是"重复右表键不会复制结果"的原因：`isin` 回答的是布尔问题，不是配对问题。

顺带对比一下"如果用 merge 会怎样"：`customers.merge(orders, left_on='id', right_on='customerId', how='left')` 再筛 `customerId` 为空的行，在customerId=[1,1,None] 这份数据上，客户 1 会被两笔订单复制成两行、None 订单还会把不匹配客户拉进来，你得再做一次去重和 NULL 过滤才能得到同样的 [b, c]。两种写法都能对，但 `~isin` 版把这些坑从根上绕开了——这也是 cell1 说"先明确键的唯一性，再判断该用哪种连接方式"的意义：想清楚要的是"配对"还是"存在性"，选错工具就得多擦屁股。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么对？** cell4 给了两条论证，翻译成大白话。第一条关于反连接：答案恰好是"在右表里找不到匹配键的那些左表行"。为什么右表重复不影响？因为"存在匹配"是个是非题——客户 1 有一笔订单还是一百笔，"客户 1 下过单"这个事实都只是"真"，判断结果不会变多也不会变少；反过来说，如果用 merge 实现就会因为一对多复制行，这就是本题不用 merge 的原因。为什么 NULL 不会误伤？因为 `dropna` 之后 NULL 订单根本不参与比较，就像 SQL 里 `NULL = 1` 永远不成立一样。第二条关于宽长变换：melt 之后每个原格子由 `(product, quarter)` 唯一标识，只要这个组合在原表里唯一（pivot 前我们已经检查过了），变换就是无损的、可逆的。而 pivot 的报错行为本身也是正确性的一部分：数据有歧义时报告歧义，好过自作主张平均出一个没人认账的数。

把"可逆"这件事再说透一点：对 cell6 的销售宽表执行 melt 得到 8 行长表，再对长表执行 `pivot(index='product', columns='quarter', values='sales')`，你会原样拿回 2 行 5 列的宽表——一来一回信息守恒。但这个守恒有前提：`(product, quarter)` 必须唯一。一旦某产品某季度有两笔记录，pivot 就无处落格（本章抛错），而 pivot_table 会把它平均掉——平均是"新造的数据"，不是"还原的数据"，这就是"pivot 不是聚合"这句契约的分量。

**复杂度怎么说？** 拼接两张表就是把 b 表的行追加到 a 表后面，O(n+m)；melt 每个格子产出一行，n 行 4 列就是 4n 行，系数 4 是"四个季度"这个固定常数；反连接把 ordered_ids 装进哈希集合后逐个客户查"在不在"，平均 O(n+m)。pivot 稍贵：要组织行列索引并排序，O(n log n)，而且产出的宽表大小由"行键值个数 × 列键值个数"决定——比如 100 个城市 × 12 个月就是 1200 个格子，就算原始观测只有几百条（稀疏），宽表框架也可能很大，这是 cell4 提醒的存储代价。

## 六、测试用例在测什么

cell8 的验证方式仍是 `assert_frame_equal` 表级比对（行索引、列名、dtype、单元格全查），外加三段 `try/except` 异常契约测试，最后还有一段和 SQLite 的交叉验证。整段测试的组织思路是"每个函数至少一组正常值 + 一组边界或契约违例"：正常值确认功能对，违例确认"错误被拒绝的方式也对"。跑测试前同样建议先预测四个输出：

- 拼接 a(2 行) + b(1 行) → 3 行，索引 0..2
- melt 2 行宽表 → 8 行长表，顺序按季度列分组
- pivot 4 行长表 → 2 行 2 列交叉表
- 反连接 3 客户对 [1,1,None] 订单 → 2 行 Customers
- 四个预言全中，说明第三节的推导你已经能独立复算。

1. `concatenate_tables(a,b)` == 三行表 —— **正常值**：两表正确摞接、索引重排。
2. `concatenate_tables(a.iloc[:0], a)` == a —— **空表边界**：第一个参数是切出来的空表（结构相同），拼上去应等于原表。
3. `concatenate_tables(a, b[['y','x']])` 必须抛 ValueError —— **契约测试**：列名相同但**顺序相反**的表不许拼，验证"有序 schema"检查真的在工作。
4. `melt_sales(r)` == 手写的 8 行期望表 —— **正常值**：期望表是测试里独立手写的（`['A','B']*4` 交错的 product、`1,5,2,6,3,7,4,8` 的 sales），行序也被锁定，验证 melt 的输出顺序契约。
5. `len(melt_sales(r)) == 4*len(r)` —— **形状不变量**：宽 n 行 4 季度列，长表必须恰好 4n 行。
6. `pivot_weather(w)` == 期望交叉表（index 名 month、columns 名 city） —— **正常值**：连 `columns.name='city'`、索引名这些元数据都被 assert_frame_equal 检查。
7. `pivot_weather(pd.concat([w, w.iloc[:1]]))` 必须抛 ValueError —— **重复键契约**：故意把 (A,1) 那行复制一遍（10 度出现两次），pivot 必须报"测量重复"而不是给平均值。
8. `customers_without_orders(customers, orders)` == `Customers ['b','c']` —— **正常值 + 特殊值**：一桌数据同时验证了"重复订单不复制"（customerId=[1,1]）和"None 订单不算匹配"。
9. 最后一段把 customers/orders 写进 SQLite，跑 `SELECT name ... WHERE NOT EXISTS (...)`，再断言 pandas 结果和 SQL 结果**逐位相等** —— **交叉验证**：用两种独立的实现路径互相印证，这是本章"pandas 反连接 == SQL NOT EXISTS"契约的最硬证据。

## 七、练习思路提示

- **练习 1（构造重复键让 pivot 报错，并讨论该不该聚合）**：提示——在 weather 里加一行 `('Seoul','Jan', 99)`，预测 `pivot_weather` 会抛 ValueError；然后思考"报错"和"用 pivot_table 平均"哪种符合业务：如果第二个 99 度是**错误录入**，平均会把错误洗白，报错才是对的；如果它是一次**补充观测**（比如早晚各测一次），聚合（平均/取最大）才说得通。用 `pivot_table(aggfunc='mean')` 跑一遍对比两种口径的输出差异，并写清楚你选哪种、为什么。
- **练习 2（SQL 反连接与 pandas 互验）**：提示——cell8 最后一段已经给了一个模板：用 `to_sql` 把两张表灌进内存 SQLite，一边跑 `NOT EXISTS`，一边跑 `customers_without_orders`，断言相等。你可以扩充边界再验一次：给订单表加 `customerId=None` 的行、给两个客户各加多笔订单、再造一个"所有客户都下过单"的场景（预期空表）。想清楚每加一种数据，两种实现是否给出同一个答案、为什么。建议按场景表交作业，每行三个字段：

- 场景（如"某客户下 3 单"、"订单表为空"、"客户表为空"）
- SQL 预期 / pandas 预期（先手算再跑）
- 两者是否一致，不一致时指出是哪一方的契约问题

## 八、对应 LeetCode 题目

- **2888. Reshape Data: Concatenate**：练 schema 检查 + `pd.concat(ignore_index=True)`，对应 `concatenate_tables`。
- **2889. Reshape Data: Pivot**：练 `pivot` 的行键/列键/值三参数与重复键报错行为，对应 `pivot_weather`。
- **2890. Reshape Data: Melt**：练 `melt` 的 id_vars/value_vars/var_name/value_name 四要素，对应 `melt_sales`。
- **183. Customers Who Never Order**（comparison）：练反连接思想——本章用 `~isin` 实现，并在测试里和 SQL `NOT EXISTS` 互验，对应 `customers_without_orders`。

最后把本章四条"先问后做"的检查单放这里，做题前过一遍：拼接前问"列名和顺序一致吗"；透视前问"(行键, 列键) 唯一吗"；熔化前问"哪些列是身份列、哪些列是观测列"；连接前问"我要的是配对还是存在性、键在两边唯一吗"。四个问题都答上来，输出形状就再也不会吓到你。

做题顺序建议照 2888 → 2890 → 2889 → 183 来：先练最机械的拼接和 melt，建立"形状直觉"，再碰要对键把关的 pivot，最后用反连接收尾——难度正好递增。
