# N175 · 陌生题迁移与结业项目 —— 说人话详解

> 对应 notebook：`notebooks/21_mastery/175_unseen_transfer_final_project.ipynb`

## 一、这章要解决什么问题？（问题描述）

这是结业章，它要解决的问题不是"再学一个新算法"，而是：**拿到一个没见过标签、没见过答案的变体题时，你能不能独立完成建模、证明、实现和复盘**。本章的做法是先复习两条已知主线，再拼出一个"没展示过"的组合变体让你迁移。

两条复习主线：

- **带权区间调度（LC 1235）**：n 份工作各有起止时间和收益，选收益总和最大、互不重叠的子集。具体例子：`start=[1,2,3,3]`、`end=[3,4,5,6]`、`profit=[50,10,40,70]`，最优是选第 1 份（1–3，50）加第 4 份（3–6，70），共 **120**（端点相接 3≤3 算不冲突）。
- **有序矩阵第 k 小行和（LC 1439）**：每行有序的矩阵，从每行各选一个数，所有选法的和中第 k 小是多少。具体例子：`[[1,3,11],[2,4,6]]`、k=5：九个和为 3,5,5,7,7,9,13,15,17（重复各占一名），第 5 名是 **7**。

然后是**迁移变体**（"陌生"指没展示给学习者的组合，不声称是研究界新问题）：输入 `instance={jobs:[(start,end,profit),...], max_jobs:K, cooldown:g}`，要选**至多 K 份**工作，且前一份的 `end+g` 不能晚于后一份的 `start`，允许一份不选（收益可负，所以最优值至少为 0），返回最大收益。具体例子：`jobs=[(1,3,20),(3,5,25),(4,6,30),(7,8,15)]`、`K=2`、`g=1`，答案是 **50**——选 `(1,3,20)` 和 `(4,6,30)`：3+1=4 ≤ 4 恰好合法，合计 50。你可以看到它就是在经典调度上改了两个约束（份数上限、冷却间隔），本章要练的就是"旧结构怎么小改迁移"。

## 二、关键概念（定义）

- **独立分析**：不靠题目标签提示算法，从问题结构本身（排序后前缀可分离）推出解法。结业考核的就是这个能力。
- **选/不选分解（take/skip）**：按结束时间排序后，考虑"最后一份工作"：任何解要么不选它（退化为前 i-1 份的子问题），要么选它（其余工作只能来自它之前兼容的前缀，收益加上它的 value）。两个分支覆盖全部解，DP 因此成立。
- **二分前驱（predecessor by bisect）**：排序后的 `ends` 数组上，用 `bisect_right` 找"结束时间不晚于当前开始时间的最后位置"，即兼容前缀的长度。它把"找前驱"从 O(n) 扫描降到 O(log n)。
- **Top-k 截断**：合并两行有序和列表时只保留最小的 k 个——排到 k 名之后的前缀不可能进入下一轮前 k，因为至少已有 k 个更小的和能配上相同的后缀。截断是整个"多行合并"可扩展的关键。
- **重数（重复和各占一名）**：`[[1,1],[2,2]]` 的四个组合和全是 3，第 4 名仍是 3。不同选择组合各占一个排名，**不能去重**——去重会把第 k 名算错。
- **强参照（independent reference）**：`reference_unseen_variant` 用指数级子集枚举直接按定义算答案，实现路径与 DP 完全不同。它是"陌生题"语境下的裁判：你自己的推导对不对，由它说了算。
- **约束变化与状态增量**：变体在经典问题上加了两个约束——份数上限 K 和冷却 g。迁移的正确姿势不是另造框架，而是给状态**加一层**（"还能选多少份"）并把前驱条件从 `end<=start` 改成 `end+g<=start`（代码里写作 `start-cooldown`）。
- **失败边界**：每个契约违反时的行为要明确——份数或冷却为负、区间零长度、名次超过组合总数，都要抛 `ValueError` 而不是悄悄给错答案。
- **数据分离**：教学演示数据和测试随机源用不同的随机种子（17501、17599），测试用例不是演示例子的复读。

