# N145 · 高级DP优化及其成立条件 —— 说人话详解

> 对应 notebook：`notebooks/17_advanced_algorithms/145_advanced_dp_optimization_conditions.ipynb`

## 一、这章要解决什么问题？（问题描述）

分段问题是这样的模型：把数组 a 切成 k 段，每段付一笔代价 cost(段)，让总代价最小。它的标准 DP 是 `dp[g][r] = min over l (dp[g-1][l] + cost[l][r])`——"前 r 个元素分成 g 段，最后一段从 l 切出来"。这个转移天然是三重循环（g × r × l），即 O(kn²)。n、k 一大（比如各 2000~4000，这是这类题的常见量级）就是百亿级操作，跑不动。

本章学两招"有条件的提速"，重点在**有条件**三个字：

1. **分治优化**：如果代价函数满足一个叫 Monge 的不等式，那么"最优切点 l"会随 r 单调不减，于是每个 r 不用再扫全部 l——用分治把总扫描量降到 O(n log n) 一层。
2. **Li Chao 树（李超线段树）**：另一类转移 `dp[i] = min over j (dp[j] + b[j]*a[i])` 可以看成"在一堆直线 y = b[j]·x + dp[j] 里查询 x = a[i] 处的最小值"。Li Chao 树每次插入/查询只要 O(log C)，而且**不要求**斜率有序、也不要求查询点有序。

给一个具体到数字的例子（cell6 第一张表）：`a=[1,2,3,4,2]`，代价取"段和的平方"，即 cost[l][r]=(a[l]+…+a[r−1])²。切成 2 段时最优是 [1,2,3] 和 [4,2]（段和 6、6，代价 36+36=72）；切成 4 段时最优是 [1]、[2,3]、[4]、[2]（代价 1+25+0+4=30？不对——再试 [1]、[2]、[3,4]、[2] 得 1+4+1+4=10）。所以 k=4 的答案是 10。有意思的是 k=5（全切开）反而要 1+4+9+16+4=34——段数更多不保证更便宜，这就是"平方代价"问题的非平凡之处。

## 二、关键概念（定义）

- **分段 DP（partition DP）**：状态 `dp[g][r]` = 前 r 个元素分成 g 段的最小总代价；转移枚举最后一段的左端点 l。本章统一用半开区间语义：`cost[l][r]` 是 a[l..r−1] 这段的代价。
- **Monge 条件 / 四边形不等式（QI）**：对所有 l<l+1、r<r+1 的"相邻四边形"，要求 `cost[l][r] + cost[l+1][r+1] ≤ cost[l][r+1] + cost[l+1][r]`。直觉读法："两段交叉切的代价和，不小于不交叉切的代价和"——代价函数"越对齐越便宜"。
- **决策单调（decision monotonicity）**：Monge 条件的回报。定义 opt(r) = 使 dp[g][r] 取到最小的**最左** l，则 opt(r) 随 r 增大不减小。这样 r 从左到右时，切点窗口只右移不左移。
- **分治优化（divide & conquer optimization）**：利用决策单调性的套路——先算区间中点 mid 的最优切点 split，那么左半段的切点必然 ≤ split、右半段的切点必然 ≥ split，递归下去每层总扫描量 O(n)。
- **凸包优化（CHT，Convex Hull Trick）**：把 `dp[j] + b[j]*a[i]` 看成直线 y = b[j]·x + dp[j]（斜率 b[j]，截距 dp[j]）在 x = a[i] 处取值；dp[i] 就是所有直线在这一点下的最小值，即"下包络"的高度。经典 CHT 要求斜率单调、查询单调；本章用 Li Chao 树去掉这些要求。
- **Li Chao 树**：建立在整数区间 [left, right] 上的线段树，每个节点存一条直线。插入新线时在中点比较，把"中点更优的"留在节点，另一条往它还可能获胜的一侧下沉；查询时沿根到叶一路取各节点直线在 x 处的最小值。两条直线至多交一次，所以"输家中要么全输、要么只在某一侧翻盘"。
- **Knuth 优化**：另一种区间 DP 的优化（opt[i][j−1] ≤ opt[i][j] ≤ opt[i+1][j] 那套夹逼）。cell4 特意声明：它需要不同的递推结构和不同的成立条件，**不能**由本章的 Monge 检查自动推出——练习 1 就是让你体会这一点。
- **整数比较**：Li Chao 全程用整数乘法和比较，不算浮点交点——cell8 里 10^30 量级的测试就是冲着这个来的，浮点在那里早就失真了。

