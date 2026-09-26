# N090 · 欧拉路径与Hierholzer —— 说人话详解

> 对应 notebook：`notebooks/11_graphs/090_eulerian_paths.ipynb`

## 一、这章要解决什么问题？（问题描述）

欧拉路径是"**每条边恰好走一次**"的行走路线。注意它和哈密顿路径（每个点恰好一次）是两码事：欧拉关心的是边别重复用，点路过多少次都无所谓。经典出身是"哥尼斯堡七桥问题"：能不能不重不漏地把每座桥走一遍？

现代的包装是 LeetCode 332 机票行程问题：你有一叠机票 tickets，每张是从城市 A 到城市 B 的单程票（**可能有重复的票**，两张 JFK→A 就是两张独立的票，不能去重），行程必须从 JFK 出发，要求**把所有机票正好用完**，并且在使用同样全部机票的可行行程里选**字典序最小**的那一个。

给一个具体到数字的例子（notebook cell6 用的）：`tickets=[('JFK','KUL'),('JFK','NRT'),('NRT','JFK')]`。

- 你在 JFK 手里有两张票：去 KUL 的和去 NRT 的。
- 如果贪心地先飞字典序更小的 KUL：到了 KUL 发现**没有任何从 KUL 出发的票**，行程当场终止，手里还剩两张票没用——失败。
- 正确行程：JFK → NRT → JFK → KUL。三张票全用完，答案是 `['JFK','NRT','JFK','KUL']`。
- 这个例子说明"每步选字典序最小的票"这种纯贪心会卡死，我们需要一个能自我修复的算法——这就是本章的 Hierholzer 算法。

## 二、关键概念（定义）

- **欧拉路径（Eulerian path）**：经过图中每条边恰好一次的路径。如果它还回到起点（首尾相同），叫欧拉回路。
- **度条件（判定欧拉路径是否存在）**：对有向图，给每个点记 delta = 出边数 − 入边数。欧拉路径存在当且仅当：要么所有点的 delta 都是 0（对应欧拉回路，起点随便挑）；要么恰好有一个点 delta=+1（起点，出比入多一条，必须是出发地）、恰好一个点 delta=−1（终点）、其余全是 0。直觉：路从起点出发、在终点收尾，中途每到一个点就必须再离开一次，所以中途点进出必须配平。
- **Hierholzer 算法**：构造欧拉路径的经典算法。核心是"一直沿着还没用的边走，走到无路可走才把点记入答案（后序），最后把答案倒过来"。倒过来之后，中途卡死的那些"支路"会被自动拼接到正确的位置上。
- **后序构造（post-order）**：点是在"弹栈退出的时刻"（即它的所有出边都耗尽之后）才被追加到输出列表的，所以输出列表天然是路径的**逆序**，最后要 `[::-1]` 翻转。
- **局部回路的拼接直觉**：把行程想象成"主路 + 若干个套环"。DFS 先钻进一个环把它走完，退出的时机正好落回进入点，于是这个环可以作为一段插进主路。逆序输出正好实现了这种拼接。
- **字典序最小**：从 JFK 出发的可行行程可能有多个，比的是城市名序列的字典顺序（逐个位置比字符串）。实现技巧：每个点的出边**降序排序**，然后用 `pop()` 从**尾部**弹出——尾部正是最小的那个，等效于"每步优先走当前剩余出边里字典序最小的"。
- **多重边（重复边）**：两张相同的票是两条独立的边，各走一次。实现里邻接表是 list 而不是 set，天然保留重复；最后还要用计数器校验"每条边（含重复）都被恰好用了一次"。
- **Counter 校验（兜底防线）**：度条件合格不代表边全连通（比如两个互不相连的环各自配平）。算法最后用 `Counter(zip(path,path[1:]))`（路径实际使用的边及次数）对比 `Counter(map(tuple,edges))`（输入的边及次数），对不上就返回 None。这一步排除不连通和任何非法拼接。

## 三、解决思路（一步步推导）

