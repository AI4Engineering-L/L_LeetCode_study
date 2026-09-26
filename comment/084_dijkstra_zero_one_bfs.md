# N084 · Dijkstra与0-1 BFS —— 说人话详解

> 对应 notebook：`notebooks/11_graphs/084_dijkstra_zero_one_bfs.ipynb`

## 一、这章要解决什么问题？（问题描述）

N081 的 BFS 解决了"每步代价相同"的最短路。可现实里边有权重：这条高速 1 小时、那条土路 5 小时。一旦边权不全相等，普通队列"先出队的距离一定最短"就失效了，需要新的调度规则。本章两条路：

1. **Dijkstra（边权任意非负）：** 每轮从"当前暂定距离最小的点"开始扩展。具体例子（notebook 小实例）：4 个点，0→1 权 1、0→2 权 4、1→2 权 1、1→3 权 5、2→3 权 1。从 0 出发，最短距离是 `[0, 1, 2, 3]`——到 2 走 0→1→2 共 2（而不是直达的 4），到 3 走 0→1→2→3 共 3（而不是 0→1→3 的 6）。
2. **0-1 BFS（边权只有 0 或 1）：** 特例专用工具，用双端队列代替堆：0 代价的邻居放队首、1 代价的放队尾，保持队列"从近到远"的秩序，跑出和 Dijkstra 完全一样的答案但更快。
3. **应用题 network_delay_time（网络传播时间）：** n 个节点、times 里每条 `[u,v,w]` 表示信号从 u 到 v 要 w 毫秒，从节点 k 发信号，问多久**所有**节点都收到；有节点收不到返回 -1。例子：`times=[[2,1,1],[2,3,1],[3,4,1]]，n=4，k=2` → 答案 2：信号从 2 出发，1 毫秒到 1 和 3，再 1 毫秒到 4，最晚收到的是 2 毫秒。若 `times=[[1,2,1]]，n=2，k=2`，2 号发不出去任何信号（边只有 1→2），1 号永远收不到，返回 -1。

一句话总结本章思想：**按边权范围选调度器**——全是 1 用普通队列（N081），只有 0/1 用双端队列，一般非负权用堆，出现负权直接拒绝（用 Bellman-Ford，不在本章）。

## 二、关键概念（定义）

- **边权（weight）：** 走这条边的代价。路径长度 = 各边权之和（而不是边数）。最短路问题从"数步数"升级为"算总代价"。
- **暂定距离（distance 数组）：** distance[v] 记录"目前所知"从源到 v 的最短代价，可能随后被更优路线改写；算法结束后就是最终答案。初始除源点为 0 外全是无穷大（float('inf')）。
- **松弛（relaxation）：** 对边 u→v 检查"经过 u 到 v 是否更便宜"：若 `distance[u]+w < distance[v]`，就更新 distance[v]。整个 Dijkstra 就是不断找机会松弛。
- **堆（heap / 优先队列）：** Python 的 `heapq`，每次弹出当前最小元素。Dijkstra 用它实现"每轮取暂定距离最小的点"，堆里存 `(距离, 点)` 元组，按距离排小顶堆。
- **过期堆项（stale entry）：** 同一个点可能因多次松弛被推进堆好几份，旧的（较大的）那份是过期的。出队时用 `if dist!=distance[u]: continue` 核对"这个距离还是不是最新值"，过期就直接跳过——这是"懒惰删除"策略，省去堆不支持改键的麻烦。
- **双端队列（deque）：** 两端都能进能出的队列。0-1 BFS 里 0 代价放左端（appendleft，插队——因为它和当前点同层）、1 代价放右端（append，排到后面一层）。
- **非负边权（Dijkstra 的命门）：** 所有 w≥0。这保证"一旦一个点被确定为最小，它不可能再被更短的路径改善"，因为任何绕路都要先走一段非负的距离。
- **最短路树：** 从源点向全图摊开的一棵树，树上源点到每点的路径就是最短路。松弛时实际记下的"前驱关系"构成这棵树（本章实现没存前驱，但概念上存在）。

## 三、解决思路（一步步推导）

**Step 1：初始化。** distance 全 inf，源点设 0，把 `(0, 源点)` 放进堆（或双端队列）。

**Step 2：取出当前最小暂定距离的点 u。** 关键信念：此刻 distance[u] 已经是最终答案（下面第五节论证为什么）。若堆里这份距离和数组对不上（过期项），跳过。

**Step 3：对 u 的每条边 (v,w) 松弛。** 更优就更新 distance[v] 并把新值推进堆（Dijkstra）；0-1 BFS 则按 w 是 0 还是 1 决定推进队首还是队尾。