## 三、解决思路（一步步推导）

**Step 1：先把 O(kn²) 参照写对。** `partition_dp_quadratic` 就是三重循环直译。用 cell6 的数据手算 k=2：prev（g=1 层）是 prev[0]=0，prev[l]=cost[0][l]（一段全覆盖前 l 个）。dp[5] = min over l∈{1,2,3,4} 的 prev[l]+cost[l][5] = min(1+121, 9+81, 36+36, 100+4) = min(122, 90, 72, 104) = **72**。逐项对应切法：[1]|[2,3,4,2]、[1,2]|[3,4,2]、[1,2,3]|[4,2]、[1,2,3,4]|[2]。

**Step 2：验证 Monge 条件，过了才许用分治。** 对"非负数组的段和平方"这个代价，cell4 给了漂亮的一笔画证明：令 A=a[l]（左外一格）、B=中段和、C=a[r]（右外一格），代入四边形不等式两边，差恰好化简为 −2·A·C。数组非负时 A·C≥0，所以差 ≤ 0，条件成立。这也立刻告诉我们反例长什么样：数组里有负数（比如 a=[1,1,−2]，A=1、C=−2 时差为 +4>0），Monge 破产——cell8 正是用它测报错分支。

**Step 3：分治怎么省？** 关键事实（Monge 的回报）：算 g 层时，若 r1 < r2，则 opt(r1) ≤ opt(r2)。于是先算**区间中点** mid 的 dp[mid]：在允许窗口 [opt_left, opt_right] 里扫一遍拿到 mid 的最优切点 split；接着左半 r∈[left, mid−1] 的窗口收缩为 [opt_left, split]，右半 r∈[mid+1, right] 收缩为 [split, opt_right]，递归。每层所有窗口拼起来总长 O(n)，一层 log n 深度，一层 g 就 O(n log n)。

**Step 4：Li Chao 手算**，用 cell6 第二张表。三条线：A: y=2x+3、B: y=−x+8、C: y=2x+1，整数域 [−4,6]。先看真相（下包络）：C 比 A 处处低 2，所以 A 永不当选；C 和 B 的交点在 x=2.33 附近——x≤2 时 C 赢（x=2: C=5 < B=6），x≥3 时 B 赢（x=3: B=5 < C=7）。所以查询结果应为：x=−4..2 时是 C 的值（−7,−5,−3,−1,1,3,5），x=3..6 时是 B 的值（5,4,3,2）。树不需要知道交点在哪：每个节点在中点存"更优者"，输家往可能翻盘的一侧下沉，查询沿路径取 min 就自动得出这个包络。

**Step 5：把 DP 接到 Li Chao 上。** `dp[i] = min_j (dp[j] + b[j]*a[i])` 里，每个 j 贡献一条直线 y = b[j]·x + dp[j]，x 就是 a[i]。按 i 递增：先用树查询出 dp[i]，再把第 i 条线（斜率 b[i]、截距 dp[i]）插进树供后面用。b[j]、a[i] 都可以乱序、有正有负——这正是选 Li Chao 而不是经典单调 CHT 的原因。

## 四、代码逐段讲解

### 前置：`_cost_size(cost)`

```python
def _cost_size(cost):
    n=len(cost)-1
    if n<0 or any(len(row)!=n+1 for row in cost): raise ValueError('cost must be an (n+1)x(n+1) matrix')
    return n
```

cost 必须是 (n+1)×(n+1) 方阵（下标 0..n），形状不对立即报错。返回 n。

### 函数一：`partition_dp_quadratic(cost, k)` —— O(kn²) 参照

```python
    if k<0: raise ValueError('nonnegative segment count required')
    if k>n: return float('inf')
    prev=[0]+[float('inf')]*n
    for groups in range(1,k+1):
        dp=[float('inf')]*(n+1)
        for r in range(groups,n+1): dp[r]=min(prev[l]+cost[l][r] for l in range(groups-1,r))
        prev=dp
    return prev[n]
```

