# N174 · Hard 图树、离线与查询综合 —— 说人话详解

> 对应 notebook：`notebooks/21_mastery/174_hard_graph_tree_capstone.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章是图树方向的综合 capstone，方法论主线是：**把"树上路径、动态候选、状态搜索"三个已知机制组合成一个算法，并且每个机制都要守住自己的前提**。具体来说有两个载体问题：

- **祖先最大异或查询（LC 1938）**：树用 `parents` 数组给出（`parents[i]` 是 i 的父节点，根为 -1）。每次查询给 `(node, val)`，要你在 node 的所有祖先（含自己）里找一个 a，使 `a XOR val` 最大。关键认识：查询需要的只是**当前 DFS 路径**（根到 node 的链），不是整棵树。具体例子：`parents=[-1,0,1,1]`（0 是根，1 是 0 的孩子，2、3 是 1 的孩子），查询 `[[0,2],[3,2],[2,5]]` 的答案是 `[2,3,7]`。以第三个查询为例：节点 2 的祖先是 2、1、0，`2^5=7`、`1^5=4`、`0^5=5`，最大是 7。逐条查询问全树会很慢（每次都爬一遍链），本章用"DFS 进退事件 + 计数 Trie"把所有查询在合适的时机顺便答掉。
- **访问全部节点的最短路径（LC 847）**：给无向图，求经过所有顶点的最短走法（可以重复经过点和边）。关键认识：状态必须是 `(当前位置, 已访问掩码)` 二元组——**同一个位置带着不同的访问历史，是两个不同的状态**。具体例子：星形图 `[[1,2,3],[0],[0],[0]]`（0 连着 1、2、3），答案是 4：从叶 1 出发走 `1→0→2→0→3`，四条边走完所有点。

另外两条工程约束贯穿全章：树和图都**用迭代（显式栈）而不是递归**，两千层深的链也不会爆递归上限；答案要和"实现路径独立"的暴力参照对拍才算数。

## 二、关键概念（定义）

- **DFS 入退事件（enter/exit events）**：迭代 DFS 给每个节点安排两次出场——进入时做"入"操作（本例：把编号插进 Trie）、回答该节点挂的查询；退出时做"出"操作（从 Trie 删除）。入退严格配对，保证任意时刻 Trie 里装的就是根到当前节点这条链。
- **计数 Trie（counting Trie）**：按二进制位建的前缀树，每个节点带一个 `counts` 计数：多少个当前路径成员经过这里。计数让我们能**删除**——删到最后计数归零的空分支不能再被查询使用，所以"分支可用"要看计数而不只是节点存在与否。
- **离线查询**：不逐条即时回答，而是把查询按节点分组（`by_node`），等 DFS 走到那个节点时再答。代价是输出顺序要按原查询下标写回（`answer[index]=query(value)`）。
- **位贪心（从高位取反）**：XOR 想最大，就从最高位开始贪心——如果能在 Trie 里走到"当前位与 val 相反"的分支，结果这一位就是 1。它成立的原因是位权支配：高一位的 1（比如 4）比所有低位之和（2+1=3）都大，所以永远值得为高位翻 1 牺牲低位。
- **恢复 / 回滚**：退出节点时执行 `change(node,-1)` 撤销插入。不撤销会怎样？兄弟分支的节点会**泄漏**进后续查询的候选集——比如查完节点 2 不删，再查节点 3 时 2 会被当成"祖先"参与异或，答案就错了。
- **状态最短路（多源 BFS over `(node,mask)`）**：把 `(位置, 已访问掩码)` 当成一个超级节点建隐式图，每条实际边成本 1，跑 BFS。多源指初始把 `(i, 1<<i)` 对所有 i 都入队，因为题目允许任选起点。
- **状态去重（seen 集合）**：BFS 按**完整状态**去重。若只按位置去重，会把"到了 0 但只访问过 {0,1}"和"到了 0 且访问过 {0,1,2}"错误合并，丢掉后者携带的历史。
- **规模约束**：两处体现——迭代 DFS 扛深链（不靠提高递归上限）、状态 BFS 只能用于 n 很小的图（状态数 n·2ⁿ 指数爆炸）。

## 三、解决思路（一步步推导）

- **Step 1：建树并分组查询。** 从 `parents` 找根（`p==-1` 的点必须恰好一个）、建 children 邻接表、把查询按节点挂到 `by_node`。同时扫描出编号和查询值的最大位宽 `width`（本例最大值 5，位宽 3）。
- **Step 2：初始化计数 Trie。** 用两个平行数组表示 Trie：`links[i]` 是节点 i 的两个孩子下标（-1 表示不存在），`counts[i]` 是经过该节点的元素个数。根节点 counts 记录 Trie 里元素总数。
- **Step 3：手算插入与查询（用第一个查询 `node=0, val=2`）。** 进入节点 0，把 0（二进制 000）插入 Trie。查询 2（010）：最高位想要 1（val 该位是 0，异或想取反），Trie 里只有 000，走不通，最高位取 0；第二位 val 是 1、想要 0，000 的该位正是 0 ✓，走过去，答案累积 `100→010` 中的 `010`（即 2）；最低位想要 1，000 是 0，走不通，取 0。最终 0^2=2，`answer[0]=2`。
- **Step 4：DFS 继续下探。** 进入 1（无查询），再进入 2。此时 Trie 装的链是 {0,1,2}（这正是"当前路径"）。查询 `node=2, val=5`（101）：最高位 val 是 1、想要 0——{0,1,2} 全部高位为 0 ✓，取 1；第二位 val 是 0、想要 1——候选里只有 2（10）该位是 1 ✓，取 1，进入只含 2 的子树；最低位 val 是 1、想要 0——2 的末位是 0 ✓，取 1。答案 111=7，正是 2^5。`answer[2]=7`。
- **Step 5：退出与回滚。** 2 处理完就退出：`change(2,-1)` 把 2 从 Trie 删掉（counts 全线减一，归零的分支从此不可用）。**这一步是本章的命门**：如果只插不删，接下来查节点 3 时 2 还躺在候选里，"祖先集合"就混进了兄弟分支。
- **Step 6：兄弟分支复用同一棵 Trie。** 进入 3，链是 {0,1,3}。查询 `val=2`（010）：最高位想要 1 不可行取 0；第二位想要 0——{0,1} 满足（3 是 11 该位为 1）✓ 取 1；最低位想要 1——1（01）满足 ✓ 取 1。答案 011=3，即 1^2=3。`answer[1]=3`。最终 `[2,3,7]`，与 cell8 断言一致；cell6 第一张表逐行打印了这条 trace（节点、当时的祖先路径、查询值/结果）。
- **Step 7（第二题）：定义状态。** 对 `[[1,2,3],[0],[0],[0]]`，状态 `(位置, 掩码)` 共 4×2⁴=64 种。初始队列装 `(0,0001),(1,0010),(2,0100),(3,1000)`，距离都是 0——多源 BFS 允许从任意点出发。
- **Step 8：逐层扩展。** 第一层从 `(1,0010)` 出发到 0 得 `(0,0011)` 距离 1；从 `(0,0001)` 出发到 1、2、3 得 `(1,0011)、(2,0101)、(3,1001)` 距离 1……继续扩展：`(2,0101)→(0,0101)` 距离 2（回到 0 但历史变多，是**新**状态），再 `(0,0111)→(3,1111)` 距离 4，掩码达到 1111=15 即"全覆盖"，返回 4。手数一下对应走法 `1→0→2→0→3`：恰好 4 条边 ✓。
- **Step 9：无解判定。** BFS 队列耗尽仍未出现全掩码，说明图不连通，返回 -1（测试里的 `[[],[]]` 两个孤立点就是这种情形）。

## 四、代码逐段讲解

### 1. 祖先最大异或 `max_genetic_difference`（按段讲）

**输入检查与建树：**

```python
    n=len(parents)
    if n==0:
        if queries:raise ValueError('Queries require a nonempty tree')
        return []
    roots=[i for i,p in enumerate(parents) if p==-1]
    if len(roots)!=1:raise ValueError('Exactly one root required')
    children=[[] for _ in range(n)]
    for node,p in enumerate(parents):
        if p!=-1:
            if not 0<=p<n or p==node:raise ValueError('Invalid parent')
            children[p].append(node)
