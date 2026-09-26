# N059 · K 路归并与有序候选生成 —— 说人话详解

> 对应 notebook：`notebooks/08_heaps/059_heap_k_way_merge.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章解决"从多个有序序列里按顺序往外拿数"的两道题：

1. **K 路归并**：给你 K 条已经排好序的链表，把它们合成一条整体有序的大链表。比如三条链 `[1,4,5]`、`[1,3,4]`、`[2,6]`，合成 `[1,1,2,3,4,4,5,6]`。
2. **前 k 小数对**：给你两个升序数组 a 和 b，从所有"从 a 里取一个、从 b 里取一个"组成的数对里，挑出和最小的 k 对。比如 a=[1,7,11]、b=[2,4,6]、k=6 时，全部 9 个数对的和是 3,5,7,9,11,13,9,11,13,13,15,17,13,15,17 中的前 6 小，答案依次是 [1,2],[1,4],[1,6],[7,2],[7,4],[7,6]，它们的和是 3,5,7,9,11,13。

为什么这两题是一家？因为第二题可以换个视角看：把"a[i] 配 b[0]、b[1]、b[2]……"看成一条关于 i 的有序流（a 有序时这些和随 j 递增），于是"前 k 小数对"就变成了"在 m 条有序流里做归并、只取前 k 个"。两道题共用同一个核心招式：**堆里永远只放每条流当前的"排头"，每弹走一个，就从同一条流补上下一个**。

具体到数字的小例子（K 路归并）：三条链 `[1,4,5]`、`[1,3,4]`、`[2,6]`，堆里先放三条链的头 1、1、2；弹出 1（输出），补上它后面的 4；再弹出 1，补 3；再弹 2，补 6；再弹 3，补 4；弹 4，补 5；弹 4；弹 5；弹 6——输出正好是 `[1,1,2,3,4,4,5,6]`。

## 二、关键概念（定义）

- **K 路归并**：同时归并 K 条有序序列。最朴素的办法是每轮扫描 K 条流的头找最小（O(K) 一轮），总共 O(NK)；用堆把"找最小"降到 O(log K)，总共 O(N log K)。
- **堆头（每路一个候选）**：不变量是"每条还没拿空的流，它的下一个数一定在堆里"。因为每条流内部有序，流里更靠后的数不可能比头部先出，所以全局最小值必然是堆里 K 个头之一。
- **惰性推进（lazy advance）**：堆里从不放整条流，只放"当前头"。拿走一个才补下一个，堆的大小始终是"还没拿空的流的条数"，这就是省时间也省内存的原因。
- **元组比较与索引打破平局**：堆里放的不是裸节点，而是 `(值, 路编号, 节点)` 这样的元组。Python 比较元组时逐位比：先比值，值相同比路编号（数字，一定能比），这样绝不会走到"比较节点对象"那一步——ListNode 之间没有定义小于关系，真比了会直接报 TypeError。
- **有序流视角（数对流）**：把 a[i] 与整个 b 的所有配对 `(a[i]+b[0]), (a[i]+b[1]), ...` 看成一条升序流，i=0..m-1 共 m 条流。求前 k 小数对 = 归并这 m 条流的前 k 个。
- **去重/并列约定**：两对数和相同时，输出顺序按堆的弹出顺序决定（本章元组键保证确定性，不额外去重——每个下标对只入堆一次，所以天然不会输出重复对）。
- **哑节点（dummy）技巧**：链表题里先造一个假头节点，最后返回 `dummy.next`，省去"头节点为空"的特殊分支。

## 三、解决思路（一步步推导）

Step 1：理解为什么"全局最小一定在某个流的头部"。每条流内部有序，说明头部是这条流中"最有可能最先出列"的代表；任何没露面的数都排在它所在流的头部后面，不可能比头部更小。于是堆里只要 K 个头就能担保拿到全局最小。

Step 2：归并主循环。弹出堆顶（全局最小），接到结果链尾部；如果这个节点在自己那条流里还有后继，就把后继推进堆。重复到堆空。

Step 3：数对问题的建模。固定 a[i]，让 j 从 0 往后走，和单调不减，这就是一条有序流。堆里放 `(a[i]+b[0], i, 0)`，弹出 `(s,i,j)` 后，若 j+1 还在 b 的范围内，就补 `(a[i]+b[j+1], i, j+1)`。

Step 4：剪枝。前 k 小的数对不可能用到 a 的第 k 行以后（更靠后的行首更大），所以初始化只放前 `min(k, len(a))` 条流的头即可。

手算演示（notebook 小实例原数据）：a=[1,7,11]，b=[2,4,6]，k=6。初始堆放前三条流的头：(3,0,0)、(9,1,0)、(13,2,0)（三元组是"和, i, j"）。过程如下：

| 弹出次序 | 数对 | 和 | 弹出后补充的候选 |
| --- | --- | --- | --- |
| 1 | [1,2] | 3 | (1+4=5, 0, 1) |
| 2 | [1,4] | 5 | (1+6=7, 0, 2) |
| 3 | [1,6] | 7 | 无（b 用完，j=2 是末尾） |
| 4 | [7,2] | 9 | (7+4=11, 1, 1) |
| 5 | [7,4] | 11 | (7+6=13, 1, 2) |
| 6 | [7,6] | 13 | 无；已凑满 k=6 对，停止 |

每一步弹出的都是"所有还没输出的候选"中最小的和——这张表与 notebook 小实例生成的表格一致（弹出次序 1~6、数对、和三列完全相同）。

## 四、代码逐段讲解

### 1. 辅助结构：链表节点与双向转换

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def list_to_nodes(values):
    dummy = tail = ListNode()
    for value in values:
        tail.next = ListNode(value)
        tail = tail.next
    return dummy.next

def nodes_to_list(head):
    values, seen = [], set()
    while head is not None:
        if id(head) in seen:
            raise ValueError('cycle in a supposedly finite list')
        seen.add(id(head))
        values.append(head.val)
        head = head.next
    return values
```

