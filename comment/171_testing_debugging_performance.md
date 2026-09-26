# N171 · 测试、调试与性能回归 —— 说人话详解

> 对应 notebook：`notebooks/21_mastery/171_testing_debugging_performance.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章的方法论解决的问题是：**怎么判断你写的实现"真的对了、真的快了"，而不是"碰巧这一组输入过了"？** 三个具体抓手：一是答案规范化——组合题的答案顺序可以乱，但重复答案通常是错的，比较前要先把顺序抹掉、把重数留住；二是内部状态检查——链表和缓存这类题，光看返回值不够，要抓住"暂时输出相同、内部状态已经错了"的实现；三是性能回归——别用毫秒数冒充复杂度，去数算法真正执行的比较次数或状态数。

这一章不是空谈方法论，cell3 里真的写了一个完整的手写 LRU 缓存（字典 + 双向链表），然后配了一个用 `OrderedDict` 实现的参照版，两套实现一步步对拍。

用具体数字演示一个最小例子（容量 2 的 LRU）：操作序列是 `put(1,10)`、`put(2,20)`、`get(1)`、`put(3,30)`、`get(2)`、`get(3)`。我们手推一下：

- `put(1,10)`、`put(2,20)` 后，缓存顺序（从最旧到最新）是 `[1,2]`；
- `get(1)` 命中，1 变成最新，顺序变成 `[2,1]`，返回 10；
- `put(3,30)` 时容量已满，淘汰最旧的 2，顺序变成 `[1,3]`；
- `get(2)` 落空，返回 -1；
- `get(3)` 命中，返回 30。

所以 get 的输出序列是 `[10, -1, 30]`——这正是 cell6 第二张表里的内容。一个只会背返回值的实现到这里全对；但如果它忘了在 `get` 时把节点移到最新端，下一步淘汰的对象就会错，而这一错误只有"每步都核对完整 LRU 顺序"才抓得到。

## 二、关键概念（定义）

- **规范化（normalize）**：把"题意允许不同"的差异（比如组合内元素顺序、组合之间的顺序）抹平后再比较。它只能消除无关差异，**不能抹掉错误**——所以 `normalize_solution_output` 保留重复元素的重数，重复答案照样能被比出来。
- **最小复现**：把 bug 触发条件缩到最小的输入。小到一眼能手推的例子，才能定位"哪一步开始错"。
- **多解比较（差分测试）**：用两个"接口相同、内部机制不同"的实现跑同一份输入再比对。本章是手写双向链表 LRU 对 `OrderedDict` 参照实现。
- **别名（aliasing）**：两个变量指向同一个对象。链表测试必须保留**节点引用**、比较 `is` 身份，而不是只比较数值——`reverse` 之后再 `reverse`，正确实现应当把每个 `next` 恢复成**原来那个对象**，换成"值相同的新节点"都算错。
- **结构断言**：不看返回值、直接检查数据结构内部不变量的断言。本章每步操作后都走一遍缓存链表：前驱指针、节点不重复、字典与链表一一对应。
- **缓存污染与状态恢复测试**：测试改了共享状态（比如手动接出个环）之后要负责恢复原状，并且验证恢复到的是"原来那些对象"。同时要检查"无环"这一前提：给链表断言函数喂一个有环的链表，它必须报警。
- **操作计数**：性能回归的度量方式——数比较次数、循环轮数这类确定性计数，替代毫秒计时。固定硬件上的毫秒门槛既证明不了复杂度，还容易产生偶发的假失败。
- **环境隔离**：用固定随机种子的 `random.Random(171)` 生成测试数据，任何人重跑得到同一序列；诊断逻辑只活在测试里，不混进算法本体。
- **二分循环不变量**：`while left<right` 这段循环里，答案始终落在半开候选区间 `[left,right)` 的边界范围内；每轮区间至少近似减半，由此导出迭代轮数的对数上界。

## 三、解决思路（一步步推导）

本章工作流是"三个诊断场景"依次展开，我们一步步走：

- **Step 1：先想清楚比较口径。** 组合题（如"求所有和为 target 的二元组"）答案顺序任意，先规范化再比：内层排序组合内元素，外层排序各组合，全部转成元组。因为元组不可变、可比较，还能当字典键。
- **Step 2：规范化保留重数（手算）。** `[[1,2],[3,4]]` 规范化后是 `((1,2),(3,4))`；`[[4,3],[2,1]]` 规范化后也是 `((1,2),(3,4))`，两者相等 ✓。而 `[[1,2],[1,2]]` 是 `((1,2),(1,2))`，和 `[[1,2]]` 的 `((1,2),)` **不相等**——重复答案没有被排序折叠掉，错误照样暴露。
- **Step 3：链表测试先抓身份。** `assert_linked_structure` 一边走一边把每个节点的 `id` 记进集合，再次出现就断言失败——它同时完成"无环检查"和"收集节点引用"两件事。`nodes_to_list` 里也有同样的环检测，一旦有环就抛 `ValueError`，避免遍历死循环。
- **Step 4：恢复测试比身份不比值（手算）。** 对 `[1,2,3]` 建链表，记下 `before`（3 个节点对象）和每个节点的 `next`；`reverse(reverse(head))` 之后断言三件事：返回的头 `is` 原来的头、节点序列 `==before`（逐个身份相等）、每个 `node.next is` 原来那个 next。中间实现如果 new 了新节点，值全对也会在这三条上翻车。
- **Step 5：故意制造故障验证诊断器。** 把 `before[-1].next=head` 接出一个环，用 try/except 断言 `assert_linked_structure` **必须**抛 `AssertionError`；随后拆掉环，再次验证所有 `next` 引用完好如初。诊断器本身也要被测试——它漏报就是测试体系的 bug。
- **Step 6：LRU 每步全量对拍。** `differential_test_lru` 用第一节那条 6 步操作序列手推：参照实现里 `OrderedDict` 的顺序从 `[1,2]`→`[2,1]`→淘汰 2→`[1,3]`，与手写链表的顺序逐步核对；同时每步走链表查前驱、查重复、查字典与链表一一对应。任何一步内部状态不一致立即断言失败。
- **Step 7：操作计数代替毫秒。** `count_binary_search_iterations` 对 n=0,1,2,4,8,16,64,256,1024，把 target 从 -1 到 n 全试一遍，数 `while left<right` 转了几轮、取最大值。手算 n=2、target=0：`left,right=0,2`，middle=1，1<0 不成立所以 right=1；middle=0，0<0 不成立所以 right=0；循环结束，共 2 轮。n=2 的最大轮数是 2，正好等于 `ceil(log2(3))`。
- **Step 8：把轮数对到对数上界。** 每个非零 n 的最大轮数都应不超过 `ceil(log2(n+1))`（n=1024 时是 11 轮）。区间每轮近似减半，所以轮数是 log 级——这是用**数出来的数字**支撑复杂度结论，而不是跑计时曲线。

## 四、代码逐段讲解

cell3 代码较多，按功能块逐个讲。先说基础设施：`ListNode`、`TreeNode` 是最简节点类；`list_to_nodes` 用一个 `dummy` 哨兵头把列表串成链表，返回 `dummy.next`；`nodes_to_list` 边走边用 `id(head)` 集合查环，有环抛异常。

### 1. 手写 LRU 的骨架：`_CacheNode` 与 `_NodeList`

```python
class _CacheNode:
    def __init__(self,key=None,value=None): self.key=key; self.value=value; self.frequency=1; self.prev=self.next=None

