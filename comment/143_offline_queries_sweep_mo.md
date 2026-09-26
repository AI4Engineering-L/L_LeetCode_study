# N143 · 离线查询、扫描线与Mo算法 —— 说人话详解

> 对应 notebook：`notebooks/17_advanced_algorithms/143_offline_queries_sweep_mo.ipynb`

## 一、这章要解决什么问题？（问题描述）

有一类题目会一次给你"一堆对象 + 一堆询问"，允许你把所有询问读完、想按什么顺序算就按什么顺序算，最后把答案按原来的编号摆回去。这就叫**离线（offline）**。与之相对的是在线接口：问一条必须立刻答一条，而且你不知道后面还会问什么——本章的方法对那种场景无能为力（cell1 特意强调了这一点）。

为什么"换个顺序算"这么值钱？看三个具体场景（输入 → 输出 → 为什么）：

1. **区间覆盖询问**：输入区间组 `[[1,4],[2,4],[3,6],[4,4]]` 和询问 `[2,3,4,5]`，对每个询问 q 找"包含 q 的最短区间长度"。输出 `[3,3,1,4]`。比如 q=4：包含 4 的区间有 [1,4](长4)、[2,4](长3)、[3,6](长4)、[4,4](长1)，最短是 [4,4]，长度 1。如果每个询问都扫全部区间，是 O(询问×区间)；把询问从小到大排序后"扫描线"一趟就能全答完。
2. **限边权连通性**：输入 2 个点、边 (0,1,2)（权重 2），询问 (0,1,2) 和 (0,1,3)——"只走权重**严格小于** limit 的边，u、v 是否连通"。输出 `[False, True]`。limit=2 时边权 2 不许用，所以不通；limit=3 时这条边能用，通了。把询问按 limit 排序、边也按权重排序，就是"逐渐往并查集里加边"的一趟扫描。
3. **区间不同数个数**：输入数组 `[1,2,1,3,2,4]`，半开区间询问 `[(2,6),(0,3),(1,5),(0,3),(4,4)]`，输出 `[4,2,3,2,0]`。比如 (2,6) 取 `nums[2:6]=[1,3,2,4]`，四个互不相同，答案是 4；(4,4) 取空段，答案是 0。静态数组 + 区间统计正是 Mo 算法的主场。

## 二、关键概念（定义）

- **离线（offline）**：先把全部询问拿到手，重排计算顺序，最后按原编号还原答案。代价是"查询编号"必须全程跟着走（本章代码里到处都是 `original`/`i` 就是在干这个）。
- **扫描线（sweep）**：把对象和询问都按同一个关键量（左端点、边权、limit……）从小到大排，然后一根"扫描指针"推过去；推到某位置时，数据结构里恰好装着"所有满足当前阈值的对象"。这就是 cell4 说的核心不变量。
- **候选堆**：`min_interval` 里用小根堆装"已经覆盖当前 q 的区间"，以 (长度, 右端点) 为键。堆顶就是当前最短者；但堆里可能残留右端点已经"过期"（右端点 < q）的区间，读答案前要先把过期堆顶弹掉。
- **离线 DSU / 并查集（union-find）**：DSU 是"几个集合各自认一个代表元，合并只需改一条父指针"的结构。`find(x)` 找代表元，`union(a,b)` 合并两集合。配合按大小合并 + 路径减半（`parent[x]=parent[parent[x]]` 这句），单次操作几乎常数。限边权问题里"只加边、不删边"的特性正好匹配 DSU 只会合不会分的特性。
- **Mo 算法**：把询问的左右端点当成一个"窗口 [left, right)"，让窗口在数组上缓慢滑动去依次对准每个询问。每次只做"窗口边缘加一个元素/减一个元素"的增量更新。窗口怎么排顺序？按"左端点所在的块号"排序，块内再按右端点排（奇偶块反向，代码里那个 `%2==0` 分支）。这样总移动量是 O((N+Q)√N) 级别。
- **平方分块（√N 分块）**：把数组切成每块长约 √N 的段。经典结论：左端点同块的询问，右端点单调走一遍数组最多 N 步；跨块的左端点每次最多跳 √N 步。两项合计 √N 块 × N + Q × √N。
- **可逆增删**：Mo 的窗口更新必须"加一个元素能准确算，减一个元素也能准确撤销"。本章维护的统计是"每个值出现次数的字典 counts + 当前不同值个数 distinct"，加减都是 O(1) 字典操作，完全可逆。

## 三、解决思路（一步步推导）

### 场景一：min_interval 的扫描线

