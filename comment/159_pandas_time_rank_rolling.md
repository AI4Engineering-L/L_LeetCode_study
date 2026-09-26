# N159 · Pandas日期、排名与滚动统计 —— 说人话详解

> 对应 notebook：`notebooks/19_specialized_tracks/159_pandas_time_rank_rolling.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章是 N155（SQL 窗口/排名）和 N156（SQL 日期/留存/滚动）的 **pandas 重制版**：同样的三类业务问题——部门前三薪、次日留存、7 天滚动营业额——这次用 pandas 的矢量化操作来表达"时间窗口"和"分组窗口"，另加一道字符串清洗题（名字规范化）。矢量化（vectorization）的意思是：不写 for 循环逐行处理，而是让 pandas 整列整列地算，代码短、速度快。

给你两个具体到数字的例子。第一个还是 7 天滚动（cell6/cell8 真实数据）：日期和金额是 `01-01:10, 01-01:20, 01-03:30, 01-07:70, 01-08:80`，问 01-08 的"过去 7 天（含当天）"总额。窗口是 01-02 到 01-08，01-01 已掉出，所以答案是 30+70+80=**180**，均值 180/7≈25.71。第二个是留存的跨月陷阱：玩家 1 在 01-31 和 02-01 各登录一次，"次日"必须从 01-31 跨月加一天到 02-01——如果你把日期字符串最后一位加一，01-31 会变成不存在的 01-32，留存就算错了。

还有一个本章特有的精度彩蛋：1/8 = 0.125，保留两位小数应该是 0.13（四舍五入）而不是 0.12（Python 内置 `round` 的"银行家舍入"会给出 0.12）。notebook 的测试就专门盯住了这个差别。

## 二、关键概念（定义）

- **to_datetime**：把 `'2024-01-31'` 这样的字符串解析成真正的时间戳类型。字符串只能看不能算，时间戳才能加减天、比大小。
- **dt 访问器**：Series 的时间"属性门"，如 `.dt.normalize()` 把时间戳抹掉时分秒、只留日期，`.dt.day` 取日。统一粒度（都是纯日期）之后才能可靠地去重和对齐。
- **rank(method='dense')**：pandas 版的 DENSE_RANK。`groupby('departmentId')['salary'].rank(method='dense', ascending=False)` 的意思是"每个部门内部按薪资从高到低做不跳号排名"，并列 90 分的两个人都是第 2，第 3 高的所有并列者都会保留。
- **groupby + transform 类操作（如 shift/rank）**：分组后做"对齐回每一行"的计算（窗口式，不折叠行）。本章 rank 就是分组窗口；SQL 章的 LAG 对应 pandas 的 `groupby(...).shift(1)`。
- **merge + validate**：`validate='many_to_one'` 声明"左表键可重复、右表键必须唯一"，`'one_to_one'` 声明两边都唯一。pandas 会在连接时**当场校验**这个形状约定，违反就报错——这是把"连接键唯一性"从口头契约变成机器检查。
- **rolling（滚动窗口）**：在有序序列上开滑动的统计窗口。`rolling(7)` 数 7 个**行**；`rolling('7D')` 看的是 7 个**自然日**——日期有缺口时两者答案不同，日期题必须用后者。
- **closed='right'**：声明时间窗口"左开右闭"，即 `(当日−7天, 当日]`。对 01-08 来说窗口是 (01-01, 01-08]，恰好 7 个自然日，01-01 被排除。
- **Timedelta**：时间差对象，`pd.Timedelta(days=1)` 就是"一天"。`日期 + Timedelta(days=1)` 由日历库正确处理跨月、跨年，01-31 加一天得到 02-01。
- **str 访问器**：字符串列的整列操作入口，如 `.str.capitalize()` 把 `'aLICE'` 变 `'Alice'`（首字母大写、其余小写）。
- **Decimal + ROUND_HALF_UP**：十进制精确算术 + "四舍五入"规则。Python 内置 `round` 用的是"银行家舍入"（0.5 向偶数靠），算报表会出鬼错，所以本章自己写了 `_round2`。
- **缺失日期贡献 0**：滚动窗口按日历范围圈行，表里没有的日期没有行、金额记 0；但输出只保留**原表出现过的**、且已满 7 天历史的日期。

## 三、解决思路（一步步推导）

**Step 1：部门内 dense 排名取前三。** 员工表（cell8 数据）：部门 1 有 a=100, b=90, c=90, d=80, e=70，部门 2 只有 f=10。先 `groupby('departmentId')` 再 `rank(method='dense', ascending=False)`，手算部门 1：a 是第 1；b、c 并列第 2；d 是第 3（不跳号！）；e 是第 4。`_rank <= 3` 留下 a、b、c、d——注意**不是只截三行**，而是"前三个不同薪资的所有人"。部门 2 的 f 是第 1，留下。最后连部门表拿名字、排好序输出：HR f 10；IT a 100, b 90, c 90, d 80。

**Step 2：次日留存。** 活动表：玩家 1 登录 01-31、02-01、02-01（同日两次），玩家 2 在 01-01，玩家 3 在 01-02。流程是：取 `(player_id, event_date)` 两列 → `to_datetime` + `normalize` 统一成纯日期 → `drop_duplicates` 去重（**分母从 5 行日志变成 3 个玩家**）→ 按玩家 `min` 取首日 → 首日 `+ Timedelta(days=1)`（玩家 1 的 01-31 跨月变 02-01）→ 拿这份"玩家+次日"清单去和去重后的登录表做**一对一 merge**，能配上对的玩家就是"次日回来的人"。手算：玩家 1 的次日 02-01 在表里 → 命中；玩家 2 的次日 01-02 不在；玩家 3 的次日 01-03 不在。命中率 1/3 = 0.333…，四舍五入 → **0.33**。

**Step 3：名字规范化。** 输入 `['aLICE','bOB']`，`.str.capitalize()` 整列变成 `['Alice','Bob']`，再按 user_id 排序、重排索引。输出顺序从 user_id 的 [2,1] 变成 [1,2]。这一步看起来最简单，但它示范了"字符串列的矢量化处理"范式：不写循环，一个 `.str.xxx` 调用整列搞定，和 Step 4 的 `pd.to_datetime` 处理日期列、Step 2 的 `dt.normalize` 是同一族操作。

**Step 4：7 天滚动营业额。** 先按日聚合：`01-01→30（10+20）, 01-03→30, 01-07→70, 01-08→80`，得到以日期为索引的日序列。再 `rolling('7D', closed='right').sum()`，逐日手算：

| 日期 | 窗口 (t−7d, t] | 覆盖到的行 | 滚动和 |
|------|----------------|-----------|--------|
| 01-01 | 12-25 ~ 01-01 | 01-01 | 30 |
| 01-03 | 12-28 ~ 01-03 | 01-01, 01-03 | 60 |
| 01-07 | 12-31 ~ 01-07 | 01-01, 01-03, 01-07 | 130 |
| 01-08 | 01-02 ~ 01-08 | 01-03, 01-07, 01-08 | **180** |

然后只留 `index >= 最早日 + 6 天` 的日期（01-07、01-08），因为更早的日期凑不满完整 7 天历史；总额转回整数，均值 = 总额/7 用 Decimal 四舍五入两位：130/7→18.57，180/7→25.71。如果这里改用按行的 `rolling(7)`，01-08 的窗口就是"往前数 7 行"——本例只有 4 行全被圈进来得 210，日期缺口下答案直接错，这正是练习 1 要你对比的。

## 四、代码逐段讲解

cell3 有一个私有工具函数加四个接口，逐个看。

```python
from decimal import Decimal, ROUND_HALF_UP

