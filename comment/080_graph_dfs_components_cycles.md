# N080 · DFS、连通分量与环检测 —— 说人话详解

> 对应 notebook：`notebooks/11_graphs/080_graph_dfs_components_cycles.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章解决四个"遍历一下图就出答案"的问题，共用一个武器：深度优先搜索（DFS）。

1. **数连通分量：** 一个无向图被切成几块"互相能到达"的部分？具体例子：5 个点、边 `[(0,1),(1,2),(3,4)]`，输出 2——因为 {0,1,2} 是一块、{3,4} 是另一块，两块之间没有任何边。再极端点：4 个点 0 条边，输出 4（人人都是孤岛）。
2. **数岛屿：** 一个 '0'/'1' 组成的网格里，'1' 代表陆地，上下左右相连的 '1' 算同一座岛，问有几座岛。具体例子：`[['1','1','0'],['0','0','1']]` 输出 2——左上角两个 '1' 相连是一座，右下角单独的 '1' 是另一座。
3. **有向图判环：** 判断有向图里是否存在"绕一圈回到自己"的路径。具体例子：邻接表 `[[1],[2],[]]`（0→1→2）无环，输出 False；`[[1],[2],[0]]`（0→1→2→0）有环，输出 True；`[[0]]`（自环）输出 True。
4. **克隆图：** 给你图里的一个起点节点（每个节点有 val 和邻居列表），深拷贝出一张结构完全相同的新图。麻烦在于图里可能有环、两个不同节点可能 val 相同，你不能"顺着抄一遍"完事，必须记住哪些节点已经复制过。

这四题的共同骨架是：**从没访问过的点启动一次搜索，一次搜索恰好覆盖一个连通块（或一条祖先链上的信息）**，数启动次数、或在搜索中识别"回到祖先"即得答案。

## 二、关键概念（定义）

- **DFS（深度优先搜索）：** 沿一条路一头扎到底，走不动了再退回来换下一条路。可以用递归实现，也可以用显式栈实现——本章全部用栈，因为递归在深图上会爆栈（Python 默认递归深度约 1000）。
- **连通分量（connected component）：** 无向图里"互相可达"的极大点集。选任何一点做 DFS，能到达的恰好是它所在的整块，所以"启动几次 DFS"就等于"有几块"。
- **洪泛填充（flood fill）：** 网格版 DFS 的别名：从一个格出发把整片相连的同色格子"淹没"（标记掉）。数岛屿就是反复洪泛、数洪泛次数。
- **三色标记法（灰与黑）：** 有向图判环的关键技巧。每个点三种状态：白（没碰过）、灰（正在当前搜索路径上）、黑（已彻底搜完）。只有"指向灰点的边"才证明有环——灰点是你的祖先，指回祖先就是绕圈；指向黑点只是两条路径汇合，不是环。
- **入栈即标记：** 节点一进栈就记为已访问，而不是出栈时才记。这样同一个节点不会被压多次栈，保证每个点只处理一次。
- **迭代器栈（栈里存 (节点, 其邻居的迭代器)）：** 用栈模拟递归的写法。栈顶元素保持"当前正探到哪个邻居"，next() 拿下一个邻居，拿完了（StopIteration）就染黑、弹栈——正好对应递归里"for 循环结束、函数返回"。
- **克隆图的映射（mapping）：** "原节点 → 新节点"的字典。它同时解决两个问题：避免同一节点复制两次，以及处理环（回到已复制的节点时直接接上现成的新节点）。**按对象身份**做键，而不是按 val——两个 val 都是 7 的节点是两个不同的点。
- **隐式图：** 岛屿题没有给你点和边，'1' 格子和它的四邻居关系就是隐含的边。

## 三、解决思路（一步步推导）

**Step 1：数分量——"从每个白点启动一次洪水"。** 维护 seen 集合；主循环扫所有点，见到没见过的点就把分量计数 +1，然后 DFS 把它整块标记掉。块内所有点都会在这一次搜索中进 seen，所以下一次"没见过"的点必然属于新的一块。

**Step 2：数岛屿——把"点"换成"格子"。** 只从值为 '1' 且未标记的格子启动洪泛，四方向蔓延，只吃 '1'。'0' 格子永远不进栈。

**Step 3：有向判环——从白点启动，路上染灰，收工染黑。** 遇到邻居是灰点立即报告有环；邻居是黑点直接跳过（它已经彻查无罪）。

**Step 4：克隆图——先复制点、再复制边。** 用映射保证每个原节点只 new 一次；用队列做 BFS 逐个处理邻居连线，环和共享邻居都自动正确。

**手算演示（count_components(5, [(0,1),(1,2),(3,4)])）：**

- 先建无向邻接表：adj = [[1],[0,2],[1],[4],[4→3]]，即 `[[1],[0,2],[1],[4],[3]]`。
- start=0：没见过。计数=1，seen={0}，栈=[0]。弹出 0，邻居 [1] 未见过 → seen={0,1}，栈=[1]。弹出 1，邻居 [0,2]，0 已见，2 未见 → seen 加 2，栈=[2]。弹出 2，邻居 [1] 已见，栈空。这一轮把 {0,1,2} 全标掉了。
- start=1、2 都在 seen 里，跳过。start=3：没见过。计数=2，栈=[3]。弹出 3，邻居 4 入栈标记；弹出 4，邻居 3 已见。{3,4} 标完。
- start=4 跳过。最终返回 2。

**手算演示（has_directed_cycle([[1],[2],[0]]) 三色过程）：**

- start=0：color[0]=1（灰），栈压 (0, 迭代器[1])。
- 取 0 的邻居 1：白，染灰，压 (1, 迭代器[2])。
- 取 1 的邻居 2：白，染灰，压 (2, 迭代器[0])。
- 取 2 的邻居 0：color[0]==1，是灰点——指回祖先，返回 True。这就是环 0→1→2→0。

对照无环的 `[[1],[2],[]]`：同样的 0→1→2，但 2 没有邻居，迭代器耗尽，2 染黑弹栈，随后 1、0 也染黑弹栈，返回 False。

**手算演示（克隆自环图）：** x 的邻居是 [x, y]，y 的邻居是 [x]。先把 x 复制成 a（mapping={x:a}），队列=[x]。处理 x：邻居 x 已在 mapping，直接 a.neighbors 追加 a（自环复制成功）；邻居 y 不在，新建 b，mapping={x:a,y:b}，a.neighbors 追加 b。处理 y：邻居 x 在 mapping，b.neighbors 追加 a。结束，返回 a：a.neighbors[0] is a 正是自环的体现。

## 四、代码逐段讲解

**第一段：count_components——栈式 DFS 数分量。**

```python
def count_components(n,edges):
    adj=[[] for _ in range(n)]
    for u,v in edges: adj[u].append(v); adj[v].append(u)
    seen=set(); count=0
    for start in range(n):
        if start in seen: continue
        count+=1; seen.add(start); stack=[start]
        while stack:
            for v in adj[stack.pop()]:
                if v not in seen: seen.add(v); stack.append(v)
    return count
