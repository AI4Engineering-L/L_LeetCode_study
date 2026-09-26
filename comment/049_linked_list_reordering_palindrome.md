# N049 · 链表重排与回文 —— 说人话详解

> 对应 notebook：`notebooks/06_linked_lists/049_linked_list_reordering_palindrome.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章是链表模块的"毕业考"：把前面三章学的三招——**找中点（N047）、反转（N046）、合并/穿插（N048）**——组合起来解决两个问题：

1. **重排链表**（LC 143）：把 `1→2→3→4` 重排成 `1→4→2→3`，规则是"第一个、最后一个、第二个、倒数第二个……"交替取。例子：输入 `1→2→3→4`，输出 `1→4→2→3`。为什么是它：1 是开头、4 是结尾、2 是剩下的开头、3 是剩下的结尾，按这个交替规则穿插就得到答案。奇数长度 `1→2→3→4→5` 重排成 `1→5→2→4→3`（中间的 3 落在最后）。
2. **判断回文链表**（LC 234）：判断链表的值序列是否正读反读一样。例子：输入 `1→2→2→1`，输出 True；输入 `1→2`，输出 False。附加要求（本章的教学亮点）：检查过程会临时反转后半段，**用完要把调用者的链恢复原样**，不能悄悄留下一个被改得乱七八糟的链表——这就是"修改副作用"问题。

## 二、关键概念（定义）

- **前后半段**：把链表从中点切成两半。本章的约定是：奇数长度时中间节点归**前半**（前半长度是 ⌈n/2⌉）。切分点用 `_first_half_end` 找，它返回"前半最后一个节点"。
- **交替穿插（interleave）**：重排的核心动作。两条链 A 和 B，交替摘头：A₁→B₁→A₂→B₂→……重排 = 前半 + 反转后的后半做交替穿插。
- **回文比较**：后半反转后，它的第 i 个节点恰好对应原链的倒数第 i 个节点。所以"前半的第 i 个 vs 反转后半的第 i 个"逐位比较，全部相等就是回文。奇数长度时中间节点没有配对者，**无需参与比较**（cell1 明确说了这一点）。
- **修改副作用（side effect）与恢复（restore）**：函数改了传入的数据结构，调用者手里同一份链表也被改了。诚实的做法是要么明确告知"我会改"（`reorder_list` 本来就是要改），要么用完恢复（`is_palindrome_list` 的 `restore=True` 参数：把临时反转的后半再反转回去，恢复原来的连接关系）。cell4 强调"恢复的是节点拓扑而非仅值"——不是重新拼一条值相同的链，而是让**原来那批节点**回到**原来的 next 关系**。
- **第一个中点/前半末尾的找法**：与 N047 的 `middle_node` 不同，这里的循环条件是 `fast.next and fast.next.next`（先看再走），使 slow 停在前半最后一个节点上，而不是正中间。两个约定对应两道题的不同需要。

## 三、解决思路（一步步推导）

两个问题共享前三步，我们合并讲。

- **Step 1（找切分点）**：用 `_first_half_end` 找到前半最后一个节点 `middle`。
- **Step 2（反转后半）**：`second=reverse_list(middle.next)` 得到反向的后半。
- **Step 3（断开两半）**：`middle.next=None`（重排用），前半从此是独立短链。
- **Step 4a（重排：交替穿插）**：first 从前半头出发、second 从反转后半头出发，每轮各摘一个，先接 first 的、再接 second 的，直到 second 耗尽。
- **Step 4b（回文：逐位比较，可选恢复）**：left 从头、right 从 second 出发同步前进比较值；`restore=True` 时把 second 再反转回去接回 middle。

**手算演示一（重排 `1→2→3→4`）：**

- Step 1：middle=2（前半 `1→2`）。
- Step 2：second=reverse(`3→4`)=`4→3`。
- Step 3：middle.next=None，前半=`1→2`。
- Step 4a 穿插：

| 轮次 | first | second | 动作 | 链变为 |
|---|---|---|---|---|
| 1 | 1 | 4→3 | 1.next=4，4.next=2 | 1→4→2 |
| 2 | 2 | 3 | 2.next=3，3.next=None | 1→4→2→3 |

second 耗尽，结果 `1→4→2→3`。奇数长度 `1→2→3→4→5` 同理：middle=3，second=reverse(`4→5`)=`5→4`，穿插两轮得 `1→5→2→4→3`，中间节点 3 自然落到队尾。

**手算演示二（回文 `1→2→2→1`）：**

- middle=2（第一个 2，前半 `1→2`），second=reverse(`2→1`)=`1→2`（由原节点 1、2 组成，只是方向反了），middle.next=second 保持整链连通。
- 比较：left=1、right=1（末节点）：1==1；left=2、right=2：2==2；right 到头，全程相等，answer=True。
- 恢复：middle.next=reverse_list(second)=`2→1`，原链重新变成 `1→2→2→1`，与进来时一模一样。

**对照 cell6 的小实例表格：** notebook 对三条链先做回文判断再做重排，表格数据为：

| 原链 | 是否回文 | 重排链 |
|---|---|---|
| [1,2,3,4] | False | [1,4,2,3] |
| [1,2,3,4,5] | False | [1,5,2,4,3] |
| [1,2,2,1] | True | [1,1,2,2] |

三行分别对应偶数、奇数、回文三种典型情形，与我们上面的手算完全一致（注意第三行：回文判断已把链恢复原状，重排是在恢复后的原链上做的，结果 `1→1→2→2`）。

## 四、代码逐段讲解

cell3 开头的积木（`ListNode`、`TreeNode`、`list_to_nodes`、`nodes_to_list`）与 N045 相同，`reverse_list` 与 N046 完全一致，都不再重复。新东西是三个函数。

### 1. `_first_half_end` —— 找前半最后一个节点

```python
def _first_half_end(head):
    slow=fast=head
    while fast.next and fast.next.next: slow=slow.next; fast=fast.next.next
    return slow
