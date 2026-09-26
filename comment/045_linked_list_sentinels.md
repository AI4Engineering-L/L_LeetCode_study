# N045 · 链表基础与哨兵节点 —— 说人话详解

> 对应 notebook：`notebooks/06_linked_lists/045_linked_list_sentinels.ipynb`

## 一、这章要解决什么问题？（问题描述）

链表和数组最大的区别是：链表的元素散落在内存各处，只靠每个节点里的 `next` 指针串成一条链。所以对链表做任何修改（删一个节点、插一个节点），本质都是**改指针的指向（next 重接）**。这一章要解决的问题是：**怎么安全地修改链表的头部和中间节点，而不把链条弄断、不丢节点**。

为什么头部特殊？因为链表的"入口"就是一个头指针 `head`。如果你删除的恰好是头节点，`head` 本身就要变，代码就得写"if 是头节点……else……"两套逻辑，非常容易出 bug。本章的核心武器"哨兵节点（dummy）"就是用来消灭这个特例的。

两个具体问题（分别对应本章两个接口）：

1. **删值**（LC 203）：给定链表头 `head` 和值 `val`，把链表里所有值等于 `val` 的节点都删掉，返回新链表头。例子：输入 `head = 6→1→6→2→6`，`val = 6`，输出 `1→2`。为什么是 1→2：链表里三个 6 全部被摘掉，剩下的 1 和 2 保持原来的先后顺序接在一起。
2. **设计链表**（LC 707）：实现一个 `MyLinkedList` 类，支持 `get(index)` 按下标取值、`addAtHead` 头插、`addAtTail` 尾插、`addAtIndex(index,val)` 按下标插入、`deleteAtIndex(index)` 按下标删除。

## 二、关键概念（定义）

- **ListNode（单链表节点）**：最小的积木，只有两个属性：`val` 存值，`next` 存"下一个节点的引用"（没有下一个就是 None）。整个链表就是一串这样的积木。
- **next 重接**：修改链表的唯一正确姿势。比如删除节点 b（a→b→c），不是"抹掉 b"，而是让 `a.next = c`，b 从此没人指向，自然脱离链条。先想清楚"谁的 next 要改"，再动手。
- **前驱（previous）**：待修改节点的前一个节点。要删或插某个节点，你必须先握住它的前驱，因为你要改的正是前驱的 `next`。这是 cell1 第一句话的含义："链表修改先找到待修改节点的前驱"。
- **哨兵节点（dummy，哑节点）**：一个不存有效数据、永远站在头节点前面的假节点。它存在的唯一目的，是让"真正的头节点"也有了前驱。这样一来，删除头节点就变成和删除任何中间节点一模一样的操作（改 dummy.next 而已），特例消失了。这是链表题最常用的防错技巧。
- **对象身份（id）**：Python 里每个对象有唯一身份编号 `id(obj)`。两个节点即使 `val` 相等，也是两个不同的对象。判断"是不是同一个节点"要看 `id` 或用 `is`，绝不能只看值。`nodes_to_list` 就是用 `id(head)` 检测"链表是不是意外成环了"（同一个节点被访问第二次说明有环）。
- **size（长度记录）**：`MyLinkedList` 里维护一个整数 `size` 随增删同步更新。有了它，判断"下标越界"就是一次整数比较，不用先遍历一遍数长度。这就是 cell1 说的"课程实现用 size 记录长度"。

## 三、解决思路（一步步推导）

### 思路 A：删值（remove_elements）

- **Step 1**：造一个 dummy 指向头：`dummy = ListNode(0, head)`。从此 dummy 站在 0 号位置，真正的头节点是它的"下一个"。
- **Step 2**：让 `previous = dummy`，我们始终保证要检查的节点是 `previous.next`。
- **Step 3**：循环：如果 `previous.next.val == val`，就执行 `previous.next = previous.next.next`（跳过它，等于删除）；**注意此时 previous 不动**，因为新接过来的节点可能也是要删的（连续待删的情况）。如果值不等，才让 `previous` 前进一格。
- **Step 4**：`previous.next` 变成 None（走到尾）时结束，返回 `dummy.next`——这才是新链表真正的头。