- **Step 1（建图排序）**：把每条边 (u,v) 登记进邻接表 adj[u]；每个点的出边列表降序排序，让 pop() 总能拿到字典序最小的候选。
- **Step 2（选起点）**：度条件检查。有 delta=+1 的点就以它为起点（只能从这出发）；全配平（回路情形）就选一个确定的起点（通用接口选最小标签，机票题固定 'JFK'）。度条件不满足直接返回 None。
- **Step 3（栈式游走）**：栈顶点如果还有没用完的出边，就弹一条出边、把边的终点压栈（这条边就此消耗掉）；栈顶没边可走了，就把这个点弹出并**追加到 out 列表**（后序记录）。
- **Step 4（翻转）**：栈空后，out 是逆序答案，翻转变正序路径。
- **Step 5（校验）**：路径长度必须等于边数+1，且路径逐段构成的边多重集合和输入完全一致；不一致返回 None（不连通、走不全等情况在这里暴露）。

**手算演示**（机票例子，adj 排序后 JFK 的出边是 `['NRT','KUL']`，pop 从尾部弹）：

- 栈 ['JFK']。JFK 还有出边，pop 得 'KUL'（字典序最小的那条），压栈：['JFK','KUL']。
- 栈顶 KUL 没有任何出边——**卡死了**。但算法不慌：KUL 弹出记入 out=['KUL']，栈回到 ['JFK']。
- JFK 剩 ['NRT']，pop 'NRT' 压栈：['JFK','NRT']。NRT 的出边 ['JFK']，pop 压栈：['JFK','NRT','JFK']。
- JFK 出边耗尽，弹出，out=['KUL','JFK']。NRT 耗尽，out=['KUL','JFK','NRT']。最后 JFK 出栈，out=['KUL','JFK','NRT','JFK']。
- 翻转：path=['JFK','NRT','JFK','KUL']。**先钻进 KUL 死胡同的那一步，翻转后被排到了路径末尾**——这正是"局部回路插入完整行程"的魔力：你一开始的错误选择不会毁掉答案，只会被自动修正到最合理的位置。
- 校验：path 长 4 = 边数 3 + 1；三段边 {('JFK','NRT'),('NRT','JFK'),('JFK','KUL')} 与输入完全一致。通过。cell6 的表格展示的正是这 3 步：步骤1 JFK→NRT、步骤2 NRT→JFK、步骤3 JFK→KUL。

**再看一个含重复票的例子**（测试最后那个）：`edges=[('JFK','A'),('A','JFK'),('JFK','B'),('B','JFK'),('JFK','A')]`，两张 JFK→A 是两张独立的票。度全部配平（每个点出=入），从 'JFK' 出发走 Hierholzer，最终 path=['JFK','A','JFK','A','JFK','B','JFK']——两张 JFK→A 各用一次，且整体字典序最小（A 排在 B 前面用光）。

## 四、代码逐段讲解

### 核心函数：`_hierholzer(edges, start)`

```python
from collections import defaultdict,Counter

def _hierholzer(edges,start):
    adj=defaultdict(list)
    for u,v in edges: adj[u].append(v)
    for a in adj.values(): a.sort(reverse=True)
```

- `defaultdict(list)`：访问不存在的键会自动建空列表，省去初始化。注意用 **list 保留重复边**——两张相同机票必须是两条可分别消耗的边（用 set 会把它们合并，这就是 cell1 说的"重复机票不能去重"）。
- `a.sort(reverse=True)` 把每个点的出边降序排，配合下面的 `pop()`（从尾部弹）等于每次取**字典序最小**的出边——排序降序 + 尾部弹出是这对黄金搭档，一行实现贪心选择。

```python
    stack=[start]; out=[]
    while stack:
        if adj[stack[-1]]: stack.append(adj[stack[-1]].pop())
        else: out.append(stack.pop())
    path=out[::-1]
```

- 整个算法就这两行分支：栈顶点**还有出边**就走下去（`adj[stack[-1]].pop()` 弹出一条出边的终点压栈，这条边即刻消耗）；**没有出边**就把该点弹出并后序记录到 out。
- `path=out[::-1]`：out 是逆序，切片翻转成正序路径。为什么后序 + 翻转是对的：一个点被记入 out 时，它钻过的所有支路都已经在 out 的更后面（即 path 的更前面）被拼好了，该点作为"接头点"位置天然正确。

```python
    if len(path)!=len(edges)+1 or Counter(zip(path,path[1:]))!=Counter(map(tuple,edges)): return None
    return path
```

