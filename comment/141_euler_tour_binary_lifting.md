# N141 · Euler序、倍增与树上查询 —— 说人话详解

> 对应 notebook：`notebooks/17_advanced_algorithms/141_euler_tour_binary_lifting.ipynb`

## 一、这章要解决什么问题？（问题描述）

树是一种"n 个点、n−1 条边、任意两点只有一条路径"的结构。拿到一棵树之后，我们经常要反复回答三类问题：

1. 节点 v 的第 k 个祖先是谁？（比如"3 号点往上走 2 步到谁？"）
2. 节点 u 和节点 v 的最近公共祖先（LCA）是谁？（比如"3 号点和 4 号点最靠近的公共祖宗是谁？"）
3. 节点 v 的子树里到底有哪几个点？

如果每次都老老实实顺着父指针一步一步爬，一次查询最坏要走 n 步；查询一多就顶不住了。本章的目标（照抄 cell0）是"把子树查询变成区间、并按二进制跳祖先"：一次 O(n log n) 的预处理之后，每种查询都只要 O(log n)。

给一个具体到数字的例子。notebook cell6 用的是这棵 5 个点的树（边为 0-1、0-2、1-3、1-4）：

```
        0
       / \
      1   2
     / \
    3   4
```

- 输入"求 3 的子树" → 输出 {3}；输入"求 1 的子树" → 输出 {1, 3, 4}。为什么？因为 1 下面挂着 3 和 4，而 2 挂在 0 下面，和 1 无关。
- 输入"LCA(3, 4)" → 输出 1。因为 3 往上是 1、0，4 往上是 1、0，两条链第一次相遇的地方是 1。
- 输入"3 的第 2 个祖先" → 输出 0。因为 3 → 1 → 0，走两步正好到根。

本章做完后，这些答案都不是"爬出来的"，而是"查表查出来的"。

## 二、关键概念（定义）

- **邻接表（adj）**：`adj[u]` 是一个列表，装着 u 的所有邻居。例子里的 `adj=[[1,2],[0,3,4],[0],[1],[1]]` 意思是：0 的邻居是 1、2；1 的邻居是 0、3、4；以此类推。树没有天然的"父子"方向，我们靠指定根（默认 0 号点）来定方向。
- **tin（进入时刻）**：DFS 从根出发，每第一次踏进一个点，就给它编号。先踏进的编号小。它不是 BFS 的层序编号，也不是把每次回边都记下来的完整 Euler walk（这点 cell1 特意强调，别混）。
- **tout（退出时刻）**：一个点的整棵子树都逛完、DFS 即将离开它时，已经发出的编号总数。可以理解为"离开时用了多少个号"。
- **子树 = 连续区间 [tin, tout)**：这是全章最值钱的一句话。一个点的子树里的所有点，它们的 tin 恰好挤满 tin[v] 到 tout[v]−1 这一段，一个外人都没有。于是"子树查询"就变成了"数组上一段连续区间的查询"。
- **倍增（binary lifting）**：与其只存"父亲"一步，不如把"跳 1 步、跳 2 步、跳 4 步、跳 8 步……到达的点"全存成一张表。大跳 = 两个中跳拼接，所以每层表都可以从上一层算出来。
- **up[v][j]**：v 往上跳 2^j 步到达的点；跳出了树就记 −1。比如 up[3][1] 就是 3 的 2 步祖先。
- **depth（深度）**：一个点离根隔了几条边。根的深度是 0。算 LCA 要靠它先把两点"抬到同一层"。
- **二进制分解**：任何 k 都能拆成若干个 2 的幂之和，比如 6 = 4 + 2 = 二进制 110。于是"跳 k 步" = 挑 k 的二进制里是 1 的那几个位，各跳一次 2^bit 步。

## 三、解决思路（一步步推导）

**Step 1：先造 Euler 序。** 我们用显式栈做一遍 DFS（避免 Python 递归太深爆栈）。每个点会被访问两次：第一次"进入"时记 tin，第二次"离开"时记 tout。

**Step 2：手算一遍 Euler 序**（就是 cell6 里那棵树，你可以先自己算，再运行 cell6 对答案）：

