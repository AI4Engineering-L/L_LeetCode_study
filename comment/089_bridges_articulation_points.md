# N089 · 桥、割点与low-link —— 说人话详解

> 对应 notebook：`notebooks/11_graphs/089_bridges_articulation_points.ipynb`

## 一、这章要解决什么问题？（问题描述）

想象你负责一个网络（道路网、通信网、社交网），老板问两个"怕不怕坏"的问题：

1. **哪条边是"命脉"？** 删掉它，原本连通的网络就会断成两截。这种边叫**桥**（bridge）。
2. **哪个点是"关键人物"？** 删掉这个点（以及它连的所有边），网络就会断开。这种点叫**割点**（articulation point）。

注意"断开"的判定基准：整个图的连通分量个数变多了才算。比如一条链 0-1-2：删掉中间边 1-2，图断成 {0,1} 和 {2}，分量从 1 变 2，所以 1-2 是桥；删掉中间点 1，剩下孤零零的 0 和 2，分量从 1 变 2，所以 1 是割点。

给一个 notebook cell6 的具体例子：4 个点，边 `edges=[(0,1),(1,2),(2,0),(1,3)]`。

- 0、1、2 组成一个三角形，1 还连着 3。
- 删掉边 1-3：3 变成孤点，图断开 → **(1,3) 是桥**，而且是唯一的桥（三角形里删任何一条边都还连通，比如删 0-1 还能走 1-2-0 绕过去）。
- 删掉点 1：3 与 0、2 断联 → **1 是割点**。删掉 0、2、3 中任何一个都不断开。
- 跑 notebook 的代码输出正是：桥 `[(1, 3)]`，割点 `[1]`。

这章的目标就是高效地（一次 DFS）把所有桥和所有割点找出来，而不是一条边一条边、一个点一个点地暴力删了试。

## 二、关键概念（定义）

- **无向图的 DFS 森林**：对无向图做深度优先搜索，走过的边形成树（树边），没走的边都是"回边"——连回自己祖先的边。无向图 DFS 不存在"横边"（连向既非祖先也非后代的点），这是本章算法成立的重要前提。
- **发现时间 disc（discovery time）**：每个点第一次被 DFS 访问到的顺序编号。祖先的 disc 一定比后代小。直觉上 disc 就是"辈分"：编号越小编号越靠上。
- **low-link 值（low）**：low[u] 回答的问题是"u 和 u 的整棵 DFS 子树，沿着树边往下走、至多借一条回边绕，**最早能摸到哪个辈分的祖先**"。low 越小，说明这棵子树和上方的联系越紧密。
- **树边 / 回边**：树边是 DFS 走进去时新开分支的边；回边是遇到"已访问过的点"时没走的边（u 到它的祖先）。low 的更新规则完全围绕这两种边。
- **父边编号 pe（parent edge id）**：u 是经哪条边（的编号）进入 DFS 树的。回到父亲的那条路只有这一条树边，处理"要不要跳过父边"时**必须按边的编号跳过，不能按邻居编号跳过**——因为平行边（重边）时两条边邻居相同但身份不同。
- **桥的判定条件**：对树边 parent→child，如果 `low[child] > disc[parent]`（严格大于），child 的子树完全绕不回 parent 及以上，这条树边是唯一的通道 → 桥。
- **割点的判定条件**：对非根点 p，如果它有某个树孩子 c 满足 `low[c] >= disc[p]`（大于等于），那么 c 的子树最多摸回 p 本人，p 一删子树就孤立 → p 是割点。**DFS 根节点要单独处理**：根没有祖先可摸，判定规则换成"根在 DFS 树里的孩子数 > 1"。
- **为什么桥用严格不等式、割点用非严格？** 桥的问题是"子树能不能绕过这条**边**"——摸回 parent 本人也要经过这条边，所以必须严格大于 disc[parent] 才算断。割点的问题是"子树能不能绕过这个**点**"——摸回 parent 本人也没用（点都删了），所以等于也算断。
- **重边（平行边）/ 自环**：两点间有多条边叫重边；自己连自己叫自环。本实现用边 ID 处理重边，cell4 明确声明支持断开图、平行边和自环。

## 三、解决思路（一步步推导）

- **Step 1**：建带边编号的邻接表：每条边 eid=(u,v) 在 adj[u] 和 adj[v] 里各登记 `(邻居, eid)`。编号是为了之后精确区分"父边"和"平行边"。
- **Step 2**：对每个没访问的点做显式栈 DFS，进点时记 `disc=low=时钟值`。
- **Step 3**：从 u 看邻居 (v, eid)：如果 eid 正是 u 的父边（`eid==pe[u]`），跳过——回到父亲的树边不算绕路。如果 v 没访问过，走树边：记 parent/pe、孩子数加一、入栈。如果 v 已访问（回边），用 `disc[v]` 压低 `low[u]`。
- **Step 4**：u 的邻居耗尽退栈时，把 `low[u]` 回传给父亲：`low[parent]=min(low[parent], low[u])`。同时做两个判定：`low[u] > disc[parent]` → 父边是桥；`low[u] >= disc[parent]` 且 parent 非根 → parent 是割点。
- **Step 5**：根节点退栈时走特殊规则：它在 DFS 树里的孩子数大于 1 才是割点。