```

- 循环条件是 `fast.next and fast.next.next`：先确认后面还有两步，才让两个指针各走。这比 N047 的 `fast and fast.next` **提前一轮刹车**，效果是 slow 停在"前半最后一个节点"而不是"第二个中点"。
- 以 `[1,2,3,4]` 为例：slow=fast=1；fast.next=2 且 fast.next.next=3 存在 → slow=2, fast=3；此时 fast.next=4 存在但 fast.next.next=None → 停车，slow=2 正是前半 `1→2` 的末尾。

### 2. `reorder_list` —— 重排

```python
def reorder_list(head):
    if head is None or head.next is None: return
    middle=_first_half_end(head); second=reverse_list(middle.next); middle.next=None
    first=head
    while second:
        following1,following2=first.next,second.next
        first.next=second; second.next=following1
        first,second=following1,following2
```

- 第 2 行：空链和单节点链无需重排，直接返回。函数没有 return 值——重排是**原地**修改，调用者手里的 head 不变（头永远是原第一个节点）。
- 第 3 行：一行干三件事——找 middle、反转后半得 second、断链（`middle.next=None`）。`second` 的长度是 ⌊n/2⌋，比前半短 0 或 1 个节点。
- 穿插循环：`following1,following2=first.next,second.next` **先存后改**（N046 的铁律）：两边的后继都要提前抓住，否则接下来两条赋值会把它们弄丢。
- `first.next=second; second.next=following1`：这一轮的穿插动作——first 节点指向 second 节点，second 节点指回前半的下一个节点，形成 `first→second→following1` 的小结构。
- `first,second=following1,following2`：两个指针齐步走到各自的下一位。
- 循环以 second 为准：second 比 first 先（或同时）耗尽，second 空时停止；偶数长度恰好全部接完，奇数长度时剩下的中间节点已被上一轮接上、其 next 天然是 None。

### 3. `is_palindrome_list` —— 回文判断（可选恢复）

```python
def is_palindrome_list(head,restore=True):
    if head is None or head.next is None: return True
    middle=_first_half_end(head); second=reverse_list(middle.next); middle.next=second
    left,right=head,second; answer=True
    while right:
        if left.val!=right.val: answer=False
        left=left.next; right=right.next
    if restore: middle.next=reverse_list(second)
    return answer
