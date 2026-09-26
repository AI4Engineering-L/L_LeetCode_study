# N114 · 概率与期望DP —— 说人话详解

> 对应 notebook：`notebooks/13_dynamic_programming/114_probability_expectation_dp.ipynb`

## 一、这章要解决什么问题？（问题描述）

前面的 DP 算的是"最少花多少代价""有多少种方案"，这一章算的是带随机性的东西：**概率**（某件事发生的可能性）和**期望**（平均要多少步）。本章三个具体问题：

1. 骑士在 n×n 棋盘的 (row,col) 上，每步等概率（各 1/8）往 8 个方向跳一个"日"字，跳 k 步之后他还留在棋盘上的概率是多少？跳出界就算失败，失败后不能复活。
2. New 21 游戏：从 0 分开始，每次等概率抽 1~max_pts 中的一个数加到分数上，一旦分数 ≥ k 就停手；停手时分数 ≤ n 的概率是多少？
3. 一个小小的随机状态机（马尔可夫链）：每个状态给出"下一步去哪儿、概率多少"，`[]` 表示到了这个状态就永远留下（吸收）。问从每个状态出发，平均要走多少步才被吸收？

**具体到数字的例子：** 3×3 棋盘、骑士在角落 (0,0)、跳 2 步，留在棋盘的概率是 0.0625（= 1/16）。为什么？第 1 步 8 个方向里只有 2 个（(1,2) 和 (2,1)）还在棋盘上，各分到 1/8 的概率；第 2 步从这两个格子出发又各只有 2 个方向留在盘内，所以每条活路只剩 (1/8)×(1/8)=1/64，四条合计 4/64=0.0625。下面的推导会把这 1/16 一轮一轮"撒概率"撒出来。

## 二、关键概念（定义）

- **概率DP / 概率质量（probability mass）：** 我们把"总共 1 的概率"想象成一堆质量，撒在各个状态上。每走一步，每个格子把手里的质量按转移概率（骑士是 1/8）分给邻居。概率 DP 就是模拟这个"撒质量"的过程。
- **全概率公式：** "下一步在某格子"的概率 = 对每个可能的前一格子，"在前一格子"的概率 × 从它过来的比例，全部加起来。代码里那句 `nxt[x][y]+=dp[r][c]/8` 就是一次全概率分解。
- **边界流失（不归一化）：** 跳出棋盘的质量直接丢掉，不再捡回来重新分配。丢掉的总和恰好就是"失败概率"，所以最后把棋盘上所有格子的质量加起来就是"还活着"的概率。千万不要在每步之后把质量重新归一化成 1，那样失败信息就没了。
- **吸收状态（absorbing state）：** 进去就出不来的状态。本章用空列表 `[]` 表示：不需要再转移，期望步数是 0。
- **期望DP / 首步方程：** 期望满足 `E[i] = 1 + Σ p(i,j)·E[j]`——站在 i 平均还要走 1 步（当前这步），再加上"下一步落在 j 的概率 × 从 j 起的平均步数"。这叫首步方程。
- **自循环（self-loop）：** 状态转移到自己的边，比如以 1/2 概率原地不动。有自循环时，状态图不是 DAG（有环），**不能**像普通 DP 那样"递归到更小的子问题"，因为 E[i] 的方程里含 E[i] 自己，要当线性方程解。
- **期望线性性：** 期望可以直接相加（"和的期望等于期望的和"），不需要事件互相独立。这是很多期望题的突破口。
- **闭类与无穷期望：** 如果有正概率走进一组"进去就出不来、又没有吸收态"的状态（比如 2→2 自循环），那么吸收时间期望是无穷大。代码会把这些状态标成 `inf`。
- **Fraction（精确有理数）：** 用分数做运算不会有 0.1+0.2≠0.3 这类浮点误差；最后再转成 float 输出。`isclose`/`1e-12` 是比较浮点数时给的数值容差。

## 三、解决思路（一步步推导）

### 3.1 骑士概率：一轮一轮撒质量