class _NodeList:
    def __init__(self):
        self.head=_CacheNode(); self.tail=_CacheNode(); self.head.next=self.tail; self.tail.prev=self.head; self.size=0
    def append(self,node):
        previous=self.tail.prev; previous.next=node; node.prev=previous; node.next=self.tail; self.tail.prev=node; self.size+=1
    def remove(self,node):
        node.prev.next=node.next; node.next.prev=node.prev; node.prev=node.next=None; self.size-=1
    def pop_left(self):
        if not self.size: raise IndexError('empty node list')
        node=self.head.next; self.remove(node); return node
```

- `_CacheNode` 带 `key/value` 和前后指针；节点记住 key 是为了淘汰后能从字典里删掉对应项。
- `_NodeList` 用两个哨兵节点（head、tail）夹住真实节点，头侧最旧、尾侧最新。哨兵让 `append/remove` 永远不用判空、不用特判端点。
- `append` 的四步指针拼接把节点插到尾哨兵前（成为最新）；`remove` 先把前后邻居互连，再把被删节点的前后指针清成 None——清空是刻意的：诊断器要检查 `node.prev is previous`，残留指针会让错误状态漏检。`pop_left` 弹出最旧节点，空表弹出抛 `IndexError`。

### 2. `LRUCache` 本体

```python
class LRUCache:
    def __init__(self,capacity):
        if capacity<0: raise ValueError('nonnegative capacity required')
        self.capacity=capacity; self.nodes={}; self.order=_NodeList()
    def _touch(self,node): self.order.remove(node); self.order.append(node)
    def get(self,key):
        if key not in self.nodes: return -1
        node=self.nodes[key]; self._touch(node); return node.value
    def put(self,key,value):
        if key in self.nodes:
            node=self.nodes[key]; node.value=value; self._touch(node); return
        if not self.capacity: return
        if len(self.nodes)==self.capacity:
            victim=self.order.pop_left(); del self.nodes[victim.key]
        node=_CacheNode(key,value); self.nodes[key]=node; self.order.append(node)