**手算演示**（cell6 的图，边编号：e0=(0,1), e1=(1,2), e2=(2,0), e3=(1,3)）：

- 从 0 开始：disc[0]=low[0]=**0**，时钟走到 1。
- 0 走 e0 到 1（pe[1]=e0）：disc[1]=low[1]=**1**。
- 1 看邻居 0（e0）：这正是 pe[1]，跳过。走 e1 到 2（pe[2]=e1）：disc[2]=low[2]=**2**。
- 2 看邻居 1（e1）：是 pe[2]，跳过。看邻居 0（e2）：0 已访问，是**回边** → low[2]=min(2, disc[0]=0)=**0**。
- 2 退栈回传给 1：low[1]=min(1,0)=**0**。判定：low[2]=0 > disc[1]=1？否，e1 不是桥；low[2]=0 >= disc[1]=1？否，1 暂不算割点。
- 1 走 e3 到 3（pe[3]=e3）：disc[3]=low[3]=**3**。
- 3 看邻居 1（e3）：是 pe[3]，跳过。3 退栈回传给 1：low[1]=min(0,3)=0 不变。判定：low[3]=**3 > disc[1]=1** → e3 是**桥**；low[3]=**3 >= disc[1]=1** 且 1 非根 → 1 是**割点**。
- 1 退栈回传给 0：low[0]=min(0,0)=0。判定：low[1]=0 > disc[0]=0？否，e0 不是桥。
- 0 是根，退栈时数 DFS 孩子：children[0]=1（只有 1 这一个树孩子），不大于 1 → 0 不是割点。

最终 disc=[0,1,2,3]、low=[0,0,0,3]（正是 cell6 表格的四行），桥 = [(1,3)]，割点 = [1]。你可以对照着看：3 的 low=3 就是"3 的子树（只有自己）哪也绕不去"的数字化表达。

## 四、代码逐段讲解

### 核心函数：`_undirected_lowlink(n, edges)`

```python
def _undirected_lowlink(n,edges):
    adj=[[] for _ in range(n)]
    for eid,(u,v) in enumerate(edges): adj[u].append((v,eid)); adj[v].append((u,eid))
```

- 建图：`enumerate(edges)` 给每条边一个编号 eid，邻接表里每项存 `(邻居, 边编号)`。无向图两个方向都要登记。存 eid 是为了后面精确跳过父边。

```python
    disc=[-1]*n; low=[0]*n; parent=[-1]*n; pe=[-1]*n; children=[0]*n
    bridges=[]; cuts=set(); clock=0
```

- 一次声明全部状态：disc 初值 -1 表示没访问；parent 是 DFS 树上的父亲；pe 是"进入该点的父边编号"；children[u] 是 u 的 DFS 树孩子计数（只给根用）；bridges 收集桥的边 ID；cuts 是割点集合（用 set 自动去重——一个割点可能被多个孩子判定重复添加）；clock 是发现时间计数器。

```python
    for s in range(n):
        if disc[s]!=-1: continue
        disc[s]=low[s]=clock; clock+=1; stack=[(s,iter(adj[s]))]
```

- 外层循环覆盖不连通图的每个连通块（`if disc[s]!=-1: continue` 跳过已访问起点，这保证支持断开图）。
- 起点记时间，压入显式 DFS 帧（点 + 邻居迭代器，和 N088 同款技术，深图不爆递归）。

```python
        while stack:
            u,it=stack[-1]
            try: v,eid=next(it)
            except StopIteration:
                stack.pop(); p=parent[u]
                if p==-1:
                    if children[u]>1: cuts.add(u)
                else:
                    low[p]=min(low[p],low[u])
                    if low[u]>disc[p]: bridges.append(pe[u])
                    if parent[p]!=-1 and low[u]>=disc[p]: cuts.add(p)
                continue
```

- 弹帧分支（StopIteration = u 的邻居看完了，u 要退栈）：`p=parent[u]` 取父亲。
- `if p==-1`（u 是根）：走**根特例**——根没有祖先，判定割点只看 DFS 树孩子数 `children[u]>1`。为什么不能套非根规则？因为根的孩子之间没有任何祖先可以互连，两个以上树孩子就意味着删根后各孩子子树散伙。
- 非根：先把 low[u] 并入父亲的 low（子树能摸到的地方父亲也算能借道摸到）；然后两个判定——`low[u]>disc[p]`（严格）→ 父边 pe[u] 是桥，append 边 ID；`parent[p]!=-1 and low[u]>=disc[p]`（非严格且 p 非根）→ p 是割点。注意 `parent[p]!=-1` 就是在把根排除在非根规则之外，交给上面的根特例处理。