k 为负报错；k>n（段数超过元素数）直接判不可行返回 inf。prev 是"上一组数"的 DP 行：0 个元素分 0 段代价 0，其余 inf。内层两个细节：r 从 groups 起步（r 个元素至少要 r ≥ groups 才分得出 groups 个非空段）；l 的范围是 `range(groups-1,r)`——l 至少是 groups−1（前 l 个元素要够分给前 groups−1 段），至多 r−1（最后一段 a[l..r−1] 非空）。滚动两行数组省内存。

### 前置：`_check_monge(cost)` —— 用之前先验货

```python
    for l in range(n):
        for r in range(l+1,n+1):
            x=cost[l][r]
            if x!=x or x in (float('inf'),float('-inf')): raise ValueError('finite segment costs required for this check')
```

先检查三角域（l<r）上所有代价是有限数——`x!=x` 是抓 NaN 的惯用写法（NaN 不等于自己）。出现 inf/NaN 时后续比较不可靠，直接拒绝。

```python
    for l in range(n-1):
        for r in range(l+2,n):
            if cost[l][r]+cost[l+1][r+1]>cost[l][r+1]+cost[l+1][r]: raise ValueError('Monge inequality failed; use the quadratic reference')
```

只查**相邻**的四边形（l 与 l+1、r 与 r+1）。cell4 解释了为什么够：相邻不等式可以像望远镜一样逐项相加，拼出任意更大的矩形不等式，所以小的全过、大的必过。一旦违反就报错并明确告诉你"退回用平方参照"。

### 函数二：`divide_conquer_dp(cost, k)` —— 分治优化

```python
def divide_conquer_dp(cost,k,*,check=True):
    ...
    if check: _check_monge(cost)
    prev=[0]+[float('inf')]*n
```

`check=True` 是默认打开的安全门：先跑 Monge 校验。`check=False` 只允许用在"你已独立证明代价满足条件"的场合——cell4 明说不能拿它绕过失败的测试。

```python
        def compute(left,right,opt_left,opt_right):
            if left>right: return
            mid=(left+right)//2; best=float('inf'); split=opt_left
            for l in range(opt_left,min(mid-1,opt_right)+1):
                value=prev[l]+cost[l][mid]
                if value<best: best=value; split=l
            dp[mid]=best
            compute(left,mid-1,opt_left,split); compute(mid+1,right,split,opt_right)
        compute(groups,n,groups-1,n-1); prev=dp
```

`compute` 负责 [left,right] 里所有 r 的 dp 值，且这些 r 的最优切点被夹在 [opt_left, opt_right] 内（初始窗口 [groups−1, n−1]，和平方版的 l 范围一致）。先算 mid：在窗口内扫（`min(mid-1,opt_right)` 把上界同时夹在"段非空"和窗口右端之内），记下最左最优切点 split。然后左半窗口变 [opt_left, split]、右半变 [split, opt_right]——两侧都允许 split，因为切点只是"单调不减"而不是严格递增。`best<value` 用严格小于号，保证 split 是**最左**最优（这正是单调性声明针对的对象）。

### 类三：`LiChaoMin` —— 整数域李超树

```python
class _LineNode:
    def __init__(self,line): self.line=line; self.left=self.right=None

def _evaluate(line,x): return line[0]*x+line[1]
```

直线用 (斜率, 截距) 二元组表示，求值就是一行整数乘加。

```python
    def add_line(self,slope,intercept):
        def insert(node,l,r,line):
            if node is None: return _LineNode(line)
            mid=(l+r)//2
            if _evaluate(line,mid)<_evaluate(node.line,mid): line,node.line=node.line,line
            if l==r: return node
            if _evaluate(line,l)<_evaluate(node.line,l): node.left=insert(node.left,l,mid,line)
            elif _evaluate(line,r)<_evaluate(node.line,r): node.right=insert(node.right,mid+1,r,line)
            return node
        self.root=insert(self.root,self.left,self.right,(slope,intercept))
```

插入的套路：走到节点 [l,r]，先在中点比一场，把"中点更优"的留在节点、输家放进变量 line 继续处理（那行三元交换 `line,node.line=node.line,line` 就是 Python 的换位写法）。叶子节点（l==r）到此为止。否则判断输家还有没有翻盘机会：它在左端点 l 处更好，说明两条线的交点在左半段，输家只可能在左侧赢 → 递归插入左孩子；在右端点 r 处更好就进右孩子；两头都不赢就彻底淘汰。全程只做整数比较，没有算交点坐标。