def _round2(value):
    return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
```

先把数转成字符串再交给 Decimal（避开二进制浮点的表示误差），`quantize(Decimal('0.01'), ROUND_HALF_UP)` 做"人类理解的四舍五入"到两位，最后转回 float。1/8 = 0.125 在这里得到 0.13，而内置 `round` 会给 0.12——这条差异后面有测试盯着。展开说就是：Python 的 `round` 采用"银行家舍入"（正好一半时向偶数位靠，0.125 的两位偶数是 2，故 0.12），而业务报表里大家默认的"四舍五入"是 HALF_UP（一半向上，0.13）；0.125 这种正卡在中间的值，两种规则给出不同答案，选哪个必须明说，本章的教学契约选了 HALF_UP。

```python
def department_top_three_salaries(employees, departments):
    ranked = employees.copy()
    ranked['_rank'] = ranked.groupby('departmentId')['salary'].rank(method='dense', ascending=False)
    kept = ranked.loc[ranked['_rank'] <= 3].merge(
        departments.rename(columns={'id':'departmentId','name':'Department'}),
        on='departmentId',how='inner',validate='many_to_one')
    return kept.rename(columns={'name':'Employee','salary':'Salary'})[
        ['Department','Employee','Salary']].sort_values(
        ['Department','Salary','Employee'],ascending=[True,False,True]).reset_index(drop=True)