- 踏进 0：tin[0]=0，order=[0]
- 踏进 1：tin[1]=1，order=[0,1]
- 踏进 3：tin[3]=2，order=[0,1,3]；3 没有孩子，立刻离开，tout[3]=3
- 踏进 4：tin[4]=3，order=[0,1,3,4]；离开，tout[4]=4
- 1 的子树逛完，离开 1：tout[1]=4
- 踏进 2：tin[2]=4，order=[0,1,3,4,2]；离开，tout[2]=5
- 最后离开 0：tout[0]=5

验证"子树=区间"：1 的子树应该是 {1,3,4}；order[tin[1]:tout[1]] = order[1:4] = [1,3,4]，严丝合缝。cell6 打印的 `DFS进入序 [0, 1, 3, 4, 2]` 和这里完全一致。

**Step 3：由 order 反推父亲和深度。** 按 order 顺序扫每个点 u，对它的邻居 v：谁 tin 更晚谁就是孩子（晚进入的必然在早进入的那个的子树下面或别处，但邻居关系保证是直接孩子），于是 parent[v]=u、depth[v]=depth[u]+1。手算得 parent=[-1,0,0,1,1]、depth=[0,1,1,2,2]。

**Step 4：搭倍增表 up。** 第 0 层就是 parent 表；之后每一层 `up[j][v] = up[j-1][up[j-1][v]]`——先跳 2^(j-1) 步，再跳 2^(j-1) 步，合起来正好 2^j 步。5 个点的树只要算到 2^2=4 步就够（n.bit_length()=3，构造 3 层）：

- up[0] = [-1, 0, 0, 1, 1]（就是父亲）
- up[1] = [-1, -1, -1, 0, 0]（3 和 4 跳 2 步到 0；1、2 跳出树）
- up[2] = [-1, -1, -1, -1, -1]（5 个点的树里没人能往上跳 4 步还留在树内）

**Step 5：查第 k 个祖先。** 例：3 的第 2 个祖先。k=2 的二进制是 10，只有第 1 位是 1，所以只跳一次 up[1][3]=0。答案 0，和我们手爬"3→1→0"一致。

**Step 6：查 LCA。** 口诀是"先对齐、再同跳"。例：LCA(3,4)。两者深度都是 2，本来就齐；然后从大步到小步试：只要"两人各自跳 2^j 步后到达不同的点"就真的跳，否则不跳。这里 up[2] 和 up[1] 层两人跳完都相等（都是 0 或都是 0），不跳；up[0] 层也相等，不跳。最后答案 = up[0][3] = 1。也就是说整个流程把 u、v 精确抬到了"LCA 的下一层"，最后再补一小步上去。cell6 打印的 `LCA(3,4) 1` 对上了。

## 四、代码逐段讲解

### 函数一：`euler_tour(adj, root)` —— 造 tin/tout/order

```python
def euler_tour(adj,root=0):
    n=len(adj)
    if not n: return [],[],[]
    if not 0<=root<n: raise IndexError('invalid root')
    tin=[-1]*n; tout=[-1]*n; order=[]; stack=[(root,-1,False)]
```

前三行是挡输入的：空图直接返回三个空列表；根不在 0..n-1 里就报错。`tin`/`tout` 先全填 −1，−1 顺便兼任"这个点还没访问过"的标记。栈里每个元素是三元组 `(点, 父亲, 是否正在离开)`：False 表示第一次见到，True 表示"我回来收尾了"。

```python
    while stack:
        u,parent,exiting=stack.pop()
        if exiting: tout[u]=len(order); continue
        if tin[u]!=-1: raise ValueError('tree required')
        tin[u]=len(order); order.append(u); stack.append((u,parent,True))
        for v in reversed(adj[u]):
            if v!=parent: stack.append((v,u,False))
```

弹出栈顶：如果是"离开"标记，此刻 order 的长度就是 tout[u]（这正是子树刚逛完的时机）。如果是第一次进入：先检查 tin[u] 是否已经是 −1，不是就说明这个点被进入过两次，输入里有环，报错；然后给 u 发号（tin=当前 order 长度）、把 u 追加进 order、立刻压一个"(u, 离开)"的回调在栈顶。注意回调压在孩子之前，所以孩子的"离开"会先弹出来——顺序才对。压孩子时用 `reversed(adj[u])`，是因为栈是后进先出，倒着压才能让最左的孩子先被访问，保证 DFS 进入序是"从左到右"的。

