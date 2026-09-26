# N009 · 类、节点与迭代协议 —— 说人话详解

> 对应 notebook：`notebooks/00_foundations/009_classes_nodes_protocols.ipynb`

## 一、这章要解决什么问题？（问题描述）

LeetCode 的链表题和树题，题目给你的输入不是现成的列表，而是"一串节点对象"，每个节点里存着一个值和一个指向下一个节点的引用。这一章要解决的问题就是：**学会自己定义这种节点"积木"（用 class），学会把一个普通列表拼成链表，并且能顺着链表走一遍完成计算。**

本章的主线例子是：**把一条表示二进制数的链表换算成十进制整数**。链表从头到尾，恰好是从二进制数的最高位到最低位。

给你一个具体到数字的例子：

- 输入：一条链表 `1 -> 0 -> 1`（三个节点，val 依次是 1、0、1）。
- 它表示的二进制数是 `101`，也就是 1×4 + 0×2 + 1×1 = 5。
- 所以输出：`5`。

为什么是 5？因为从高位往低位读，每读一位就相当于"把已经读过的部分整体左移一位（乘 2），再加上新读到的这一位"。读完 1：值是 1；读完 0：值是 1×2+0=2；读完 1：值是 2×2+1=5。这就是位置记数法，我们全程只做整数运算，不需要先把链表拼成字符串 `"101"` 再调用转换函数。

## 二、关键概念（定义）

- **class（类）**：类是你自己定义的"数据形状说明书"。你规定这种数据有哪些字段（比如"一个 val，一个 next"），以后每造一个对象就自动带上这些字段。我们用它是因为 Python 自带的 int、list 里没有一个类型能表达"值 + 指向下一个人的引用"这种结构。
- **`__init__`（构造方法）**：这是类里面的一个特殊函数，在你创建对象的那一刻自动执行，负责给字段填初值。你写 `ListNode(5)` 时，Python 就是在调用 `ListNode.__init__`，把 val 设成 5。
- **属性引用（attribute）**：用点号去访问对象身上的字段，比如 `head.val`、`head.next`。链表的一切操作都是"顺着 next 一个个摸过去"。
- **ListNode（链表节点）**：本章定义的最小链表节点类，只有两个字段：`val` 存值，`next` 存下一个节点的引用（没有下一个就是 None）。一条链表就是若干个 ListNode 串起来的。
- **TreeNode（树节点）**：树的最小节点类，有三个字段：`val` 存值，`left` 指左孩子，`right` 指右孩子。它和 ListNode 的唯一区别是"往后分两条路"而不是"一条路"。
- **值相等 vs 对象身份相同**：两个节点 `val` 都是 3，它们是两个不同的对象；判断"是不是同一个对象"要用 `is`（比内存地址），判断"值是否一样"用 `==`。链表里"值相同"和"是同一个节点"完全是两码事，这在判环等场景至关重要。
- **哑节点/哨兵节点（dummy node）**：造链表时先立一个"假头"放在最前面，真正的节点全部挂在它后面，最后返回 `dummy.next` 就是真头。我们用它是因为它能让"第一个节点"和"后面的节点"走完全一样的挂接逻辑，省掉特殊判断。
- **迭代器与生成器（导览）**：知识点中提及的概念——迭代器是"能被 for 循环逐个吐值的对象"，生成器是用 `yield` 写的、暂停/恢复执行的函数。本章只需知道链表的 `while head: ... head = head.next` 本质上就是手动迭代。
- **位置记数法（positional notation）**：一个数字每一位的含义取决于它所在的位置。二进制里往左挪一位，数值翻倍，所以"读新位 = 旧值 × 2 + 新位"。

## 三、解决思路（一步步推导）

`binary_list_to_int` 的思路只有三步：

- **Step 1：准备一个累加器 value，初始为 0。** 它表示"到目前为止读过的位所代表的整数"。
- **Step 2：从头节点走到尾节点，每走一步做一次 `value = value*2 + 当前位`。** 乘 2 是因为来了一位新数字，前面读过的所有位都整体往左挪了一位（二进制左移一位等于翻倍）；加上当前位，就是新读入的这一位的贡献。
- **Step 3：走完返回 value。** 空链表（head 是 None）时循环一次不进，value 保持 0，正好符合"没有数字就是 0"的直觉。

**手算演示（输入链表 `1 -> 0 -> 1`）：**

