# N086 · 最小生成树与割性质 —— 说人话详解

> 对应 notebook：`notebooks/11_graphs/086_minimum_spanning_trees.ipynb`

## 一、这章要解决什么问题？（问题描述）

想象你是一个施工队长，手里有 n 个村庄，要在某些村庄之间修路，要求**任意两个村庄都能互相到达**（连通），并且**修路总成本最低**。每条候选道路有一个造价。你要挑出一组路，使得总造价最小——这就是**最小生成树（MST）**问题。

它和最短路问题很容易混淆，但完全不是一回事：最短路关心的是"从某个出发点到各点分别多近"，而最小生成树关心的是"把所有人连成一片，总花费最少"。MST 甚至不保证从某点到另点走它的路径是最短的（这正是练习 1 要你构造的反例）。

给一个具体到数字的例子（notebook 里反复用的就是这个）：3 个点，边 `(0,1,1),(1,2,2),(0,2,3)`。

- 我们要挑 2 条边（n 个点恰好需要 n-1 条边）把 3 个点连通。
- 候选方案：{0-1, 1-2} 总成本 1+2=3；{0-1, 0-2} 总成本 1+3=4；{1-2, 0-2} 总成本 2+3=5。
- 答案是 **3**，选边 0-1（成本 1）和 1-2（成本 2）。

注意一个细节：0 到 2 的最短距离走这条路是 1+2=3，而直连边 0-2 只要 3——两者相等纯属巧合，一般情形 MST 上的路径完全可以不是最短路径。

另一个必须处理的边界：如果图根本不连通（比如两个村庄群之间没有候选路），那生成树不存在，本章的实现选择**抛出异常报错**，而不是悄悄返回"只连了一半"的成本——悄悄返回会让调用者误以为拿到了正确答案，这比报错危险得多。

## 二、关键概念（定义）

- **生成树（spanning tree）**：从原图里挑出 n-1 条边，把所有 n 个点连通且不成环，这组边构成一棵"覆盖全部顶点的树"。它叫"生成"是因为每个点都被用到。
- **最小生成树（MST）**：所有生成树里总边权最小的那棵。
- **割（cut）**：把顶点集合分成两堆（比如"已连通的一堆"和"还没连进来的一堆"）。"跨割的边"指一端在一堆、另一端在另一堆的边。
- **割性质（cut property，本章正确性的基石）**：对任何一个割，所有跨越这个割的边里**最轻的那条**，一定属于某棵最小生成树。换句话说，贪心地挑跨割最短边不会错。Kruskal 和 Prim 的正确性都从它来。
- **环性质（cycle property）**：与割性质对偶的说法——图中任何一个环上**最重的那条边**一定不属于任何 MST（除非有并列）。直觉是：环上最重的边总有"绕路"的替代方案，可以把它踢掉而不增加成本。
- **DSU（并查集，Disjoint Set Union）**：一个能高效回答"x 和 y 现在在不在同一堆"并支持"把两堆合并"的结构。Kruskal 用它来判断"这条边的两端是不是已经连通了"——已连通再选就会成环，必须跳过。
- **路径压缩**：DSU 的 find 里那句 `self.parent[x]=self.parent[self.parent[x]]`，意思是找祖宗的路上顺手把父亲直接挂到爷爷上，让树越来越扁，查询越来越快。
- **按大小合并（union by size）**：合并两堆时，把小堆挂到大堆底下，避免树越长越高。与路径压缩配合，单次操作几乎是常数时间。
- **图不连通**：无论挑哪些边都无法把所有点连通。此时生成树不存在，本实现抛 `ValueError('graph is disconnected')`。

## 三、解决思路（一步步推导）

### Kruskal（全局贪心：从最便宜的边开始挑）

- **Step 1**：把所有边按权重从小到大排序。
- **Step 2**：从最便宜的边开始逐条考察：用 DSU 判断这条边的两个端点是否已在同一连通块。不在（`union` 返回 True）就选它；在就跳过（选了会成环）。
- **Step 3**：选满 n-1 条边即完工；如果边扫完了还没选满 n-1 条，说明图不连通，报错。

**手算演示**（就是 cell6 表格的数据）：`edges=[(0,1,1),(1,2,2),(0,2,3)]`。