```python
    if len(order)!=n: raise ValueError('connected tree required')
    return tin,tout,order
```

逛完发现 order 凑不齐 n 个点，说明图不连通（有些点根本到不了），报错。这三个报错就是本章对输入的"教学契约"：必须是一棵连通、无环的树。

### 类二：`BinaryLifting` —— 预处理 + 三种查询

```python
class BinaryLifting:
    def __init__(self,adj,root=0):
        self.tin,self.tout,self.order=euler_tour(adj,root); self.n=len(adj); self.depth=[0]*self.n
        parent=[-1]*self.n
        for u in self.order:
            for v in adj[u]:
                if self.tin[v]>self.tin[u]: parent[v]=u; self.depth[v]=self.depth[u]+1
```

构造函数先跑一遍 euler_tour，然后按 order（父一定先于子出现）扫一遍定出 parent 和 depth。判据是 `tin[v]>tin[u]`：邻居中进入更晚的那个只能是孩子。

```python
        self.up=[parent]
        for _ in range(1,max(1,self.n.bit_length())):
            old=self.up[-1]; self.up.append([-1 if p==-1 else old[p] for p in old])
```

up[0] 就是父亲表；往上叠 `n.bit_length()` 层就够了（n 个点的树最深的链长不超过 n−1，而 2^层数 一定盖过它；n=1 时用 max(1,…) 保底造一层）。新层的每个格子：上一层里父位置已经是 −1 的保持 −1（表示"再跳就出树了"），否则就是"跳两次 2^(j−1)"。

```python
    def get_kth_ancestor(self,v,k):
        if not 0<=v<self.n or k<0: raise ValueError('valid vertex and nonnegative k required')
        if k>self.depth[v]: return -1
        bit=0
        while k:
            if k&1: v=self.up[bit][v]
            bit+=1; k>>=1
        return v
```

两道防线：点号非法或 k 为负直接报错；k 超过 v 的深度说明跳出树了，立刻返回 −1（不去访问越界的层，这是 cell4 特意说明的细节）。之后从 k 的最低位往最高位扫：某一位是 1，就跳一次对应的 2^bit 步。比如 k=6（二进制 110）= 跳 2 步 + 跳 4 步。

```python
    def lca(self,u,v):
        if not 0<=u<self.n or not 0<=v<self.n: raise IndexError('vertex outside tree')
        if self.depth[u]<self.depth[v]: u,v=v,u
        u=self.get_kth_ancestor(u,self.depth[u]-self.depth[v])
        if u==v: return u
        for j in range(len(self.up)-1,-1,-1):
            if self.up[j][u]!=self.up[j][v]: u,v=self.up[j][u],self.up[j][v]
        return self.up[0][u]
```

第一步换位保证 u 是深的那个，然后把 u 抬 `depth[u]-depth[v]` 步，两人同层。如果这时 u==v，说明 v 本来就是 u 的祖先，直接返回。否则从最大步长往下试：只要"两人跳 2^j 后不同"就跳——这个条件保证永远不越过 LCA，两人始终停在 LCA 的正下方（孩子那层）；循环结束再各自上 1 步（up[0]）就是 LCA 本尊。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么子树恰好是 [tin, tout)？** 想象你亲自走这趟 DFS：你一脚踏进 v 的时刻是 tin[v]；在离开 v 之前，你只能、也必然会逛遍 v 的所有子孙（逛别的分支必须先回到 v 再走，因为树上没有别的路）。这期间发出的所有编号都属于 v 的子树，一个外人插不进来；等轮到你离开 v 时，编号正好发到 tout[v]。所以这半开区间里的点集合不多不少就是子树。

**为什么 up 表是对的？** up[0] 存的是"跳 1 步"，这天然正确。如果 up[j−1] 已经正确（存的是"跳 2^(j−1) 步"），那么"跳 2^j 步"就是先跳 2^(j−1) 步到中途点，再从中途点跳 2^(j−1) 步——两次用同一张可信的表，拼起来还是对的。这样一层层推上去，每一层都成立。