## 三、解决思路（一步步推导）

- **Step 1（复习线一）：排序并建 DP。** 把工作按结束时间排序得 `(3,1,50),(4,2,10),(5,3,40),(6,3,70)`，`ends=[3,4,5,6]`。`dp[i]` 表示"前 i 份工作（按 end 排序）能取得的最大收益"。
- **Step 2：手算经典版。** i=1（1–3，50）：无兼容前驱，dp[1]=max(不选 0, 选 50)=50。i=2（2–4，10）：前驱位置是"end≤2"的个数=0，dp[2]=max(50, 0+10)=50。i=3（3–5，40）：end≤3 的有 1 个，dp[3]=max(50, dp[1]+40=90)=90。i=4（3–6，70）：end≤3 的有 1 个，dp[4]=max(90, dp[1]+70=120)=**120**。这就是 cell8 第一条断言的 120。
- **Step 3（复习线二）：逐行合并 + 截断。** `sums` 从 `[0]` 出发。第一行 `[1,3,11]`：拿堆把 `{0+1, 0+3, 0+11}` 归并出前 k 个，得 `[1,3,11]`（k=5 时全保留）。第二行 `[2,4,6]`：堆里放 `1+2、3+2、11+2`，每次弹最小、再推"同行下一个元素"的候选。弹的过程：3、5、5、7、7——第 5 个是 7。注意 5 出现两次（1+4 和 3+2），各占一名，这就是重数的意义。
- **Step 4（迁移）：识别变体改了什么。** 与经典版比，变体多了"至多 K 份"和"冷却 g"。不另起炉灶：把 `dp[i]` 升级成 `dp[round][i]`——"恰好用 round 轮选择机会、考虑前 i 份工作的最大收益"，滚动两层即可。
- **Step 5（迁移）：改前驱条件。** 兼容不再是 `end<=start` 而是 `end+cooldown<=start`。手算例子：jobs 按 end 排序为 `(1,3,20),(3,5,25),(4,6,30),(7,8,15)`，`ends=[3,5,6,8]`，g=1。对每份工作 i 算 `predecessors[i]=bisect_right(ends, start-1, hi=i)`：工作 0（start=1）→ 0；工作 1（start=3，找 end≤2）→ 0；工作 2（start=4，找 end≤3）→ 1；工作 3（start=7，找 end≤6）→ 3。得到 `[0,0,1,3]`。
- **Step 6（迁移）：两层 DP 手算。** 第 1 轮（只许选 1 份）：previous 全 0，current 依次为 20、25、30、30（选单份最好的是 30）。第 2 轮（至多 2 份）：i=3 时 current=max(25, previous[1]+30=20+30=**50**)=50；i=4 时 max(50, previous[3]+15=45)=50。最终答案 **50**，与参照枚举一致——cell6 第二张表把 `subset enumeration → 50` 和 `predecessor + K-layer DP → 50` 并排打印，就是这个对拍。
- **Step 7：参照按定义暴力算。** `reference_unseen_variant` 枚举所有大小 ≤limit 的子集、按 start 排序、逐对检查 `a.end+g<=b.start`、收益取最大。指数级，只在小组子上跑。
- **Step 8：把变体退化回经典题验证。** 令 `max_jobs=len(jobs)`、`cooldown=0`，变体就退化成经典带权调度。cell8 的桥接断言拿同一批随机工作同时跑两套实现，确认退化一致——迁移"没走样"由这条保证。
- **Step 9：复盘。** 解释三件事：为什么选/不选分解在加计数层后仍然覆盖全部解；为什么 `start-cooldown` 恰好实现 `end+g<=start`；复杂度从 O(n log n) 变为 O(n log n+nK) 后规模边界在哪（大输入只跑 DP，不跑指数参照）。

## 四、代码逐段讲解

### 1. 经典带权调度 `job_scheduling`