```

- 空树但带查询是矛盾输入，抛错；空树无查询返回空答案。
- `roots` 必须恰好一个（既是树的定义，也防森林）；父节点下标越界或自环同样拒绝。这些契约在后面对拍里被随机树全部满足。

**查询分组与位宽：**

```python
    by_node=[[] for _ in range(n)]
    maximum=n-1
    for i,(node,value) in enumerate(queries):
        if not 0<=node<n or value<0:raise ValueError('Invalid query')
        by_node[node].append((i,value));maximum=max(maximum,value)
    width=max(1,maximum.bit_length())
```

- 查询离线化：按节点收集 `(原下标, 查询值)`，这样 DFS 到哪答到哪。
- `width` 取"最大节点编号"和"最大查询值"的位长（节点编号本身也要进 Trie），后面所有位循环都按它走；`max(1,...)` 兜住全零的情形。

**计数 Trie 的插入/删除 `change`：**

```python
    links=[[-1,-1]];counts=[0]
    def change(value,delta):
        current=0;counts[current]+=delta
        assert counts[current]>=0
        for bit in range(width-1,-1,-1):
            digit=(value>>bit)&1
            if links[current][digit]==-1:
                assert delta==1
                links[current][digit]=len(links);links.append([-1,-1]);counts.append(0)
            current=links[current][digit];counts[current]+=delta
            assert counts[current]>=0