**为什么 LCA 不会跳过头？** 我们只在"两人跳完落在不同点"时才跳。LCA 和它的所有祖先，两人跳过去必然是同一个点，这类跳全被禁止了；反过来，LCA 以下（更深的公共点里不是公共祖先的情况不存在，两人只要还在 LCA 下方，位置就不同）允许跳。所以循环结束时两人恰好停在 LCA 的两个孩子位置上（或是同一点），最后补 1 步必然命中且必然是最近的那个公共祖先。

**复杂度，代入数字感受一下：** Euler 序一趟是 O(n)；倍增表有约 log₂n 层、每层 n 个格子，预处理是 O(n log n)；每次祖先/LCA 查询是 O(log n)。设 n = 10⁵：预处理约 10⁵ × 17 ≈ 170 万次填表，一眨眼；单次查询约 17 次查表，做 10⁵ 次查询也才约 170 万次操作。对比朴素做法每次 O(n)=10⁵ 步、10⁵ 次查询就是 10¹⁰ 步（要跑几十分钟），差距就是这么大。

## 六、测试用例在测什么

cell8 的主体是一个循环：对 n=1 到 27，每次随机生成一棵树、随机选一个根，然后拿"暴力真值"逐项对拍：

- `assert lift.get_kth_ancestor(u,k)==(c[k] if k<len(c) else -1)`：先用 `chain(u)` 暴力把 u 到根的整条链爬出来当标准答案，k 在链长内应等于链上第 k 个点；k 超出链长（包括测试特意试的 n+2 这种越界 k）必须是 −1。这测的是"正常值 + 越界值"两件事。
- `assert set(lift.order[lift.tin[u]:lift.tout[u]])==expected`：expected 是暴力枚举出的"以 u 为祖先的所有点"（即 u 的子树）。它验证的就是本章的核心承诺——切片 [tin[u]:tout[u]) 恰好等于子树集合，一条边界都不能差。
- `assert lift.lca(u,v)==next(x for x in chain(v) if x in set(c))`：暴力求 LCA 的方式是"沿 v 到根的链，找到第一个也出现在 u 链上的点"。n 最多 27，但 n=27 时这就是约 27×27×27 ≈ 2 万次暴力比对，随机树 × 多种根把各种形态（链、星、随机）都覆盖了。
- `assert lift.get_kth_ancestor(root,1<<100)==-1`：给一个天文数字的 k（2 的 100 次方）。正确行为是靠"k>深度"这一条提前返回 −1，而不是去访问不存在的表层。这是压力边界测试。
- 最后一段：手工搭一条 1500 个点的纯链（最深的树），断言末端点的第 1499 个祖先是 0 号点。这专门验证大链下 up 表层数够用、显式栈 DFS 也不会递归爆掉。

## 七、练习思路提示

**练习 1（子树更新 + 点查询/子树查询，配 Fenwick）：** 提示：既然子树是连续区间 [tin, tout)，那么"给 v 的整棵子树每个点加 x"就等于"给数组位置 tin[v]..tout[v]-1 这段每个位置加 x"。区间加可以用差分：在 tin[v] 处加 x、在 tout[v] 处减 x，然后前缀和就是单点的真实值——而前缀和正好用树状数组（Fenwick）动态维护。先写清楚：输入是 (v, x) 和查询点 u，输出是 u 当前的值；边界要考虑 u 在/不在 v 子树里两种情况。手算例子不妨就用本章那棵 5 点树。

**练习 2（子树区间 vs 路径区间）：** 提示：子树对应"进入序上的一段连续区间"；但任意两点 u→v 的路径不是一段区间，它是"两条竖链 + 一条横链"。思考方向：如果做"点权放边上"的技巧（每个点的权记到它和父亲之间的边上），路径和可以拆成 depth[u]+depth[v]−2·depth[LCA] 这类式子，用 tin 做下标配 Fenwick 做"单点改、前缀查"。建议先用暴力路径和当对拍标准，写清楚输入输出再动手。

## 八、对应 LeetCode 题目

- **1483. Kth Ancestor of a Tree Node（树的第 K 个祖先）**：这题就是 `get_kth_ancestor(v, k)` 的原题直接落地，练的是 up 表的搭建和二进制分解跳跃。
- **236. Lowest Common Ancestor of a Binary Tree（二叉树的最近公共祖先）**：这题练的是本章 `lca(u, v)` 的"先对齐深度、再从大步到小步同跳"那套流程；题面给的是二叉树，你只需要把它转成邻接表再套本章接口即可。