```python
def job_scheduling(start,end,profit):
    if not len(start)==len(end)==len(profit):raise ValueError('Length mismatch')
    jobs=sorted(zip(end,start,profit))
    if any(left>=right for right,left,value in jobs):raise ValueError('Positive job duration required')
    ends=[right for right,left,value in jobs]
    dp=[0]*(len(jobs)+1)
    for i,(right,left,value) in enumerate(jobs,1):
        previous=bisect_right(ends,left,hi=i-1)
        dp[i]=max(dp[i-1],dp[previous]+value)
    return dp[-1]
```

- 先核对三个数组等长；`sorted(zip(end,start,profit))` 把元组按 end 排序（元组比较自动以 end 为主键）；`left>=right` 拒绝零长度或负长度工作。
- `ends` 单独抽出来供二分。`dp[i]` 对应"前 i 份"；`bisect_right(ends,left,hi=i-1)` 在前 i-1 份里数出"结束 ≤ 当前开始"的份数 previous——右界 `hi=i-1` 保证只看已处理的前缀。
- 转移一行就是选/不选：不选当前是 `dp[i-1]`，选当前是 `dp[previous]+value`（前缀最优加当前收益）。空输入时 dp 长度 1，`dp[-1]=0`。

### 2. 第 k 小行和 `kth_smallest_row_sum`

```python
def kth_smallest_row_sum(mat,k):
    if not mat or any(not row for row in mat):raise ValueError('Nonempty rows required')
    if k<1:raise ValueError('Positive rank required')
    combinations_count=1
    for row in mat:
        if any(a>b for a,b in zip(row,row[1:])):raise ValueError('Each row must be sorted')
        combinations_count*=len(row)
    if k>combinations_count:raise ValueError('Rank exceeds the number of choices')
    sums=[0]
    for row in mat:
        heap=[(value+row[0],i,0) for i,value in enumerate(sums)]
        heapq.heapify(heap);merged=[]
        while heap and len(merged)<k:
            value,i,j=heapq.heappop(heap);merged.append(value)
            if j+1<len(row):heapq.heappush(heap,(sums[i]+row[j+1],i,j+1))
        sums=merged
    return sums[k-1]
```

- 前半是契约检查：行非空、k 为正、每行确实有序（逐对比较验证）、k 不超过组合总数（各行长度之积）。最后一条对应 cell8 里 `[[1],[2]]`、k=2 抛错的测试——只有 1 种组合，第 2 名不存在。
- `sums` 维护"已处理各行组合出的前 k 小和"。每来一行，堆里初始放 `(sums[i]+row[0], i, 0)`：以旧和 sums[i] 开头、本行先取第 0 个（行有序所以这是该前缀的最小延伸）。
- 弹出堆顶即当前最小组合和，存入 `merged`；若该前缀在本行还有下一个元素，推入 `sums[i]+row[j+1]` 作为后继候选。`len(merged)<k` 是 Top-k 截断：只归并出最小的 k 个。
- 处理完所有行后 `sums[k-1]` 即答案。重复值（相同和的不同组合）各自入堆、各占一位，重数天然保留。

### 3. 变体的公共预处理 `_variant_jobs`

```python
def _variant_jobs(instance):
    jobs=sorted(instance['jobs'],key=lambda job:(job[1],job[0],job[2]))
    limit=instance['max_jobs'];cooldown=instance['cooldown']
    if limit<0 or cooldown<0 or any(start>=end for start,end,value in jobs):
        raise ValueError('Invalid job limit, cooldown or interval')
    return jobs,min(limit,len(jobs)),cooldown
```

- 按 `(end,start,profit)` 排序——和经典版同构；同时把"份数上限超过工作总数"钳到 `min(limit,len(jobs))`，避免多余轮次。两个实现共享这段预处理，保证对拍口径一致。

### 4. 迁移实现 `solve_unseen_variant`

