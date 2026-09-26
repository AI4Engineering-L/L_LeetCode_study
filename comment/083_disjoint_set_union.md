# N083 · 并查集与动态连通性 —— 说人话详解

> 对应 notebook：`notebooks/11_graphs/083_disjoint_set_union.ipynb`

## 一、这章要解决什么问题？（问题描述）

想象 n 个点一开始各自孤立，然后一条一条地给你边，随时可能问你"这两个点现在连通吗？"或者"现在一共分成几伙？"。用 DFS 每问一次全图重跑，边多时太慢。**并查集（DSU）**换一种活法：它不存整张图，只给每个团伙维护一个"代表"，合并就改挂靠关系，查询只需看两个点的代表是否同一个。

本章三个具体问题：

1. **DSU 基本操作：** 5 个点 0..4，依次合并 (0,1)、(1,2)、(3,4)、(0,2)、(2,4)。前三条是真合并（团伙从 5 变 4、3、2）；第四条 (0,2) 是重复连接——0 和 2 早已同伙，合并失败返回 False，团伙数不变；第五条 (2,4) 把最后两伙并成一伙，团伙数变 1。
2. **找冗余边（树加一条边成环）：** 给一个无向图，它本来是一棵树多加了恰好一条边。问按输入顺序**最后出现**的那条"多余边"。例子：`[[1,2],[1,3],[2,3]]` → 答案 `[2,3]`——加 (1,2)、(1,3) 时都还是森林，加 (2,3) 时发现 2 和 3 已经连通，这条边就是冗余的。
3. **账户合并：** 每个账户是 `[姓名, 邮箱1, 邮箱2, ...]`，**两个账户只要共享任何一个邮箱，就是同一个人**，要合并它们（姓名相同但邮箱毫无交集的算不同账户）。例子：`[['John','a@x','b@x'], ['John','b@x','c@x'], ['John','z@x']]` → 合并前两个（共享 b@x），输出 `[['John','a@x','b@x','c@x'], ['John','z@x']]`。注意"都叫 John"本身不能说明是同一人——z@x 那个 John 就独立保留。

## 二、关键概念（定义）

- **并查集（DSU / Union-Find）：** 维护"哪些点属于同一伙"的数据结构。它不关心边的具体连法（那是邻接表的活），只回答"你们连通吗"——所以叫"只维护等价类"。
- **代表（根 / root）：** 每个团伙选一个固定成员当队长。判断两点是否同伙 = 判断它们向上找到的根是否相同。根就是 parent 指针一路向上、指向自己的那个节点。
- **parent 数组：** `parent[x]` 存 x 的上级。初始 `parent[x]=x`，人人自成一伙、自己就是根。
- **find(x)：** 沿 parent 一路向上爬到根，返回根编号。两个 find 结果相等 ⟺ 两点连通。
- **union(a,b)：** 先分别找根；根相同说明早就是一伙，返回 False 什么也不做；根不同才把一个根挂到另一个根下面，返回 True。
- **路径压缩（path compression）：** find 爬树时顺手把沿途节点的 parent 改成"祖父"（隔一代一跳），树被越压越扁。本章用的是**路径减半**写法：`parent[x]=parent[parent[x]]`，一次改一跳，效果同样是让后续 find 越来越接近 O(1)。
- **按大小合并（union by size）：** 合并两棵树时，永远把**小的**那棵挂到**大的**那棵的根下，并累加大树的 size。这样树的高度被控制在很矮的水平，防止退化成一条长链。
- **均摊代价（amortized）：** 单次操作偶尔要爬几层，但路径压缩把路铺平了，之后的操作都便宜。m 次操作的总代价是 O(m·α(n))，其中 α 是增长极慢的反阿克曼函数——n 在天文数字级别时 α 也不超过 4，实践中当常数看待。
- **连通块计数（components）：** DSU 顺手维护的计数器：初始等于 n（人人一伙），每次 union 成功（返回 True）减 1。想随时知道"几伙"，读这个数即可，不用重新扫。
- **等价类：** "连通"这种关系满足自反、对称、传递，所以同伙的点构成一个等价类。DSU 干的就是动态维护这些类。

## 三、解决思路（一步步推导）

**Step 1：初始化。** parent = [0,1,...,n-1]（人人是自己的根），size 全 1，components = n。

