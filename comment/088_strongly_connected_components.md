# N088 · 强连通分量与缩点 —— 说人话详解

> 对应 notebook：`notebooks/11_graphs/088_strongly_connected_components.ipynb`

## 一、这章要解决什么问题？（问题描述）

在有向图里，"我从 A 能走到 B"不代表"B 能走回 A"。**强连通分量（SCC）**研究的是：哪些点彼此都能互相到达？把每个这样的"互相到达的小团体"压缩成一个超级点之后，整个图会发生神奇的变化——所有环都消失了，变成一张有向无环图（DAG）。这个压缩操作叫**缩点**，它是处理"带环有向图"的万能第一步：环内的问题先在分量内部解决，分量之间的问题在 DAG 上解决（DAG 可以按拓扑序处理，无比好算）。

给一个具体到数字的例子（notebook cell6 用的）：6 个点，邻接表 `adj=[[1],[2,3],[0],[4],[3],[]]`，也就是边 0→1、1→2、1→3、2→0、3→4、4→3。

- 0→1→2→0 构成一个圈，这三点互相可达，是一个 SCC：{0,1,2}。
- 3→4→3 也互相可达，是另一个 SCC：{3,4}。
- 1→3 有边，但从 3、4 出发回不到 0、1、2，所以两个 SCC 不合并。
- 5 谁也到不了（除自己），自成一个 SCC：{5}。

跑 `tarjan_scc(adj)` 得到每个点的分量标签 `[1,1,1,0,0,2]`，再跑 `condensation_graph` 得到缩点图 `[[], [0], []]`——分量 1 有一条边指向分量 0，其余分量没有出边。你看，原来带环的 6 点图压缩成了 3 个超级点的 DAG，这就是本章要达成的效果。

## 二、关键概念（定义）

- **强连通分量（SCC，Strongly Connected Component）**：一组点，组内任意两点互相可达，而且不能再扩大（"最大"的这种集合）。单独一个点如果到不了任何别的点再回来，自己就是一个分量。
- **相互可达（reach 双向）**：i 能走到 j 且 j 能走回 i。"i 和 j 同属一个 SCC"就是"i、j 相互可达"，这是测试里暴力判定的定义式。
- **完成时间（finish time）**：DFS 中一个点"所有后代都探索完毕、即将退栈"的时刻。Kosaraju 靠它排序。
- **反图（reverse graph）**：把每条边 u→v 掉头成 v→u 得到的图。能走到的地方不变，只是方向全反。
- **Kosaraju 算法**：两遍 DFS 的 SCC 算法。第一遍在原图上按完成时间排序；第二遍在反图上按完成时间**从晚到早**做 DFS，每次 DFS 捡起来的恰好是一个分量。
- **Tarjan 算法（lowlink 版）**：一遍 DFS 的 SCC 算法。一边 DFS 一边用 `disc`（发现时间）和 `low`（能绕回去的最早祖先）判断"从哪弹出分量"。
- **disc / low**：disc[u] 是 u 第一次被访问的编号（时钟计数）；low[u] 是从 u 出发、沿着 DFS 树往下走再沿回边/横边绕，**还能回到的活动点里最早的编号**。当 low[u]==disc[u] 时，u 自己就是它所在分量的"根"。
- **活动栈（active stack）与栈内标记 on**：Tarjan 维护一个栈，存"已访问但还没归属任何分量"的点；`on[v]` 标记 v 是否还在栈里。**关键规则：只有仍在栈里的点才允许用来压低 low**——不在栈里的点属于已完工的分量，那是一个"过去的世界"，从它绕不回当前分量（这是练习 2 的主题，也是最容易写错的地方）。
- **缩点（condensation）**：把每个 SCC 换成一个超级点，分量之间的原有边换成超级点之间的边（去重）。缩出来的图一定是 DAG。
- **显式 DFS 帧**：用 `stack=[(u, iter(adj[u]))]` 这种手工栈模拟递归，每帧存"当前点 + 它邻居的迭代器"。好处是 1500 层深的链也不会爆 Python 的递归上限（测试里真放了这么一条链）。

## 三、解决思路（一步步推导）

### Kosaraju：两遍 DFS

