# N050 · K组反转、相交与随机指针 —— 说人话详解

> 对应 notebook：`notebooks/06_linked_lists/050_linked_list_advanced_structures.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章其实装了三道经典的链表难题，它们的共同主题是：**别只看链表里存的数字，要看节点本身是谁、指针怎么连**。

1. **K 个一组翻转链表**：给你一条链表和一个数字 k，你要每 k 个节点为一组，把组内顺序颠倒；如果最后一组凑不够 k 个节点，这一组就保持原样。比如链表 `1→2→3→4→5`，k=2：第一组是 (1,2) 翻成 (2,1)，第二组是 (3,4) 翻成 (4,3)，剩下的 5 不够一组，原地不动，所以输出 `2→1→4→3→5`。
2. **两个链表的交点**：两条链表可能在某个节点汇合成一条公共尾巴。你要返回**那个共同的节点对象本身**，而不是值相等的节点。比如 A 链是 `1→8→9`，B 链是 `2→3→8→9`，其中 `8→9` 是两个链表**共享**的同一段内存，那么答案就是节点 8（用 `is` 判断才相等）。如果两条链只是各自长得像 `1→2`，没有任何共享节点，答案就是 None。
3. **带随机指针的链表深拷贝**：每个节点除了 `next` 还有一条 `random` 边，可以指向链里任何节点或 None。你要造出一条**全新的**链表，结构一模一样，但一个原节点都不能复用。比如 `7→13→11`，且 7.random→11、13.random→7、11.random→11，拷贝出来的新链也要满足同样的关系，且新旧两套节点完全没有交集。

## 二、关键概念（定义）

- **节点身份（identity）**：两个节点"是同一个"，指它们是同一块内存，Python 里用 `x is y` 判断。值相等（`==`）不代表身份相同，比如两个值都是 8 的节点可以是不同的对象。
- **引用拓扑**：链表的"形状"是由 next/random 这些引用连出来的。本章关心的是"谁连谁"，而不是"存的数字是多少"。
- **局部重连（指针换轨）**：不新建链表，只改节点里的 next 指向，让一段链表"改道"。K 组反转就靠它做到 O(1) 额外空间。
- **哑节点（dummy，哨兵节点）**：在真正的头节点前面额外加一个假头。它让"翻转第一组时头节点也会变"这种情况不再特殊，最后返回 `dummy.next` 就是新头。
- **K 组边界**：反转前先数一数"从这里往后还够不够 k 个节点"。够才翻，不够就到此为止，尾巴保持原序。
- **双指针换轨（走完自己换到对方）**：求交点的技巧。指针 p 从 A 链头出发，走完了就跳到 B 链头继续；q 反过来。这样两者走过的总路程都是 len(A)+len(B)，终点必然对齐。
- **深拷贝（deep copy）**：连结构带节点全部重新造一份，而不是只复制引用（那是浅拷贝）。浅拷贝会让新旧链共享节点，本题明确禁止。
- **映射法（哈希表：原节点→新节点）**：复制随机链表时，先用一遍循环建 `mapping[原节点]=新节点`；第二遍再查表补 next 和 random 边。random 指向谁，就去表里取对应的新节点。
- **交织法（interleaving）**：映射法的省空间亲戚。把新节点直接插在原节点后面，形成 `原1→新1→原2→新2...`，这样"新节点的 random"就是"原节点的 random 的下一个"，不需要哈希表。本章练习 2 会让你比较两者。

## 三、解决思路（一步步推导）

**reverse_k_group 的思路：**

1. 先在头上加一个 dummy，用 `before` 指向"上一组的结尾"（初始是 dummy 本身）。
2. 从 `before` 往后数 k 步，走到 `end`。如果中途变 None，说明凑不齐一组，直接返回，尾巴不动。
3. 记下组后第一个节点 `after=end.next`，然后把 `before.next` 到 `end` 这一段原地反转。
4. 反转的巧招：把 `previous` 初始化为 `after`（而不是 None）。这样组内最后一个节点反转后自然指向 `after`，尾巴不用二次修补。
5. 反转完，`before.next` 要改成新组头（也就是 `end`），然后 `before` 移到旧组头（反转后变成了组尾）。

**手算演示：`1→2→3→4→5`，k=2，第一轮——**

- 起点：`dummy→1→2→3→4→5`，`before=dummy`。
- 数 2 步：`end=2`（节点 2），够一组。
- `after=3`（节点 3），`previous=3`，`current=1`（节点 1）。
- 循环第一圈：`following=2`；1.next 改指向 3（即 previous）；`previous=1`，`current=2`。
- 循环第二圈：`following=3`；2.next 改指向 1（即 previous）；`previous=2`，`current=3`。此时 `current is after`（都是节点 3），停止。
- 现在 `2→1→3→4→5`。`old_start=1`；`before.next=2`；`before=1`。
- 第二轮同理翻 (3,4)，得到 `2→1→4→3→5`，`before=3`。第三轮数 2 步时只走到 5 再走一步就 None，返回。

对照 cell6 的小实例表（输入固定 `a=[1,2,3,4,5]`）：

| k | 重连后 |
|---|--------|
| 1 | [1, 2, 3, 4, 5]（每组 1 个，翻了等于没翻） |
| 2 | [2, 1, 4, 3, 5]（整两组翻，剩 5 原样） |
| 3 | [3, 2, 1, 4, 5]（翻一组，剩 4、5 原样） |
| 6 | [1, 2, 3, 4, 5]（凑不齐一组，整体原样） |

**get_intersection_node 的思路（手算）：** A=`1→8→9`（长 3），B=`2→3→8→9`（长 4）。p 从 1 出发走 3 步到 None 后跳到 B 头；q 从 2 出发走 4 步到 None 后跳到 A 头。两者各走 3+4=7 步：p 的路线是 1,8,9,2,3,8,9；q 的路线是 2,3,8,9,1,8,9。可以看到走到第 6 步时两者都停在共享的节点 8 上，循环条件 `p is not q` 结束，返回节点 8。

**copy_random_list 的思路：** 第一遍只造节点存进字典（此刻新节点还是孤岛，互相不连）；第二遍查三次表：新.next = mapping[原.next]，新.random = mapping[原.random]。`mapping={None:None}` 这一项让"原节点的 next/random 是 None"的情况不用单独 if 判断。

## 四、代码逐段讲解

cell3 里的 `ListNode`、`TreeNode` 是全书通用的节点定义（本章只用 ListNode）；`list_to_nodes` 把 Python 列表搭成链表；`nodes_to_list` 把链表读回列表，并用 `id(head)` 记录走过的节点、一旦重复就报错，防止有环链表把读取函数变成死循环。

**K 组反转（逐字照抄）：**

```python
def reverse_k_group(head,k):
    if k<1: raise ValueError('k must be positive')
    dummy=ListNode(0,head); before=dummy
    while True:
        end=before
        for _ in range(k):
            end=end.next
            if end is None: return dummy.next
        after=end.next; previous=after; current=before.next
        while current is not after:
            following=current.next; current.next=previous
            previous,current=current,following
        old_start=before.next; before.next=end; before=old_start