**Step 2：find 带路径减半。** 爬树时每一步先 `parent[x]=parent[parent[x]]` 再上移，让树越用越扁。

**Step 3：union 按大小挂接。** 两根不同时，小树挂大树，size 累加，components 减 1，返回 True；两根相同直接 False。

**Step 4：应用层把"连接证据"翻译成 union。** 冗余边：逐条 union，第一条返回 False 的边（保留最后一次的写法是不断覆盖 answer）就是答案。账户合并：邮箱是证据——第一次见到的邮箱记下所属账户编号，再次遇到同一邮箱就把两个账户 union 起来。

**手算演示（notebook 小实例：DSU(5) 依次 union (0,1),(1,2),(3,4),(0,2),(2,4)）：**

| 合并 | 是否新连接 | 分量数 | 各顶点代表 [0..4] |
|---|---|---|---|
| (0,1) | True | 4 | [0, 0, 2, 3, 4] |
| (1,2) | True | 3 | [0, 0, 0, 3, 4] |
| (3,4) | True | 2 | [0, 0, 0, 3, 3] |
| (0,2) | False | 2 | [0, 0, 0, 3, 3] |
| (2,4) | True | 1 | [0, 0, 0, 0, 0] |

逐行看懂它你就懂了 DSU：第一行 0 和 1 都是一人团伙，size 相等不满足 `size[a]<size[b]`，所以 0 当根、1 挂 0。第二行 find(1)=0（size 2）对 find(2)=2（size 1），小挂大，2 挂到 0 下。第四行 (0,2)：find(0) 和 find(2) 都爬到 0，同根，返回 False——这就是"重复 union 不能减少分量数"。第五行把 {0,1,2} 和 {3,4} 两棵树并成一棵，全员代表变 0。

**手算演示（find_redundant_connection([[1,2],[1,3],[2,3]])）：** 建大小为 4 的 DSU（下标 0..3，人 1..3）。union(1,2) True、union(1,3) True——此刻 1、2、3 已成一伙。union(2,3)：find(2)==find(3)，返回 False，answer 被覆盖为 [2,3]。输出 [2,3]，正好是输入中最后那条多余的边。

## 四、代码逐段讲解

**第一段：DSU 类——路径减半 + 按大小合并。**

```python
class DSU:
    def __init__(self,n): self.parent=list(range(n)); self.size=[1]*n; self.components=n
    def find(self,x):
        while self.parent[x]!=x:
            self.parent[x]=self.parent[self.parent[x]]; x=self.parent[x]
        return x
    def union(self,a,b):
        a=self.find(a); b=self.find(b)
        if a==b: return False
        if self.size[a]<self.size[b]: a,b=b,a
        self.parent[b]=a; self.size[a]+=self.size[b]; self.components-=1
        return True
```

- `__init__` 三件事：parent 指向自己（`list(range(n))` 一行生成 [0,1,...,n-1]）；size 全 1；components 初始 n。size 记的是"以这个根为首的团伙人数"。
- `find` 的 while 循环：`self.parent[x]!=x` 表示 x 还不是根，继续爬。循环体第一句 `self.parent[x]=self.parent[self.parent[x]]` 是路径减半——把 x 直接挂到它祖父（上级的上级）名下，跳过了一层；第二句 `x=self.parent[x]` 上移一步（注意此时已是新祖父）。爬完返回根。由于每步都压缩，第二次 find 同一个点几乎一步到位。
- `union` 先把 a、b **替换成各自的根**（后面操作的都是根，不是原节点）。
- `if a==b: return False`：同根即已连通，不动任何东西，返回"这次没合并"。这个返回值是冗余边问题直接依赖的信号。
- `if self.size[a]<self.size[b]: a,b=b,a`：交换保证 a 永远是较大（或相等）团伙的根。接着 `parent[b]=a` 小挂大；`size[a]+=size[b]` 人数累加（只有大树的 size 是准的，b 的旧 size 从此没人看）；`components-=1` 两伙并一伙；返回 True。
- 为什么 size 挂接控制树高：小挂大保证任何节点到根的距离每次合并最多增加很小，树高被压在 O(log n) 内；再叠加路径压缩，实际几乎扁平。

**第二段：find_redundant_connection——第一条/最后一条失败边。**