- **Step 1：** 初始 dp[row][col]=1.0，其余全 0——"第 0 步骑士百分之百在起点"。
- **Step 2：** 每一轮新建全 0 的 nxt，把 dp 每个格子的质量除以 8，往 8 个方向各推一份；落点出界的直接丢弃。
- **Step 3：** 推完 k 轮后，把整个棋盘的质量加总，就是"没跳出界"的概率。

**手算 3×3、起点 (0,0)：**

- 第 0 轮：(0,0)=1.0，总质量 1.0。
- 第 1 轮：(0,0) 的 8 个方向只有 (1,2)、(2,1) 在盘内，各得 1/8；总质量 2/8=0.25。
- 第 2 轮：从 (1,2) 出发只有 (2,0)、(0,0) 在盘内，各得 (1/8)/8=1/64；从 (2,1) 出发只有 (0,2)、(0,0) 在盘内，各得 1/64。总质量 4/64=**0.0625**。
- notebook 第 6 格的表格给出前 5 轮：1.0、0.25、0.0625、0.015625（=1/64）、0.00390625（=1/256）——每轮恰好约 1/4 的质量存活。

### 3.2 New 21 游戏：按分数建 DP + 滑动窗口

- **Step 1：** 设 dp[score] = "抽牌过程中分数恰好路过 score（且此时还没停）"的概率。停在 ≥k 的分数不再往下传。
- **Step 2：** 路过 score 的唯一方式是从 score−1, score−2, …, score−max_pts 中的一个抽过来，每个等概率 1/max_pts，所以 dp[score] =（前 max_pts 个可转移分数的概率和）/max_pts。
- **Step 3：** 这个"前 max_pts 项的和"用滑动窗口 window 维护：每算一个新 score 就把它（若 <k）加进窗口，把滑出范围的最老一项减掉，避免每个分数都重新求和。
- **Step 4：** 答案 = 所有满足 k ≤ score ≤ n 的 dp[score] 之和（这些是"停手且不超 n"的终点）。

**手算 n=2, k=2, max_pts=2：** 抽 1 或 2 各半。路线：先抽 1（概率 1/2），再抽 1 或 2，停在 2 或 3；或先抽 2 直接停在 2。所以停在 2 的概率 = 1/2+1/2×1/2 = 3/4，停在 3 的概率 = 1/4；P(≤2)=**0.75**。代码算出来也是 0.75（dp[1]=1/2，window=1.5，dp[2]=1.5/2=0.75）。

### 3.3 期望步数：从"递归"改成"解方程"

- **Step 1：** 对每个非吸收状态写首步方程 E[i] = 1 + Σ p·E[j]；吸收状态 E=0。自循环会让自己出现在自己的方程里。
- **Step 2：** 手算链 `[[(0,1/2),(1,1/2)], []]`：E[1]=0（吸收）；E[0] = 1 + 0.5·E[0] + 0.5·0，移项得 0.5·E[0]=1，所以 E[0]=**2.0**。直觉：每步一半概率"通关"，平均试 2 次。
- **Step 3：** 先做图检查：哪些状态能到达吸收态（安全），哪些能钻进"出不来的非吸收闭环"（期望无穷，标 inf）。
- **Step 4：** 对剩下的有限状态，把方程整理成矩阵，用高斯消元精确求解（全程 Fraction，最后转 float）。

notebook 第 6 格的第二张表就是这个二状态链：状态 0 期望 2.0 步，状态 1（吸收）0.0 步。

## 四、代码逐段讲解

### 4.1 `knight_probability(n, k, row, col)`

```python
def knight_probability(n,k,row,col):
    if n<=0 or not (0<=row<n and 0<=col<n): return 0.0
    dp=[[0.0]*n for _ in range(n)]; dp[row][col]=1.0
    moves=[(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]
    for _ in range(k):
        nxt=[[0.0]*n for _ in range(n)]
        for r in range(n):
            for c in range(n):
                for dr,dc in moves:
                    x,y=r+dr,c+dc
                    if 0<=x<n and 0<=y<n: nxt[x][y]+=dp[r][c]/8
        dp=nxt
    return sum(map(sum,dp))
```

