# N047 · 快慢指针、环与中点 —— 说人话详解

> 对应 notebook：`notebooks/06_linked_lists/047_linked_list_fast_slow.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章用一个朴素到不可思议的技巧——"两个指针以不同速度走路"——一口气解决四个经典问题：

1. **判断链表有没有环**（LC 141）：链表某个节点的 next 指回了前面的节点，从此在里面绕圈出不来。要你判断有没有这样的环。例子：`1→2→3→4` 且 4 的 next 指回 2，输出 True。
2. **找出环的入口**（LC 142）：不但要知道有环，还要返回"环开始的那一个节点"。上例里入口是节点 2（4 指回的位置）。
3. **找中点**（LC 876）：返回链表正中间的节点。约定：偶数长度时返回**第二个**中点。例子：`1→2→3→4` 共 4 个节点，两个候选是 2 和 3，按约定返回 3。
4. **删除倒数第 n 个节点**（LC 19）：例：`1→2→3` 删倒数第 3 个（就是头节点 1），输出 `2→3`。

为什么"两个速度不同的指针"能管这么多事？直觉：在环形跑道上，跑得快的迟早会从背后追上跑得慢的（套圈）；在直道上，快的是否提前撞线能告诉我们链的奇偶；让快的先走 n 步，两者保持的固定间距就是一把"间隔尺"。

## 二、关键概念（定义）

- **快慢指针（slow/fast）**：两个引用同时从起点出发，慢指针每轮走 1 步（`slow=slow.next`），快指针每轮走 2 步（`fast=fast.next.next`）。
- **Floyd 相遇（龟兔赛跑）**：速度差为 1 时，一旦两个指针都进了环，每一轮它们的间距就缩小 1，所以**有限轮内必然相遇**；若链表无环，快指针会先撞到 None（走到头）。判断"相遇 or 到头"就能区分有环无环。
- **环入口推导（μ 和 λ）**：设头到入口的距离是 μ 步，环长 λ 步（cell1 的记号）。可以证明：相遇那一刻慢指针总共走的步数 s 恰好是 λ 的倍数，于是"从相遇点再走 μ 步"和"从头走 μ 步"会落在同一个地方——环入口。所以相遇后把一个指针送回头部，两个改为同速前进，再次相遇的地方就是入口。
- **奇偶长度（中点约定）**：慢指针走 1 步时快指针走 2 步，快指针到头时慢指针恰好在中间。长度为奇数时中点唯一；长度为偶数时有两个候选，**本章约定返回第二个**（靠后的那个）。
- **倒数第 K 个（间距尺思想）**：让 fast 先走 n 步，之后 fast 和 slow 同速前进，两者之间永远隔着 n 条边。fast 抵达末节点时，slow 恰好停在"倒数第 n 个节点的前驱"上——因为从 slow 到链尾正好还剩 n 条边。
- **对象身份（is）**：判断"是不是同一个节点"必须用 `slow is fast` 这种身份比较，不能用值比较——两个节点值相等不代表是同一个节点，环的判定只关心身份。

## 三、解决思路（一步步推导）

### 问题 1/2：判环与找入口

- **Step 1**：slow、fast 都从头出发，每轮 slow 走 1 步、fast 走 2 步。
- **Step 2**：无环则 fast 先变成 None（或 fast.next 是 None 时下一轮会越界，所以循环条件带上 `fast.next`），返回"无环"。
- **Step 3**：有环则两者都会进入环，此后每一轮间距缩小 1，必然某一轮 `slow is fast`，返回"有环"。
- **Step 4**（找入口）：相遇后，把 slow 拨回头部，fast 留在相遇点，两个都改为每轮 1 步；它们再次相遇的节点就是入口。

**手算演示：** `1→2→3→4`，且 4 的 next 指回 2（入口是 2，μ=1，λ=3）。

- 判环阶段：初始 slow=fast=1。
  - 第 1 轮：slow=2，fast=3。
  - 第 2 轮：slow=3，fast=2（3→4→2）。
  - 第 3 轮：slow=4，fast=4——相遇！注意此刻 slow 走了 3 步，恰好是 λ=3 的 1 倍。
- 找入口阶段：slow 拨回 1，fast 留在 4。
  - slow=1、fast=4 不相等 → 各走一步：slow=2，fast=4.next=2——相等，返回节点 2，正是入口。

### 问题 3：找中点

- **Step 1**：slow、fast 从头出发。
- **Step 2**：只要 fast 和 fast.next 都存在就继续：slow 1 步、fast 2 步。
- **Step 3**：fast 到头（None 或停在末节点）时，slow 就是中点；偶数长度时 slow 停在第二个中点上。

**手算演示：** `1→2→3→4`。

- 第 1 轮：slow=2，fast=3。
- 第 2 轮：slow=3，fast=3.next.next=4.next=None。
- fast 为 None，循环结束，返回 slow=节点 3——偶数长度的第二个中点。

**对照 cell6 的小实例表格：** notebook 对长度 1 到 8 的链表 `list(range(n))` 逐个列出"第二中点值"：

| 长度 | 链表 | 第二中点值 |
|---|---|---|
| 1 | [0] | 0 |
| 2 | [0,1] | 1 |
| 3 | [0,1,2] | 1 |
| 4 | [0,1,2,3] | 2 |
| 5 | [0,1,2,3,4] | 2 |
| 6 | [0,...,5] | 3 |
| 7 | [0,...,6] | 3 |
| 8 | [0,...,7] | 4 |

规律一眼可见：偶数长度 n 返回第 n/2+1 个（第二个中点），奇数长度返回正中间那个。

### 问题 4：删除倒数第 n 个

- **Step 1**：照例造 dummy（倒数第 n 个可能是头节点，前驱不存在，哨兵兜底）。
- **Step 2**：fast 从 dummy 先走 n 步（走完 fast 停在倒数第 n 个节点上）。
- **Step 3**：fast、slow 同速前进，直到 fast 停在**末节点**（`fast.next` 为 None）。
- **Step 4**：此刻 slow 到 fast 之间恰好 n 条边，slow 就是删除目标的前驱，执行一次 next 重接。

**手算演示：** `1→2→3`，n=3（删头）。fast=slow=dummy。

- fast 先走 3 步：dummy→1→2→3，fast 停在 3（末节点）。
- `while fast.next` 不成立（3.next 是 None），slow 一步不用走，还停在 dummy。
- `slow.next=slow.next.next`：dummy→2→3。返回 `[2,3]`，头节点删除成功。

## 四、代码逐段讲解

cell3 开头的 `ListNode`、`TreeNode`、`list_to_nodes`、`nodes_to_list` 与 N045 相同，不再重复。

### 1. `has_cycle` —— 判环

```python
def has_cycle(head):
    slow=fast=head
    while fast and fast.next:
        slow=slow.next; fast=fast.next.next
        if slow is fast: return True
    return False