- `ListNode`/`TreeNode` 是本章自带的节点定义，`TreeNode` 只为先修衔接出现，本章算法没用到它。
- `list_to_nodes` 用哑节点 `dummy` 串链表：`tail` 一直指向最后一个节点，逐个 `ListNode(value)` 接上去，最后返回 `dummy.next`（真正的头）。
- `nodes_to_list` 反向把链表读回列表，方便测试断言。里面那个 `id(head) in seen` 检查是防御性设计：如果链表意外成环，这函数会死循环，所以先用集合记住访问过的节点对象身份（`id()`），发现重复立刻报错。

### 2. `merge_k_lists`：堆头归并 K 条链

```python
import heapq

def merge_k_lists(lists):
    heap=[(node.val,i,node) for i,node in enumerate(lists) if node]
    heapq.heapify(heap); dummy=tail=ListNode()
    while heap:
        _,i,node=heapq.heappop(heap)
        following=node.next
        tail.next=node; tail=node
        if following: heapq.heappush(heap,(following.val,i,following))
    if tail is not dummy: tail.next=None
    return dummy.next
```

- 第一行列表推导一次收集所有非空流的头，`if node` 把空链表直接排除（空链没有候选）。元组 `(node.val, i, node)` 的三段分别是"值、路编号、节点本体"。
- `heapq.heapify(heap)` 把这堆候选原地整理成小根堆，O(K) 一步到位。
- `_,i,node=heapq.heappop(heap)` 弹出全局最小；`_` 是我们不再关心的值，`i` 记住它来自哪条流，`node` 是要接走的节点。
- 先把 `following=node.next` 存下来，再 `tail.next=node; tail=node` 把节点接到结果链上——注意接走前必须存后继，否则接完就找不到了。
- `if following` 只有后继存在才补堆，这条路拿空了堆就少一路，堆自动缩小。
- `if tail is not dummy: tail.next=None` 收尾：被接来的节点身上还挂着旧链的 `next` 指针，最后一个节点的 next 必须切成 None，否则结果链尾巴上拖着别家的节点。（用 `is not` 判断而不是 `!=`，因为比的是对象身份：tail 还停在 dummy 上说明结果链为空。）

### 3. `k_smallest_pairs`：前 k 小数对

```python
def k_smallest_pairs(a,b,k):
    if not a or not b or k<=0: return []
    heap=[(a[i]+b[0],i,0) for i in range(min(k,len(a)))]; heapq.heapify(heap)
    out=[]
    while heap and len(out)<k:
        _,i,j=heapq.heappop(heap); out.append([a[i],b[j]])
        if j+1<len(b): heapq.heappush(heap,(a[i]+b[j+1],i,j+1))
    return out
```

- `if not a or not b or k<=0: return []` 是边界守卫：任一数组为空就没有数对，k 非正也不要任何输出，统一给空列表。
- 初始化只放前 `min(k,len(a))` 条流的头，这是第四节的剪枝：第 k 行之后的行首不小于前 k 行首，不可能贡献更小的前 k 项。
- 循环条件 `while heap and len(out)<k`：堆空（候选耗尽）或凑满 k 对，任一满足就停。
- 每轮弹出 `(s,i,j)` 后输出 `[a[i],b[j]]`，然后只在 j 方向前进一格补堆——这就是"固定 i、推进 j"的流式视角。