```

- 字典 `nodes` 做 key→节点的映射，链表 `order` 维护新旧顺序：**期望 O(1)** 的读写全靠"字典定位 + 链表摘插"这套组合。
- `_touch` 就是"移到最新端"：先 `remove` 再 `append`。`get` 和 `put` 更新已有 key 都要 `_touch`——忘了这一步，淘汰就会错对象（第一节手推的例子里这正是分水岭）。
- `put` 的三个分支依次处理：key 已存在则只更新值并 touch；容量为 0 则直接丢弃（边界情形，参照实现里同样用 `if capacity:` 挡住）；满了则 `pop_left` 淘汰最旧节点并同步删字典项。

### 3. 规范化与链表断言

```python
def normalize_solution_output(x):
    """For unordered collections of unordered integer combinations only.
    Multiplicity is preserved so duplicate answers remain detectable.
    """
    return tuple(sorted(tuple(sorted(row)) for row in x))

def assert_linked_structure(head):
    nodes=[];seen=set()
    while head is not None:
        assert id(head) not in seen, 'Cycle found'
        seen.add(id(head));nodes.append(head);head=head.next
    return nodes
```

- `normalize_solution_output` 是双层"排序+转元组"：内层 `tuple(sorted(row))` 规范组合内部顺序，外层 `sorted` 规范组合之间顺序。返回元组的元组，天然可比、可散列。注意它**只适用于"无序组合的无序集合"**——路径题节点顺序有意义，不能拿它抹。
- `assert_linked_structure` 用 `id()`（对象的身份号）查环，同时把节点按序收集返回，供后续身份比较复用。

### 4. 差分测试器 `differential_test_lru`

```python
def differential_test_lru(operations, capacity=2):
    cache=LRUCache(capacity);reference=OrderedDict();results=[]
    for op in operations:
        if op[0]=='put':
            _,key,value=op
            cache.put(key,value)
            if capacity:
                if key in reference:del reference[key]
                elif len(reference)==capacity:reference.popitem(last=False)
                reference[key]=value
        elif op[0]=='get':
            _,key=op
            expected=reference.get(key,-1)
            if key in reference:reference.move_to_end(key)
            actual=cache.get(key)
            assert actual==expected
            results.append(actual)
        else:raise ValueError('Unknown cache operation')
        nodes=[];node=cache.order.head.next;previous=cache.order.head
        while node is not cache.order.tail:
            assert node.prev is previous and node not in nodes
            nodes.append(node);previous,node=node,node.next
        assert cache.order.tail.prev is previous
        assert [(node.key,node.value) for node in nodes]==list(reference.items())
        assert set(nodes)==set(cache.nodes.values()) and cache.order.size==len(nodes)
    return results