- **Step 1**：对原图做 DFS（用显式帧），把每个点**完成**（所有邻居探索完）的顺序记录在 order 里。
- **Step 2**：把所有边反向，得到反图 rev。
- **Step 3**：按 order **从后往前**逐点检查：还没归属的点 s 就从它出发在反图上做一次 DFS，这次 DFS 捡到的所有点构成一个分量，打上同一个标签。
- **直觉**：完成最晚的点一定属于它分量的"源头"；在反图上从源头出发只能灌满"能回到源头的点"，恰好就是这个分量。

**手算演示**（就用 cell6 的图，6 个点）：

- 第一遍 DFS 求 order：从 0 出发，0→1→2（2 的邻居 0 已访问，2 完成）、1 再试 3→4（4 的邻居 3 已访问，4 完成；3 完成）、1 完成、0 完成；最后 5 单独完成。order=[2,4,3,1,0,5]。
- 反过来看的顺序：5,0,1,4,3,2。
- 反图边：1→0 变 0←1（rev[0]=[2]，来自 2→0），rev[1]=[0]（来自 0→1），rev[2]=[1]（来自 1→2），rev[3]=[1,4]（来自 1→3 和 4→3），rev[4]=[3]（来自 3→4）。
- 第二遍：先 s=5，在反图上只能到它自己 → 分量 0 = {5}。再 s=0：反图上 0←2←1 一路灌过去 → 分量 1 = {0,1,2}（rev[1]=[0] 已标记，停止）。再 s=4：4←3 → 分量 2 = {3,4}。
- Kosaraju 的标签是 [1,1,1,2,2,0]——和 Tarjan 的 [1,1,1,0,0,2] 标签不同，但**分组完全相同**。这正是 cell4 说"分量编号只是标签，不比较具体编号"的原因，测试也只比较"谁和谁同组"。

### Tarjan：一遍 DFS + lowlink + 活动栈

- **Step 1**：给每个点记 disc（首次访问时间）和 low（初始等于 disc），压入活动栈。
- **Step 2**：DFS 每走到树边 u→v（v 是新点），就给 v 记时间入栈；v 完成时用 `low[v]` 去压低 `low[u]`。
- **Step 3**：遇到"邻居 v 已访问且 v 还在活动栈里"（回边或指向栈内的横边），用 `disc[v]` 压低 `low[u]`。**如果 v 已访问但已不在栈里，什么都不做**——它属于已完工的分量，绕不过去。
- **Step 4**：一个点 u 完成时检查 `low[u]==disc[u]`：相等说明 u 绕不回任何更早的祖先，u 就是分量的根，从活动栈顶一路弹出直到 u，弹出的这批点是一个 SCC。

**手算演示**（同图，时钟从 0 开始）：

- 访问 0：disc[0]=low[0]=0，栈 [0]。沿树边到 1：disc[1]=low[1]=1，栈 [0,1]。到 2：disc[2]=low[2]=2，栈 [0,1,2]。
- 2 看邻居 0：0 已访问且**在栈里**，是回边 → low[2]=min(2, disc[0]=0)=**0**。2 完成，回传：low[1]=min(1,0)=0。
- 1 再走树边到 3：disc[3]=low[3]=3，栈 [0,1,2,3]。3→4：disc[4]=low[4]=4，栈 [0,1,2,3,4]。
- 4 看邻居 3：在栈里 → low[4]=min(4,3)=3。4 完成，low[4]=3 ≠ disc[4]=4，不弹。回传 low[3]=min(3,3)=3。
- 3 完成：low[3]=3==disc[3]=3，是根！从栈顶弹出 4、3（栈里 3 之上恰好是 4），它们组成分量 {3,4}，标签 0。栈剩 [0,1,2]。
- 1 完成：low[1]=0 ≠ disc[1]=1，不弹，回传 low[0]=min(0,0)=0。
- 0 完成：low[0]=0==disc[0]=0，是根！弹出 2、1、0 → 分量 {0,1,2}，标签 1。
- 最后 5 单独访问：disc[5]=low[5]=5，无邻居，立刻自成分量，标签 2。
- 得 comp=[1,1,1,0,0,2]，与 cell6 表格一致：顶点 0/1/2 → 分量 1，顶点 3/4 → 分量 0，顶点 5 → 分量 2。

### 缩点