**手算演示：** `head = 6→1→6→2→6`，`val = 6`。初始链条：`dummy→6→1→6→2→6`。

| 轮次 | previous 在 | previous.next 是 | 动作 | 链条变为 |
|---|---|---|---|---|
| 1 | dummy | 6（等于 6） | 摘除，previous 不动 | dummy→1→6→2→6 |
| 2 | dummy | 1（不等） | previous 前进 | dummy→1→6→2→6 |
| 3 | 1 | 6（等于 6） | 摘除，previous 不动 | dummy→1→2→6 |
| 4 | 1 | 2（不等） | previous 前进 | dummy→1→2→6 |
| 5 | 2 | 6（等于 6） | 摘除，previous 不动 | dummy→1→2 |
| 结束 | 2 | None | 退出循环 | 结果 1→2 |

对照 cell6 的小实例表格，`原值 [6,1,6,2,6]、删除值 6、剩余链 [1,2]`，和我们手算完全一致。

### 思路 B：按下标增删查（MyLinkedList）

- **Step 1**：类里只放两样东西：`self.dummy`（永远不动的哨兵）和 `self.size`（当前长度）。
- **Step 2**：任何按下标的操作都拆成两步——先从 dummy 出发走 `index` 步，走到"目标位置的前驱 `before`"；然后对 `before.next` 做一次 next 重接。
- **Step 3**：插入：`before.next = ListNode(val, before.next)`（新节点先抓住原后继，前驱再抓住新节点），`size += 1`。删除：`before.next = before.next.next`，`size -= 1`。
- **Step 4**：边界约定（cell1 明确写了课程契约）：`get` 越界返回 -1；负的插入位置按 0 处理（等于插到头上）；超过长度的插入直接不执行。

**手算演示（cell6 的第二张表）：** 依次执行 `addAtIndex(0,1)`、`addAtIndex(1,3)`、`addAtIndex(1,2)`。

- 插 (0,1)：从 dummy 走 0 步，`before=dummy`，接上新节点 → 链为 `1`。
- 插 (1,3)：从 dummy 走 1 步，`before` 是节点 1，接上 3 → 链为 `1→3`。
- 插 (1,2)：从 dummy 走 1 步，`before` 还是节点 1，在它后面插入 2 → 链为 `1→2→3`。

notebook 的表格（插入位置、插入值、链）逐行就是 `[1]`、`[1,3]`、`[1,2,3]`，和手算一致。

## 四、代码逐段讲解

### 1. 两个基础积木和两个转换函数

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

- `ListNode`：单链表节点，`val` 默认 0、`next` 默认 None。`self.val, self.next = val, next` 是元组赋值的紧凑写法，等价于分两行赋值。
- `TreeNode`：二叉树节点（`left`、`right` 两个孩子），本章暂不使用，是为后续章节统一放置的数据结构积木。
- `list_to_nodes`：把 Python 列表转成链表，方便测试。它自己就用了一个 dummy：`tail` 永远指向"链表最后一个节点"，新节点接在 `tail.next` 上，然后 `tail` 前进。最后 `return dummy.next` 返回真正的头。
- `nodes_to_list`：反向转换，把链表读回列表。它一边读一边把每个节点的 `id` 记进集合 `seen`：如果同一个节点（注意是身份不是值）被访问第二次，说明链表意外成环了，立刻抛异常——这就是"对象身份"概念落地的例子，也保证测试不会在坏链表上无限转圈。

### 2. `remove_elements` —— 本章主角：用 dummy 删值

```python
def remove_elements(head,val):
    dummy=ListNode(0,head); previous=dummy
    while previous.next:
        if previous.next.val==val: previous.next=previous.next.next
        else: previous=previous.next
    return dummy.next
```

- `dummy=ListNode(0,head)`：造哨兵，值 0 只是占位，永远不会被比较（我们比较的是 `previous.next.val`，dummy 自己的值不参与）。第二个参数直接把 `next` 设成 `head`，一行完成"哨兵接管头节点"。
- `while previous.next:`：只要"下一个待检查节点"存在就继续；用节点本身当真值（非 None 即真）。
- 删除分支 `previous.next=previous.next.next`：让前驱跨过待删节点去抓住下一个，待删节点就此脱链。**注意这个分支里 previous 不前进**，这正对应 cell4 说的"删除时不推进 previous，防止漏掉连续待删节点"——想象 `6→6→1`，删掉第一个 6 后，新的 `previous.next` 还是 6，必须原地再检查一次。
- 非删除分支才 `previous=previous.next` 前进一格。
- `return dummy.next`：不管头换没换，dummy.next 永远是当前的头，调用者拿到的一定正确。