```python
def solve_unseen_variant(instance):
    """Choose at most K nonoverlapping jobs, with a fixed gap after each selected job."""
    jobs,limit,cooldown=_variant_jobs(instance)
    ends=[end for start,end,value in jobs]
    predecessors=[bisect_right(ends,start-cooldown,hi=i) for i,(start,end,value) in enumerate(jobs)]
    previous=[0]*(len(jobs)+1)
    for _ in range(limit):
        current=[0]*(len(jobs)+1)
        for i,(start,end,value) in enumerate(jobs,1):
            current[i]=max(current[i-1],previous[predecessors[i-1]]+value)
        previous=current
    return previous[-1]
```

- `predecessors[i-1]=bisect_right(ends,start-cooldown,hi=i-1)`：要求前面工作的 `end <= start-cooldown`，即 `end+cooldown <= start`——冷却约束的全部改动就在这一个减法上。
- 外层 `for _ in range(limit)` 是"还能选多少份"这一层：`previous` 是少一轮机会时的 DP，`current` 是多一轮时的 DP。转移 `current[i]=max(current[i-1], previous[predecessors[i-1]]+value)`——本轮"不再选"继承 `current[i-1]`（同层左边，本轮还没用满也行），"选当前"则消耗一次机会、落在上一层的兼容前缀上。
- 滚动数组只用两层 O(n) 空间；`previous` 初始全 0 对应"一份都不选、收益 0"，负收益的工作自然被这个 0 兜底（"至少为 0"的契约）。
- 返回 `previous[-1]`：考虑全部工作、用完至多 limit 次机会的最优值。

### 5. 强参照 `reference_unseen_variant`

```python
def reference_unseen_variant(instance):
    jobs,limit,cooldown=_variant_jobs(instance)
    best=0
    for count in range(limit+1):
        for subset in combinations(jobs,count):
            ordered=sorted(subset,key=lambda job:job[0])
            if all(a[1]+cooldown<=b[0] for a,b in zip(ordered,ordered[1:])):
                best=max(best,sum(job[2] for job in ordered))
    return best
```

- 完全按定义算：枚举 0..limit 份的所有子集、按 start 排序、逐对验证冷却条件 `a[1]+cooldown<=b[0]`、取最大收益；`best=0` 起步对应"可以一份不选"。
- 实现与 DP 无任何共享逻辑（除了预处理），指数级复杂度只配小数据——它是裁判，不是选手。

## 五、为什么是对的？复杂度是多少？（说人话）

**调度为什么对。** 按结束时间排序后，任何一个包含"第 i 份工作"的合法解，它的其余工作必然全部落在第 i 份之前的兼容前缀里（结束不晚于它开始的工作）；而任何解要么包含第 i 份要么不包含。所以 `dp[i]=max(dp[i-1], dp[前缀]+value)` 两分支不重不漏地覆盖全部解。变体加上"至多 K 份"后这个分解原样保留：选当前工作就消耗一次机会、落到"少一次机会"的那一层 DP 上；排序前缀的兼容性判断只被冷却平移了一格（`end<=start` 变 `end<=start-g`）。收益可以为负也没关系：`best=0`/`dp` 初值 0 代表"全不选"，它兜住了下界。

**行和合并为什么对。** 关键在截断的安全性：如果某个旧和 sums[i] 在合并本行后已经排到第 k 名开外，那它配上"本行剩下的任何元素"都救不回来——因为至少有 k 个不大于它的组合和存在，而这 k 个前缀配上本行最小元素的组合仍不大于它配上较大元素的组合。所以只保留前 k 名，第 k 名答案不会丢。重复和不去重是同一论证的一部分：相等的值各占一个名次，去重会少数组合。

**代价。** 经典调度：排序 O(n log n)、每份工作一次二分 O(log n)，时间 O(n log n)、空间 O(n)——四份工作就是几次比较的事。迁移版：预处理 O(n log n) 加上限 K 轮、每轮 O(n) 的 DP，时间 O(n log n+nK)，滚动两层空间 O(n)；测试里 5000 份工作、K=12 也只是 5000×12 次转移，瞬间完成。行和合并：每行一次 O(k log k) 的堆归并，r 行合计 O(rk log k)，工作空间 O(k)——50 列 ×10 行、k=20 的冒烟也就是几百次堆操作。参照枚举是指数级的（组合数爆炸），只允许在十份工作以内的小数据上运行，大输入绝不能碰它。