```

- 第 2 行 `if k<1: raise ValueError(...)` 是在挡非法输入：k 是 0 或负数时，"每 k 个一组"没有意义，直接抛异常而不是给出错误答案。
- `dummy=ListNode(0,head); before=dummy`：造假头并让 `before` 表示"上一组的最后一个节点"，一开始上一组就是空的 dummy。
- 内层 `for` 循环从 `before` 往后走 k 步找 `end`；中途 `end is None` 说明剩余节点不足 k 个，尾巴必须保持原序，所以立刻 `return dummy.next`（这也是唯一的正常出口）。
- `previous=after` 是最省事的一步：组内反转的初值直接设成"组后的第一个节点"，反转结束时组尾自动接上后半段，不需要事后修尾巴。
- `while current is not after` 这个条件用 `is` 比较，确保只翻本组、翻到 after 前一格为止；`following=current.next` 先把后继存起来再改指向，否则改完就找不到下一站了。
- 最后一行把 `before` 挪到"旧组头"（反转后它成了这一组的最后一个节点），为下一组做准备。

**求交点（逐字照抄）：**

```python
def get_intersection_node(a,b):
    p,q=a,b
    while p is not q:
        p=p.next if p else b
        q=q.next if q else a
    return p
```

- `p,q=a,b`：两个指针各自从自己链的头出发。
- `p=p.next if p else b` 是紧凑的条件表达式：p 还没走到头就往前一步；p 已经是 None（走完了）就"换轨"跳到另一条链 b 的头部。q 对称。
- 两不相交时会发生什么？两者最终都会变成 None，`None is None` 成立，循环结束返回 None——所以"无交点"不需要单独分支。

**随机链表拷贝（逐字照抄）：**

```python
def copy_random_list(head):
    mapping={None:None}; node=head
    while node:
        mapping[node]=RandomNode(node.val); node=node.next
    node=head
    while node:
        mapping[node].next=mapping[node.next]
        mapping[node].random=mapping[node.random]
        node=node.next
    return mapping[head]