- 排序后顺序：0-1（权1）、1-2（权2）、0-2（权3）。
- 考察 0-1（权1）：0 和 1 不连通，选它。chosen=[(0,1,1)]，total=1。
- 考察 1-2（权2）：1 和 2 不连通，选它。chosen=[(0,1,1),(1,2,2)]，total=3。已经选满 n-1=2 条。
- 考察 0-2（权3）：0 和 2 已经（经由 1）连通，跳过。
- 结果：总成本 3。cell6 的 show_table 表格正是这个选择过程：第一张表列出选择次序 0 → 边 (0,1) 成本 1、次序 1 → 边 (1,2) 成本 2；第二张表给出总成本 3。

### Prim（局部贪心：从一棵小树往外长）

- **Step 1**：维护一个"已在树中"的集合 seen，初始为空；一个堆，里面放"(边权, 目标点, 来源点)"三元组，初始塞入 `(0, 0, -1)`——意思是"进入起点 0 不花钱，没有父亲"。
- **Step 2**：从堆里弹最便宜的跨割边（割 = seen 与其余点）。如果目标点已在 seen 里就丢弃这条（堆里会残留过期边），否则把它纳入树。
- **Step 3**：每纳入一个新点，就把它到所有"还没进树"邻居的边推进堆。
- **Step 4**：seen 收齐 n 个点结束；收不齐就是图不连通，报错。

**手算演示**（同一张图，邻接表 adj 略）：堆初始 [(0,0,-1)]。

- 弹 (0,0,-1)：0 进树，chosen 空（parent=-1 不记边）。
- 0 的邻居边入堆：来自边的 (1,1,0) 和 (3,2,0)。
- 弹 (1,1,0)：1 进树，chosen=[(0,1,1)]，total=1。
- 1 的邻居入堆后，堆里有 (2,2,1) 和 (3,2,0)。
- 弹 (2,2,1)：2 进树，chosen=[(0,1,1),(1,2,2)]，total=3，收齐 3 个点，结束。

两次结果一致：总成本 3。

### min_cost_connect_points（LeetCode 1584：稠密图上的 Prim）

- **Step 1**：题面给的是平面上的点，任意两点之间的代价是**曼哈顿距离** `|x1-x2| + |y1-y2|`。n 个点两两都有边，这是"完全图"，边数约 n²/2，先把所有边显式建出来再跑 Kruskal/堆 Prim 会浪费。
- **Step 2**：所以用数组版 Prim：`best[v]` 记录"还没进树的点 v 到树的最短距离"，初始除起点外全是无穷大。
- **Step 3**：重复 n 次：在未进树的点里挑 `best` 最小的点 u 纳入树，把它付出的 `best[u]` 加进总成本，然后用 u 到各点的曼哈顿距离去更新剩余点的 `best`。
- **Step 4**：返回总成本。

**手算演示**（测试用例的前几步）：points=`[[0,0],[2,2],[3,10],[5,2],[7,0]]`。初始 best=[0,inf,inf,inf,inf]。

- 第 1 轮选点 0。用它更新各点：到 1 是 2+2=4，到 2 是 3+10=13，到 3 是 5+2=7，到 4 是 7+0=7。best=[·,4,13,7,7]。
- 第 2 轮选 best 最小的点 1（4）。总成本累计 4。点 1 到点 2 距离 1+8=9<13，更新；到点 3 距离 3+0=3<7，更新；到点 4 距离 5+2=7，不比 7 小，不更新。best=[·,·,9,3,7]。
- 第 3 轮选点 3（3），累计 7。点 3 到点 2 距离 2+8=10，不比 9 小；到点 4 距离 2+2=4<7，更新。best=[·,·,9,·,4]。
- 第 4 轮选点 4（4），累计 11。点 4 到点 2 距离 4+10=14，不更新。best=[·,·,9,·,·]。
- 第 5 轮选点 2（9），累计 **20**。与断言 `==20` 一致。

## 四、代码逐段讲解

### 类：`DSU`（并查集）

```python
class DSU:
    def __init__(self,n): self.parent=list(range(n)); self.size=[1]*n; self.components=n
```