```

- `while fast and fast.next:`：走两步之前必须确认两步都存在——`fast` 为 None 说明快指针已到头（无环），`fast.next` 为 None 说明只剩一步可走（同样无环）。这个条件同时防了越界访问。
- `fast=fast.next.next`：快指针一次跨两步。
- `if slow is fast:`：身份比较，同一轮走到同一对象即相遇。注意比较放在**移动之后**（起点本来就是同一个 head，先比会误报）。
- 循环自然退出说明快指针到头，返回 False。

### 2. `detect_cycle` —— 找环入口

```python
def detect_cycle(head):
    slow=fast=head
    while fast and fast.next:
        slow=slow.next; fast=fast.next.next
        if slow is fast:
            slow=head
            while slow is not fast: slow=slow.next; fast=fast.next
            return slow
    return None
```

- 前半段与 `has_cycle` 完全一样，先跑到相遇。
- `slow=head`：把慢指针拨回头部，fast 留在相遇点。
- `while slow is not fast:`：两个指针改为同速（各 1 步）前进，直到相遇。
- `return slow`：第二次相遇的节点就是环入口。
- 函数末尾 `return None`：外层循环没相遇就退出说明无环，按题意返回 None。

### 3. `middle_node` —— 找中点

```python
def middle_node(head):
    slow=fast=head
    while fast and fast.next: slow=slow.next; fast=fast.next.next
    return slow
