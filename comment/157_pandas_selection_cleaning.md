# N157 · Pandas选择、缺失与类型 —— 说人话详解

> 对应 notebook：`notebooks/19_specialized_tracks/157_pandas_selection_cleaning.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章解决的是"拿到一张乱糟糟的表，怎么把它洗干净，而且洗的时候不弄坏数据"。乱在四个地方：列表数据要变成规整的表；同一个邮箱可能注册了两次；有的学生姓名是空的；成绩一会儿是浮点数一会儿干脆没有。对应的四道 LeetCode pandas 题（2877/2882/2883/2886）就是这四个动作。

给你一个具体到数字的例子（notebook cell6 的真实数据）：

```
student_id  name    grade
1           Li      90.0
2           None    81.0      ← name 是缺失值（Python 的 None）
3           ""      None      ← name 是空字符串，grade 缺失
4           Zhou    75.0
```

清洗目标：删掉"name 真缺失"的第 2 行，但**必须留下**第 3 行（空字符串是"填了空"，不是"没填"）；同时把 grade 从浮点转成"可空整数"，90.0 变 90、缺失变 `<NA>`。最终输出是三行：`Li 90`、`"" <NA>`、`Zhou 75`。为什么第 2 行删、第 3 行留？因为"姓名缺失"和"姓名是空串"是两种不同的业务状态，本章的契约是只删前者。

更深一层，cell1 点出了本章的灵魂：表格操作首先是**数据契约**——列名是什么？缺失用什么表示？重复保留哪一行？结果索引有没有意义？不能只看屏幕上"长得一样"就下结论。

## 二、关键概念（定义）

- **DataFrame / Series**：DataFrame 是带行列标签的二维表（像 Excel 一页）；Series 是带标签的一维列（表里的一列）。标签（索引）是行和列的"名字"，很多诡异 bug 都出在索引上。
- **loc / iloc**：两种取行列的方式。`loc` 按**标签**取（`loc[3]` 取索引名叫 3 的行），`iloc` 按**位置**取（`iloc[3]` 取第 4 行）。测试里 `customers.iloc[[0,2]]` 就是"按位置取第 0 行和第 2 行"。
- **布尔筛选**：用一个True/False 序列当筛子，比如 `students[students['grade'] > 80]` 只留成绩超过 80 的行。筛选只改变"哪些行在场"，不改变行本身。
- **NA / NaN / None**：都表示"缺失"。Python 层面写 `None`，NumPy 浮点层面叫 `NaN`，pandas 统一用 `isna()` 识别它们。注意 NaN 有个怪脾气：`NaN == NaN` 结果是 False，所以判断缺失必须用 `isna()`，不能用 `==`（练习 1 就是这个）。
- **空字符串 `""`**：它是"有值，值是空"，不是缺失。`dropna` 不会删它——这是业务口径，不是技术自动判断。
- **astype 类型转换**：把一列从一种类型转成另一种，比如 `'float64'` 转 `'Int64'`。
- **`Int64` vs `int64`（就一个大写一个不小写）**：小写 `int64` 是 NumPy 的老整数，**不允许缺失**，硬转含 NaN 的列会报错或被偷偷换成浮点；大写 `Int64` 是 pandas 的可空整数（nullable integer），既能装 `90` 也能装 `<NA>`，而且**拒绝无声截断**——把 90.5 转成它会直接抛异常，而不是悄悄变成 90。
- **去重（drop_duplicates）**：按某些列判断"重复"，`keep='first'` 表示一组重复里保留**第一次出现**的那行。注意缺失值也算"一个值"：两个 `None` 邮箱互为重复。
- **reset_index(drop=True)**：删行之后索引会留下"窟窿"（0,2,4 变成 0,2），`reset_index(drop=True)` 把索引重排成 0,1,2……并扔掉旧的。它是在明确声明"旧索引不是业务主键，可以丢"。
- **链式赋值风险**：像 `df[df['a']>0]['b'] = 1` 这种"筛选完再赋值"的链式写法，pandas 可能只改了临时副本、原表纹丝不动，还给你 FutureWarning。正确做法是先用 `.copy()` 拿到独立副本再改，本章 `change_grade_type` 就是这么写的。之所以有这个坑，是因为 pandas 的索引操作（方括号）有时返回视图、有时返回副本，规则复杂到官方都建议别依赖——一条语句里链两次索引再赋值，到底改了谁就成了玄学。

补一个和 `Int64` 相关的细节：`astype('Int64')` 处理的是"类型层"的转换，它对 float 列里的 `90.0` 认定为安全（无损），对 `90.5` 认定为不安全（有损）并抛错。而 `int()` 强转或某些 `fillna(0).astype(int)` 的组合会悄悄把 90.5 变 90、把缺失变 0——数据看起来"干净"了，其实是被涂改了。本章选"报错优先"，和"空字符串不算缺失"是同一种立场：**区分'数据缺失'和'数据违规'，前者可以删，后者必须让人知道**。

## 三、解决思路（一步步推导）

**Step 1：把列表变成类型确定的表。** 输入是 `[[1,20],[2,21]]` 这样的行列表，用 `pd.DataFrame(data, columns=['student_id','age'])` 指定列名，再 `astype({'student_id':'int64','age':'int64'})` 把两列钉死成整数。为什么要显式指定？因为空列表 `[]` 建表时 pandas 猜不出类型，不给 `columns` 连列名都没有——这就是"数据契约"的第一条。

**Step 2：按邮箱去重，保留首次出现。** 输入 `id=[3,1,2,4]`、`email=['a@x','a@x',None,None]`。手算一遍 `drop_duplicates(subset=['email'], keep='first')` 从上往下扫：

| 行 | email | 判定 |
|----|-------|------|
| 0 | a@x | a@x 第一次见 → 保留 |
| 1 | a@x | 重复 → 删 |
| 2 | None | None 第一次见 → **保留**（"第一个缺失邮箱也算首次出现"是本章契约） |
| 3 | None | 重复 → 删 |

结果留下第 0、2 行，再 `reset_index(drop=True)` 把索引 [0,2] 重排成 [0,1]。

**Step 3：只按 name 删缺失行。** 输入 `name=['a', None, '']`、`grade=[90.0, 75.0, nan]`。`dropna(subset=['name'])` 只看 name 这一列：第 1 行 None → 删；第 2 行 `''` 是空串不是 NA → 留；第 0 行 → 留。结果 `iloc[[0,2]]`。关键点有两个：一是**只检查指定列**，不因为别的列有缺失就顺手删行；二是空串和缺失严格区分。

**Step 4：成绩转可空整数。** 拿 Step 3 的结果（grade 是 90.0、NaN、75.0），`astype('Int64')` 之后：90.0 → 90，NaN → `<NA>`，75.0 → 75。dtype 从 float64 变成 Int64，"看起来只是去掉小数点"，实际上是换了一套能装缺失的类型系统。如果 grade 里出现 90.5，转换会**当场报错**而不是截断成 90——宁可失败，不偷偷改数据。这一步的判断标准可以总结成三问：

- 数据里有没有缺失？有 → 小写 int64 直接出局，必须用大写 Int64。
- 数据是不是精确整数？不是（如 90.5）→ 转换失败是**正确行为**，别想着"约一下就行"。
- 转完之后打印出来 `90` 和 `<NA>` 长得和原来不一样了？那是好事——类型系统在如实报告数据的真实状态。

**Step 5：每个函数都返回新表。** 本章所有函数都不动输入表：去重/删缺失靠 pandas 本来就返回新对象的操作；类型转换先 `students.copy()` 再改副本。cell6 里 `change_grade_type(drop_missing_names(raw))` 串起 Step 3 和 Step 4，`raw` 自身从头到尾没变。cell6 还打了一张"清洗前 vs 清洗后"的状态对照表，我们把它补全成具体数值：

| 阶段 | 行数 | 索引 | 各列 dtype |
|------|------|------|------------|
| before（raw） | 4 | [0, 1, 2, 3] | student_id=int64, name=object, grade=float64 |
| after（clean） | 3 | [0, 1, 2] | student_id=int64, name=object, grade=**Int64** |

看这张表能读出三件事：行数从 4 变 3（只有 name 为 None 的第 2 行被删）；索引从 [0,1,2,3] 压回 [0,1,2]（reset_index 生效，窟窿被抹平）；grade 的 dtype 从小写 float64 变成大写 Int64（可空整数落地）。屏幕上"90 和 90.0 长得一样"，但 dtype 那一列不会骗人——这正是 cell1 说的"不能只检查屏幕上看起来相同"。

## 四、代码逐段讲解

cell3 的全部实现一共四个函数，都很短，我们逐个看。

```python
def create_dataframe(student_data):
    """Rows are (student_id, age); an empty input keeps both integer columns."""
    return pd.DataFrame(student_data, columns=['student_id', 'age']).astype(
        {'student_id': 'int64', 'age': 'int64'})