- 兜底校验：路径 V 个点对应 V−1 条边，所以完整行程点数必须恰为 len(edges)+1。
- `Counter(zip(path,path[1:]))`：把 path 相邻两点配成边并**计数**（重复边各计一次）；`Counter(map(tuple,edges))` 是输入边的计数。两个多重集合必须完全相等——既不能少走（不连通），也不能多走或走错。任何异常都返回 None（cell4 契约：None 表示无完整欧拉路径）。

### 函数 1：`eulerian_path(edges)`（通用接口）

```python
def eulerian_path(edges):
    if not edges: return []
    delta=Counter()
    for u,v in edges: delta[u]+=1; delta[v]-=1
    starts=[u for u,d in delta.items() if d==1]; ends=[u for u,d in delta.items() if d==-1]
    if any(abs(d)>1 for d in delta.values()) or not (len(starts)==len(ends)==1 or not starts and not ends): return None
    start=starts[0] if starts else min(u for u,v in edges)
    return _hierholzer(edges,start)
```

- `if not edges: return []`：零条边的空输入，空路径即答案，不进后续逻辑。
- `delta` 用 Counter 当可加减的字典：每条边给起点 +1（出）、终点 −1（入）。
- `starts`/`ends` 收集 delta=+1 和 −1 的点。判定行是两个条件的或非：任何点 |delta|>1 直接出局；否则要么"恰一个起点配恰一个终点"（路径情形），要么"两者皆空"（回路情形），别的组合都返回 None。
- 起点选择：有奇点就用它（delta=+1 的点，只能作为出发点）；回路情形没有奇点，为了结果确定，取**最小标签**（`min(u for u,v in edges)`）——这就是 cell4 说的"顶点标签必须可排序"的用意。
- 最后交给 `_hierholzer` 完成（它内部还有 Counter 校验兜底连通性）。

### 函数 2：`find_itinerary(tickets)`（机票题接口）

```python
def find_itinerary(tickets):
    path=_hierholzer(tickets,'JFK')
    if path is None: raise ValueError('no itinerary using all tickets from JFK')
    return path
```

- 机票题起点固定 'JFK'，不做度条件预判，直接从 JFK 跑 Hierholzer。
- 拿到 None 说明"从 JFK 出发根本无法用完全部机票"，此时**抛异常**而不是返回 None——这是本章对这道题选定的错误契约（调用者传错输入应该立刻被炸醒，而不是拿到 None 还要猜含义）。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么"后序记录 + 倒序输出"能拼出正确的欧拉路径？** 我们跟着栈的过程看：一个点 u 被弹出记入 out，意味着它此刻的所有出边都已经被走过。它弹出之前，最后一次"钻出去又回来"的那段支路，其上的点已经在 out 里排在 u 的后面（更早弹出）。倒过来之后，u 前面紧跟的正是最后那条支路的起点……这样一段一段接起来，每段支路都恰好接回 u 这个"接头点"。所以整体路径里，每条边恰好出现一次——中途所有看似"卡死"的绕路都被无缝缝合了。最终再用 Counter 全量对账一遍：走出来的边集合和输入完全一致才放行，所以不连通图（比如两个分开的环，度全配平但根本走不通）也会被这最后一关拦下并返回 None。

**为什么这样走能得到字典序最小的行程？** 每一步我们都从栈顶点的剩余出边里挑字典序最小的走。在保证"全部边都能用完"的前提下，能先闭合的小回路（比如先去 A 再回 JFK 的环）会被优先走完并拼到前面，而一旦走进真正收尾的支路（比如最后飞 B 的尾巴），那条支路上的点没有出边了、会被后序留在 out 的最前面（= path 的最后）。于是越"早能绕回来"的小字典路线排得越靠前，最终整条路径字典序最小。直观记忆：**能回来的先走（排前面），回不来的留到最后（排末尾）**。

**复杂度，用具体数字说：** 排序出边是 O(E log E)，遍历每条边进出栈各一次是 O(E)，辅助结构 O(V+E)。假设 300 张机票（LeetCode 332 规模），排序约 300×8≈2400 次比较，加上几百次栈操作，总共毫秒级完成。度条件检查也是 O(E)。空间上邻接表存所有边 O(V+E)。

**两个前提要记住**：顶点标签必须**可排序**（要做字典序）且**可哈希**（要做 dict 键）；接口用返回 None 表示"没有完整欧拉路径"（机票接口则抛异常）。

## 六、测试用例在测什么