```

- `delta=+1` 是插入、`-1` 是删除，同一段代码两个方向复用——这正是"恢复"机制的实现：退出节点时原路把计数减回去。
- 沿途每层 `counts[current]+=delta`，节点不存在时**只允许在插入时创建**（`assert delta==1`）；`assert counts[current]>=0` 保证永远不会删掉不存在的元素，这是内部不变量的自检。
- 删除后节点**保留**但计数可能为 0——查询侧必须看计数决定分支可用性。

**查询 `query`：**

```python
    def query(value):
        current=0;answer=0
        assert counts[0]>0
        for bit in range(width-1,-1,-1):
            digit=(value>>bit)&1;preferred=links[current][digit^1]
            if preferred!=-1 and counts[preferred]>0:
                answer|=1<<bit;current=preferred
            else:
                current=links[current][digit]
                assert current!=-1 and counts[current]>0
        return answer
```

- 从最高位（`width-1`）到最低位，每一步先试"相反位"分支 `digit^1`：分支存在**且计数大于 0** 才走，并在答案里把这一位置 1（位贪心）。
- 走不通就顺着"相同位"下去，该位结果为 0。两个 assert 保证当前路径集合非空（Trie 里至少有从根到当前节点的链）。
- `assert counts[0]>0` 在入口确认 Trie 非空——查询时路径至少含当前节点自己。

**迭代 DFS 主体：**

```python
    answer=[0]*len(queries);path=[];visited=0
    stack=[(roots[0],False)]
    while stack:
        node,exiting=stack.pop()
        if exiting:
            change(node,-1);assert path.pop()==node
            continue
        visited+=1;change(node,1);path.append(node)
        for index,value in by_node[node]:answer[index]=query(value)
        if trace is not None:trace.append((node,path[:],[(v,answer[i]) for i,v in by_node[node]]))
        stack.append((node,True))
        stack.extend((child,False) for child in reversed(children[node]))
    if visited!=n:raise ValueError('Disconnected cycle in parent relation')
    assert counts[0]==0 and not path
    return answer
```

- 栈里放 `(节点, 是否退出标记)`：先弹到"进入"就插入、答查询、把 `(node,True)` 压栈（预约退出），再把孩子们**倒序**压栈（保证按正序访问）。
- 弹到"退出"就 `change(node,-1)` 回滚并从 `path` 弹出，`assert path.pop()==node` 检查配对正确。
- `visited!=n` 抓住"parents 里有环或断链"的非法输入；结束时 `counts[0]==0 and not path` 断言 Trie 与路径双双清空——又一条收尾不变量。
- `trace` 参数是可选的观测接口，cell6 的小实例表就靠它打出来。

### 2. 状态 BFS `shortest_path_visiting_all`

```python
def shortest_path_visiting_all(graph):
    n=len(graph)
    if n<=1:return 0
    full=(1<<n)-1
    queue=deque((i,1<<i,0) for i in range(n))
    seen={(i,1<<i) for i in range(n)}
    while queue:
        node,mask,distance=queue.popleft()
        if mask==full:return distance
        for other in graph[node]:
            state=(other,mask|(1<<other))
            if state not in seen:
                seen.add(state);queue.append((*state,distance+1))
    return -1