- `if n<=0 or not (0<=row<n and 0<=col<n): return 0.0`：挡住非法输入——棋盘不存在或起点就在界外，概率直接是 0。
- `dp=[[0.0]*n for _ in range(n)]; dp[row][col]=1.0`：初始把全部质量放在起点。用列表推导生成 n 行，避免所有行共享同一个列表的坑。
- `moves=[...]`：骑士 8 个"日"字位移。循环里 `x,y=r+dr,c+dc` 算落点。
- `if 0<=x<n and 0<=y<n: nxt[x][y]+=dp[r][c]/8`：落点在盘内才把 1/8 的质量送过去；出界的质量被这行直接丢掉——这就是"边界流失"。
- `dp=nxt`：一轮结束换表。必须用新表，不能原地改，否则同一轮里后处理的格子会用到本轮刚更新的值。
- `return sum(map(sum,dp))`：`map(sum,dp)` 先把每行求和，外层 sum 再加总，即整个棋盘的质量和。

### 4.2 `new21_game(n, k, max_pts)`

```python
def new21_game(n,k,max_pts):
    if max_pts<=0 or min(n,k)<0: raise ValueError('invalid game parameters')
    if k==0 or n>=k-1+max_pts: return 1.0
    dp=[0.0]*(n+1); dp[0]=1.0; window=1.0; answer=0.0
    for score in range(1,n+1):
        dp[score]=window/max_pts
        if score<k: window+=dp[score]
        else: answer+=dp[score]
        old=score-max_pts
        if 0<=old<k: window-=dp[old]
    return answer
```

- `if max_pts<=0 or min(n,k)<0: raise ValueError(...)`：参数不合法（每次至少要能抽 1 分、n 和 k 不能为负）直接抛异常，不悄悄返回错的数。
- `if k==0 or n>=k-1+max_pts: return 1.0`：两个保证必胜的捷径——k=0 表示一开始就停手（分数 0 ≤ n）；而停手时的分数最多是 (k−1)+max_pts（最后一抽前最多 k−1，一抽最多加 max_pts），所以 n ≥ k−1+max_pts 时必然 ≤ n，概率是 1。
- `dp[score]=window/max_pts`：window 恰好是"能转移到 score 的那些分数的概率和"，除以 max_pts 就是路过 score 的概率。
- `if score<k: window+=dp[score] else: answer+=dp[score]`：分数 <k 才会继续抽（才放进窗口供后面的分数转移）；≥k 就停手，把它累计进答案。
- `old=score-max_pts; if 0<=old<k: window-=dp[old]`：把滑出窗口的最早一项减掉，窗口始终保持"最近 max_pts 个仍在抽牌的分数"。条件带 `<k` 是因为 ≥k 的 dp 值根本没进过窗口。

### 4.3 `expected_steps_small_chain(transitions)`

```python
def expected_steps_small_chain(transitions):
    # Row i contains (next_state, probability); [] is absorbing.
    rows=[[(j,p if isinstance(p,Fraction) else Fraction(str(p))) for j,p in row] for row in transitions]
    n=len(rows); reverse=[[] for _ in rows]
    for i,row in enumerate(rows):
        if row and sum(p for j,p in row)!=1: raise ValueError('nonempty rows must sum exactly to one')
        for j,p in row:
            if not 0<=j<n or p<0: raise ValueError('invalid transition')
            if p>0: reverse[j].append(i)
    def ancestors(seeds):
        seen=set(seeds); q=deque(seen)
        while q:
            for u in reverse[q.popleft()]:
                if u not in seen: seen.add(u); q.append(u)
        return seen
    absorbing={i for i,row in enumerate(rows) if not row}
    can_absorb=ancestors(absorbing)
    infinite=ancestors(set(range(n))-can_absorb)
    finite=[i for i in range(n) if i not in absorbing and i not in infinite]; index={v:i for i,v in enumerate(finite)}
    m=len(finite); a=[[Fraction(0) for _ in range(m+1)] for _ in range(m)]
    for r,u in enumerate(finite):
        a[r][r]=1; a[r][-1]=1
        for v,p in rows[u]:
            if v in index: a[r][index[v]]-=p
    for c in range(m):
        pivot=next(r for r in range(c,m) if a[r][c])
        a[c],a[pivot]=a[pivot],a[c]; divisor=a[c][c]; a[c]=[x/divisor for x in a[c]]
        for r in range(m):
            if r!=c:
                factor=a[r][c]; a[r]=[x-factor*y for x,y in zip(a[r],a[c])]
    answer=[float('inf') if i in infinite else 0.0 for i in range(n)]
    for u,r in index.items(): answer[u]=float(a[r][-1])
    return answer
```