```

- 前两行建**无向**邻接表：每条边两头各存一次（上一章 N079 的知识直接复用）。
- `if start in seen: continue`：这块已经数过了，跳过。`continue` 的意思是"本轮主循环剩下的事都不做了，直接看下一个起点"。
- 计数 +1 的时机是"启动一次新搜索"时，这就是分量的定义点。
- 内层 while 是栈式 DFS：`stack.pop()` 弹出栈顶，遍历它的邻居，没见过的就标记并入栈。注意是**入栈时**就 `seen.add(v)`，防止同一个点被压多次。这份实现允许同一节点短暂在栈里出现重复吗？不允许——入栈必先查 seen，而入栈即标记，所以每个点至多入栈一次。

**第二段：num_islands——洪泛数岛。**

```python
def num_islands(grid):
    if not grid or not grid[0]: return 0
    rows,cols=len(grid),len(grid[0]); seen=set(); count=0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c]!='1' or (r,c) in seen: continue
            count+=1; stack=[(r,c)]; seen.add((r,c))
            while stack:
                x,y=stack.pop()
                for nx,ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                    if 0<=nx<rows and 0<=ny<cols and grid[nx][ny]=='1' and (nx,ny) not in seen:
                        seen.add((nx,ny)); stack.append((nx,ny))
    return count