- 初始化时每个点自成一个集合：`parent=[0,1,...,n-1]`（自己的父亲是自己），每堆大小 1，连通块计数为 n。`components` 这个字段本章虽没直接用，但它随手维护了"当前还剩几堆"，在别的问题里很常用。

```python
    def find(self,x):
        while self.parent[x]!=x:
            self.parent[x]=self.parent[self.parent[x]]; x=self.parent[x]
        return x
```

- find 找 x 所在集合的代表（根）。循环条件 `self.parent[x]!=x` 表示"只要 x 还不是根就继续往上爬"。
- `self.parent[x]=self.parent[self.parent[x]]` 是**路径压缩**：把 x 的父亲直接改成祖父，树每查一次就扁一点。
- 返回根编号，作为这个集合的"身份证"。

```python
    def union(self,a,b):
        a=self.find(a); b=self.find(b)
        if a==b: return False
        if self.size[a]<self.size[b]: a,b=b,a
        self.parent[b]=a; self.size[a]+=self.size[b]; self.components-=1
        return True
```

- 先把 a、b 都替换成各自的根。若根相同说明本来就在一堆，返回 False（这条边会成环）。
- `if self.size[a]<self.size[b]: a,b=b,a` 是**按大小合并**：保证 a 始终是较大的堆，把小堆的根挂到大堆上。
- 更新大堆的大小、堆数减一、返回 True 表示"真的合并了"。Kruskal 只在返回 True 时才收下这条边。

### 函数 1：`kruskal(n, edges)`

```python
def kruskal(n,edges):
    dsu=DSU(n); chosen=[]; total=0
    for u,v,w in sorted(edges,key=lambda e:e[2]):
        if dsu.union(u,v): chosen.append((u,v,w)); total+=w
    if n and len(chosen)!=n-1: raise ValueError('graph is disconnected')
    return total,chosen
```

- 第 2 行准备并查集、已选边列表、总成本。
- 第 3 行 `sorted(edges,key=lambda e:e[2])` 按每条边的第三个元素（权重 w）升序排序。
- 第 4 行：尝试合并两端点；返回 True（确实合并了，即这条边连接了两个不同分量）才把边记入 chosen 并累加成本。返回 False 时什么都不做，相当于跳过成环边。
- 第 5 行是连通性检查：只要 n>0（`if n and ...` 里这个 `n` 就是在挡"空图"这种 0 个点的退化输入，空图不该报错），选出的边数必须恰好 n-1。少于 n-1 说明有点永远连不上，抛 ValueError。这就是"不连通要明确报错"这条契约的落点。
- 第 6 行返回 (总成本, 选中的边列表)。

### 函数 2：`prim(n, adj)`

```python
def prim(n,adj):
    if n==0: return 0,[]
    seen=set(); heap=[(0,0,-1)]; total=0; chosen=[]
```

- `if n==0: return 0,[]` 挡住空图：0 个点成本 0、没有边。
- `heap=[(0,0,-1)]`：初始堆里放"(权重0, 点0, 无父亲)"。堆元素是三元组，Python 的堆按字典序比较，所以权重放第一位，保证每次弹出的是当前最便宜的跨割边。

```python
    while heap and len(seen)<n:
        weight,u,parent=heapq.heappop(heap)
        if u in seen: continue
        seen.add(u); total+=weight
        if parent!=-1: chosen.append((parent,u,weight))
        for v,w in adj[u]:
            if v not in seen: heapq.heappush(heap,(w,v,u))
```

- 循环条件 `heap and len(seen)<n`：堆空了或点收齐了都停。收齐后提前退出是优化，免得继续弹出残留的过期边。
- `if u in seen: continue`：堆里同一点可能有多条候选边，弹出时点可能已经进树了，这条就是过期边，丢弃。
- `if parent!=-1`：起点那条虚拟边（权重 0、无父亲）不算真正的边，不记入 chosen。
- 最后一行把 u 到所有未进树邻居的边压入堆，三元组 `(w,v,u)` 里第三位记下来源 u，将来 v 进树时就知道这条边是从 u 连过来的。

```python
    if len(seen)!=n: raise ValueError('graph is disconnected')
    return total,chosen
```