```

- 第 2 行：空链和单节点链是平凡的回文，直接返回 True。
- 第 3 行：同样是"找中点 + 反转后半"，但接回时用 `middle.next=second` 而**不是** None——保持整条链连通（没有游离的半截链），比较时 left 可以顺着走下去，恢复时也有明确的锚点。
- 比较循环以 right（反转后的后半，⌊n/2⌋ 个节点）为准：left 和 right 同步前进，逐位比值。`answer=False` 后**不提前 break**，仍走完全程——因为要保证 `second` 链在恢复前结构完整可预测（这里的 second 头一直没动，提前退出也不影响正确性，但不提前退出让"比较阶段不改变任何指针"这条纪律更明确）。
- 奇数长度时中间节点在前半末尾：right 恰好比 left 早一步耗尽，所以中间节点从未被比较——这正是 cell1 说的"奇数长度的中间节点无需参与比较"。
- `if restore: middle.next=reverse_list(second)`：恢复。`reverse_list` 是它自己的逆操作（反转再反转回到原序），比较阶段只读不写、second 头节点没变，所以把 second 再反转一次、接回 middle 后面，所有节点的 next 关系与进函数前**逐个相同**。若调用者传 `restore=False`，则明确接受"后半次序改变"的副作用（cell4 的契约）。

## 五、为什么是对的？复杂度是多少？（说人话）

**重排为什么对？** 反转后的后半，第 i 个节点恰好是原链的倒数第 i 个节点。穿插时前半出第 i 个、反转后半出倒数第 i 个，拼出来正是"正数第一个、倒数第一个、正数第二个、倒数第二个……"的题目要求。节点一个不丢：每轮四个引用先存后改，穿插只是重接 next，没有节点被创建或遗弃；second 先耗尽时剩下的节点（奇数情形的中间节点）已经被上一轮的 `second.next=following1` 接好。

**回文判断为什么对？** 回文的定义是"第 i 个值 = 倒数第 i 个值"。反转后的后半从尾往头读，所以 left 的第 i 步遇上 right 的第 i 步，恰好就是"正数第 i 个 vs 倒数第 i 个"的比较。right 只有 ⌊n/2⌋ 个节点，比较刚好覆盖全部配对，一个不多一个不少（中间节点无配对，不需要比）。

**恢复为什么彻底？** 因为比较阶段对链**只读**：left、right 只是两个走路引用，一个 next 都没改。进函数时链被唯一的写操作改成了"前半 + 反转后半"的形状；出函数前再做一次"反转后半"就把它变回原状——反转这个操作做两次等于什么都没做。而且恢复的是**节点之间的连接本身**（middle.next 重新指向原来的那个节点对象），不是"再造一条值相同的链"，这就是 cell4 说的"恢复的是节点拓扑而非仅值"。测试里用"每个节点的 next 是否还是原来那个对象"逐点验证了这一点。

**复杂度是多少？** 两个函数各做三件线性的事：找中点一趟 O(n)、反转后半一趟 O(n)（只扫一半）、比较/穿插一趟 O(n)。加起来还是 O(n)。空间方面不建新链、递归也没有，只有常数个指针，O(1)。举个具体的数：十万节点的链，判断回文也就三趟扫描共约二十万次指针操作，一瞬间完成。对比"把值拷进数组再首尾对撞"的做法（O(n) 额外空间），本题解法省了一个十万元素的数组——代价是要小心翼翼地处理"用完恢复"。

## 六、测试用例在测什么

cell8 的断言逐条看：

- `assert is_palindrome_list(list_to_nodes([1,2,2,1]))`：**正常回文**，偶数长度、带重复值，验证前半与反转后半逐位相等返回 True。
- `assert not is_palindrome_list(list_to_nodes([1,2]))`：**正常非回文**，最短的反例（1≠2），验证一旦出现不等值就返回 False。
- 后面的双重循环是**暴力对拍 + 副作用检查**，n 从 0 到 6、枚举所有 0/1 序列（2⁰+2¹+…+2⁶=127 条链）：
  1. 先用字典 `old` 把**每个节点的 next 指向哪个对象**原样记录下来（按身份记录，不是按值）。
  2. `assert is_palindrome_list(h,restore=True)==(list(a)==list(a)[::-1])`：回文结果与"列表反转比对"这个朴素参考一致——同时覆盖了 n=0、n=1（平凡回文）和奇偶各种长度。
  3. `assert all(node.next is nxt for node,nxt in old.items())`：判断完成后，**每个节点的 next 仍然指向进入前的同一个对象**——这就是"恢复的是节点拓扑而非仅值"的逐点机器验证，比"值序列看起来一样"严格得多。
  4. 接着对同一条链做 `reorder_list(h)`，用双下标 l、r 从两端交替取值构造参考答案 `ref`（while l<=r：取 a[l]，再取 a[r]……），断言重排后的值序列与参考完全一致——把"开头、结尾、次开头、次结尾"的定义直接编码成了测试。
- `print('N049: 所有本章断言通过')` 只是打一行确认信息。

测试顺序里还藏着一个细节值得注意：每条链先做 `is_palindrome_list`（restore=True，链被完整恢复），然后才在**同一条原链**上做 `reorder_list` 再对拍重排结果。如果恢复不彻底（哪怕只差一个节点的 next），重排的输入就不是 `a` 原型的链，后面的重排断言会跟着失败——两项检查在这里互相兜底。

另外 `product([0,1],repeat=n)` 从 n=0 开始，空链（返回 None）和单节点链（平凡回文）这两个最容易被漏掉的边界都被自动覆盖了。

## 七、练习思路提示

- **练习 1（回文检查后恢复原链）**：方向是独立写一遍"破坏 + 恢复"，并解释恢复为什么可靠。建议输入 `1→2→3→2→1`（奇数回文）：先手算 middle 是中间的 3、反转后半得 `1→2`、比较 (1,1)、(2,2) 全等、恢复后 middle.next 重新指向原来的 2。写验证时可以照抄 cell8 的招数：进函数前把每个节点的 next 存进字典，出函数后逐个用 `is` 核对。再想一个加深的问题：如果比较阶段提前 break，恢复还能对吗？（能，因为没改指针——但要能说出"为什么敢说没改"。）
- **练习 2（用额外数组做独立参照）**：方向是写一个 O(n) 空间的朴素参照解：把链表的值顺次读进数组 `vals`，然后用双下标 `i=0, j=len(vals)-1` 从两端向中间对撞比较。它完全不动链表，天然无副作用，适合当"标准答案"去对拍本章的 O(1) 空间版。建议拿 `[1,2,2,1]`、`[1,2]`、`[1]`、`[]` 各手算一遍参照解的输出，再随机生成几十条 0/1 链做对拍，体会"空间换简单"与"原地方巧但要管恢复"两种风格的取舍。

## 八、对应 LeetCode 题目

- **143. Reorder List（重排链表）**：本章 `reorder_list` 的原型题，练的是"找前半末 → 反转后半 → 交替穿插"三步组合，以及穿插时"先存两个后继再改指针"的手感。
- **234. Palindrome Linked List（回文链表）**：本章 `is_palindrome_list` 的原型题，练的是"反转后半逐位比较"这个 O(1) 空间解法，附带"函数副作用与恢复调用者数据"这个工程素养考点。