| 当前位 | 旧值 | 新值 = 2×旧值 + 位 |
|--------|------|--------------------|
| 1 | 0 | 0×2+1 = 1 |
| 0 | 1 | 1×2+0 = 2 |
| 1 | 2 | 2×2+1 = 5 |

这张表就是 cell6 里 `show_table` 实际生成的那张表（表头原文是"当前位/旧值/新值=2×旧值+位"）。三步走完，答案是 5。你可以拿 101 的二进制含义验算：4+0+1=5，一致。

**造链表 `list_to_nodes([1,0,1])` 的过程也手演一遍：**

1. 立哑节点 dummy，tail 指向 dummy。此时链表：`dummy ->`（空）。
2. 读到 1：tail 后面挂新节点(1)，tail 前移到新节点。链表：`dummy -> 1`。
3. 读到 0：同样挂新节点(0)。链表：`dummy -> 1 -> 0`。
4. 读到 1：挂新节点(1)。链表：`dummy -> 1 -> 0 -> 1`。
5. 返回 `dummy.next`，也就是真正的头节点（val=1 的那个）。

整个过程 tail 像针线一样往后缝，每个新节点的挂法完全一样——这就是哑节点带来的好处。

## 四、代码逐段讲解

cell3 一共定义了两个类和三个函数，我们逐段看。

### 类 1、2：`ListNode` 和 `TreeNode`

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right
```

- `class ListNode:`：声明一个名叫 ListNode 的类。
- `def __init__(self, val=0, next=None):`：构造函数带默认参数——不传 val 就当 0，不传 next 就当 None（"没有下一个"）。有了默认值，你可以只写 `ListNode(7)` 就造一个"孤立"节点。
- `self.val, self.next = val, next`：这是一行多赋值，把参数 val 和 next 存到对象自己的字段上，等价于分开写两行 `self.val = val` 和 `self.next = next`，紧凑但功能完全一样。注意 `next` 虽然和内置函数 `next()` 撞名，但作为属性名没有冲突，这是 LeetCode 官方模板的惯用写法。
- `TreeNode` 结构完全同理，只是把"一个 next"换成"left、right 两个孩子"。

### 函数 1：`list_to_nodes` —— 列表拼成链表

```python
def list_to_nodes(values):
    dummy = tail = ListNode()
    for value in values:
        tail.next = ListNode(value)
        tail = tail.next
    return dummy.next
```

- `dummy = tail = ListNode()`：一口气造一个哑节点，让 dummy 和 tail 两个名字同时指向它。dummy 负责"记住起点"，tail 负责"跟着往后走"。
- `tail.next = ListNode(value)`：在尾巴后面挂一个新节点。
- `tail = tail.next`：把尾巴指针挪到刚挂上的新节点，下一轮继续往后挂。
- `return dummy.next`：dummy 本身是假头，它后面第一个才是真头；values 为空时循环不执行，返回 None（空链表），行为自然正确。

### 函数 2：`nodes_to_list` —— 链表拆回列表（带防环检查）

```python
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

- `values, seen = [], set()`：values 收集节点值；seen 是一个集合，记录"已经路过的节点"。
- `if id(head) in seen: raise ValueError(...)`：`id()` 返回对象的唯一身份证号。如果当前节点的身份证号之前见过，说明链表绕回来了（有环），再走下去就是死循环——所以直接抛异常，报错信息原意是"在一条本该有限的链表里发现了环"。这体现了"值相同不代表对象相同"：判环必须比对象身份，不能比值。
- `seen.add(id(head))`、`values.append(head.val)`：登记当前节点，收集它的值。
- `head = head.next`：往后走一步。走到 None 时 `while head is not None` 条件不成立，循环结束，返回收集好的列表。

### 函数 3：`binary_list_to_int` —— 二进制链表转整数

```python
def binary_list_to_int(head):
    value=0
    while head:
        if head.val not in (0,1):
            raise ValueError('only binary digits are allowed')
        value=value*2+head.val
        head=head.next
    return value
```