## 六、测试用例在测什么

cell8 的断言分六组：

1. **经典调度冒烟**：`[1,2,3,3]/[3,4,5,6]/[50,10,40,70]` 得 120（正常值，第三节手算过）；`[],[],[]` 得 0（空输入边界）；`[1,2]/[2,3]/[-1,-2]` 得 0（**特殊值：全负收益**——一份不选是最优，验证"至少为零"的契约）。
2. **行和冒烟**：`[[1,3,11],[2,4,6]]`、k=5 得 7（正常值）；`[[1,1],[2,2]]`、k=4 得 3（**特殊值：全部组合同值**，四个 3 各占一名，专测重数不被去重）。
3. **行和随机对拍**：固定种子 17501 生成 160 组随机矩阵（行数、行长、元素都随机，值域 -3..7），用 `itertools.product` 穷举全部组合取排序后第 k 名当期望；k 取三档——1（最小）、len（最大）、随机中段——分别覆盖两端和中间。
4. **变体对拍（关键）**：另用种子 17599 生成 300 组随机实例（最多 9 份工作、时长 1..4、收益 -4..20、K=0..5、g=0..3），断言 DP 解等于子集枚举参照。负收益、零冷却、K 超过工作数等情形都被随机覆盖。
5. **桥接退化测试**：同一批工作构造成 `max_jobs=len(jobs)、cooldown=0` 的实例，断言 `job_scheduling` 与变体参照一致——证明变体实现退化回经典问题时行为不变，迁移没有引入偏差。
6. **规模与契约**：5000 份工作、K=12、g=1 的大实例答案为 12（每份收益 1，间隔恰好允许全选，但 K 封顶），注释明确"大输入不跑指数参照"；50×10 矩阵 k=20 只冒烟检查非负；最后用 try/except 验证 `kth_smallest_row_sum([[1],[2]],2)` 抛 `ValueError`（组合总数只有 1，第 2 名不存在），漏抛即测试失败。

## 七、练习思路提示

- **练习 1（自编变体作考核）**：自己出一道没在本课程展示过答案的组合变体，比如"带权调度 + 每天至少休息 g + 总时长上限"或"行和第 k 小但每行必选不同列"。流程照抄本章契约：写明输入输出与边界（非法参数抛什么）、先手算一个 4–6 元素的小例子、再同时实现快解和暴力强参照并对拍随机实例。热身可以用本章的 cooldown 变体，但考核必须用自编题。
- **练习 2（改一个条件重新推导）**：从四类条件（在线/加权/重复/规模）里挑一个改动并重推。示例方向：把行和问题改成"在线到达的行"（每行来了立刻合并，不能重排）；把调度改成"每份工作可做多次"（重复选取，前驱条件怎么变）；把 k 改成动态查询（多档 k 一次算）。要求写清新旧复杂度的差距和哪个论证步骤失效了，手算一个最小例子展示失效点，再用暴力参照验证新推导。

## 八、对应 LeetCode 题目

- **42. Trapping Rain Water（comparison）**：迁移方向的对照题——它考察的是在无标签提示下识别"逐位置左右前缀最大值"的结构，练本章"独立分析"的建模起点，本章未给实现。
- **1235. Maximum Profit in Job Scheduling（comparison）**：复习主线一的正式版，`job_scheduling` 是其完整教学实现，练"排序 + 二分前驱 + 选/不选 DP"。
- **1439. Find the Kth Smallest Sum of a Matrix With Sorted Rows（comparison）**：复习主线二的正式版，`kth_smallest_row_sum` 练"逐行堆归并 + Top-k 截断 + 重数保留"。

notebook 结尾照例提醒：这些题号用于知识映射，本章实现遵循教学契约，不要把教学实例当成官方题的完整答案。结业提交的评分记录的是接口正确、证明完整、边界处理、复杂度与迁移解释，不以已刷题数代替能力。