```

- 参照实现用 `OrderedDict`：`move_to_end` 模拟 touch、`popitem(last=False)` 淘汰最旧。它和手写版接口相同、机制完全不同，正适合互相当裁判。
- put 分支照抄 LRU 语义三件套：已存在先删旧记录、满容量先淘汰、最后写入新值；`if capacity:` 保证容量 0 时参照也不动状态，与手写版 `if not self.capacity: return` 对齐。
- get 分支：先算期望值（miss 为 -1）、命中就 `move_to_end`，再调被测实现并 `assert actual==expected`。顺序很重要：参照的状态更新要在调用被测方之前完成。
- 每一步操作后的大段结构断言是本章的招牌：沿链表从 `head.next` 走到尾哨兵，断言每个节点的 `prev is previous`（双向连接真实有效）、`node not in nodes`（无重复、无环）、尾哨兵前驱接得上；再把链表读出的 `(key,value)` 序列和 `list(reference.items())` 逐位比较（**完整 LRU 顺序**一致）；最后用集合比较确认"链表里的节点集合 == 字典的值集合"且计数吻合。返回值骗得过、内部状态骗不过。

### 5. 操作计数 `count_binary_search_iterations`

```python
def count_binary_search_iterations():
    rows=[]
    for n in [0,1,2,4,8,16,64,256,1024]:
        maximum=0
        for target in range(-1,n+1):
            left,right=0,n;count=0
            while left<right:
                middle=(left+right)//2;count+=1
                if middle<target:left=middle+1
                else:right=middle
            assert left==min(n,max(0,target))
            maximum=max(maximum,count)
        rows.append((n,maximum))
    return rows