```python
assert find_itinerary([('JFK','KUL'),('JFK','NRT'),('NRT','JFK')])==['JFK','NRT','JFK','KUL']
```
正常值 + 核心陷阱：如果实现纯贪心选字典序最小的票，第一步会飞 KUL 然后卡死（KUL 无出票）。正确算法必须输出 JFK,NRT,JFK,KUL——先绕 NRT 回来，把 KUL 留到最后。这条专测 Hierholzer 的"死胡同后置"修复能力。

```python
assert eulerian_path([(0,1),(0,1),(1,0)])==[0,1,0,1]
```
多重边专项：0→1 有两条平行边、1→0 一条。delta[0]=+1、delta[1]=−1，起点 0。答案 [0,1,0,1] 恰好把两条平行边各走一次——验证重复边作为独立边被分别消耗，Counter 校验也承认多重集合相等。

```python
assert eulerian_path([(0,1),(2,3)]) is None
```
不连通反例：两条边分居两处。度检查这关就不过——delta[0]=+1、delta[2]=+1 出现两个起点，直接返回 None（不连通图在此暴露）。

```python
assert eulerian_path([])==[]
```
空输入边界：没有边就没有行程，返回空列表而不是 None 或报错。

```python
from itertools import permutations
edges=[('JFK','A'),('A','JFK'),('JFK','B'),('B','JFK'),('JFK','A')]
valid=[]
for perm in permutations(edges):
    path=['JFK']
    for u,v in perm:
        if path[-1]!=u: break
        path.append(v)
    if len(path)==len(edges)+1: valid.append(path)
assert find_itinerary(edges)==min(valid)
```
字典序对拍：5 张票（含重复的 JFK→A）。暴力法枚举全部 5!=120 种使用顺序，能从 JFK 首尾相接走完的（当前点必须等于下一张票的起点）收集为 valid；`min(valid)` 按 Python 列表比较规则取字典序最小的行程。本章算法输出 ['JFK','A','JFK','A','JFK','B','JFK'] 必须与之相等。这条同时验证了"用完全部票（含重复）"和"字典序最小"两个要求。

最后 `print('N090: 所有本章断言通过')` 供肉眼确认全绿。

## 七、练习思路提示

**练习 1：构造"逐步选最小边但不回溯会卡住"的例子。**
思路方向：你要展示的是朴素贪心（只管选当前最小、不知道回头）失败而 Hierholzer 成功的对比。提示：cell6 的三票例子就是最小反例——朴素贪心第一步飞 KUL 就死局；把朴素贪心写成代码（每步选剩余最小出边、走过去就再也不回头），跑同输入展示它半路卡住或用不完票；再跑 `find_itinerary` 展示正确输出，并解释 Hierholzer 靠后序拼接把死胡同 KUL 挪到了末尾。更刁钻的构造可以叠两层环套环（如 JFK→A→JFK、JFK→B→JFK、JFK→C）让贪心错得更早。

**练习 2：检查重票按多重边消费。**
思路方向：构造包含重复票的输入，验证两张相同票被各用一次。提示：直接用测试里的 `[(0,1),(0,1),(1,0)]`（输出 [0,1,0,1]），或者机票版 `('JFK','A'),('A','JFK'),('JFK','A')` 手算一遍 path。重点检查两处：一是邻接表必须用 list（若是 set，重复票被合并成一条，路径长度校验 `len(path)!=len(edges)+1` 就会失败返回 None）；二是 `Counter(zip(...))` 对多重集合计数时两条 (0,1) 计为 2，与输入计数一致才通过。把"改成 set 会怎样"的实验现象写进验收说明里。

## 八、对应 LeetCode 题目

- **332. Reconstruct Itinerary（重新安排行程，canonical）**：这题就是本章 `find_itinerary` 的原始场景——从 JFK 出发用完全部机票且字典序最小，考点是 Hierholzer 后序构造 + 出边降序排序弹尾部的字典序技巧 + 重复票当多重边处理。
- **2097. Valid Arrangement of Pairs（合法重新排列数对，canonical）**：这题是欧拉路径的无机票包装——给一堆 (start,end) 数对，要求重排后相邻数对首尾相接（即把每个数对当边走出一条欧拉路径）。与 332 的区别是不要求字典序、起点要自己按度条件找（delta=+1 的点，没有就用任意点），对应本章 `eulerian_path` 接口；有解保证存在，重点练"找起点 + Hierholzer"。