```python
    def query(self,x):
        if not self.left<=x<=self.right: raise ValueError('query outside fixed integer domain')
        node=self.root; l,r=self.left,self.right; answer=float('inf')
        while node:
            answer=min(answer,_evaluate(node.line,x)); mid=(l+r)//2
            if l==r: break
            if x<=mid: node=node.left; r=mid
            else: node=node.right; l=mid+1
        return answer
```

查询 x 越界直接报错（树只对建树时声明的整数域负责）。然后沿 x 的搜索路径从根走到叶，**沿途每个节点的直线都参与取 min**。为什么不能只看叶子？因为某条对 x 最优的线可能在中点比较时输给了别人、被下沉到路径之外，但它一定还"驻留"在路径上的某个祖先节点里；沿路全取 min 就把它捞回来了。

### 函数四：`cht_dp_reference(a, b)` 与 `cht_dp_li_chao(a, b)`

```python
def cht_dp_reference(a,b):
    if len(a)!=len(b): raise ValueError('equal lengths required')
    if not a: return []
    dp=[0]
    for i in range(1,len(a)): dp.append(min(dp[j]+b[j]*a[i] for j in range(i)))
    return dp
```

O(n²) 暴力参照：dp[0]=0，dp[i] 枚举所有 j<i。返回整条 dp 数组（不只是末项），方便逐位对拍。

```python
def cht_dp_li_chao(a,b):
    if len(a)!=len(b): raise ValueError('equal lengths required')
    if not a: return []
    tree=LiChaoMin(min(a),max(a)); tree.add_line(b[0],0); dp=[0]
    for i in range(1,len(a)): dp.append(tree.query(a[i])); tree.add_line(b[i],dp[-1])
    return dp
```

整数域取 [min(a), max(a)]（所有查询点都在其中）。第 0 条线是 y=b[0]·x+0（截距是 dp[0]=0）。每个 i：先查询得 dp[i]，再插入斜率 b[i]、截距 dp[i] 的新线。注意 b[j] 可正可负、a[i] 乱序，两种"无序"在经典 CHT 里都要重排序或分情况，在 Li Chao 里天然不是问题。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么 Monge ⇒ 决策单调？** 一句话版：Monge 不等式说的是"代价结构上，交叉的切法不占优"。把它和上一层的 dp[g−1][l] 加在一起后（cell4 说"加上每行 dp 后仍成立"，因为 dp 那一行对两边是同加同减的），可以推出：若 r1<r2 而 opt(r2)<opt(r1)（切点倒退了），把这两组配对做一次"交叉换切点"，总代价不会变大还可能变小——与 opt 都是最优矛盾。所以切点只能右移。更细的一层：本章声明的是"**最左**最优切点单调"，代码里严格小于号保证拿到的是最左那个，两个声明才严丝合缝。

**为什么查相邻四边形就够？** 把一串相邻不等式的左右两边分别加起来，中间项像望远镜一样两两抵消，剩下的就是跨越更大范围的不等式。所以小的全成立蕴含大的全成立，校验只需扫相邻对。

**为什么 Li Chao 的下沉规则不丢线？** 两条直线至多有一个交点。中点比输的线，如果连左端点都比不过，那它在整个左半段都不会赢（线性函数无弯折，端点输则沿途输）；如果左端点赢了，交点必在左半段，它就只在左半有戏——递归进左孩子就完事。右端同理。所以每条线要么被淘汰得心服口服，要么被送到它唯一可能赢的那半边；查询沿路径取 min，恰好覆盖所有"可能赢的驻留点"。

**复杂度，代入数字感受一下：** 平方参照 O(kn²)：n=k=2000 时约 2000×400 万 = 80 亿次——太慢。分治部分 O(kn log n)：同样规模约 2000×2000×11 ≈ 4400 万次内层比较，一两秒。**但** cell4 特别提醒两笔隐藏账：默认的 Monge 校验本身就是 O(n²)（2000² = 400 万，还行），而且你总得先把 cost 矩阵算出来，那也是 O(n²) 时间和内存——分治优化省的是转移的循环，不是建 cost 的账；真要更快得用"边分治边算 cost"的进阶写法。Li Chao 每次插入/查询 O(log C)，C 是整数域宽度：a[i] 在 ±10⁹ 内时 log C≈31，n=10⁵ 个元素也就几百万次树操作，毫秒级。

