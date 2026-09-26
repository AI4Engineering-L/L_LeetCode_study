# N046 · 链表反转与局部反转 —— 说人话详解

> 对应 notebook：`notebooks/06_linked_lists/046_linked_list_reversal.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章解决两个问题，它们是大量链表难题的基本功：

1. **整链反转**（LC 206）：给定链表头 `head`，把整条链的箭头全部掉头，返回新的头。例子：输入 `1→2→3`，输出 `3→2→1`。为什么是 3→2→1：原来 1 指向 2、2 指向 3，反转后 3 指向 2、2 指向 1，1 的 next 变成 None，链的入口自然换成原来最末尾的 3。
2. **局部反转**（LC 92）：只反转链表中从第 `left` 个到第 `right` 个节点（一基闭区间，即下标从 1 数、两头都含），其余部分原样不动。例子：输入 `1→2→3→4→5`，`left=2, right=4`，输出 `1→4→3→2→5`。为什么是它：下标 2 到 4 的那一段是 `2→3→4`，反转成 `4→3→2` 再装回去，前面的 1 和后面的 5 都不动。

核心难点只有一句话（cell0 的目标）：**在覆盖 next 之前先保存后继，并始终维护"已反转好的前缀"**。链表的每个节点只有一个 next 指针，你一旦改了它，后面半条链就找不回来了——所以必须"先存后改"。

## 二、关键概念（定义）

- **prev/curr/next 三指针**：反转时同时盯三个位置。本章代码用 `previous`（已反转部分的头）、`head`（当前正在处理的节点，兼作未处理后缀的头）、`following`（当前节点的下一个节点）。`following` 就是那个"必须先保存的后继"——不存它，改完 `head.next` 后半条链就丢了。
- **循环不变量**：循环每一轮开始时都为真的性质，是论证链表算法正确性的标准工具。本章的不变量是：`previous` 指向"原链前缀反转之后的链"，`head` 指向"还没碰过的后缀"，两段节点互不重叠、总数不变。 invariant 成立一轮传一轮，循环结束时它就直接给出正确性。
- **头插法（局部反转的核心动作）**：把一个节点从链上摘下来，插到某段开头。局部反转就是反复把"区间里 tail 后面的节点"摘出来头插到"区间开头"，每插一次，区间就多反转一个节点。
- **子区间拼接**：局部反转改动的是区间内部，但区间**外**有两个衔接点（前驱 `before` 和后继）必须保持接对。代码里 `before` 和 `tail` 两个引用就是钉住这两个衔接点的钉子。
- **一基闭区间（1-based, closed interval）**：下标从 1 开始数（不是从 0），且 `left`、`right` 两端都包含在反转范围内。这是 LC 92 的约定，cell1 也明确写了"参数使用一基闭区间，且要求区间在链表范围内"。
- **原地反转**：不 new 任何新节点，只改已有节点的 next 指向。本章两个函数都是原地的，辅助空间 O(1)。

## 三、解决思路（一步步推导）

### 整链反转 reverse_list

- **Step 1**：初始化 `previous=None`（已反转部分一开始是空的，空的头是 None）。
- **Step 2**：循环处理当前节点 `head`：先把 `following=head.next` 存起来（不然下一步就丢了后缀）。
- **Step 3**：调转箭头：`head.next=previous`——当前节点脱离后缀、成为"已反转前缀"的新头。
- **Step 4**：两个指针同时右移：`previous,head = head,following`。重复直到 `head` 为 None。
- **Step 5**：返回 `previous`，它就是原链最后一个节点、也就是新链的头。

**手算演示（和 cell6 的表格一模一样）：** 输入 `1→2→3→4`，初始 `previous=None`。

| 轮次 | 动作 | 已反转前缀 previous | 未处理后缀 head |
|---|---|---|---|
| 1 | 存 following=2；1.next=None；双移 | 1 | 2→3→4 |
| 2 | 存 following=3；2.next=1；双移 | 2→1 | 3→4 |
| 3 | 存 following=4；3.next=2；双移 | 3→2→1 | 4 |
| 4 | 存 following=None；4.next=3；双移 | 4→3→2→1 | （空） |

`head` 变 None，返回 `previous`，即 `4→3→2→1`。notebook 的 `show_table(['已反转前缀','未处理后缀'],rows)` 打出来的四行数据正是上面这张表，你可以逐行核对。

### 局部反转 reverse_between

- **Step 1**：造哨兵 `dummy=ListNode(0,head)`（沿用 N045 的技巧，处理 left=1 时"区间前驱不存在"的特例）。
- **Step 2**：`before` 从 dummy 走 `left-1` 步，停在区间第一个节点的前驱上。
- **Step 3**：`tail=before.next` 是区间第一个节点。反转结束后它会是区间的**最后一个**节点，我们全程不让 `tail` 挪窝，用它钉住"区间和后段的衔接点"。
- **Step 4**：循环 `right-left` 次，每次做一次"摘出 + 头插"：`moved=tail.next`（摘区间里的下一个）；`tail.next=moved.next`（tail 跨过 moved 抓住再下一个）；`moved.next=before.next`（moved 指向区间当前的开头）；`before.next=moved`（moved 成为区间新的开头）。每轮区间开头多一个节点，恰好全来自区间尾部的顺序。
- **Step 5**：返回 `dummy.next`。

**手算演示：** `1→2→3→4→5`，`left=2, right=4`。走 1 步后 `before=1`，`tail=2`，要循环 2 次。

| 轮次 | moved | 动作 | 整条链变为 |
|---|---|---|---|
| 1 | 3 | 2.next=4；3.next=2；1.next=3 | dummy→1→3→2→4→5 |
| 2 | 4 | 2.next=5；4.next=3；1.next=4 | dummy→1→4→3→2→5 |

区间 `2..4` 变成了 `4→3→2`，前面的 1、后面的 5 分毫未动，结果 `[1,4,3,2,5]`，和 cell8 断言一致。

再看一个"区间贴着头"的手算，检验哨兵的价值：`1→2→3→4→5`，`left=1, right=3`。`for _ in range(left-1)` 走 0 步，`before` 就是 dummy 本身，`tail=1`，循环 2 次：

| 轮次 | moved | 动作 | 整条链变为 |
|---|---|---|---|
| 1 | 2 | 1.next=3；2.next=1；dummy.next=2 | dummy→2→1→3→4→5 |
| 2 | 3 | 1.next=4；3.next=2；dummy.next=3 | dummy→3→2→1→4→5 |

区间 1..3 反转成 `3→2→1`，头节点真的换人了，但返回 `dummy.next` 照样拿到正确的新头——写带 dummy 的版本时你甚至没意识到这是"特例"。

## 四、代码逐段讲解

cell3 开头的 `ListNode`、`TreeNode`、`list_to_nodes`、`nodes_to_list` 与 N045 完全相同（节点积木 + 列表/链表互转 + 用 id 防环），这里不再重复，直接讲两个新函数。

### 1. `reverse_list` —— 整链反转

```python
def reverse_list(head):
    previous=None
    while head:
        following=head.next
        head.next=previous
        previous,head=head,following
    return previous