**Step 1**：区间按左端点排序，询问按 q 排序（同时记下原编号）。**Step 2**：q 从小到大扫。q 变大时，"左端点 ≤ q"的区间只增不减（单调性！），所以一个 index 指针只前进地把新区间压进堆，堆里就装着"左端点合格"的区间。**Step 3**：再弹掉堆顶那些"右端点 < q"的（不再覆盖 q），堆顶的长度就是答案。堆深处可能还埋着过期区间，但没关系——它们比堆顶更长，永远不会被读到（cell4 特意解释了"允许保留非顶端过期区间"）。

手算 `[[1,4],[2,4],[3,6],[4,4]]`、询问 `[2,3,4,5]`：q=2 时压入 [1,4]、[2,4]，最短是 [2,4] 长 3；q=3 时再压 [3,6]，最短仍是 3；q=4 时压入 [4,4]，它长 1 且覆盖 4，答案 1；q=5 时 [4,4]、[2,4]、[1,4] 的右端点都小于 5 被依次弹掉，只剩 [3,6]，长 4。四个答案 3、3、1、4，与 cell8 断言一致。

### 场景二：限边权连通性

**Step 1**：边按权重升序排，询问按 limit 升序排。**Step 2**：limit 单调增大时，"权重 < limit"的合格边集合只增不减——又是一条单调扫描线！一个 index 指针把所有权重 < 当前 limit 的边 union 进 DSU。**Step 3**：此刻 `find(u)==find(v)` 就是答案。

手算 `n=2, edges=[(0,1,2)], queries=[(0,1,2),(0,1,3)]`：第一个询问 limit=2，没有边权严格小于 2，DSU 里 0、1 各自为政，False；第二个询问 limit=3，边权 2 < 3，union(0,1)，True。输出 `[False, True]`。注意"严格小于"这个细节，练习 1 就拿它做文章。

### 场景三：Mo 算法求区间不同数

**Step 1**：验证询问合法（`0<=l<=r<=n`，半开区间）。**Step 2**：按 (左端点块号, 块内右端点，奇偶块方向相反) 排询问。n=6 时 block=isqrt(6)=2，cell6 的五个询问排出来顺序是 [1,2,3,0,4]（q1、q2、q3 左端点都在 0 号块按 r 升序，q0 在 1 号块反向，q4 在 2 号块）。**Step 3**：窗口从空 [0,0) 出发，四个 while 把窗口 edges 一点点挪到 [l,r)：左边要扩就 add，右边要缩就 remove，全程 counts/distinct 增量更新。

手算 cell6（nums=[1,2,1,3,2,4]）：先处理 (0,3)，加 nums[0..2]={1,2,1}，counts={1:2,2:1}，distinct=2，答案 2 ✓；挪到 (1,5) 时 remove(nums[0])、add nums[3]、nums[4]，counts={2:2,1:1,3:1}，distinct=3 ✓；挪回 (0,3) 时加回 nums[0]、删掉 nums[4] 和 nums[3]，distinct 回到 2 ✓；再挪到 (2,6)，删 nums[0]、nums[1]，加 nums[5]，counts={1:1,3:1,2:1,4:1}，distinct=4 ✓；最后 (4,4) 全删光，distinct=0 ✓。最终 `[4,2,3,2,0]`，正是 cell6 表格展示的五 行（也是暴力 `len(set(nums[l:r]))` 的结果）。注意第 4 步"挪回去再删光"正是 Mo 的日常：窗口来回蹭，靠的就是 add/remove 完全可逆。

## 四、代码逐段讲解

### 前置：DSU 类

```python
class DSU:
    def __init__(self,n): self.parent=list(range(n)); self.size=[1]*n; self.components=n
```

开始时每个点自成一个集合（父指针指向自己），size 记集合大小，components 记当前集合个数。

```python
    def find(self,x):
        while self.parent[x]!=x:
            self.parent[x]=self.parent[self.parent[x]]; x=self.parent[x]
        return x
```

顺着父指针爬到根。爬的过程中顺手 `parent[x]=parent[parent[x]]`：把 x 直接挂到爷爷下面（路径减半），下次再查就短一半，防止链长了退化成 O(n)。

```python
    def union(self,a,b):
        a=self.find(a); b=self.find(b)
        if a==b: return False
        if self.size[a]<self.size[b]: a,b=b,a
        self.parent[b]=a; self.size[a]+=self.size[b]; self.components-=1
        return True
```

先找两边的根；根相同说明本来就在一个集合，返回 False。否则保证 a 是较大的集合，把小集合的根 b 挂到 a 下（按大小合并，防止越并越深的链）。返回 True 表示真的发生了合并。

### 函数一：`min_interval(intervals, queries)`