- `rows=[[(j, p if isinstance(p,Fraction) else Fraction(str(p))) ...]`：把所有概率统一转成 Fraction。注意走 `str(p)` 这一步——直接 `Fraction(0.1)` 会得到一个超长的二进制近似分数，而 `Fraction(str(0.1))` 得到的正是 1/10。
- 校验循环：非空行的概率必须**精确**加起来等于 1（有 Fraction 才敢这么严格）；转移目标必须在范围内、概率不能为负；非法就抛 ValueError。
- `reverse[j].append(i)`：建反向邻接表，"谁能一步走到 j"。
- `ancestors(seeds)`：从 seeds 出发沿反向边 BFS，找出"能走到 seeds 里任一状态"的所有状态。
- `absorbing`：行是空的那些状态（[] 即吸收）。
- `can_absorb=ancestors(absorbing)`：能到达吸收态的状态集合（含吸收态自身）。
- `infinite=ancestors(set(range(n))-can_absorb)`：能走到"永远到不了吸收态"的状态的人——他们有正概率陷入不吸收的闭环，期望步数是无穷大。
- `finite=[...]`：剩下的是"非吸收、又保证最终被吸收"的瞬态状态，`index` 给它们重新编号 0..m−1。
- 建方程：对每个有限状态 u，首步方程 E[u] = 1 + Σ p·E[v]。写成矩阵行：`a[r][r]=1`（自己的系数）、`a[r][-1]=1`（右端常数 1）、`a[r][index[v]]-=p`（把每个有限后继的 p 移到左边变减号）。吸收态后继的 E 是 0，不用写。
- 消元循环：标准的 Gauss-Jordan——`next(r for r in range(c,m) if a[r][c])` 找这一列第一个非零行当主元，交换、除以主元把它变成 1，再把其他所有行的这一列消成 0。全 Fraction 运算，零舍入误差。
- 收尾：无穷状态给 `float('inf')`，吸收态给 0.0，有限状态取增广矩阵最后一列 `a[r][-1]` 转 float。

## 五、为什么是对的？复杂度是多少？（说人话）

**骑士为什么对：** 每一轮的更新就是一次全概率公式——"这一步在 (x,y) 的概率"等于"上一步在每个前驱的概率 × 各占 1/8"之和。跳出去的质量被丢弃而不是重新分配，所以任何时候棋盘上的总质量 = "至今没跳出去"的概率，最后一步的总和就是答案。

**New21 为什么对：** 停手条件保证了"还在抽牌"的分数都 <k，所以窗口里只放进 <k 的 dp 值；每个终点分数恰好被它的所有可能来源（前 max_pts 个分数）贡献一次，滑窗加减不重不丢。`n>=k-1+max_pts` 那个短路是把"最大可能终点"论证直接变成了代码。

**小链为什么对：** 期望无穷的判定依据是——只要你有正概率进入一个出不来又没有吸收态的状态集合，就存在一条"永远不停"的路线，平均步数自然是无穷。把安全状态筛掉后，剩下的方程组里每个未知数的方程都只含有限值，而且这个方程组有唯一解，高斯消元解出来的一定是正确期望。全程用分数算，最后才转浮点，所以测试能用 `abs_tol=1e-12` 这么苛刻的容差。

**复杂度（拿具体数字感受）：** 骑士是 O(k·n²)：n=8、k=100 时，每轮 64 个格子 × 8 个方向 = 512 次加法，100 轮共约 5 万次操作，一瞬间算完；空间 O(n²) 存两张表。New21 是 O(n)：n=10⁴ 时一万个分数各算一次，滑窗让每步 O(1)。小链：图检查（BFS）是 O(V+E)；高斯消元 O(V³) 次有理数运算、O(V²) 空间——V=50 时约 12.5 万次有理数乘加，本机毫秒级；但要注意分数的分子分母会变长，位数增长带来的额外开销（notebook 说的"位复杂度另计"）在 V 很大时会显现。