```

先 `copy()` 保护输入，再用"新增一列 `_rank`"的方式做分组窗口排名（不折叠行）；筛 `<=3` 后 merge 部门表——部门表的 id 先 rename 成同名的 `departmentId` 才能当连接键，`validate='many_to_one'` 声明"多个员工对一个部门"，若部门表里有重复 id 会当场报错；最后挑列、改名、三键排序（部门升、薪资降、姓名升，让并列 90 的 b、c 有确定顺序）并重排索引。

```python
def next_day_retention(activity):
    if activity.empty:
        return 0.0
    days = activity[['player_id','event_date']].copy()
    days['event_date'] = pd.to_datetime(days['event_date']).dt.normalize()
    days = days.drop_duplicates()
    first = days.groupby('player_id',as_index=False)['event_date'].min()
    first['event_date'] += pd.Timedelta(days=1)
    hits = first.merge(days,on=['player_id','event_date'],validate='one_to_one')
    return _round2(Decimal(len(hits)) / Decimal(len(first)))
```

空表直接返回 0.0。中段是 Step 2 的流程：normalize 统一粒度、去重（同日多次登录只算一天）、按玩家取首日、加一天。`hits` 是"次日确实有登录"的玩家清单；`validate='one_to_one'` 保证每个玩家最多匹配一次（first 里一人一行、days 去重后一键一行），分子不会膨胀。最后分子分母都走 Decimal 再四舍五入。（运行时这两行 `Timedelta` 运算会弹 DeprecationWarning，那是新版 NumPy 对时间差单位规范的提醒，不影响结果。）

```python
def normalize_names(users):
    """ASCII alphabetic names; retain schema and sort by user_id."""
    result = users.copy()
    result['name'] = result['name'].str.capitalize()
    return result.sort_values('user_id').reset_index(drop=True)
```

copy 后整列 `.str.capitalize()`，排序重索引。docstring 说明了契约：只处理 ASCII 字母名字、保留表结构、按 user_id 排序。

```python
def daily_rolling_sales(df):
    """Seven natural days, missing days contribute zero; output observed days only."""
    data = df[['visited_on','amount']].copy()
    data['visited_on'] = pd.to_datetime(data['visited_on']).dt.normalize()
    daily = data.groupby('visited_on')['amount'].sum().sort_index()
    if daily.empty:
        return pd.DataFrame({...三个空列、类型齐全...})
    total = daily.rolling('7D',closed='right').sum()
    total = total.loc[total.index >= daily.index.min()+pd.Timedelta(days=6)]
    # The teaching inputs are bounded integer amounts, exactly representable as float64.
    result = total.astype('int64').rename('amount').reset_index()
    result['average_amount'] = [_round2(Decimal(int(x))/Decimal(7)) for x in result['amount']]
    return result