## 六、测试用例在测什么

- 主对拍段一：n 从 1 到 15、每个 n 随机 8 组非负数组（值域 0..5），k 从 1 到 n 逐一断言 `divide_conquer_dp == partition_dp_quadratic`。非负数组的平方段和已被证明满足 Monge，所以这两条路必须处处一致。这是"优化版 = 参照版"的随机等价测试。
- 主对拍段二：n 从 1 到 7，用 `itertools.combinations` 枚举全部 C(n−1, k−1) 种切法的代价当真值，验证平方参照本身没写错。这是给"参照"上保险——参照错了对拍就全白搭。
- `try: divide_conquer_dp(squared_cost([1,1,-2]),2) except ValueError: pass else: raise`：含负数的数组会违反 Monge（−2·1·(−2)=4>0），分治版必须**报错**而不是给一个静默的错误答案。这条测的就是"有条件的定理"的守门机制。注意写法：没抛异常反而算失败。
- Li Chao 增量穷检：70 轮，每轮随机一条线（斜率 −20..20、截距 −100..100）插入树，插完立刻对整数域 [−30,30] 的**每一个** x 断言 `tree.query(x)==min(所有已插线在 x 的值)`。每插一条查全 61 个点，穷尽而不抽样。
- CHT 对拍：70 轮，长 14 的随机 a（−20..20）、b（−6..6），断言 Li Chao 版 dp 数组与 O(n²) 参照逐位相等。b 有正有负，正好覆盖"斜率不单调"这一经典 CHT 的痛点。
- 大整数测试：`[10**30, -10**30, 10**30+1]` 配 `[10**30, 10**30, -2]`，断言两版仍相等。若 Li Chao 里混入任何浮点运算（比如算交点用除法），10^30 量级的精度早崩了——这条测试守的是"全程整数比较"这条实现纪律。

## 七、练习思路提示

**练习 1（Knuth 只属于二路合并模型）：** 提示：Knuth 优化的递推是区间型的（dp[i][j] 由 dp[i][m]、dp[m+1][j] 合并而来），其夹逼条件 opt[i][j−1] ≤ opt[i][j] ≤ opt[i+1][j] 依赖"二叉合并"的结构。拿石头合并 K=2 验证它能用；再想 LeetCode 1000（每次合并恰好 K 堆）：合并步把区间切成 K 段而不是 2 段，最优中点的夹逼论证在哪一步断掉了？给出一个 K=3 的小反例（比如 5~7 堆手算）说明 Knuth 的窗口假设不成立，从而证明"不推广任意 K"。

**练习 2（找不满足 Monge 的反例）：** 提示：从"平方段和"的证明式 −2·A·C 入手——只要让某个 a[l]·a[r] < 0（一正一负）就可能翻转不等号。可以先用 `_check_monge` 当探测器，随机生成含负数的小数组（长 3~5）直到它报错；然后**手算**那个四边形：写出 cost[l][r]+cost[l+1][r+1] 与 cost[l][r+1]+cost[l+1][r] 的四个具体数，展示左Strictly大于右。最后解释为什么此时决策单调性也可能失效（构造一个 opt 倒退的 k、n 小例子直接枚举 opt(r) 给师兄看）。

## 八、对应 LeetCode 题目

- **1478. Allocate Mailboxes（安排邮筒）**：把房屋排序后"一组房屋配一个邮筒"的代价是到中位数的距离平方和，这个代价满足四边形不等式——练的正是本章"平方型代价 + 分治优化/Monge 检查"的主线。
- **1000. Minimum Cost to Merge Stones（合并石头的最低成本）**：区间 DP + K 路合并，是"Knuth/四边形优化不能无脑推广"的活教材——练的是先验证条件、再决定用不用优化（对应练习 1）。
- **2463. Minimum Total Distance Traveled（移动机器人到工厂的最小总距离）**：排序后机器人与工厂的匹配代价同样满足"交叉不优"的结构，可用本章的分治/决策单调思想或排序+DP 解决——练的是把"越对齐越便宜"的直觉迁移到新题面。