```python
def min_interval(intervals,queries):
    intervals=sorted(intervals); heap=[]; index=0; answer=[-1]*len(queries)
    for q,original in sorted((q,i) for i,q in enumerate(queries)):
```

区间按左端点排；询问排成 (q, 原编号) 对按 q 升序遍历。answer 默认全 −1（"没有区间覆盖"的答案）。

```python
        while index<len(intervals) and intervals[index][0]<=q:
            l,r=intervals[index]; heappush(heap,(r-l+1,r)); index+=1
```

把所有左端点 ≤ q 的区间压堆，键是 (长度, 右端点)——堆顶自动是"最短的、其次右端点更大的"区间。index 只前进，因为 q 单调增大后左端点合格的集合只会更多。

```python
        while heap and heap[0][1]<q: heappop(heap)
        if heap: answer[original]=heap[0][0]
    return answer
```

弹掉堆顶右端点 < q 的（不再覆盖 q）。剩下的堆顶长度写回 `answer[original]`——注意必须写回原编号位置，这就是"离线重排后按 ID 恢复结果"。

### 函数二：`distance_limited_paths_exist(n, edges, queries)`

```python
def distance_limited_paths_exist(n,edges,queries):
    edges=sorted(edges,key=lambda e:e[2]); ordered=sorted(enumerate(queries),key=lambda x:x[1][2]); dsu=DSU(n); index=0; answer=[False]*len(queries)
```

边按第 3 个分量（权重）排；询问也按 limit（第 3 个分量）排，enumerate 保住原编号。

```python
    for original,(u,v,limit) in ordered:
        while index<len(edges) and edges[index][2]<limit:
            a,b,w=edges[index]; dsu.union(a,b); index+=1
        answer[original]=dsu.find(u)==dsu.find(v)
    return answer
```

注意判据是 `edges[index][2]<limit`（严格小于），与题意"边权严格小于 limit"逐字对齐。加完所有合格边后，u、v 同根即连通。

### 函数三：`mo_distinct_counts(nums, queries)`

```python
def mo_distinct_counts(nums,queries):
    n=len(nums); block=max(1,isqrt(n)); answer=[0]*len(queries)
    if any(not 0<=l<=r<=n for l,r in queries): raise IndexError('half-open query outside array')
```

块长取 √n（n=0 时 max(1,…) 兜底为 1）。任何一个询问越界（l<0、r>n 或 l>r）立即报错——这是输入契约。

```python
    order=sorted(range(len(queries)),key=lambda i:(queries[i][0]//block,queries[i][1] if queries[i][0]//block%2==0 else -queries[i][1]))
```

Mo 的排序键：先按左端点所在块号，块内偶数块按 r 升序、奇数块按 r 降序。奇偶交替（"奇偶优化"）让右端点在块间呈"锯齿形"往返而不是每块都从头扫一遍，实测能省近一半移动量。

```python
    counts={}; left=right=0; distinct=0
    def add(i):
        nonlocal distinct
        x=nums[i]; counts[x]=counts.get(x,0)+1
        if counts[x]==1: distinct+=1
    def remove(i):
        nonlocal distinct
        x=nums[i]; counts[x]-=1
        if counts[x]==0: distinct-=1; del counts[x]
```

窗口是半开区间 [left, right)。add：值计数 +1，从 0 变 1 说明新出现一种值，distinct+1。remove：计数 −1，变 0 说明这种值在窗口里绝迹，distinct−1 并顺手 `del` 掉键，让字典只保留窗口内出现过的值。

```python
    for i in order:
        l,r=queries[i]
        while left>l: left-=1; add(left)
        while right<r: add(right); right+=1
        while left<l: remove(left); left+=1
        while right>r: right-=1; remove(right)
        answer[i]=distinct
    return answer
```

四个 while 的顺序有讲究：先做两个"扩"的方向（不会让区间暂时非法），再做两个"缩"的方向，保证中途 left ≤ right 永不破坏。窗口对准 [l,r) 后，distinct 就是该询问的答案，写回 answer[i]。

## 五、为什么是对的？复杂度是多少？（说人话）

**扫描线为什么对？** 关键在于"单调性 + 不变量"：q（或 limit）是从小到大走的，"左端点 ≤ q"的区间集合、"权重 < limit"的边集合都只会变大不会变小，所以那个只前进不后退的 index 指针不会漏掉任何对象；而在回答每个询问之前，数据结构里装的恰好是"全部合格对象"（对堆来说还要再清一次过期堆顶）。一句话：**扫到哪个阈值，结构里就是哪个阈值该有的东西**。