```

- 外层挑了从 0 到 1024 的 9 个规模；内层把 target 从 -1（比所有元素小）到 n（比所有元素大）全部试遍，包括两个端点外的哨兵值——这是边界测试。
- 循环体是标准"求下界"二分：`middle<target` 就收缩左端，否则收缩右端。不变量保证结束时 `left` 等于 `min(n,max(0,target))`，这个内置断言先自证二分本身正确，再谈轮数。
- `maximum` 记录最坏 target 的轮数，`rows` 收集 (n, 最大轮数)，就是 cell6 第一张表的数据来源。

## 五、为什么是对的？复杂度是多少？（说人话）

**测试为什么有说服力。** 差分测试的说服力来自"两套实现独立犯错还错得一样的概率很低"：参照版用 `OrderedDict` 的现成语义，被测版是手写指针操作，机制毫无交集；两者任何一步输出或内部顺序不一致，断言当场失败。结构断言则补上返回值覆盖不到的盲区：`node.prev is previous` 检查的是双向链接是否真实成立，`set(nodes)==set(cache.nodes.values())` 检查字典与链表是否一一对应（不多节点、不丢节点）。恢复测试比"身份"不比"值"，是因为链表操作的正确性本来就定义在"哪些对象被串在一起"上。二分那段的 `assert left==min(n,max(0,target))` 是循环不变量的落地：答案始终在 `[left,right)` 的边界范围内，循环结束时边界收敛到目标位置。

**复杂度，以及别把账算混。** LRU 的 `get/put` 都是"一次字典操作 + 常数次指针操作"，期望 O(1)——这是**算法**的代价。但差分测试器每一步都要把整条链表扫一遍，测试开销是 O(操作数×容量)：拿 500 步操作、容量 3 来说，诊断扫了约 1500 个节点，这些是**测试**的开销，不能误记到算法头上（这就是"环境隔离"的账目含义：诊断器不进求解路径）。二分方面，区间每轮至少近似减半：从 1024 起步，最坏 11 轮内必然收敛，正式查询是 O(log n)；毫秒门槛证明不了这件事，因为同一台机器上计时随负载抖动，而"轮数 ≤ ceil(log2(n+1))"是确定成立的整数不等式。

## 六、测试用例在测什么

cell8 的断言分五组：

1. **规范化口径**：`normalize_solution_output([[1,2],[3,4]])==normalize_solution_output([[4,3],[2,1]])` 测顺序差异被正确抹掉（正常值）；`normalize_solution_output([[1,2],[1,2]])!=normalize_solution_output([[1,2]])` 测重数被保留（特殊值）——重复答案是错误，绝不能被排序折叠掉。
2. **链表身份与恢复**：`restored is head`、节点序列等于 `before`、每个 `next is` 原对象，这三条合起来确认双向 reverse 把链表恢复到"同一批对象、同一批连接"的原状。
3. **诊断器自测**：手动接环后 `assert_linked_structure` 必须抛 `AssertionError`（try/except 结构验证这一点，漏报则主动 `raise AssertionError('Cycle went undetected')`）；拆环后再确认 `next` 引用完好。测的是"诊断工具本身可靠"。
4. **LRU 差分压力测试**：用固定种子 `random.Random(171)` 生成 500 步随机操作（key 0..6、value 0..49），容量分别取 0、1、3 三档（0 是"永不满、也不存"的边界，1 是"每次 put 都可能淘汰"的边界）。对每个容量跑两遍并断言两次结果相等——确定性测试要求同种子同结果；而每一步的内部结构断言在函数内部已经全部执行过了。
5. **二分轮数上界**：对表里每个 `(n, iterations)`，n 为 0 时断言轮数恰为 0（空区间连循环都不进），否则断言 `iterations<=ceil(log2(n+1))`。例如 n=1024 的行是 11 轮，恰好等于 `ceil(log2(1025))`，把"对数复杂度"钉死在数字上。

## 七、练习思路提示

- **练习 1（修复注入的错误）**：三个故障分别对应三类典型 bug。链表断链：先用 `assert_linked_structure` 抓最小复现，再画三节点小图检查 remove/append 的指针顺序（多半是漏接了 prev 或邻居只接了一半）。LRU 淘汰错：手推 4 步操作序列（如 `put a; put b; get a; put c`），核对淘汰的是不是没被 touch 过的那个，重点查 `get` 路径有没有 `_touch`。二分边界错：用 `count_binary_search_iterations` 的 target=-1 和 target=n 两个哨兵值试，常见病是 `middle<target` 写成 `<=` 或区间用闭端点导致差一；修完后跑 `left==min(n,max(0,target))` 断言验收。
- **练习 2（区分速度噪声与阶数变化）**：思路是用操作计数而非计时。对同一实现分别在 n 和 2n 规模数关键操作次数，看比值接近 2（线性）、4（平方）还是 1（对数/常数）；毫秒数据则多跑几轮看方差。手算示例可以拿二分表：n 从 512 到 1024，轮数只从 10 变 11，增量是常数级的——这就是"阶数没变"的证据，而毫秒层面那点波动很可能只是噪声。

## 八、对应 LeetCode 题目

- **146. LRU Cache（comparison）**：本章手写的 LRUCache 就是它的教学版，练"字典 + 双向链表"的结构实现，以及用差分测试器验证内部状态这套方法。
- **234. Palindrome Linked List（comparison）**：这题练的是链表身份与结构断言的用武之地——反转/恢复链表后要确认节点和指针回到原状，正是本章恢复测试的场景。
- **34. Find First and Last Position of Element in Sorted Array（comparison）**：这题是"下界二分 + 边界处理"的标准练习，正好套用 `count_binary_search_iterations` 里那个循环不变量和轮数上界的分析。

notebook 结尾照例提醒：这些题号用于知识映射，本章实现遵循教学契约，不要把教学实例当成官方题的完整答案。