**Step 4：重复直到堆/队空。** distance 数组即答案，仍是 inf 的点不可达。

**Step 5：network_delay_time 收尾。** 对全部点的最短距离取 max（最晚收到的时间），有 inf 说明有人收不到，返回 -1。

**手算演示（dijkstra 在 adj=[[(1,1),(2,4)],[(2,1),(3,5)],[(3,1)],[]] 上，源 0）：**

- 初始：distance=[0,inf,inf,inf]，堆=[(0,0)]。
- 弹 (0,0)，与数组一致。松弛 0→1：0+1<inf，distance[1]=1，压 (1,1)。松弛 0→2：0+4<inf，distance[2]=4，压 (4,2)。堆=[(1,1),(4,2)]。
- 弹 (1,1)，一致。松弛 1→2：1+1=2<4，**改善**！distance[2]=2，压 (2,2)。松弛 1→3：1+5=6<inf，distance[3]=6，压 (6,3)。堆=[(2,2),(4,2),(6,3)]。
- 弹 (2,2)，一致（注意 (4,2) 还躺在堆里，它过期了）。松弛 2→3：2+1=3<6，distance[3]=3，压 (3,3)。堆=[(3,3),(4,2),(6,3)]。
- 弹 (3,3)，一致，无出边。
- 弹 (4,2)：`4 != distance[2]=2`，过期项，跳过。弹 (6,3)：`6 != 3`，同样跳过。堆空。
- 返回 `[0,1,2,3]`。这一趟你能亲眼看到两件事：中间点的更优路线如何改写答案（0→2 从 4 降到 2），以及过期堆项如何被核对丢弃。

**手算演示（0-1 BFS 为什么要把 0 代价插队首）：** 反例图：0→1 权 1、0→2 权 1、2→1 权 0（N081 练习 2 用过它）。真实最短路：d[1]=1（走 0→2→1：1+0=1，与直达并列 1）；换更能看出差别的：0→1 权 1、0→2 权 0、2→1 权 0，真实 d[1]=0。0-1 BFS 过程：队=[(0,0)]。弹 0：邻居 1 权 1 → d[1]=1，append 到队尾；邻居 2 权 0 → d[2]=0，**appendleft 插到 1 前面**。队=[(0,2),(1,1)]。弹 (0,2)：邻居 1 权 0，0+0=0<1，d[1] 改 0，再 appendleft。队=[(0,1),(1,1)]。弹 (0,1) 生效；弹 (1,1) 过期跳过。答案 [0,0,0]，正确。若 0 代价也放队尾，(1,1) 会先出队并"定稿"错误距离 1——插队首就是为了不让同层的 0 代价被上一层的 1 代价抢跑。

## 四、代码逐段讲解

**第一段：dijkstra——堆 + 松弛 + 过期项丢弃。**

```python
import heapq
from collections import deque

def dijkstra(n,adj,source):
    if any(w<0 for row in adj for _,w in row): raise ValueError('Dijkstra requires nonnegative weights')
    distance=[float('inf')]*n; distance[source]=0; heap=[(0,source)]
    while heap:
        dist,u=heapq.heappop(heap)
        if dist!=distance[u]: continue
        for v,w in adj[u]:
            if dist+w<distance[v]:
                distance[v]=dist+w; heapq.heappush(heap,(distance[v],v))
    return distance
```

- 第一行是**负边拒绝**：`any(w<0 for row in adj for _,w in row)` 扫全部边，发现负权立即抛 ValueError。宁可拒绝也不照跑——负边会破坏算法的正确性前提，跑出的答案看似有数字实则是错的（练习 1 让你亲手构造这种事故）。
- `distance=[float('inf')]*n`：无穷大当"还没摸到"的初值，任何有限距离都比它小，第一条到达路径必然生效。
- 堆元素是 `(距离, 点)` 元组：heapq 按元组第一项排，所以每次弹出暂定距离最小的点。初始只放 `(0,source)`。
- `if dist!=distance[u]: continue`：**过期项核对**。u 可能被多次推进堆，只有"出队距离 == 数组当前值"那份才有效；不一致说明它已被更优值取代，跳过本次。`continue` 回到 while 取下一个。
- 松弛那两行：`dist+w<distance[v]` 成立就更新数组并把 `(新距离, v)` 压堆。注意没有"删除旧项"的操作——旧的留在堆里等出队时被核对环节跳过，这就是懒惰删除。
- 隐式终止条件：每个点的每条有效松弛至多产生一个堆项，堆终会耗尽；数组里留下的就是最终最短距离。