### 3. `MyLinkedList` —— 用 dummy + size 实现五个操作

```python
class MyLinkedList:
    def __init__(self): self.dummy=ListNode(); self.size=0
    def get(self,index):
        if not 0<=index<self.size: return -1
        node=self.dummy.next
        for _ in range(index): node=node.next
        return node.val
    def addAtHead(self,val): self.addAtIndex(0,val)
    def addAtTail(self,val): self.addAtIndex(self.size,val)
    def addAtIndex(self,index,val):
        index=max(index,0)
        if index>self.size: return
        before=self.dummy
        for _ in range(index): before=before.next
        before.next=ListNode(val,before.next); self.size+=1
    def deleteAtIndex(self,index):
        if not 0<=index<self.size: return
        before=self.dummy
        for _ in range(index): before=before.next
        before.next=before.next.next; self.size-=1
```

- `__init__`：整条链的全部状态就两个：哨兵 `self.dummy` 和长度 `self.size`。
- `get`：`if not 0<=index<self.size: return -1` 一行挡掉两类越界（负下标、≥size 的下标），返回 -1 是课程契约。合法时从 `dummy.next`（真头）出发走 `index` 步，落在的节点就是第 index 个，返回它的值。
- `addAtHead` / `addAtTail`：都不自己写逻辑，直接转调 `addAtIndex`。头插就是"在下标 0 插"，尾插就是"在下标 size 插"（走到 size 步恰好是最后一个节点后面）。一个函数收编两个特例，这是 dummy 带来的第二种简化。
- `addAtIndex`：`index=max(index,0)` 把负位置钳到 0（cell1 契约"负插入位置按 0 处理"）；`if index>self.size: return` 静默拒绝超界插入（契约"超过长度的插入不执行"）。然后从 dummy 走 index 步拿到前驱 `before`，执行 `before.next=ListNode(val,before.next)`——先让新节点的 next 抓住原来的后继，再让前驱抓住新节点，一次赋值完成插入，最后 `size+=1`。
- `deleteAtIndex`：`if not 0<=index<self.size: return` 挡掉非法下标（包括删空链表），注意这里是静默返回而不是报错。同样走到前驱，`before.next=before.next.next` 摘除节点，`size-=1`。
- 你会发现增、删、查的"找前驱"代码长得一模一样（从 dummy 走 index 步）——因为有了哨兵，**下标 0 不再是特例**，这就是本章标题"哨兵节点"的全部意义。

## 五、为什么是对的？复杂度是多少？（说人话）

**remove_elements 为什么对？** 我们靠一个始终成立的承诺（循环不变量）来论证：每一轮循环开始时，"previous 以及它前面的所有节点都已经过滤完毕（链上再没有值等于 val 的节点），而 previous.next 是下一个还没检查的节点"。初始时 previous=dummy，前面没有节点，承诺天然成立。每轮要么删掉一个待删节点（previous 不动，承诺依然成立，因为新接上来的节点还没检查）、要么确认 previous.next 干净后前进一格（承诺仍然成立）。循环结束时 previous.next 是 None，说明所有节点都检查过了，链上再无 val，正确。

**为什么头部不会丢？** 因为真正的头永远是 `dummy.next`：删的是头时，dummy.next 自动指向新头；一个不剩时 dummy.next 自然是 None。我们从不持有"头指针"这个易碎品，所以不存在"删了头忘了更新 head"的经典事故。

**MyLinkedList 为什么对？** 五个操作都建立在同一件事上：`size` 始终等于链上真实节点数（每次插入加一、删除减一、别处不动它），所以 `0<=index<size` 就是合法下标的准确判据；而"从 dummy 走 index 步"一定能停在下标 index 的前驱上，因为 dummy 相当于"下标 -1 的节点"。