```

（空表分支我省略号缩写了，原文是三个带 dtype 的空 Series。）流程：日聚合 `groupby(...).sum()` 得到"日期索引 → 日总额"的 Series 并按日期排序；`rolling('7D', closed='right')` 按**时间跨度**开窗，缺失的日子没有行、贡献自然为 0；`index >= min+6天` 只留满窗日期；注释特意声明教学前提——金额是有界整数，float64 能精确装下，转 int64 不会丢精度；最后均值固定除以 7，逐个用 `_round2` 四舍五入。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么对？** cell4 的核心论点翻译过来是：**顺序不可交换**。你必须先"定统计单位"（先按日聚合、先按玩家去重），再"做排名或日期对齐"；如果先排名再聚合，排名基于的行数就是错的。具体到三处：留存的正确性来自"一对一匹配"——`first` 是每人一行的首日清单，`days` 去重后每个 (玩家, 日期) 键唯一，`validate='one_to_one'` 让每个玩家最多给分子贡献一次，重复登录想多贡献都没门。滚动窗口的正确性来自"窗口定义在日历上"——`'7D'` 圈的是时间区间不是行数，跨月、有缺口都不会改变"过去七个自然日"的定义，01-01 之所以在 01-08 的窗口外，是因为日历上它就是 7 天前，与它在表里的位置无关。排名的正确性来自 dense 语义——"第三个**不同**薪资的所有员工"恰好等于"rank ≤ 3 的所有行"，并列不会挤掉后面的人。

**复杂度怎么说？** 分组（groupby + rank / min / sum）在哈希分桶下平均线性；排名和排序要 O(n log n)。拿本章数据量感受一下：6 个员工排名、5 行销售流水，代价可忽略；放大到 10 万名员工也就是 10 万 × 17 ≈ 170 万次比较的量级。滚动窗口的关键优势是：它在**已排序的序列**上滑动，窗口滑一格只吐出一行进、一行出，不用每行都回头扫 7 天的全表——整体线性；如果是朴素做法（每个日期都全表扫一遍范围）就是 O(n²)，10 万行就是百亿级操作，天壤之别。存储上每步都产生新表，O(n)。

## 六、测试用例在测什么

cell8 用 `assert_frame_equal` 加标量断言，最后还和 SQLite 做了一次交叉验证。老规矩，先预测再对答案：

- 前三名输出 5 行（HR 1 行 + IT 4 行，并列 90 的 b、c 都在）
- 留存 0.33（1/3），空表 0.0，闰日场景 0.13（1/8）
- 滚动窗口只出 01-07 和 01-08 两天，130 和 180
- 名字清洗后按 user_id 排序为 Bob、Alice
- 五个预言全中，第三节的推导就闭环了。

1. `department_top_three_salaries(employees, departments)` == 期望表 —— **正常值 + 并列值**：并列 90 的 b、c 都在第 2，第 3 高 80 的 d 也保留，e（第 4）被拒；期望表连"HR 在前、IT 内按薪资降序、并列按姓名升序"的排序契约一起锁死。
2. `next_day_retention(a) == 0.33` —— **正常值 + 跨月**：玩家 1 的首日 01-31 次日是 02-01（跨月加一天），且同日双登录只算一次，1/3 → 0.33。
3. `next_day_retention(a.iloc[:0]) == 0.0` —— **空表边界**：没有玩家时返回 0.0 而不是除零崩溃。
4. `next_day_retention(one_eighth) == 0.13` —— **特殊值三连**：8 个玩家都在 2024-02-28 首登，只有玩家 0 在闰日 02-29 回来，1/8=0.125；同时测了**闰年**（02-29 存在）和**四舍五入规则**（0.125 用 ROUND_HALF_UP 是 0.13，内置 round 会给 0.12，这条断言就是防退回内置 round）。
5. `normalize_names(users)` == `['Bob','Alice']` 按 user_id 排序 —— **正常值**：大小写混乱的名字被修好，乱序输入被排成 user_id 顺序。
6. `daily_rolling_sales(sales)` == 01-07:130/18.57、01-08:180/25.71 —— **正常值 + 缺日期边界**：01-08 验证 01-01 滑出窗口（180 不是 210）；01-07 验证"满 7 天才输出"的下边界；连 visited_on 的 datetime 类型都被比对。
7. `daily_rolling_sales(sales.iloc[:0]).empty` —— **空表边界**：空进空出，且返回的是带好列名的空表不是裸 None。
8. 最后把 sales 灌进 SQLite，跑 N156 那条 `RANGE BETWEEN 6 PRECEDING` 的 SQL，断言 pandas 结果和 SQL 结果**逐位相等** —— **交叉验证**：两条完全独立的实现路径（pandas 时间索引 vs SQL 儒略日 RANGE）给出同一张表，互为正确性证据。

## 七、练习思路提示

- **练习 1（按行 rolling vs 按时间 rolling）**：提示——就用本章的 5 行销售数据（中间缺 01-02 等日子）。先手算：`rolling(7).sum()` 在 01-08 会把全部 4 行（不足 7 行取所有）圈进来得 210，而 `rolling('7D').sum()` 是 180；想清楚"7 行"和"7 天"分别在数什么。再故意往表里塞一段日期连续但只有 3 天的数据，对比两个窗口何时答案一致、何时分叉。边界别忘了"首部不满窗口"时两者的 min_periods 行为。
- **练习 2（避免不必要的逐行 apply）**：提示——找一个你写过 `df.apply(lambda row: ..., axis=1)` 的场景（比如本章的"首日加一天"或"金额除以 7 四舍五入"），改写成矢量化版本：日期加减用整列 `+ pd.Timedelta(days=1)`，逐元素四舍五入可以用列表推导配 `_round2` 或直接 Decimal 数组。手算 3 行的小例子确认两种写法输出一致，再用 `%timeit` 对比 10 万行数据上的耗时差距，体会"矢量化为什么快"。

## 八、对应 LeetCode 题目

- **185. Department Top Three Salaries**（comparison）：练 `groupby + rank(method='dense')` 保留并列前三，对应 `department_top_three_salaries`，和 N155 的 SQL 版互为镜像。
- **550. Game Play Analysis IV**（comparison）：练"去重定分母 + 首日加一天 + 一对一匹配"，对应 `next_day_retention`，和 N156 的 SQL 版互为镜像。
- **1667. Fix Names in a Table**（canonical）：练 `.str.capitalize()` 字符串整列处理加排序，对应 `normalize_names`。