```

`pd.DataFrame(student_data, columns=[...])` 把行列表立成表并**显式给列名**——就算传入空列表，表也带着两个列名；`.astype({...})` 再把两列统一转成 NumPy 整数 `int64`（这里没有缺失，小写 int64 够用；有缺失的场景见第四个函数）。

```python
def drop_duplicate_emails(customers):
    # First occurrence wins, including the first missing email.
    return customers.drop_duplicates(subset=['email'], keep='first').reset_index(drop=True)
```

`subset=['email']` 声明"只看邮箱列判重复"；`keep='first'` 声明"重复组里留第一个"，注释特意说明连缺失邮箱也遵守这个规则（第一个 None 留下）；`reset_index(drop=True)` 重排行号，语义是"旧索引只是行号，不是业务主键"。

```python
def drop_missing_names(students):
    # An empty string is present, not a missing value.
    return students.dropna(subset=['name']).reset_index(drop=True)
```

`dropna(subset=['name'])` 只按 name 判缺失，其他列有 NaN 也不影响；注释强调空串"在场"（present），不算缺失（missing），所以不会被删。

```python
def change_grade_type(students):
    """Teaching contract: nullable integer Int64 preserves missing grades."""
    result = students.copy()
    result['grade'] = result['grade'].astype('Int64')
    return result