**Mo 为什么对？** add/remove 每次都精确同步 counts 和 distinct，所以无论窗口怎么绕路，"窗口对准 [l,r) 的那一刻，distinct 恰好等于该段不同数个数"。处理顺序只影响挪窗口要花多少步，不影响最终每条询问读到什么——这就是 cell4 说的"处理顺序只影响代价，不改变目标窗口统计"。

**复杂度，代入数字感受一下：** 前两个算法都是"排序 + 线性扫描"：设对象 N 个、询问 Q 个，排序 O((N+Q)log(N+Q))，扫描中每个对象只进出结构一次、堆/DSU 操作近似 O(log) 或反Ackermann，总体 O((N+Q)log(N+Q)) 级别。N=Q=10⁵ 时约 10⁵×17≈170 万量级的排序比较，秒级。Mo 是 O((N+Q)√N)：N=Q=10⁵ 时 √N≈316，总移动量约 10⁵×316 ≈ 3×10⁷ 次 O(1) 更新，几秒内跑完——比暴力（每次询问 O(N)，共 10¹⁰ 次）快三百倍，但注意它**并不**是 O((N+Q)logN) 级别的，这是 Mo 和线段树类解法的分野。空间上 Mo 要存 Q 个答案和 counts 字典，O(N+Q)。

## 六、测试用例在测什么

- `assert min_interval([[1,4],[2,4],[3,6],[4,4]],[2,3,4,5])==[3,3,1,4]`：正常值，第三节手算过。q=4 那条顺带覆盖了"堆顶过期弹出"（右端点等于 q 的边界：[2,4] 在 q=4 时仍有效，q=5 时才被弹）。
- `assert distance_limited_paths_exist(2,[(0,1,2)],[(0,1,2),(0,1,3)])==[False,True]`：专测"严格小于"边界——边权 2 在 limit=2 时不可用、limit=3 时可用，一假一真把 `<` 和 `<=` 的区别焊死。
- `assert mo_distinct_counts([],[(0,0)])==[0]`：空数组 + 空窗口，答案 0。极小边界。
- 随机对拍段一（100 轮）：数组长 20、值域 0..6（故意让重复多），25 条随机半开询问，标准答案直接 `len(set(nums[l:r]))`；同时随机 8 个区间、12 个询问测 `min_interval`，暴力答案是 `min(所有覆盖 q 的区间长度, 默认 -1)`——`default=-1` 正好对应"无覆盖"的语义。
- 随机对拍段二（80 轮）：6 个点、12 条随机边、12 条随机限权询问，暴力解是对每条询问做 BFS（只许走 w≥limit 之外即 w<limit 的边）看终点可达性。多轮随机保证覆盖"自环边、重边、limit 大于所有边权"等情况。
- `print('N143: 所有本章断言通过')` 前的任何一条不相等都会让 assert 当场报错停机。

## 七、练习思路提示

**练习 1（严格小于 vs 小于等于）：** 提示：找一条"边权恰好等于 limit"的最小反例就行——比如 n=2、边 (0,1,5)、询问 (0,1,5)：严格小于返回 False，小于等于返回 True。写清楚两种语义各自的输入输出契约，然后论证：把代码里的 `edges[index][2]<limit` 改成 `<=` 只影响"权重 == limit 的边何时入场"，凡存在这种边的实例答案就会翻转。别忘了"无恰好相等边权的实例两者答案相同"这半边也要说。

**练习 2（自编离线区间去重计数）：** 提示：不调用 `mo_distinct_counts`，自己从零写：先定义输入（数组 + 半开区间列表）与输出（每条询问的不同数个数）；把"窗口移动四个 while + add/remove 字典"重写一遍；边界至少覆盖空窗口 (i,i)、整段 (0,n)、重复询问。对拍标准直接用 `len(set(nums[l:r]))`，随机 100 组确认一致后再解释为什么奇偶块排序能省移动量。

## 八、对应 LeetCode 题目

- **1851. Minimum Interval to Include Each Query（包含每个查询的最小区间）**：`min_interval` 的原题，练的是"询问排序 + 候选堆 + 过期堆顶清理"这条扫描线。
- **1697. Checking Existence of Edge Length Limited Paths（边权受限路径）**：`distance_limited_paths_exist` 的原题，练的是"边和询问双排序 + 只加不删的离线 DSU"，本质是 Kruskal 重建树的离线版。
- **315. Count of Smaller Numbers After Self（计算右侧小于当前元素的个数）**：另一类扫描线/离线树状数组（Fenwick）的代表——把"每个数右边更小的数"转成"按值离散化 + 从右往左扫、Fenwick 查前缀"，练的是本章"按阈值排序 + 树状数组"那条知识线（cell0 知识点里点名的 Fenwick）。