- `value=0`：累加器从 0 开始。
- `while head:`：只要当前节点存在就继续；None 会让条件为假、循环停止（等价于 `while head is not None`，写法更紧凑）。
- `if head.val not in (0,1): raise ValueError(...)`：这是输入合法性检查——二进制链表每一位只能是 0 或 1，混进来别的数字就抛异常，报错原意是"只允许二进制数字"。
- `value=value*2+head.val`：本章的核心一行，即第三节推导的"左移一位再加新位"。
- `return value`：全部位读完后返回结果。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么 `binary_list_to_int` 算出的值是对的？** 我们用一句话把论证说完整：读第 1 位之后，value 恰好等于第 1 位单独表示的数（0 或 1，显然成立）；此后每多读一位，我们就把旧值乘 2 再加新位——而"在二进制数后面追加一位"在数学上恰好就是"旧数整体乘 2 再加这位"。所以读到第 k 位时，value 恰好等于前 k 位组成的二进制数。全部读完，value 就是整条链表示的数。这不是碰运气，而是每一步都维持着同一个性质，一直保持到最后。

**为什么 `nodes_to_list` 的防环检查有效？** 有限条"无环"链表的节点总数是有限的，每个节点被走到一次就登记身份证号；如果链表有环，沿着 next 迟早第二次撞见同一个节点对象，身份证号在集合里查得到，立刻报错停机。所以这个函数要么正常走完，要么明确失败，不会无限转圈。

**复杂度是多少？** 三个函数都只把链表从头到尾走一遍，每个节点处理一次，所以时间都是 O(n)，n 是节点数。具体感受一下：n = 10⁵ 个节点，也就是十万次"取值、乘 2、加法、挪指针"，一瞬间就算完。空间上，`binary_list_to_int` 只用一个 value 变量，额外空间 O(1)；`nodes_to_list` 的列表和集合各装 n 项，是 O(n)。有一个 Python 特有的小提醒（cell4 原文也点了）：如果二进制位数特别长，value 会变成很大的整数，Python 能算，但每一步乘 2 加法的代价会随位数增长，此时不能简单当作 O(1) 一次加法来看。

## 六、测试用例在测什么

cell8 每条 assert 的用意：

- `h=list_to_nodes([1,0,1]); assert binary_list_to_int(h)==5`：**正常值测试**。101 二进制等于 5，和第三节手算表逐格对应。
- `assert binary_list_to_int(list_to_nodes([0]))==0`：**特殊值测试（最小数字）**。单节点 0 表示二进制 0，结果必须是 0，验证"乘 2 加 0"从 0 出发不会凭空多出值。
- `assert h is not h.next and h.next is not h.next.next`：**对象身份测试**。三个节点虽然各自是独立对象，但这条确认相邻节点确实是**不同的对象**（`is not` 比的是身份不是值）——链表没有把所有 next 指向同一个节点。
- `assert h.next.next.next is None`：**结构边界测试**。第三个节点再往后必须是 None，确认链表在正确的地方收尾（长度恰好 3，没有多挂也没有成环）。
- `assert nodes_to_list(h)==[1,0,1]`：**往返一致性测试**。列表变链表再变回列表，应还原出同样的序列，验证 `list_to_nodes` 和 `nodes_to_list` 互为逆操作。
- `assert binary_list_to_int(None)==0`：**边界值测试（空链表）**。传 None 当头，循环一次不进，返回 0，验证空输入不崩溃且语义合理。

## 七、练习思路提示

cell9 的两道练习：

- **练习 1（手工构造三个节点）**：别用 `list_to_nodes`，直接用 `ListNode(...)` 一个一个 new 出来，再用赋值语句把它们串起来。提示：从尾节点开始造会顺手些——先造最末节点（next 不传就是 None），再造中间的（next 指向它），最后造头。造完用手动 print 每个节点的 val 和 next 验证。边界情况：试着造"只有一个节点"的链表，它的 next 应该是 None。
- **练习 2（比较值相等与对象身份相同）**：造两个节点 `a = ListNode(3)` 和 `b = ListNode(3)`，分别检查 `a == b`、`a is b`，再检查 `a is a`。你会发现 `is` 只在同一个对象时为真。提示：再用 `id(a)`、`id(b)` 打印身份证号对比，直观看到"两个对象，值相同"。这个结论在链表判环、复制链表等题目里会反复用到。

## 八、对应 LeetCode 题目

cell10 列出的题目：

- **1290. Convert Binary Number in a Linked List to Integer（二进制链表转整数）**：这题就是 `binary_list_to_int` 的原题——练的是"沿着 next 遍历链表 + 每步 value*2+位"这个模式，warmup 难度。本章的 ListNode 定义也和该题官方给定的节点结构一致。

最后照 notebook 原文提醒一句：这里的实现遵循教学契约，核心思路与该题一致，但刷题时应以 LeetCode 官方题面与评测为准。