```

- `previous=None`：已反转前缀初始为空链。
- `while head:`：只要还有未处理的节点就继续；用节点本身当真值（None 即假）。
- `following=head.next`：**必须先做**的一步。下一行就要覆盖 `head.next`，不存住后继，后半条链当场丢失——这就是 cell0 目标里"在覆盖 next 前保存后继"的含义。
- `head.next=previous`：调转当前节点的箭头，让它指向已反转前缀；这一刻当前节点从"后缀的开头"变成了"前缀的新头"。
- `previous,head=head,following`：元组赋值，右边先全部求值再赋给左边，所以不借助临时变量就能同时完成"前缀头换成当前节点、当前节点换成原后继"。如果拆成两行顺序赋值就会用错已更新的值，这是新手常犯的错。
- `return previous`：循环退出时 head 是 None，previous 指向原链尾、即新链头。

### 2. `reverse_between` —— 局部反转

```python
def reverse_between(head,left,right):
    if not 1<=left<=right: raise ValueError('requires 1 <= left <= right')
    dummy=ListNode(0,head); before=dummy
    for _ in range(left-1): before=before.next
    tail=before.next
    for _ in range(right-left):
        moved=tail.next; tail.next=moved.next
        moved.next=before.next; before.next=moved
    return dummy.next