- **Step 1**：对每条原图边 u→v，看两端分量：同分量就丢掉（内部边），不同分量就在缩点图里连 component[u]→component[v]，用 set 去重（两点间可能有多条平行边）。
- **Step 2**：把每个 set 排序后输出，方便查看。例子缩出来是 `[[], [0], []]`：分量 1（即 {0,1,2}）有出边到分量 0（即 {3,4}），其余无出边。

## 四、代码逐段讲解

### 函数 1：`kosaraju_scc(adj)`

```python
def kosaraju_scc(adj):
    n=len(adj); seen=set(); order=[]
    for s in range(n):
        if s in seen: continue
        seen.add(s); stack=[(s,iter(adj[s]))]
        while stack:
            u,it=stack[-1]
            try: v=next(it)
            except StopIteration: order.append(u); stack.pop(); continue
            if v not in seen: seen.add(v); stack.append((v,iter(adj[v])))
```

- 这段是**第一遍 DFS**：外层循环保证不连通的每个部分都被扫到（`if s in seen: continue` 跳过已访问起点）。
- `stack=[(s,iter(adj[s]))]` 是显式 DFS 帧：每帧存"点 + 它邻居的迭代器"。迭代器记住"我这个点探索到第几个邻居了"，等价于递归 DFS 的现场。
- `try: v=next(it)` 取下一个邻居；`except StopIteration` 表示邻居耗尽，这个点**完成**了：记入 order（完成顺序）并弹帧。`continue` 回到 while 取上一帧。
- 注意 order 记录的是**完成时间顺序**（先完成的在前），不是访问顺序——这是 Kosaraju 的命门。

```python
    rev=[[] for _ in range(n)]
    for u,a in enumerate(adj):
        for v in a: rev[v].append(u)
```

- 三行建反图：原图边 u→v 在反图里变成 rev[v] 里多了个 u。

```python
    component=[-1]*n; label=0
    for s in reversed(order):
        if component[s]!=-1: continue
        component[s]=label; stack=[s]
        while stack:
            for v in rev[stack.pop()]:
                if component[v]==-1: component[v]=label; stack.append(v)
        label+=1
    return component
```

- 第二遍：`reversed(order)` 按完成时间从晚到早取起点；已归属的跳过。
- 从 s 出发在**反图**上做普通栈式 DFS，把灌到的所有未归属点打上当前 label。
- 每次外层循环 label 加一，返回"每个点属于哪个分量"的标签表。

### 函数 2：`tarjan_scc(adj)`

```python
def tarjan_scc(adj):
    n=len(adj); disc=[-1]*n; low=[0]*n; active=[]; on=[False]*n; comp=[-1]*n; clock=label=0
```

- 一行准备全部状态：disc 初始 -1（没访问过）；low 先随便填 0（访问时会重写）；active 是活动栈；on[v] 标记 v 是否在活动栈里；comp 存每个点的分量标签；clock 是时间戳计数器，label 是分量计数器——`clock=label=0` 是链式赋值，两个都设 0。

```python
    for s in range(n):
        if disc[s]!=-1: continue
        disc[s]=low[s]=clock; clock+=1; active.append(s); on[s]=True
        frames=[(s,iter(adj[s]),-1)]
```

- 外层照例覆盖所有连通部分。新起点 s：记时间、low 同值、入活动栈、压一帧（第三个元素 -1 表示"这个点没有父亲"，是树根）。

```python
        while frames:
            u,it,parent=frames[-1]
            try: v=next(it)
            except StopIteration:
                frames.pop()
                if parent!=-1: low[parent]=min(low[parent],low[u])
                if low[u]==disc[u]:
                    while True:
                        v=active.pop(); on[v]=False; comp[v]=label
                        if v==u: break
                    label+=1
                continue
```

- 帧结构比 Kosaraju 多一个 parent：u 完成后要知道把 low[u] 回传给谁。
- StopIteration 分支 = "u 的邻居耗尽、u 完成"：先弹帧；`if parent!=-1` 把 low[u] 并进父亲的 low（根没有父亲，跳过）；然后是**判定**：若 low[u]==disc[u]，u 绕不回更早的点了，是分量根——从 active 栈顶一直弹到 u 自己（`if v==u: break`），这批点全打上当前 label，label 加一。弹出的点要置 `on[v]=False`（它们离开活动栈，从此不能再用于压低别人的 low）。