- 循环结束后 seen 没收齐 n 个点，说明剩下的点根本不可达，同样抛 ValueError——和 Kruskal 的报错行为保持一致。

### 函数 3：`min_cost_connect_points(points)`

```python
def min_cost_connect_points(points):
    n=len(points)
    if not n: return 0
    best=[float('inf')]*n; best[0]=0; used=[False]*n; total=0
```

- `if not n: return 0` 挡空输入（0 个点不需要连接，成本 0）。
- `best[v]` 是未进树点 v 到当前树的最短距离；起点置 0 让它第一轮必然被选中。`used` 标记点是否已进树。

```python
    for _ in range(n):
        u=min((i for i in range(n) if not used[i]),key=lambda i:best[i])
        total+=best[u]; used[u]=True
```

- 一共要做 n 轮，每轮选一个点进树。`min(...)` 在所有未使用的点里挑 `best` 最小的——这句是 O(n) 线性扫描，取代了堆 Prim 里的堆。对完全图来说这是划算的（下面第五节细说）。
- 选中后把它付出的接入成本累加，标记已用。

```python
        for v in range(n):
            if not used[v]: best[v]=min(best[v],abs(points[u][0]-points[v][0])+abs(points[u][1]-points[v][1]))
    return total
```

- 用新点 u 去刷新其余未进树点的 best：候选值是 u、v 两点的曼哈顿距离（横坐标差绝对值 + 纵坐标差绝对值），能变小就更新。这就是"树往外长一步"之后割的变化。
- 循环跑满 n 轮，所有点都进树了，返回总成本。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么贪心是对的（割性质的口语版）？** 我们来证明"跨越任何一个割的最轻边 e 可以安全加入 MST"。用反证：假设某棵最小生成树 T 不含 e。那我们把 e 加进 T，由于 e 跨割而 T 里必有另一条边 f 也跨这个割（否则 T 就不连通了），e 和 f 以及 T 中的路径会构成一个环。此时把环上的 f 换成 e：树依然连通、依然 n-1 条边，而 e 是跨割最轻的，所以 e 不比 f 重，换完总成本不会变大。也就是说，任何 MST 都能通过这种"交换"改造成包含 e 的树——所以贪心选 e 永远不会把我们逼进死角。Kruskal 每一步选的是"跨某个割（已建成分量 vs 其余）的最轻边"，Prim 每一步弹出的也是"树内 vs 树外这个割的最轻边"，两者每一脚都踩在割性质上，所以都对。环性质是同一件事的反面视角：环上最重的边永远可以被绕开，所以不会出现在 MST 里。

**为什么恰好 n-1 条边就停？** n 个点要连通至少 n-1 条边（少一条就断），而 n-1 条边若不成环恰好是一棵树。所以"连通 + 无环"的生成树边数必然是 n-1，这也解释了 Kruskal 里 `len(chosen)!=n-1` 这个连通性检查的依据。

**复杂度，用具体数字说：**

- Kruskal 是 O(E log E)：瓶颈在排序。比如 10⁵ 条边，排序约 10⁵×17 ≈ 2×10⁶ 次比较，一瞬间完成；DSU 部分几乎是线性的。
- 堆版 Prim 是 O(E log E)：每条边进出堆各一次。同样 10⁵ 条边量级时毫无压力。
- `min_cost_connect_points` 的数组版 Prim 是 O(n²)：完全图本来就有约 n²/2 条边，与其花 O(n²) 把边全部显式建出来再排序，不如直接 O(n²) 扫描。n=1000 时约 10⁶ 次操作；空间只要 O(n) 两个数组，避免了显式存 n² 条边的内存开销（n=10⁵ 时存边就要 5×10⁹ 条，根本存不下）。这正是 cell4 说"完全点图的稠密 Prim 避免显式保存全部 O(n²) 边"的意思。

## 六、测试用例在测什么

```python
assert kruskal(1,[])[0]==0
```
边界值：只有 1 个点、没有边。1 个点本来就连通，MST 成本为 0。这条同时确认"n=1 时 `if n and len(chosen)!=n-1` 的检查不会误报"（此时 chosen 为 0 条恰好等于 n-1=0）。