```python
            if eid==pe[u]: continue
```

- 这一行只有十几个字符，却是**全函数最容易写错的地方**：如果当前边正是 u 进入树时走的那条父边，跳过。必须比边 ID 而不是比"v 是否等于 parent[u]"——重边时 u 和父亲之间可能有第二条边，那第二条边是货真价实的回边（提供了绕路通道），不能被连带跳过。测试里 `find_bridges(2,[(0,1),(0,1)])==[]` 专抓这个 bug：如果按邻居跳过，两条平行边都被当父边跳过，low[1] 停留在 1 > disc[0]=0，(0,1) 会被误报成桥。

```python
            if disc[v]==-1:
                parent[v]=u; pe[v]=eid; children[u]+=1
                disc[v]=low[v]=clock; clock+=1; stack.append((v,iter(adj[v])))
            else: low[u]=min(low[u],disc[v])
    return bridges,cuts,disc,low
```

- v 没访问过：走树边——登记父亲、父边、孩子数加一、记时间、压新帧。
- v 访问过（且回边没被上一行跳过）：u 能借这条回边摸到 v 的辈分，用 **disc[v]**（不是 low[v]）压低 low[u]。用 disc 就够且更标准：回边指向的是一个确定的祖先位置，一次只借一条回边（cell4 说"经至多一条回边"正是这个含义）。
- 返回四元组：桥边 ID 列表、割点集合、disc、low（后两个供 cell6 的表格展示）。

### 封装 1：`find_bridges(n, edges)`

```python
def find_bridges(n,edges):
    ids,_,_,_=_undirected_lowlink(n,edges)
    return sorted(tuple(sorted(edges[i])) for i in ids)
```

- 调核心函数拿桥边 ID（其余三个返回值用 `_` 丢弃），把 ID 翻译回边，每条边内部排序（保证 (1,3) 和 (3,1) 统一成 (1,3)），再整体排序输出。输出规范化是为了测试好比较。

### 封装 2：`articulation_points(n, edges)`

```python
def articulation_points(n,edges):
    return sorted(_undirected_lowlink(n,edges)[1])
```

- 拿割点集合（`[1]` 索引取第二个返回值），排序成列表输出。

## 五、为什么是对的？复杂度是多少？（说人话）

**low 到底在概括什么？** 一句话：low[u] 是"u 的整棵 DFS 子树，往下走树边、中途至多借一条回边，能摸到的最早发现时间"。子树和上层的所有联系，本质上都表现为某条从子树深处指回上方的回边；每条回边能摸到的位置就是它的 disc。孩子退栈时把 low 传上来，父亲取最小值，就等于把整棵子树所有回边的能力汇总了一遍。

**桥的判定为什么用严格大于？** 树边 p→c 是桥，当且仅当删了它 c 的子树和外面彻底失联——也就是 c 的子树**连 p 本人这条线都摸不到**，形式化就是 low[c] > disc[p]（子树最早只能摸到比 p 更晚的点）。如果 low[c] 恰好等于 disc[p]，说明子树有回边直接摸到 p 本人：p 一点没删时确实多一条路，但这条路要经过 p，删**边** p→c 时……等等，删的是边不是点，摸回 p 之后不还是过不了 p→c 这条边吗？注意图是无向的：回边摸到 p 之后，p 还在图里，从 p 可以走任何别的方向离开——所以等于时删边确实不断图，桥必须严格大于。而删**点** p 时连 p 都没了，子树摸到 p 也没处可去——所以割点用大于等于。两者的差别就在"删掉的是边还是点"。

**根为什么要特判？** 非根割点规则的直觉是"孩子的子树摸不回 p 的上方"。但根没有上方，任何孩子的 low 也不可能小于 disc[root]（root 是最早的），非根规则对根永远成立或永远不成立都说明它失效。根真正的风险是"根是几棵 DFS 子树的汇合点"：如果根有两个以上树孩子，这些子树之间不可能有回边互连（有回边的话第二个孩子早在第一个子树里就被访问了），删根必断。所以根的规则就是数树孩子。

**复杂度，用具体数字说：** 整个搜索是 O(V+E)：每点进出各一次，每条边两端各看一次。10⁵ 点、2×10⁵ 边的图约几十万次操作，瞬间完成。空间 O(V+E)（邻接表本身）。输出前的排序另有 O(E log E + V log V) 的上界——10⁵ 条边排序约两百万次比较，依旧很快。加上外层循环覆盖所有连通块、父边按 ID 跳过，实现明确支持断开图、平行边和自环（自环 eid==pe[u] 永远不成立，它作为回边 min 进 low 不影响判定）。