## 六、测试用例在测什么

```python
assert knight_probability(3,2,0,0)==0.0625
assert knight_probability(3,0,0,0)==1.0
assert expected_steps_small_chain([[(0,Fraction(1,2)),(1,Fraction(1,2))],[]])==[2.0,0.0]
assert expected_steps_small_chain([[(1,1)],[(2,1)],[]])==[2.0,1.0,0.0]
a=expected_steps_small_chain([[(1,0.5),(2,0.5)],[],[(2,1)]])
assert isinf(a[0]) and a[1]==0 and isinf(a[2])
...
```

（省略号处是 notebook 里 New21 的三重循环精确对拍与骑士值域检查，下面逐条讲。）

- `knight_probability(3,2,0,0)==0.0625`：正常值抽查，对应第三节手算的 1/16，验证两轮撒质量与丢边界都正确。
- `knight_probability(3,0,0,0)==1.0`：边界 k=0——一步不动，必然还在棋盘上。
- 第 3 条：带自循环的二状态链，期望 [2.0, 0.0]，对应手解方程 E[0]=1+0.5E[0]，专测"有环不能当 DAG 递归"。
- 第 4 条 `[(1,1)],[(2,1)],[]`：无环纯链 0→1→2，期望 [2,1,0]——E[2]=0、E[1]=1、E[0]=2，测的是普通链上方程依然成立。
- 第 5 条 `a=...`：状态 2 自循环（2→2 概率 1）构成"不吸收的闭环"——E[2] 应为无穷，能走到 2 的状态 0 也无穷，吸收态 1 为 0。用 `isinf` 分别检查，专测无穷检测。
- New21 三重循环（k=0..6、max_pts=1..5、n=0..11，共 420 组）：用记忆化递归 `exact`（全程 Fraction 精确算）当真值，对每组断言浮点结果落在 [−1e-12, 1+1e-12] 且与精确值之差不超过 1e-12——这是"数值容差"概念的落地。
- 最后 `for k in range(5): assert 0<=knight_probability(4,k,1,1)<=1`：4×4 棋盘中心出发，任何步数的概率都必须在 [0,1] 之间，是最基本的合理性检查。

## 七、练习思路提示

- **练习 1（概率之和 vs 期望之和）：** 提示——期望天生可加（线性性，不要求独立），概率直接相加往往会重复计算重叠的事件。建议构造一个小例子：某试验中事件 A、B 各以 0.5 概率发生，比较"E[A 发生次数 + B 发生次数]"（=0.5+0.5=1）和"P(A 或 B 发生)"（≤1，取决于是否独立、是否互斥）。再回到骑士题：把"第 t 步仍在盘上"的概率记 p_t，想一想 Σp_t 代表什么（提示：期望意义下"总共在盘上度过的步数"）。写清输入输出和边界后，用本章接口或暴力模拟验证。
- **练习 2（含自循环的期望方程）：** 提示——先老老实实写首步方程 E[i]=1+Σp·E[j]，发现 E[i] 出现在等式右边时不要慌，把它当未知数移项解出来；比如 E=1+0.5·E 直接解得 E=2。多个状态互相环引用时就是小线性方程组，可以手算消元，也可以交给 `expected_steps_small_chain` 对拍。注意写清边界：吸收态 E=0；判无穷的条件是什么。

## 八、对应 LeetCode 题目

- **688. Knight Probability in Chessboard**：这就是 `knight_probability` 的原题——练"逐轮撒概率质量 + 边界流失不归一化"的前向概率 DP。
- **837. New 21 Game**：这就是 `new21_game` 的原题——练"按分数建状态 + 滑动窗口把 O(n·max_pts) 压成 O(n)"，外加两个必胜短路边界。
- **808. Soup Servings（extension）**：这题是本章方法的迁移扩展——同样是概率 DP，但状态是二维剩余量、用记忆化递归而非逐轮迭代，且要靠"分配比例期望对称"把无穷过程截断成有限状态。