```

- `full=(1<<n)-1` 是"所有点都访问过"的掩码（n=4 时 1111=15）；单点或空图直接 0。
- 初始队列装全部 `(i, 1<<i, 0)`：多源 BFS，起点任选；`seen` 一开始就把这些状态标掉。
- 每次弹出一个状态，掩码已满就返回距离（BFS 按层扩展，第一次到达就是最短）。否则对每个邻居生成新状态 `(other, mask|1<<other)`——**注意掩码按位或会吸收新点，但历史不丢**；`seen` 按完整二元组判重。
- 队列耗尽返回 -1（不连通）。每个状态至多入队一次，总状态数 n·2ⁿ 封顶。

## 五、为什么是对的？复杂度是多少？（说人话）

**祖先查询为什么对。** 核心不变量：任意时刻，Trie 中计数为正的元素集合恰好等于"根到当前节点的路径"。理由是入退配对——进入插入、退出删除，DFS 的栈式结构保证一条链上的节点都在 Trie 里、岔出去的都被删干净了。所以每个查询只会看到合法祖先，兄弟分支的值不会泄漏进来。位贪心的正确性来自位权支配：高一位翻 1 带来的收益（比如 4）超过所有低位全翻 1 的收益（3），所以从高位到低位逐位"能翻则翻"得到的就是最大 XOR。删除语义靠计数实现：空分支计数为 0，查询侧 `counts[preferred]>0` 挡住它们。

**状态 BFS 为什么对。** 隐式状态图里每条边（走一步实际边）成本都是 1，BFS 天然按距离分层，第一次到达全掩码状态的距离就是最短。判重必须按 `(位置, 掩码)`：同一个位置不同掩码代表不同历史，错误合并会让某些"绕路换取覆盖"的走法永远出不了队。

**代价。** 祖先查询：每个节点一次插入一次删除、每个查询一次 Trie 下行，每次都是 B 位（B 是最大位长），合计 O((n+q)B) 时间、Trie 空间上界 O(nB)。拿测试里的真实规模说：n=34、30 个查询、值不超过 128（B=7），总共几千次位步进；两千深的链（n=2000、B=12）也照跑，因为 DFS 是迭代的。全访问 BFS：状态至多 n·2ⁿ 个，每个状态扫邻居一次，时间 O((n+m)2ⁿ)、空间 O(n2ⁿ)——n=5 时才 160 个状态，但 n=20 就是两千万级，这就是"规模约束"：这算法只对很小的 n 可用。

## 六、测试用例在测什么

cell8 的断言分五组：

1. **冒烟**：`[-1,0,1,1]` 的三个查询得 `[2,3,7]`——第三节手算的完整用例，三个值分别覆盖"根上查询""叶上查询""回滚后再查询"三条路径。
2. **随机树对拍（逐祖先慢参照）**：n=1..34、每棵随机树挂 30 个查询，期望值由"沿 parents 一路爬到根、逐个算 XOR 取最大"的朴素循环直接算出。这个参照和 Trie/DFS 的实现路径完全不同，是独立正确性来源。查询值限制在 128 以内，位宽可控。
3. **乱序标号树**：`[2,2,-1]`——根是下标 2，孩子 0、1 的父节点写在数组前部。它测的是实现不依赖"父节点下标小于孩子"这类隐藏假设；两查询答案都是 `2^1=3`。
4. **深链规模测试**：`parents=[-1]+list(range(1999))` 是 2000 层的直链，查询 `(1999,2048)` 的期望是 `max(i^2048 for i in range(2000))`。它同时验证迭代 DFS 扛得住深链（递归版在这里会撞 `sys.setrecursionlimit`）和大位宽（2048 是 12 位）下的正确性。
5. **状态 BFS：对拍 + 边界**。`metric_reference` 用 Floyd-Warshall 求全源距离、再枚举所有访问排列取最小总距离——与状态 BFS 毫无实现交集。对 n=1..5、各 45 张随机图（每对点以 1/3 概率连边）对拍，覆盖了各种连通/不连通情形。`[[],[]]==-1` 专测不连通返回 -1 的分支。

## 七、练习思路提示

- **练习 1（逐祖先慢参照）**：把测试组 2 里的朴素参照独立成一个函数：输入 `(parents, queries)`，对每个查询从 node 爬到根、逐祖先算 `a^val` 取最大。写明边界（空树带查询、查询节点越界要如何处理，可对照本章抛 ValueError 的做法）。手算示例用 `[2,2,-1]`、`[(0,1)]`：祖先链是 0→2，`max(0^1, 2^1)=3`。再对随机树和本章接口对拍，确认两者一致——慢参照的意义正是"用独立路径定义正确"。
- **练习 2（网格暴力边枚举 vs 候选跳过）**：对应扩展题 2617 的场景。暴力做法对每个格子枚举它能到达的所有格子（O(边数) 转移）；候选跳过则是用平衡结构/单调结构把"每次从全部候选里挑最优"变成跳过已失效候选。建议先在 3×3 或 4×4 的小网格上手算一轮两种方法的转移次数，数出各自做了多少次比较，再用随机网格对拍两者的答案和转移计数。边界包括单行/单列网格、全阻塞无解（返回 -1）的情形。

## 八、对应 LeetCode 题目

- **1938. Maximum Genetic Difference Query（canonical）**：本章第一个接口的原题，练"DFS 入退事件 + 计数 Trie + 离线查询"三件套组合，回滚与计数判可用是核心考点。
- **847. Shortest Path Visiting All Nodes（canonical）**：本章第二个接口的原题，练"(位置, 掩码) 状态最短路 + 多源 BFS + 按完整状态判重"。
- **2617. Minimum Number of Visited Cells in a Grid（extension）**：迁移方向：把"跳过失效候选"的结构化技巧用到网格最短访问上，对应练习 2 的比较实验；本章未给实现，作为综合扩展练习。

notebook 结尾照例提醒：这些题号用于知识映射，本章实现遵循教学契约，不要把教学实例当成官方题的完整答案。