```

- `if not grid or not grid[0]: return 0`：挡空网格和空行两种退化输入，直接返回 0 座岛。
- 启动条件 `grid[r][c]!='1' or (r,c) in seen`：格子不是陆地、或陆地已属于某座数过的岛，都不启动。短路求值顺序保证先判字符再查集合。
- `for nx,ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]`：上下左右四个方向的偏移写死在列表里；`0<=nx<rows and 0<=ny<cols` 是边界检查，防止越界访问。网格只走四方向，不含对角线。
- 整体结构和 count_components 一模一样，只是"点"变成了"(行,列)坐标"、"邻居"变成了"界内相邻的 '1' 格"——这就是隐式图的全部含义。

**第三段：has_directed_cycle——三色迭代 DFS。**

```python
def has_directed_cycle(adj):
    color=[0]*len(adj)
    for start in range(len(adj)):
        if color[start]: continue
        color[start]=1; stack=[(start,iter(adj[start]))]
        while stack:
            u,neighbors=stack[-1]
            try: v=next(neighbors)
            except StopIteration:
                color[u]=2; stack.pop(); continue
            if color[v]==1: return True
            if color[v]==0: color[v]=1; stack.append((v,iter(adj[v])))
    return False
```

- `color` 数组：0=白（没碰过）、1=灰（在当前搜索路径上）、2=黑（已彻底完成）。用整数数组而不是三个集合，省事又快。
- 栈里存的不是节点而是 `(节点, 该节点邻居的迭代器)`。`stack[-1]` 永远指向当前正在展开的节点，模拟递归的"函数帧"。
- `try: v=next(neighbors) except StopIteration`：next 从迭代器取下一个邻居；取不到说明这个节点的邻居全探完了，于是染黑（color=2）、弹栈、continue 处理栈里下一层——对应递归函数的返回。
- `if color[v]==1: return True`：全函数的灵魂。邻居是灰点意味着我们找到了一条边指回自己的祖先，立刻宣布有环。
- 灰点 v==白色时才继续压栈；**黑色邻居什么都不做**——它已经彻底搜完且没发现环，再走一遍纯属浪费。

**第四段：clone_graph——映射 + 队列克隆。**

```python
class GraphNode:
    def __init__(self,val=0,neighbors=None): self.val=val; self.neighbors=[] if neighbors is None else neighbors

def clone_graph(node):
    if node is None: return None
    mapping={node:GraphNode(node.val)}; queue=deque([node])
    while queue:
        u=queue.popleft()
        for v in u.neighbors:
            if v not in mapping: mapping[v]=GraphNode(v.val); queue.append(v)
            mapping[u].neighbors.append(mapping[v])
    return mapping[node]