```

- 与 `has_cycle` 共用同一套走路循环，只是不做相遇判断，循环结束时直接返回 slow。
- 循环条件 `fast and fast.next` 决定了偶数长度时 fast 停在 None、slow 停在第二个中点；这就是"不同中点约定"的全部秘密：想返回第一个中点，就把条件改成 `fast.next and fast.next.next`（练习 2 会让你体会）。

### 4. `remove_nth_from_end` —— 删倒数第 n 个

```python
def remove_nth_from_end(head,n):
    if n<1: raise ValueError('n must be positive')
    dummy=ListNode(0,head); fast=slow=dummy
    for _ in range(n):
        fast=fast.next
        if fast is None: raise ValueError('n exceeds length')
    while fast.next: fast=fast.next; slow=slow.next
    slow.next=slow.next.next
    return dummy.next
```

- `if n<1: raise ValueError(...)`：挡住"倒数第 0 个、倒数第负数个"这类非法输入，直接报错。
- `for _ in range(n):`：fast 先走 n 步；每走一步检查一次 `fast is None`，中途变 None 说明 n 大于链长（连倒数第 1 个都数不到 n 个），抛异常"n exceeds length"。
- `while fast.next:`：同速推进，直到 fast 停在末节点（fast.next 为 None）。注意停的条件是"fast 还有前 further 后继为空"，不是 fast 变 None——这保证 slow 停下的位置恰好差 n 条边到链尾。
- `slow.next=slow.next.next`：标准的前驱跨接，删掉倒数第 n 个。
- `return dummy.next`：删的可能是头节点，永远从哨兵后面取新头。

## 五、为什么是对的？复杂度是多少？（说人话）

**判环为什么对？** 无环时链是直线，快指针必然先走到 None，返回 False 显然正确。有环时两个指针迟早都掉进环里，此后问题变成"环上两个同向跑步者，快的每轮多走 1 步"。设某一时刻两者在环内相距 d 步（沿前进方向数，d 在 0 到 λ-1 之间），每一轮距离变成 d-1（因为快追近 1 步）；哪怕 d=0 已经相遇，否则 d 一轮轮减到 0，最多 λ 轮必相遇。所以"有限轮内相遇"是保证，不是运气。

**找入口为什么对？** 设头到入口 μ 步、环长 λ。相遇时慢指针走了 s 步，快指针走了 2s 步；快比慢多走的 s 步全部发生在"进环以后多绕的圈"上，所以 s 必是 λ 的整倍数。再看相遇点：慢指针进环后走了 s-μ 步，也就是相遇点在入口后方 (s-μ) 步处；从相遇点继续前进 μ 步，走过的总路程是 (s-μ)+μ = s 步，而 s 是 λ 的倍数，绕回环的起点——恰好是入口！而"从头出发走 μ 步"按定义也正好落在入口。所以两个"各走 μ 步"的指针必然在入口撞上。这就是 cell1 那段推导的完整口语版。

**中点为什么对？** 慢指针走的步数永远是快指针的一半。快指针走完整条链（n-1 条边量级）时，慢指针恰好走了一半，停在中点。偶数长度时这套循环让 fast 最后停在 None，slow 多走了半步，落在第二个中点上——这是循环条件决定的确定性结果，不是巧合。

**倒数删除为什么对？** fast 先走 n 步后，"fast 领先 slow 恰好 n 条边"这个关系在同速前进中保持不变（这就是 cell4 说的"保持 fast 比 slow 领先 n 个 next 边"）。fast 停在末节点时，从 slow 位置到链尾恰好 n 条边，倒数第 n 个节点就是 slow 的下一个，slow 自然是前驱。

**复杂度是多少？** 四个函数都只把链扫常数遍：走路指针最多各走 2n 步以内，都是 O(n) 时间；只用常数个指针变量，O(1) 辅助空间——没有哈希表记录访问过的节点，这正是快慢指针比"用集合存 id 查重"高明的地方。举个具体的数：十万节点的链，判环也就二三十万次指针跳转，一瞬间完成。cell4 还提醒了一个前提：`middle_node` 和 `remove_nth_from_end` 要求输入无环，否则"末节点""中点"根本没有定义。

## 六、测试用例在测什么

cell8 的断言逐条看：

- `h=list_to_nodes([1,2,3,4]); entry=h.next; h.next.next.next.next=entry`：手工造一个环，4 指回 2，入口记为 entry（节点 2）。
- `assert has_cycle(h) and detect_cycle(h) is entry`：判环返回 True，且找入口返回的**对象**就是节点 2 本人（用 `is` 做身份断言，比比值严格）。这是我们第三节的演示例。
- `h=ListNode(9); h.next=h; assert detect_cycle(h) is h`：**极小环**——单节点自指，μ=0、λ=1，是最容易写错的边界；入口必须是它自己。
- `assert not has_cycle(list_to_nodes([1,2])) and detect_cycle(None) is None`：**无环短链**和**空链表**两个边界：无环要返回 False，空链表的入口约定为 None。
- `assert middle_node(list_to_nodes([1,2,3,4])).val==3`：**偶数长度的中点约定**，确认返回第二个中点 3，不是 2。
- `assert nodes_to_list(remove_nth_from_end(list_to_nodes([1,2,3]),3))==[2,3]`：删倒数第 3 个 = 删头节点，考验 dummy 兜底。
- `assert nodes_to_list(remove_nth_from_end(list_to_nodes([1,2,3]),1))==[1,2]`：删倒数第 1 个 = 删尾节点，考验 fast 停在末节点的判断。
- `assert remove_nth_from_end(ListNode(1),1) is None`：**单节点删光**，返回 None（链表变空）。
- `print('N047: 所有本章断言通过')` 只是打一行确认信息。

## 七、练习思路提示

- **练习 1（推导相遇后回到头部的理由）**：方向是把第五节那段"快指针多走的 s 步全在环里、s 是 λ 的倍数、从相遇点补走 μ 步正好回到入口"的论证自己写一遍。建议手算一个 μ=2、λ=3 的小例子（比如 `1→2→3→4→5` 且 5 指回 3）：先算出相遇时 slow 走了几步（应为 6，λ 的 2 倍），再验证从相遇点走 μ=2 步确实落在节点 3。最后用 `detect_cycle` 对拍确认。
- **练习 2（区分偶数长度前中点和后中点）**：方向是改循环条件。本章条件 `while fast and fast.next` 给出第二个中点；改成 `while fast.next and fast.next.next` 会先一步刹车，给出第一个中点。建议用 `[1,2,3,4]` 手算两种条件各走几轮、slow 分别停在 2 还是 3，再用列表切片（`a[:n//2]`、`a[n//2:]` 的分界）写出两种约定的参考答案做对拍；别忘了核对奇数长度时两种写法应返回同一个节点。

## 八、对应 LeetCode 题目

- **141. Linked List Cycle（环形链表）**：本章 `has_cycle` 的原型题，练的是"速度差 1 保证相遇 + 循环条件防越界"。
- **142. Linked List Cycle II（环形链表 II）**：本章 `detect_cycle` 的原型题，练的是"相遇后一指针回头、同速再走 μ 步在入口会合"这步推导。
- **876. Middle of the Linked List（链表的中间结点）**：本章 `middle_node` 的原型题，练的是"慢指针步数恒为快指针一半"，含偶数长度返回第二个中点的约定。
- **19. Remove Nth Node From End of List（删除链表的倒数第 N 个结点）**：本章 `remove_nth_from_end` 的原型题，练的是"fast 先走 n 步造一把间距尺 + dummy 兜底删头"。