```

- 第 2 行是参数检查：`not 1<=left<=right` 一行挡住三种违约——left 小于 1、right 小于 left、right 小于 1。区间不合法直接抛异常，而不是悄悄返回错误结果。
- `dummy=ListNode(0,head)`：哨兵兜底 `left=1` 的情形。没有它，"区间前驱"在 left=1 时不存在，你又要写头节点特例。
- `for _ in range(left-1): before=before.next`：从哨兵（相当于"第 0 个节点"）走 left-1 步，正好停在区间第一个节点的前驱。left=1 时走 0 步，before 就是 dummy，特例自动消失。
- `tail=before.next`：区间第一个节点，反转完它会是区间最后节点。它后面永远跟着"还没搬进区间的节点"，它是唯一的摘取来源。
- 循环体三行是"摘出 + 头插"的标准动作（第三节 Step 4 已逐句讲过）。注意 `moved.next=before.next` 与 `before.next=moved` 的顺序不能颠倒：必须先让 moved 抓住区间现在的开头，再让 before 抓住 moved；颠倒的话区间开头就断了。
- 循环恰好执行 `right-left` 次：区间长度是 `right-left+1`，头插 `right-left` 次后，区间开头累计有 1+(right-left) 个节点、且顺序全部倒转，收工。
- `return dummy.next`：真正的头永远挂在哨兵后面。

## 五、为什么是对的？复杂度是多少？（说人话）

**整链反转为什么对？** 靠循环不变量：每一轮开始时，"previous 串着原链开头若干个节点的**逆序**，head 串着原链剩下的节点的**原序**，两段拼起来恰好是原链的全部节点、一个不多一个不少"。第一轮开始时 previous 是空、head 是整条链，显然成立。每一轮我们把 head 的第一个节点搬到 previous 的最前面，两段仍然拼成原链且前者逆序、后者原序，性质原样传给下一轮。循环结束时 head 是空，说明所有节点都搬进了 previous，而 previous 串着全部节点的逆序——这正是"整条链反转"。箭头掉头不会丢节点，因为每改一个 next 之前都先用 `following` 把后继存好了。

**局部反转为什么对？** 两个衔接点被钉死了：`before` 永远是"区间外的前驱"，`tail` 永远是"原区间第一个节点、现在的区间末尾"，并且 `tail.next` 在每一轮结束时都指向"区间外的后段开头"（因为最后一轮搬走的那个节点原来就排在 tail 后面第 right-left 位）。所以循环结束时，链的形状必然是：前段 →（before.next 开始的）反转后的区间 →（tail.next 开始的）原后段。区间外的连接从头到尾没有被破坏，这就是 cell4 说的"局部头插保留区间尾 tail，不改变区间外连接"。

**复杂度是多少？** 两个函数都把链扫常数遍：整链反转每节点碰一次，O(n)；局部反转走 left-1 步找 before，再做 right-left 次头插，总共不超过 n 步，O(n)。辅助空间只有 dummy 和常数个指针，O(1)，而且**不创建任何新数据节点**（dummy 是唯一的局部哨兵）——反转是纯指针重接。举个具体的数：十万节点的链，反转也就是十万次指针赋值，一瞬间完成；对比"拷贝到数组里倒序再重建"的做法，原地版省掉了十万个新节点的内存。

**顺带盘点三个新手常见错误**，每个都对应代码里的一行"防呆"：

1. 忘了先存 `following` 就改 `head.next`：后半条链当场失联，循环下一轮直接空转或漏节点。对应 `reverse_list` 第 4 行必须放在第 5 行之前。
2. 把 `previous,head=head,following` 拆成两行顺序赋值：比如先 `previous=head` 再 `head=following` 看似没事，但反过来先 `head=following` 再 `previous=head` 就把 previous 改成了后继，链表当场接错。元组赋值右边先整体求值，天然免疫这个问题。
3. `reverse_between` 里 `moved.next=before.next` 和 `before.next=moved` 写反：先执行后者的话，区间原来的开头就被 `moved` 覆盖丢了，之后的每次头插都接不上正确的节点。顺序是"新节点先抓住旧开头，前驱再抓住新节点"。

## 六、测试用例在测什么

cell8 的断言逐条看：

- `assert nodes_to_list(reverse_list(list_to_nodes([1,2,3])))==[3,2,1]`：**正常值测试**，验证整链反转的值顺序。三个节点足够暴露"头尾.next 忘置 None"之类的问题。
- `assert nodes_to_list(reverse_between(list_to_nodes([1,2,3,4,5]),2,4))==[1,4,3,2,5]`：**正常值测试**，区间在链中间（left=2、right=4），同时检验"区间内倒序、区间外不动"两件事。这是我们第三节手算的例子。
- 接下来四行是**对象身份测试**（比比值的测试更严格）：先把原链每个节点对象按顺序收进 `original`，然后 `reverse_list` 做两次得到 `restored`，再按顺序收一遍节点对象，断言 `restored==original`。它验证的是：反转两次后**同一批对象**回到了**同一顺序**。这同时说明实现是真正原地的（没有偷偷换节点）且无副作用（没有把谁弄丢、弄环）。这也呼应 cell1 那句"节点身份和 next 结构比打印出的值更重要"。
- 最后的三重循环是**暴力对拍**：n 从 1 到 7，枚举所有合法的 `(l,r)` 组合，参考答案是切片公式 `a[:l-1]+a[l-1:r][::-1]+a[r:]`（前段不动 + 区间切片倒序 + 后段不动）。它把 left=1（区间顶到头）、right=n（区间顶到尾）、left==right（区间长度 1，等于不反转）这些边界全部自动覆盖了。切片公式里的下标换算也值得看一眼：一基的 `left` 换成零基切片是 `l-1`，一基闭区间的右端 `right` 恰好等于零基切片的 exclusive 右端，所以区间正是 `a[l-1:r]`。
- `print('N046: 所有本章断言通过')` 只是打一行确认信息。

一个小提醒：对拍循环里 `a=list(range(n)` 的链表值是 0..n-1 且互不相等，所以它能测值序，但测不出"相等节点相对次序"的问题——那类问题（稳定性）要到 N048 的合并里才会出现。这也是"测试通过不等于一般性证明"的一个具体例子。

如果你想在本地快速复现这组对拍，把三重循环抄进任意 Python 环境、调用本章两个函数即可，总用例数是 1+3+6+10+15+21+28=84 组，跑起来瞬间结束。

## 七、练习思路提示

- **练习 1（写递归反转并计入调用栈）**：方向是把"把当前节点接到后缀反转结果的开头"写成递归：`new_head = reverse_list(head.next)`，然后 `head.next.next = head`、`head.next = None`。建议拿 `1→2→3` 手算递归展开：先一路递归到 3，回溯时 2 接到 3 后面、1 接到 2 后面。"计入调用栈"是要你意识到递归深度等于链长，栈空间是 O(n)——十万节点就可能爆栈，这正是迭代版 O(1) 空间的价值所在。验证时和本章迭代版对拍同一组输入。
- **练习 2（局部反转后验证两端拼接）**：方向是专门构造"区间贴边"的用例来考验衔接点。建议输入 `[1,2,3,4,5]` 分别取 `(left,right)=(1,5)`、`(1,3)`、`(3,5)`、`(2,2)`，手算每种情况循环结束后 `before` 指着谁、`tail.next` 指着谁，再对照 `nodes_to_list` 的输出验证拼接正确。特别注意 left=1 时 `before` 是 dummy 本身，这恰好是哨兵在兜底。

## 八、对应 LeetCode 题目

- **206. Reverse Linked List（反转链表）**：本章 `reverse_list` 的原型题，练的是"先存 following 再掉头 + previous/head 双指针齐移"这套节奏。
- **92. Reverse Linked List II（反转链表 II）**：本章 `reverse_between` 的原型题，练的是"dummy + before/tail 两个钉子 + 摘出头插"，即在一基闭区间上做局部反转而不破坏区间外的连接。