```

- `GraphNode` 的构造参数 `neighbors=None` 加 `[] if neighbors is None else neighbors`：默认给空列表，避免所有节点共享同一个列表的经典坑。
- `if node is None: return None`：边界输入——空图直接返回 None。
- mapping 是"原节点 → 新节点"字典；queue 里放的是**原节点**，处理它时给对应的新节点接边。
- 循环体两句：没复制过的邻居先复制并入队；然后无条件把新邻居接到新 u 的邻居表后面。自环和共享邻居都不需要特判——v 在 mapping 里就直接用现成的。
- 字典按对象身份（内存地址）当键，所以两个 val 同为 7 的不同节点不会被混淆——这正是正确性论证里强调的一点。

## 五、为什么是对的？复杂度是多少？（说人话）

**一次 DFS 为什么恰好覆盖一个分量：** 从点 s 出发能走到的所有点，按定义就是 s 所在连通块的全部成员；DFS 沿边走，一个不落全标进 seen。反过来，块外的点没有边连进来，DFS 也绝无可能跳过去。所以"启动次数 = 分量数"。

**为什么必须三色、只用 seen 不行：** 举个反例：0→1、2→1、2…… 设图 `[[1],[2],[1]]`（0→1, 1→2, 2→1）。点 1 被两条路径共享，但 0→1→2→1 不构成从 0 出发的祖先环吗？这里 1 确实在路径上，构成环。真正区分的场景是菱形：0→1、0→2、1→3、2→3。从 0 出发先走 0→1→3，3 彻底搜完（黑）；回溯后走 0→2，2 的邻居 3 是黑点——若只记"访问过"，你没法区分"3 是我祖先（环）"还是"3 是别的岔路已完工的点（不是环）"。灰色专门标记"还在我的路径上"，黑色标记"已完工、无罪"，两者缺一不可。

**克隆为什么对环成立：** 任何节点要被第二次访问时（也就是环绕回来的那一刻），它必然已经在 mapping 里了，我们直接接上第一次创建的那个新节点，不会无限复制下去。

**复杂度（用具体数字感受）：** 全部算法都是每点处理一次、每边扫一次，时间 O(V+E)，空间 O(V)（访问状态和栈）。10 万个点、20 万条边的图约 30 万次基本操作，毫秒级。岛屿是网格版：O(RC)，300×300 的网格是 9 万格，同样瞬间。深图（比如一条 10 万长的链）正是本章全用迭代不用递归的原因——递归 10 万层早就 RecursionError 了。

## 六、测试用例在测什么

```python
assert count_components(0,[])==0 and count_components(4,[])==4
```
两个**边界值**：0 个点当然是 0 块；4 个点 0 条边，人人孤立，必须是 4 块。这条抓"空图崩溃"和"忘算孤立点"两类 bug。

```python
assert has_directed_cycle([[0]]) and not has_directed_cycle([[1,2],[2],[]])
```
自环（0 指向自己，一步就绕圈）必须算有环；链 0→1→2 无环。自环是判环实现最容易漏的特例。

```python
assert num_islands([list('110'),list('001')])==2
```
正常值：两片不相连的陆地。注意两片在对角方向"擦肩而过"（(0,1) 和 (1,2) 对角相邻），但网格不许走对角线，所以是 2 座岛——这条同时测了方向规则。

```python
x,y=GraphNode(7),GraphNode(7); x.neighbors=[x,y]; y.neighbors=[x]
a=clone_graph(x)
assert a is not x and a.val==7 and a.neighbors[0] is a
assert a.neighbors[1] is not y and a.neighbors[1].neighbors[0] is a
```
克隆的**特殊值**测试：两个节点 val 都是 7（测身份区分）；x 有自环（测环不死循环）。`a is not x` 确认真是新对象不是原对象；`a.neighbors[0] is a` 确认自环结构保真；`a.neighbors[1] is not y` 确认没有把原节点直接挂进新图。

```python
for mask in range(1<<len(pairs)): ... assert count_components(n,edges)==len(groups)
```
**穷举对拍**：4 个点的所有无向简单图（6 种可能点对 × 有/无 = 2⁶=64 种，用位掩码枚举）。对每个图，用 Floyd 传递闭包算出所有点的可达关系，按"能互达"分组数出标准答案，再和 count_components 对比。64 个图覆盖了所有 4 点图结构，任何数错分量的实现都逃不掉。

## 七、练习思路提示

**练习 1（用迭代 DFS 避免深递归）：** 思路方向：写一个递归版 count_components，再和本章的栈版对比。提示：构造一条长链（0—1—2—…—99999），递归版会直接 RecursionError，栈版稳如泰山；如果想在递归版里活下来，可以查 `sys.setrecursionlimit`，但要想清楚为什么"调大限制"只是掩盖问题。先手算一条 5 个点的链在栈版里的出入栈顺序，再运行验证。

**练习 2（有向 vs 无向判环条件）：** 思路方向：无向图判环不需要三色，只需要"回到非父非自身的已访问点"。提示：DFS 时把父亲（来的那个点）传下去，遇到邻居等于父亲就跳过——因为"走回去再走回来"用每条边两次，不是环。但有向图里"父边豁免"不成立，比如重边或平行路径场景。可以拿 `[[1],[0]]`（无向存成双向后 0 和 1 之间有两条记录）和菱形图 `[[1,2],[3],[3],[]]` 做手算例子，分别预测两个版本（有向三色 vs 无向父边）的输出再验证。

## 八、对应 LeetCode 题目

- **200. Number of Islands（canonical）：** 就是本章的 num_islands，练"网格即隐式图 + 洪泛 + 数启动次数"。
- **547. Number of Provinces（canonical）：** 就是 count_components 换了个城市背景（isConnected 矩阵形式给边），练"邻接矩阵输入下的连通分量计数"。
- **133. Clone Graph（canonical）：** 就是本章的 clone_graph，练"映射表复制节点 + 处理环与共享邻居"，GraphNode 接口与 LeetCode 完全一致。