```

第一步 `students.copy()` 先做深拷贝——这就是防"链式赋值/原地修改"坑的写法：后面无论怎么改 `result`，原表都不受影响。然后把 grade 列**重新赋值**回 `result['grade']`（这是 pandas 正规的单列赋值姿势，不是链式赋值），目标类型是大写 `Int64`：可空、能装 `<NA>`、拒绝把 90.5 无声截断。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么对？** 三条论证，对应 cell4。第一，筛选（布尔筛选、dropna）只改变"行集合"，不会篡改任何留下的行的内容，所以删完缺失后剩下的数据一个字节都没变。第二，去重的输出可以精确描述为"每个邮箱等价类**第一次出现的位置**"——`keep='first'` 从上往下扫一遍，第一次见到的键留下、之后再见就丢，这个规则对普通值和 None 一视同仁，所以手算表格能逐一推出来。第三，类型转换**只碰 grade 一列**（`result['grade'] = ...` 只改这一列），转换失败时抛异常是"契约错误"——它告诉你数据不符合约定，而**不是**给你填个 0 糊弄过去。`reset_index` 的意义也在正确性里：显式声明旧索引可以丢，避免调用方误把行号当成学号。

**复杂度怎么说？** 建表要逐行填数据，筛选和类型转换都要扫一遍每一行，所以都是 O(n)——表里有 100 万个学生，建表/清洗就大约是百万次操作的量级。去重内部用哈希表记"见过的键"，平均每次查一下是常数，整体期望 O(n)。所有函数都返回**新表**，所以空间也是 O(n)。cell4 最后特意说：这些是算法量级上的结论，pandas 内部具体怎么实现（比如是不是真的用了哈希）不影响这个层面的判断。

## 六、测试用例在测什么

cell8 用 `assert_frame_equal`（pandas 官方的表级比对，连 dtype 和索引一起查）做了 9 条断言。它比 `==` 加 `all()` 严格得多：两表的行索引、列名、每列 dtype、每个单元格的值（包括 None 与 NaN 的位置）必须全部一致才算相等，所以这些断言查的不只是"数字对不对"，还包括"类型契约、索引契约、纯度契约"是否都被遵守。测试开头的 `original = customers.copy(deep=True)` 和 `before = students.copy(deep=True)` 就是为后面的纯度断言准备的"执行前快照"。

1. `assert_frame_equal(create_dataframe([]), ...int64 空表...)` —— **空表边界**：空输入也必须返回"两列、都是 int64"的表，验证 Step 1 的数据契约。
2. `assert_frame_equal(create_dataframe([[1,20],[2,21]]), ...)` —— **正常值**：两行数据正确落位，列名列对。
3. `assert_frame_equal(drop_duplicate_emails(customers), customers.iloc[[0,2]].reset_index(drop=True))` —— **正常值 + 缺失值参与去重**：预期值手算见第三节表格（留 0、2 行）。用 `iloc[[0,2]]` 当"标准答案"很巧妙——它不经过去重逻辑，直接按位置取行，两边逻辑独立，比对才有说服力。
4. `assert_frame_equal(customers, original)` —— **纯度测试**：函数跑完后原表必须和执行前的深拷贝一模一样，验证"返回新表、不改输入"。
5. `assert_frame_equal(drop_missing_names(students), students.iloc[[0,2]].reset_index(drop=True))` —— **特殊值**：None 被删、空串 `''` 被留，这是本章最重要的业务口径断言。
6. `assert_frame_equal(change_grade_type(students), 预期 Int64 表)` —— **正常值 + 类型**：90.0→90、75.0→75、NaN→None，且 dtype 必须是 `Int64`（assert_frame_equal 连 dtype 一起查）。
7. `assert_frame_equal(students, before)` —— 又一条**纯度测试**：类型转换后原表不动，验证 `copy()` 起了作用。
8. `try: change_grade_type(pd.DataFrame({'grade':[90.5]})) except (TypeError, ValueError): pass else: raise AssertionError(...)` —— **异常行为测试**：90.5 必须让转换**抛错**，如果没抛（说明被无声截断成 90），测试反而失败。这条测的是"拒绝静默截断"的契约。
9. `assert_frame_equal(drop_missing_names(students.iloc[:0]), ...)` —— **空表边界**：空表进去空表出来，不报错。

## 七、练习思路提示

- **练习 1（解释 NaN 不能用 == 比较）**：提示——在 Python 里跑 `float('nan') == float('nan')`，你会发现结果是 False（IEEE 754 浮点标准规定 NaN 和任何值都不相等，包括它自己）。所以 `df[df['grade'] == NaN]` 永远筛不出缺失行。手算示例可以用本章的 grade 列 [90.0, 75.0, nan]：预测 `== nan` 得到三个 False，而 `isna()` 得到 [False, False, True]。验证方式：把两种筛选各跑一遍，对比行数。再补一个延伸思考：

- `dropna` 内部用的就是 isna 一族判断，所以它能删掉 NaN 却删不掉空串——两者底层是"缺失判定"和"字符串值"两套语义。
- 交作业时把"三个 False 的筛子留下 0 行"这个手算结论写进去，它就是 `==` 方案失效的直接证据。
- **练习 2（区分原地修改和返回新表）**：提示——设计一个对照实验：先 `df2 = drop_missing_names(df)`，再打印 `df`，看它变没变（本章实现应该没变）；然后对比"危险写法" `df[df['name'].notna()]['grade'] = 0`，跑完检查 `df['grade']` 是否真的被改（大概率没改，还可能弹 Warning）。想清楚哪些 pandas 操作返回副本、哪些返回视图，`copy()` 在什么时候是必须的。边界可以试试"空表上做原地赋值"和"对函数返回的新表再赋值"。整理结论时可以按三档写：

- 确定安全：`df.loc[条件, '列'] = 值`（一次索引加赋值，pandas 官方推荐的原地改法）。
- 确定安全（不改原表）：`df2 = df.copy()` 之后随便改 `df2`，本章 `change_grade_type` 的做法。
- 高危：链式两次索引再赋值（`df[...][...] = ...`），结果取决于版本和运气，一律重写。

## 八、对应 LeetCode 题目

读题之前，先用四句话把本章的四条契约串起来复述一遍：建表要显式列名和类型；去重保留首次出现（含首个缺失值）；删缺失只看指定列、空字符串不算缺失；类型转换拒绝无声截断。四道题其实就是这四句话各自的考场。

- **2877. Create a DataFrame from List**：练 `pd.DataFrame` 建表 + 显式列名/类型，对应 `create_dataframe`。
- **2882. Drop Duplicate Rows**：练 `drop_duplicates(subset=..., keep='first')` 的"保留首次"契约，对应 `drop_duplicate_emails`。
- **2883. Drop Missing Data**：练 `dropna(subset=[...])` 只按指定列删缺失，对应 `drop_missing_names`。
- **2886. Change Data Type**：练 `astype` 类型转换，本章把目标类型升级成可空 `Int64`，对应 `change_grade_type`。

做题顺序建议照 2877 → 2882 → 2883 → 2886 来：先会建表，再去重、删缺失，最后碰类型——每题恰好用到前一题的结果，这就是本章四个函数被串成一条流水线的原因。