```python
def find_redundant_connection(edges):
    dsu=DSU(max((max(e) for e in edges),default=0)+1); answer=[]
    for u,v in edges:
        if not dsu.union(u,v): answer=[u,v]
    return answer
```

- `max((max(e) for e in edges),default=0)+1`：先求所有边里出现过的最大编号，开"最大编号+1"个槽；`default=0` 挡**空边列表**——没有边时 max 会抛错，默认值 0 让 DSU 至少开 1 个槽，函数平静返回 []。
- 循环里 `if not dsu.union(u,v): answer=[u,v]`：union 返回 False 意味着这条边连接的两个点早已连通——这条边在树上多余。注意是**覆盖赋值**而不是 return：题目要"按输入顺序最后出现的冗余边"，所以每次失败都更新 answer，循环跑完留下的就是最后一条。
- 本题模板保证恰好一条多余边；即使输入有多条失败边，这个"保留最后一条"的语义也和 LeetCode 684 的要求一致。

**第三段：accounts_merge——以共享邮箱为合并证据。**

```python
def accounts_merge(accounts):
    dsu=DSU(len(accounts)); owner={}
    for i,account in enumerate(accounts):
        for email in account[1:]:
            if email in owner: dsu.union(i,owner[email])
            else: owner[email]=i
    groups={}
    for i,account in enumerate(accounts): groups.setdefault(dsu.find(i),set()).update(account[1:])
    return [[accounts[root][0],*sorted(emails)] for root,emails in sorted(groups.items())]
```

- 顶点是**账户编号**（0..len-1），不是邮箱——DSU 合并的是账户。
- `owner` 是"邮箱 → 第一次见到它时的账户编号"。遍历每个账户的邮箱（`account[1:]` 跳过第 0 位的姓名）：邮箱第一次出现就登记归属；再出现（哪怕在别的账户里）就 `union(i, owner[email])`——共享邮箱是同一个人的证据。
- 第二遍循环归堆：`groups.setdefault(dsu.find(i),set())` 取"该账户根"对应的集合（没有就建空集合），`.update(account[1:])` 把这个账户的全部邮箱并进去。同伙账户会落到同一个根下、邮箱自动并成一堆。
- 最后一行组装输出：每个团伙的姓名取根账户的姓名（`accounts[root][0]`，同伙账户姓名按题意相同）；`*sorted(emails)` 是星号解包，把排序后的邮箱逐个展开进列表；`sorted(groups.items())` 按根编号排输出顺序，保证结果确定、可测试。
- 关键认知：**同名不是证据，共享邮箱才是**。都叫 John 但邮箱不相交的账户保持独立（z@x 那位）。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么"根相同"准确等于"已连通"：** union 只在两根不同时把它们接起来，所以任何时刻，parent 指针形成的每一棵树恰好就是一个连通团伙；find 爬到的根就是这棵树的唯一标识。同伙必同根、同根必同伙，一一对应。

**为什么重复 union 无害且被识别：** 已经连通的两点 find 出同一个根，`a==b` 分支直接返回 False，团伙结构一个字节都没动，components 也不会错减。反过来，返回 False 这件事本身就是"这条边是多余的"的证明——它闭合了一条已经存在的路径。

**为什么路径压缩不改变团伙划分：** 压缩只把节点改挂到"自己祖先链上的更高层"，最终爬到的根不变。根没变，"谁和谁同根"的答案就没变——我们只是把通往根的路抄了近道，团伙本身纹丝不动。

**为什么按大小合并防退化：** 每次都是小树挂大树，意味着一个节点想要"变深"，它所在的团伙至少得翻倍。所以任何节点到根的距离最多是 O(log n)（1 万个点最多约 14 层）。两个优化叠在一起，m 次操作总代价 O(m·α(n))。拿具体数字感受：n = 10⁵、m = 10⁶ 次操作，α(n) 约等于 4，总共约四百万次基本操作，一瞬间跑完；而每次全图 DFS 的做法做 10⁶ 次查询就是 10⁶ × (10⁵+边数) 次，完全不可比。

**普通 DSU 不支持删边：** union 只会"接起来"，没有"拆开"操作——parent 指针一改就是永久合并。想要支持删除得用更复杂的结构或离线倒序处理，cell4 特意说明这是能力边界。