**第二段：zero_one_bfs——双端队列版。**

```python
def zero_one_bfs(n,adj,source):
    if any(w not in (0,1) for row in adj for _,w in row): raise ValueError('only 0/1 weights supported')
    distance=[float('inf')]*n; distance[source]=0; queue=deque([(0,source)])
    while queue:
        dist,u=queue.popleft()
        if dist!=distance[u]: continue
        for v,w in adj[u]:
            if dist+w<distance[v]:
                distance[v]=dist+w
                if w==0: queue.appendleft((distance[v],v))
                else: queue.append((distance[v],v))
    return distance
```

- 第一行同样先验输入：`w not in (0,1)` 挑出一切非 0/1 的权值并拒绝。0-1 BFS 的论证只对 0/1 权成立，混入 2 就悄悄错了，所以挡在门口。
- 整体骨架和 dijkstra 逐行对应：同样的 distance 数组、同样的过期项核对（双端队列同样会积压过期项）、同样的松弛判断。唯一区别在"新项放哪"。
- `if w==0: queue.appendleft(...) else: queue.append(...)`：本章点睛之笔。0 代价的邻居和 u 同层，插队首保住"队头距离 ≤ 队尾距离"的秩序；1 代价的邻居属于下一层，规矩排队尾。秩序保住了，"先出队的距离不大于后出队的"就依然成立，于是 BFS 式的一次定稿论证照搬可用，而且不需要堆的 log 开销。
- 复杂度收益：每个点仍可能多次入队（0 代价改善一次、1 代价改善一次，均摊常数次），总量 O(V+E)，比 Dijkstra 的 O((V+E)log(V+E)) 快一个 log 因子。

**第三段：network_delay_time——Dijkstra 的应用包装。**

```python
def network_delay_time(times,n,k):
    adj=[[] for _ in range(n)]
    for u,v,w in times: adj[u-1].append((v-1,w))
    maximum=max(dijkstra(n,adj,k-1))
    return -1 if maximum==float('inf') else maximum
```

- 题目节点编号是 1..n，本章实现用 0..n-1，所以 `u-1`、`v-1`、`k-1` 三处都在做"减一"平移（和 N079 法官题的"开 n+1 槽"是同一类编号适配，只是方向相反）。
- `for u,v,w in times` 三元解包直接拿头、尾、权，构图成本 O(E)。
- `max(dijkstra(...))`：所有节点的到达时间取最大——信号是同时发出的，全网都收到的时间就是最晚那个到达时间。
- `return -1 if maximum==float('inf') else maximum`：最大值是无穷大说明至少一个点不可达，按题意返回 -1；这行紧凑写法等价于 if/else 两行。

## 五、为什么是对的？复杂度是多少？（说人话）

**Dijkstra 为什么"取出的最小距离就是最终答案"：** 用反证法说人话。假设某一轮我们弹出点 u，它的暂定距离是 d，是全堆最小的；但假设其实存在一条更短的路线，真实最短是 d' < d。沿着这条更短路线从源点走到 u，路上必然存在第一个"还没被确定最终答案"的点 x（u 自己就是候选，所以 x 存在）。x 的前一跳 y 一定已经被确定（因为 x 是第一个未确定的），而 y 被确定时松弛过 x，会给 x 一个不超过 d' 的暂定距离。可 d' < d，也就是说堆里本应有一个距离 ≤ d' < d 的点 x 轮先出队——矛盾，因为 d 才是最小的。所以不存在更短路线，d 就是定稿值。

**非负权在论证里干了什么：** 它保证"已确定点的答案不会被绕路改善"。绕路 = 已确定的 d 加上后面一段非负的距离，总和不可能小于 d。如果有负边，后面一段可能把总和拉下去，整套"定稿"逻辑当场作废——这就是开头要 raise ValueError 的原因。

**0-1 BFS 为什么不用堆也对：** 双端队列维护着这条性质：任何时刻从队首到队尾，距离最多相差 1、且不下降（0 代价插首保持同层、1 代价插尾开启新层）。于是"出队顺序 = 距离不降顺序"，和 Dijkstra"每轮取最小"的效果一样，一次定稿的论证原样成立。第三节的手算演示展示了这条秩序怎么靠 appendleft 保住。

**复杂度（用具体数字感受）：**