```python
assert kruskal(3,[(0,1,1),(1,2,2),(0,2,3)])[0]==3
```
正常值：本章的招牌 3 点图，验证贪心选边顺序（1、2 两条边，跳过 3）并算出总成本 3，与 cell6 表格互为印证。

```python
assert min_cost_connect_points([[0,0],[2,2],[3,10],[5,2],[7,0]])==20
```
正常值 + 应用题：LeetCode 1584 的官方示例 1，5 个点两两之间按曼哈顿距离连接。我们在第三节逐步手算过，5 轮选择依次付出 0+4+3+4+9=20。

```python
from itertools import combinations
from random import Random
rng=Random(86)
for n in range(2,6):
    for _ in range(12):
        edges=[(u,v,rng.randrange(-2,6)) for u,v in combinations(range(n),2)]
```
随机对拍的准备：种子 86 固定保证可复现；对 2 到 5 个点各生成 12 张**完全图**，边权取 -2 到 5 的随机数——注意这里故意包含负权边，验证实现不依赖"边权非负"的假设（MST 不怕负权，负边只会更优先被选中）。

```python
        adj=[[] for _ in range(n)]
        for u,v,w in edges: adj[u].append((v,w)); adj[v].append((u,w))
```
把同一组边整理成 Prim 需要的邻接表（无向，两个方向都记）。

```python
        ref=float('inf')
        for subset in combinations(edges,n-1):
            reach={0}
            for _ in range(n):
                for u,v,_ in subset:
                    if u in reach or v in reach: reach.update([u,v])
            if len(reach)==n: ref=min(ref,sum(w for _,_,w in subset))
        assert kruskal(n,edges)[0]==prim(n,adj)[0]==ref
```
暴力参考解：枚举所有 n-1 条边的组合，检查它是否连通（从点 0 出发反复扩散 n 轮，看能否覆盖全部点），在所有连通组合里取最小边权和。然后把 Kruskal、Prim 和这个暴力解三者对齐——两个贪心算法和穷举法在几十张随机图上结果全部一致，正确性的信心就非常足了。

最后 `print('N086: 所有本章断言通过')` 供肉眼确认。

## 七、练习思路提示

**练习 1：构造"MST 路径不是最短路径"的反例。**
思路方向：你要找一张图，使得沿着 MST 的边从 A 走到 B，比原图里 A 到 B 的最短路更贵。提示：经典构造是一条"三边小于两边"的链——比如点 0、1、2，边 0-1 权 1、1-2 权 1、0-2 权 1.5（用整数的话 0-1 权 2、1-2 权 2、0-2 权 3）。MST 会选两条便宜边（0-1、1-2），于是 MST 上 0 到 2 的路径成本是 4，但直连边 0-2 只要 3。验证时可以调用本章的 `kruskal` 拿到 chosen 边集，再人工沿边集算路径，说明"生成树 ≠ 最短路径树"。

**练习 2：处理不连通图并明确返回契约。**
思路方向：设计一张明显断成两截的图（比如 4 个点只给 0-1 和 2-3 两条边），调用 `kruskal` 或 `prim`，观察它们抛出的 `ValueError`。提示：写测试时用 `try/except ValueError` 捕获并断言异常消息内容；再对比讨论"抛异常"和"返回部分森林成本 + 分量数"两种契约各自的利弊——前者把问题暴露在调用方，后者需要额外的返回字段说明"其实没连完"。手算示例很简单：n=4、边选了 2 条 < n-1=3 条，必然触发检查。

## 八、对应 LeetCode 题目

- **1584. Min Cost to Connect All Points（连接所有点的最小费用）**：这题练的就是本章 `min_cost_connect_points` 的原始场景——完全图上的稠密 Prim，考点是"不显式建边、用 best 数组 + 线性扫描选点"的 O(n²) 写法。
- **1489. Find Critical and Pseudo-Critical Edges in Minimum Spanning Tree（找出 MST 中的关键边和伪关键边）**：这题是本章的延伸（notebook 标注为 extension），练的是对 MST 结构性质的深度理解——关键边对应"去掉它 MST 总成本必然变大"（本质是割性质），伪关键边对应"存在某棵 MST 含它"。做法通常是反复跑 Kruskal 做对比实验，恰好复用本章接口。