## 五、为什么是对的？复杂度是多少？（说人话）

为什么堆顶一定是"所有还没输出候选"的最小值？因为每条流里还没暴露出来的数都不小于该流当前头部（流内部升序），而所有头部都待在堆里，所以"没暴露的"整体不小于"堆里最小的"，堆顶自然是全场下一个该出列的。归纳着说：只要这个性质在某一轮成立，弹掉堆顶、补上后继之后性质依然成立，所以从第一轮到最后一路成立。

数对版只初始化前 k 行为什么够？因为 a 有序，第 k+1 行的行首 a[k]+b[0] 不小于前 k 行的任何行首 a[i]+b[0]（i<k）。如果某个第 k+1 行的候选真的进了前 k 小，那它前面的至少 k 个行首也都不大于它，早就把前 k 个名额挤占了——矛盾。所以后面的行连初始化都不必要。

复杂度：K 路归并共 N 个节点，每个节点进堆一次、出堆一次，堆大小不超过 K，每次堆操作 O(log K)，总计 O(N log K) 时间、O(K) 堆空间。举例：K=100 条流共 N=10⁶ 个节点，约 10⁶×7=700 万次比较；对比朴素"每轮扫 K 个头"要 10⁶×100=10⁸ 次，差一个数量级还多。数对版实际输出 q=min(k, m×n) 对，堆大小不超过 min(k,m)，时间 O(q log min(k,m))：k=100、m=1000 时也只有约 700 次比较量级，几乎瞬间完成。

## 六、测试用例在测什么

```python
h=merge_k_lists([list_to_nodes([1,4,5]),None,list_to_nodes([1,3,4]),list_to_nodes([2,6])])
assert nodes_to_list(h)==[1,1,2,3,4,4,5,6]
```
正常用例，且故意在中间塞了一条 `None` 空链：验证空流被安全跳过、三条真链正确归并成整体升序。

```python
assert merge_k_lists([]) is None
```
边界用例：一条链都没有，答案就是空（None），测的是空输入不炸、返回值符合"链表空即 None"的约定。

```python
for a in combinations_with_replacement([0,1,2],3):
    for b in combinations_with_replacement([0,1,2],2):
        all_sums=sorted(x+y for x in a for y in b)
        for k in range(8):
            out=k_smallest_pairs(a,b,k)
            assert [sum(p) for p in out]==all_sums[:k]
            assert all(x in a and y in b for x,y in out)
```
穷举对照测试：`combinations_with_replacement` 生成所有 3 元素非降数组 a 和 2 元素非降数组 b（共 10×6=60 种组合，含大量重复值），对每组把全部 m×n 个和排序当标准答案，再让 k 从 0 一路取到 7。第一条断言验证"输出数对的和的序列恰是全局前 k 小"；第二条验证"输出的每对确实来自 a 和 b（没有编造数对）"。k=0 这条边界也在其中。注意它只比较"和的序列"而不比较数对本身，因为和相同的数对不同输出顺序都合法。

## 七、练习思路提示

- 练习 1（实现多个有序生成器归并）：把"链表/数组"换成 Python 生成器（比如 `itertools.count` 或排序好的文件块迭代器）。提示：难点是生成器只能"next 一次拿一个、不能回头"，所以 `following` 的预读必须小心；你可以用"先 next 再入堆"的两步走，并想清楚流耗尽（StopIteration）时怎么让堆自然缩路。手算例子可用三条生成器 `[1,4,5]`、`[2,3]`、`[6]`。
- 练习 2（避免比较不可排序节点对象）：故意把堆里元组写成 `(node.val, node)` 跑一次，观察两条流头部值相等时 Python 试图比较 ListNode 而 TypeError。提示：修复方式就是本章的"值后插一个一定能比的路编号"；再想想如果路编号也相同会不会出问题（同一流不会有两个候选同时在堆里，所以编号足够打破平局）。这也是元组键设计的通用套路：最后一位放"保证互异且可比"的东西。

## 八、对应 LeetCode 题目

- **23. Merge k Sorted Lists（合并 K 个升序链表）**：`merge_k_lists` 的原题，练的是"每路一个堆头 + 弹一个补一个"的惰性归并。
- **373. Find K Pairs with Smallest Sums（查找和最小的 K 对数字）**：`k_smallest_pairs` 的原题，练的是"把数对看成 m 条有序流再归并 + 只初始化前 k 行"的建模。