## 六、测试用例在测什么

```python
d=DSU(3); assert d.union(0,1) and not d.union(1,0) and d.components==2
```
正常值 + 去重语义：union(0,1) 首次连接返回 True；union(1,0) 参数顺序反过来也一样返回 False（连通是对称的，与书写顺序无关）；components 恰好从 3 减到 2——重复合并不多减。这条抓"重复 union 错误地再减一次计数"的经典 bug。

```python
assert find_redundant_connection([[1,2],[1,3],[2,3]])==[2,3]
```
第三节手算过的最小三角形：前两条边搭成树，第三条 (2,3) 闭合成环，答案必须是它。测"冗余 = 使已连通两点再次相连的边"这一定义。

```python
accounts=[['John','a@x','b@x'],['John','b@x','c@x'],['John','z@x']]
out=accounts_merge(accounts); assert sorted(out)==[['John','a@x','b@x','c@x'],['John','z@x']]
```
正常值 + **关键语义检查**：三个账户全叫 John。前两个共享 b@x 必须合并；第三个虽然同名但邮箱不相交必须独立。如果实现用"姓名相同就合并"，这条立即失败。sorted(out) 排序后比对，避免依赖账户输出顺序。

```python
rng=Random(83); d=DSU(8); adj=[set() for _ in range(8)]
for _ in range(100):
    u,v=rng.randrange(8),rng.randrange(8); d.union(u,v); adj[u].add(v); adj[v].add(u)
    for s in range(8):
        seen={s}; stack=[s]
        while stack:
            for t in adj[stack.pop()]:
                if t not in seen: seen.add(t); stack.append(t)
        assert all((d.find(s)==d.find(t))==(t in seen) for t in range(8))
```
**随机对拍**：随机做 100 次 union（允许重复、允许自环），同时维护一份真实邻接表；每做一次，对每个起点 s 用 DFS 算出真实可达集合 seen，然后断言"DSU 说同根 ⟺ 真实可达"对全部 8×8 点对成立。这个测试每加一条边就全量复核一次等价性，是把"DSU 维护的划分 == 图的真实连通划分"这条不变量直接当成断言来跑——通过它，路径压缩和按大小合并的每一步都没破坏正确性。

## 七、练习思路提示

**练习 1（连通性查询 vs 路径查询）：** 思路方向：想清楚 DSU 只答"通不通"，不答"怎么通"。提示：构造一棵树（比如 8 个点的链），分别问"5 和 7 连通吗"（DSU 一次 find 比较，瞬间）和"从 5 到 7 的路径是什么"（DSU 无能为力，得靠邻接表 DFS/BFS）。手算示例：链 0—1—2—…—7，5 和 7 连通 True、路径 [5,6,7]；把实现写成两个函数对比，结论落成一句话：要路径就得存图（N079 的邻接表 + N080 的搜索），只要连通性 DSU 更省。

**练习 2（普通 DSU 不能删边）：** 思路方向：找一个小反例演示"合并容易拆分难"。提示：union(0,1)、union(1,2) 之后，parent 里 2 挂 1、1 挂 0（或按大小 0 为根）；现在想删掉边 (0,1)，你会发现 1 和 2 的连通性信息与 0 和 2 的纠缠在同一个树结构里，光改一两个 parent 无法恢复"删边后的正确划分"。手算示例：删掉 (0,1) 后 0 应孤立、1 和 2 仍连通——试着在纸上改 parent 数组达到这个效果，体会为什么做不到。顺带了解两个补救方向：离线倒序把删变加、或用按大小分裂的更复杂结构（本章不要求实现）。

## 八、对应 LeetCode 题目

- **684. Redundant Connection（canonical）：** 就是本章的 find_redundant_connection，练"union 返回 False 即冗余边"的信号用法。
- **721. Accounts Merge（canonical）：** 就是本章的 accounts_merge，练"以共享元素为合并证据建 DSU、再按根归堆输出"的两遍扫描套路。
- **1319. Number of Operations to Make Network Connected（canonical）：** 用 DSU 数出连通分量数 c，答案就是 c−1（把 c 伙连成一体最少要 c−1 条线）；同时用"冗余边数是否 ≥ c−1"判断可行性——练 components 计数器和 union 返回值的组合应用。