## 六、测试用例在测什么

测试的策略是**随机图 + 暴力定义对拍**：

```python
def components(n,edges,removed=None):
    seen=set(); count=0
    for s in range(n):
        if s==removed or s in seen: continue
        count+=1; stack=[s]; seen.add(s)
        while stack:
            u=stack.pop()
            for a,b in edges:
                if removed in (a,b): continue
                v=b if a==u else a if b==u else None
                if v is not None and v not in seen: seen.add(v); stack.append(v)
    return count
```

- 朴素的"数连通分量"函数：`removed` 可以是一个**点**（跳过该点、跳过与其相连的边）——不传就数原图。`v=b if a==u else a if b==u else None` 这句是在无向边里找 u 的另一端。它是暴力判定的地基。

```python
for _ in range(180):
    n=rng.randrange(1,7); edges=[(rng.randrange(n),rng.randrange(n)) for _ in range(rng.randrange(10))]
    base=components(n,edges)
```

- 种子 89 固定可复现；每轮随机 1–6 个点、0–9 条**完全随机**的边——注意随机边可能产生自环（u==v）和重边，这正好把 cell4 声称支持的退化结构全都覆盖了。base 是原图分量数。

```python
    want=sorted(tuple(sorted(e)) for i,e in enumerate(edges) if components(n,edges[:i]+edges[i+1:])>base)
    assert find_bridges(n,edges)==want
```

- 桥的暴力定义：逐条边删掉（`edges[:i]+edges[i+1:]` 是去掉第 i 条的列表切片拼接），分量数比 base 多的边就是桥。随机 180 张图全部和 `find_bridges` 对齐。

```python
    assert articulation_points(n,edges)==[u for u in range(n) if components(n,edges,u)>base]
```

- 割点的暴力定义：逐个点删掉（`components(n,edges,u)` 排除该点及其邻边），分量数变多的点是割点。同样 180 张图对拍。

```python
assert find_bridges(2,[(0,1),(0,1)])==[]
```

- 重边专项：0 和 1 之间两条平行边，删任何一条都不断开，所以没有桥。这条专抓"父边按邻居而不是按边 ID 跳过"的经典 bug——那种错误实现会把 (0,1) 误报为桥。

```python
assert articulation_points(2,[(0,1)])==[]
```

- 边界：两个点一条边。删掉任何一个点，剩下的孤立点自成 1 个分量，数量没变多，所以谁也不是割点（"删点后剩 1 个点"不算断开）。这防止实现把普通叶子点误判为割点。

最后 `print('N089: 所有本章断言通过')` 供肉眼确认。

## 七、练习思路提示

**练习 1：用删边/删点暴力验证。**
思路方向：其实 cell8 的对拍代码就是这个练习的参考形态——你自己再写一遍独立版本：一个 `count_components`，然后双层循环"删每条边数分量 / 删每个点数分量"，和你手算的桥、割点集合对比。提示：挑一张你自己画的小图（比如 5 个点、6 条边、含一个"8 字形"两个环共享一个点——共享点就是割点的好例子），先把答案人肉推出来，再让两边机器结果对上。边界别忘了试：单点图、两点一边、完全不连通的两块。

**练习 2：把无重边题扩展到多重图并按边 ID 处理。**
思路方向：构造一个"重边改变判定结果"的对照实验。提示：拿单边图 `[(0,1)]`（(0,1) 是桥）和双平行边图 `[(0,1),(0,1)]`（不是桥）并排跑；更进一步的例子是给某个桥补一条平行边，观察它从结果里消失。然后故意把代码里的 `if eid==pe[u]` 改成 `if v==parent[u]`，跑双平行边图，观察 (0,1) 被误报成桥——这让你亲眼看到"按边 ID"四个字的分量。写清楚输入、期望输出、错误实现的输出三方对照。

## 八、对应 LeetCode 题目

- **1192. Critical Connections in a Network（网络中的关键连接，canonical）**：这题就是"找桥"的原始场景（服务器=点、连接=边，critical connections=删掉后断网的边），直接对应本章 `find_bridges`。题目保证无重边，所以这题里甚至不需要边 ID 技巧——但本章实现支持重边，更通用。
- **1568. Minimum Number of Days to Disconnect Island（使陆地分离的最少天数，extension）**：这题是本章知识的延伸应用——网格岛屿删陆地格子使其断开，答案只会是 0、1、2：先用 DFS 建图判连通（0 天的情况），再套割点判定（1 天的情况，对应本章 `articulation_points` 的思路），都不行就必然 2 天（任何形状的连通陆地至多删 2 个角点必断）。