- Dijkstra（二叉堆版）：时间 O((V+E)log(V+E))——每次松弛压堆一次 log，每个堆项出队一次 log。1 万点、5 万边的图约 6 万 × log(6 万)≈6 万×16 ≈ 百万次操作，毫秒级。
- 0-1 BFS：时间 O(V+E)，没有 log。同样的图 6 万次操作，快一个数量级——边权恰好只有 0/1 时，它就是更快的 Dijkstra。
- 空间都是 O(V+E)（邻接表 + 堆/队列）。
- network_delay_time 在此之上加 O(E) 建图和 O(V) 取最大，不改变量级。

## 六、测试用例在测什么

```python
assert network_delay_time([[2,1,1],[2,3,1],[3,4,1]],4,2)==2
```
正常值：LeetCode 743 的官方示例。信号 1 毫秒到 1、3，2 毫秒到 4，最晚到达 2 毫秒。同时测了编号 1-based 到 0-based 的平移是否做对（没做的话会越界或全 inf 返回 -1）。

```python
assert network_delay_time([[1,2,1]],2,2)==-1
```
**特殊值（不可达）**：唯一的边是 1→2，从 2 出发无路可走，1 号点距离保持 inf，必须返回 -1。这条抓"忘了处理不可达、把 inf 当时间返回"的错误。

```python
for _ in range(150):
    n=6; edges=[(u,v,rng.randrange(2)) for u in range(n) for v in range(n) if rng.randrange(5)==0]
    adj=[[] for _ in range(n)]
    for u,v,w in edges: adj[u].append((v,w))
    ref=[float('inf')]*n; ref[0]=0
    for _ in range(n-1):
        old=ref[:]
        for u,v,w in edges: ref[v]=min(ref[v],old[u]+w)
    assert dijkstra(n,adj,0)==zero_one_bfs(n,adj,0)==ref
```
**随机对拍**（150 组）：随机生成 6 点、0/1 权随机图，用**Bellman-Ford 式参考实现**（把所有边松弛 n−1 轮，第 4 节代码里那三行 for）算出标准答案，然后断言 dijkstra、zero_one_bfs、ref 三者逐点相等。这一条同时验证两件事：Dijkstra 的堆调度没算错；0-1 BFS 的双端队列调度和堆调度殊途同归。150 组随机图把各种拓扑（环、重边、不可达点）都滚进去了。

```python
try: dijkstra(2,[[(1,-1)],[]],0)
except ValueError: pass
else: raise AssertionError('negative edge must be rejected')
```
**负边拒绝测试**：图里有边 0→1 权 −1。期望 dijkstra 抛 ValueError；try/except/else 的写法是"必须抛异常才算过"的标准测试模式——异常没抛反而执行到了 else 分支，就主动 raise 失败。这条把"契约：负边不做"变成可执行检查，防止有人图省事删掉防御行。

## 七、练习思路提示

**练习 1（负边怎么破坏 Dijkstra）：** 思路方向：造一个"贪心定稿后被负边翻盘"的最小反例。提示：三 点图 0→1 权 1、0→2 权 2、2→1 权 −2。Dijkstra 弹出 1（距离 1）就把它定稿；但真实最短路 0→2→1 = 2+(−2) = 0 < 1。手算时把"弹出即定稿"的每一步和真实最优写成两张小表对照，看清翻盘发生在哪一步。再想一想：为什么 N081 等权 BFS 不怕这个问题（提示：等权时绕路永远不省）；真要解负权得换 Bellman-Ford（对拍测试里那三行就是它的雏形）。

**练习 2（用 0-1 BFS 替换堆并比较操作数）：** 思路方向：在 0/1 权图上两份实现都跑同一输入，数一数"点出队/堆弹出"的次数和真实耗时。提示：给两份代码各加一个计数器（出队一次 +1），在同一个大随机图上对比总次数；再感受一下 heapq 每次 heappop 都要 O(log n) 而 deque 是 O(1)。手算示例可以用第三节那个三点反例图，把两种算法各自的弹出序列写出来，你会发现 0-1 BFS 靠 appendleft 省掉了"排错层"的弹压。结论落成一句话：权值只有 0/1 时 0-1 BFS 严格不劣。

## 八、对应 LeetCode 题目

- **743. Network Delay Time（canonical）：** 就是本章的 network_delay_time，练"Dijkstra 完整落地 + 1-based 编号平移 + 不可达返回 -1"。
- **1368. Minimum Cost to Make at Least One Valid Path in a Grid（canonical）：** 网格版 0-1 BFS——沿箭头方向走代价 0、逆着走代价 1，正是"权只有 0/1 用双端队列"的教科书应用；把本章 zero_one_bfs 的邻接表换成网格四方向隐式图即可迁移。