**复杂度是多少？** `remove_elements` 要把链表扫一遍，是 O(n)；它对头部的删除和对中间的删除花同样的工夫（这就是 dummy 的功劳）。`MyLinkedList` 里：头插 `addAtIndex(0,val)` 只走 0 步，是 O(1)；按下标的 get、插入、删除都要从 dummy 走到前驱，最坏走整条链，是 O(n)；辅助空间只有 dummy 和几个指针变量，O(1)。举个具体的数：链表有 10⁵ 个节点时，一次 `get(99999)` 要走约十万步，也就是十万次指针跳转，一瞬间完成；但如果你的场景是"频繁头插"，O(1) 的 `addAtHead` 每次只做常数次操作，比数组头插（要整体挪动十万个元素）快得多——这就是链表存在的意义。

## 六、测试用例在测什么

cell8 的断言逐条看：

- `assert nodes_to_list(remove_elements(list_to_nodes([6,1,6,2,6]),6))==[1,2]`：**正常值测试**，头部、中间、尾部各埋了一个 6，确认三处都能删干净且顺序保持。这正是我们第三节手算的例子。
- `assert remove_elements(list_to_nodes([6,6]),6) is None`：**极端边界——全删光**。注意用的是 `is None` 而不是 `== None`，因为判断"没有节点"是对象身份问题；此时 dummy.next 是 None，新链表头不存在。
- `assert remove_elements(None,6) is None`：**空链表输入**。链表本来就是空的，删完还是空的，代码必须不崩、安静地返回 None。
- `x=MyLinkedList(); x.addAtHead(1); x.addAtTail(3); x.addAtIndex(1,2)`：组合操作，先构造出 `1→2→3`。
- `assert x.get(1)==2`：验证中间下标读取正确（下标 1 是第二个元素 2）。
- `x.deleteAtIndex(1); assert x.get(1)==3`：删掉下标 1（节点 2）之后，原来的下标 2（节点 3）顶上来变成新的下标 1，验证删除后链条正确重接、size 语义没漂移。
- `assert nodes_to_list(x.dummy.next)==[1,3] and x.size==2`：从哨兵后面把整条链读出来核对为 `[1,3]`，并确认 size 同步减到了 2——同时测"链的实际内容"和"账面计数"两份记录一致。
- `x.deleteAtIndex(9); assert x.size==2`：**越界删除**。下标 9 不存在，操作应被静默忽略，size 不变。这条专门测契约"越界删除不执行、不报错"。
- `print('N045: 所有本章断言通过')` 只是打一行确认信息。

## 七、练习思路提示

- **练习 1（不使用 dummy 再实现一次）**：方向是体会"哨兵到底帮你省了什么"。你要写两套分支：删除/插入目标是头节点时，直接修改 `head` 变量本身；目标是中间节点时，走位找前驱再改 `next`。建议输入就用 `[6,1,6,2,6]` 删 6，先手算"第一轮就要改头指针"的情形，再注意连续 6 在头部出现时（比如 `[6,6,1]`）while 循环的条件该写什么才不会漏删。最后和本章带 dummy 的版本对拍同样的输入。
- **练习 2（说明两种写法边界复杂度）**：方向是数"分支"和"代码路径"。带 dummy 的写法：头和中间走同一条路径，只有一套逻辑，越界判断也只有一处；不带 dummy 的写法：每个操作都要先问"是不是头"，代码路径翻倍，出 bug 的机会也翻倍。但两者的时间复杂度都是 O(n)——dummy 换来的不是速度，而是**统一性**（消灭特例）。建议用 `addAtHead` 做手算对比：带 dummy 走 0 步插入；不带 dummy 直接 `head = ListNode(val, head)`，一步到位，连"找前驱"都省了——顺便想想这算不算不带 dummy 版本的一个小优点。

## 八、对应 LeetCode 题目

- **203. Remove Linked List Elements（移除链表元素）**：本章 `remove_elements` 的原型题，练的是"dummy 让头节点删除不再是特例 + 删除后 previous 不前进"这两个点。
- **707. Design Linked List（设计链表）**：本章 `MyLinkedList` 的原型题，练的是"dummy + size 双状态维护五个按下标的操作"，以及越界/负下标这些边界契约的落实。