```python
            if disc[v]==-1:
                disc[v]=low[v]=clock; clock+=1; active.append(v); on[v]=True
                frames.append((v,iter(adj[v]),u))
            elif on[v]: low[u]=min(low[u],disc[v])
    return comp
```

- 邻居 v 没访问过（disc==-1）：走树边——记时间、入活动栈、压新帧（父亲是 u）。
- `elif on[v]`：v 访问过且**还在活动栈里**——这是回边或栈内横边，用 disc[v] 压低 low[u]。
- 隐含的第三种情况（访问过且不在栈里）什么都不做，这就是"已完工分量的点不参与回传"那条铁律的代码体现。返回 comp 标签表。

### 函数 3：`condensation_graph(adj, component)`

```python
def condensation_graph(adj,component):
    result=[set() for _ in range(max(component,default=-1)+1)]
    for u,a in enumerate(adj):
        for v in a:
            if component[u]!=component[v]: result[component[u]].add(component[v])
    return [sorted(a) for a in result]
```

- 第 2 行按分量个数建结果表，每个槽是一个 **set**（自动去重：两个分量之间哪怕有 10 条平行边也只留一条）。`max(component,default=-1)+1` 里的 default=-1 是挡"空图"——component 为空列表时 max 会抛错，给了默认值就算出 0 个分量，返回空表。
- 中间三行：扫每条原图边，两端同分量（内部边）直接丢；跨分量才在缩点图里记录一条边。
- 最后一行把每个 set 排序成列表输出，纯粹为了展示结果稳定可读。

## 五、为什么是对的？复杂度是多少？（说人话）

**Tarjan 为什么在 low[u]==disc[u] 时弹栈是对的？** 此刻活动栈里 u 的上方有哪些点？都是"进了 u 的子树、还没归属"的点。它们显然能沿 DFS 树走到 u（都在 u 的探索过程中），所以"它们到 u"没问题；而它们没能在 u 完成前弹栈，说明它们各自的 low 都没低过 disc[u]——也就是说它们都绕不回比 u 更早的点，既然能回到 u 且 u 能沿树到达它们，它们和 u 互相可达，恰好构成一个分量。反过来说，如果栈里 u 上方有个点 x 真的绕回了更早的祖先，那 low 就会一路回传把 low[u] 压到 disc[u] 以下，判定条件不成立，u 不弹——两头都严丝合缝。

**为什么"不在栈里的点不能压低 low"？** 一个点离开活动栈，只有一种原因：它所属的分量已经整体弹出完工了。这个分量整体位于 DFS 里"更早完工"的部分，从它那里没有任何边能回到当前正在探索的分量（否则当时两者就该是同一个分量，能互相到达就该一起弹）。所以拿一个已完工的点来压 low，等于声称"我能绕回到过去的世界"，这是幻觉。误用会导致 low 被错误压低、分量被错误合并——这正是练习 2 要你论证的失效条件。

**Kosaraju 为什么对？** 直觉版：完成时间最晚的点一定在它分量的"最深处"；在反图上从它出发能走到的点，恰好是原图上"能走回它"的点，也就是同分量伙伴。跨分量的点即使第一步能碰到，也走不进"完整的回路"，灌不满。严格证明要分量的"完成时间最大点"归纳，这里记住直觉就够用。

**缩点图为什么一定是 DAG？** 用反证：假如缩点后有环，环上的每个分量都能沿这条环到达彼此，那它们本来就该合并成同一个分量——和"分量是极大的互相可达集合"矛盾。所以缩点图不可能有环。测试里那段 `walk` 递归正是暴力验证无环：沿着缩点图走，一旦重访路径上的点（`assert u not in path`）就说明有环，立刻失败。

**复杂度，用具体数字说：** Kosaraju 和 Tarjan 都是 O(V+E)：每个点、每条边只被常数次触碰。一张 10⁵ 点、2×10⁵ 边的图，也就几十万次基本操作，一瞬间完成。空间上 Kosaraju 要多存一张反图（O(V+E)），Tarjan 不用反图但多了 low/on/active 等数组（O(V)）。缩点本身 O(V+E)（set 去重平均常数），最后每条保留边的排序再加一点排序开销。测试里那条 1500 个点的长链专门验证显式帧不爆递归栈——递归版 DFS 在默认递归上限（1000）下会直接 RecursionError，而显式帧把"栈"放在堆内存里，多深都不怕。