```

- `mapping={None:None}` 预先把 None 映射到 None，这让后面 `mapping[node.random]` 在 random 为 None 时也能直接查到答案。
- 第一个 `while` 只负责"造人"：给每个原节点配一个值相同的新节点，此时新节点还没有任何边。
- 第二个 `while` 负责"接线"：next 和 random 都通过查表拿到对应的新节点，保证 random 指向的是新链里的节点而不是原链的。
- `return mapping[head]` 顺带处理了空链：head 是 None 时返回 mapping[None]，也就是 None。

## 五、为什么是对的？复杂度是多少？（说人话）

- **K 组反转为什么对**：反转一组之前，我们一定已经确认了"这组恰好有 k 个节点"，而反转动作只改这 k 个节点内部的指针，加上组前 `before` 和组后 `after` 这两个边界，所以组外的部分完全没被碰坏。每组处理完，`before` 都会准确地挪到本组反转后的最后一个节点，下一组的边界因此又是正确的。不足 k 个的尾巴根本不进入反转循环，自然保持原序。
- **求交点为什么对**：p 走的路线是 A 的独有部分 + 公共尾巴 + B 的独有部分；q 走的是 B 的独有部分 + 公共尾巴 + A 的独有部分。两条路线长度都是"全长 A + 全长 B"，所以当它们第一次同时站在公共尾巴上时，走的步数一样，必然在同一个节点相遇（或者同时走到 None）。
- **拷贝为什么对**：字典里每个原节点对应且只对应一个新节点，第二遍接线时"原节点的 next 指向谁，新节点的 next 就指向谁的新副本"，random 同理，所以新链的形状和原链一模一样，而且全部是新节点，绝不和原链共享。
- **复杂度**：反转和拷贝都是把链表走常数遍，是 O(n) 时间；求交点是 O(n+m)（两条链的长度）。n=10⁵ 个节点时，O(n) 大约就是几十万次指针操作，一瞬间算完。额外空间上：反转和求交点只用了几个变量，是 O(1)；拷贝的字典必须存 n 条映射，所以是 O(n) 空间——这正是练习 2 里交织法想优化的点。
- **前提**：本章假设 next 链有限且无环（cell4 原文：next 链必须有限无环），random 只能指向链内节点或 None。如果链有环，`reverse_k_group` 的计数循环会永远停不下来。

## 六、测试用例在测什么

- `assert nodes_to_list(reverse_k_group(list_to_nodes([1,2,3,4,5]),2))==[2,1,4,3,5]`：正常情况——正好整除加一组余数，验证"整组翻、余数不动"。
- `assert nodes_to_list(reverse_k_group(list_to_nodes([1,2]),3))==[1,2]`：边界情况——k 比整条链还长，一个组都凑不齐，应原样返回。
- `shared=list_to_nodes([8,9]); a=ListNode(1,shared); b=ListNode(2,ListNode(3,shared))` 然后断言 `get_intersection_node(a,b) is shared`：特殊构造——两条链真的共享同一段节点（a 的 next 直接接在 shared 上），断言用 `is` 强调返回的是那个对象本身，而不是值碰巧相等的别的节点。
- `assert get_intersection_node(list_to_nodes([1,2]),list_to_nodes([1,2])) is None`：两条独立的链，即使值完全相同也没有共享节点，必须返回 None。这条专防"按值比较"的错误实现。
- 接着构造 x(7)→y(13)→z(11)，x.random=z、y.random=x、z.random=z（自环 random 也覆盖了）。
- `assert not set(originals)&set(clones)`：新旧节点集合的交集必须为空，验证这是深拷贝、没有偷懒复用原节点。
- `assert [n.val for n in clones]==[7,13,11]`：next 链顺序正确。
- `assert clones[0].random is clones[2] and clones[1].random is clones[0] and clones[2].random is clones[2]`：三条 random 边逐条对上，且都指向**新链内部**的节点（注意 `is` 而非值比较）。
- `assert copy_random_list(None) is None`：空链是最后一个边界，返回值也必须是 None。

## 七、练习思路提示

- **练习 1（不足 K 组保持原序）**：先把"输入输出"写死，例如 `[1,2,3,4,5], k=4` 应得 `[4,3,2,1,5]`。提示：关键在于"什么时候决定不再反转"——数节点的动作必须发生在改指针**之前**；想想为什么本章代码把"数不够就 return"放在内层 for 循环里，而不是先翻再检查。手算时盯住"最后一组的 before 指到谁"。
- **练习 2（映射拷贝 vs 交织拷贝）**：提示：交织法的三步是（1）每个原节点后面插入它的拷贝，形成 `A→A'→B→B'`；（2）此时 `原.random` 的下一个就是 `原.random` 的新副本，用它接 `A'.random`；（3）最后把交织链拆成两条。对比维度：映射法多用了一个 O(n) 的字典；交织法不用字典，但会**临时改动原链的 next**，拆完才恢复——考虑如果中途抛异常，原链会处于什么状态（副作用）。建议先对 3 个节点的小例子把三步画在纸上。

## 八、对应 LeetCode 题目

- **25. Reverse Nodes in k-Group**：练的就是本章第一件事——K 组边界确认 + 哑节点辅助的局部反转，本题是其标准原型。
- **160. Intersection of Two Linked Lists**：练"比较节点身份而不是值"，双指针换轨抵消长度差正是它的最优解。
- **138. Copy List with Random Pointer**：练"建映射再接线"的深拷贝套路，random 边必须查表（或交织）才能找对新节点。