## 六、测试用例在测什么

```python
for bits in product(range(2),repeat=9):
    adj=[[v for v in range(3) if bits[u*3+v]] for u in range(3)]
```
穷举所有 2⁹=512 张 3 点有向图（每对 (u,v) 的连边位独立取 0/1），保证覆盖各种刁钻结构：空图、完全图、自环（bits 里 u==v 的三位）都有。

```python
    reach=[[i==j or j in adj[i] for j in range(3)] for i in range(3)]
    for k in range(3):
        for i in range(3):
            for j in range(3): reach[i][j]|=reach[i][k] and reach[k][j]
```
暴力传递闭包（Floyd 式三重循环）：reach[i][j] 表示 i 能走到 j。这是"相互可达"判定的基准真值。

```python
    a=kosaraju_scc(adj); b=tarjan_scc(adj)
    for i in range(3):
        for j in range(3): assert (a[i]==a[j])==(b[i]==b[j])==(reach[i][j] and reach[j][i])
```
核心对齐：对每对点 (i,j)，"Kosaraju 同组"、"Tarjan 同组"、"暴力判定相互可达"三者必须完全一致。注意比的是 `a[i]==a[j]` 这种**同组关系**而不是具体编号——两个算法的编号方案本来就不同（第三节手算已经展示过），比编号就错了。

```python
    dag=condensation_graph(adj,b)
    def walk(u,path):
        assert u not in path
        for v in dag[u]: walk(v,path|{u})
    for u in range(len(dag)): walk(u,set())
```
验证缩点图无环：从每个分量出发做一次不回头路径检查，路径上出现重复点即断言失败。这直接测了"缩点图必为 DAG"这条性质。

```python
chain=[[i+1] for i in range(1499)]+[[]]
assert len(set(tarjan_scc(chain)))==1500
```
压力边界：一条 1500 个点的长链（0→1→2→…→1499），每个点自成一个分量（谁也回不去），分量数应为 1500。这条专测显式 DFS 帧——递归实现会在这条链上爆栈。

```python
assert tarjan_scc([])==kosaraju_scc([])==[]
```
空图边界：0 个点应该返回空列表，不抛异常。

最后 `print('N088: 所有本章断言通过')` 供肉眼确认。

## 七、练习思路提示

**练习 1：用"反向拓扑"的思路对照 LeetCode 802（找最终安全状态）。**
思路方向：802 的定义是"从某点出发最终会走进一个终点（没有出边的点）的点是安全的"，等价说法是"永远不走进任何环"。提示：先跑本章 SCC，把图缩点；缩点图是 DAG，按**出度为 0 往回**的顺序处理（或建反图做拓扑），所有"分量是单点且无自环"的分量逐步标记安全。你也可以手算一个含环的小例子（比如 0→1→2→1、2→3）：哪些点陷进环里不安全、哪些能逃出去。用 `tarjan_scc` + `condensation_graph` 两个接口就能拼出来。

**练习 2：解释"不在栈内的点不能用于压低 Tarjan 的回边值"。**
思路方向：构造一张"完成 Tarjan 之后又有横边指向旧分量"的图。提示：经典形状是一条链分叉再汇合——比如 0→1、1→2、2→3、1→3，再加 3→2 让 {2,3} 成环先完工，之后探索别的分支时遇到指向 3 的边。分别手算"用 disc[v] 更新"与"用 0（不更新）"两种规则下的 low 值，展示错误规则会把两个无关分量黏成一个，导致 `low[u]==disc[u]` 的判定永远不触发。验收时讲清楚因果：离开活动栈 = 分量已完工 = 没有边能回到当前分量。

## 八、对应 LeetCode 题目

- **802. Find Eventual Safe States（最终安全状态，extension）**：这题练的是"SCC + 缩点 + 在 DAG 上按拓扑序倒推"的完整流水线——环上的点全不安全，能走到环的点也不安全，缩点之后从出度为 0 的分量反向标记即可。它对应本章练习 1，是强连通分量最典型的应用题。

（本章 notebook 只列了这一道题；SCC 的知识还能迁移到"2-SAT 判定"等更高级的专题，那属于后续章节的内容。）
