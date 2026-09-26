# N149 · 迭代器、惰性展开与查看下一项 —— 说人话详解

> 对应 notebook：`notebooks/18_design/149_iterators_lazy_evaluation.ipynb`

## 一、这章要解决什么问题？（问题描述）

普通函数处理序列时，习惯把结果一次性全算出来放进一个列表再返回。但有些场景这样不行：数据可能大到装不进内存，或者调用方只要前几项、后面根本用不着。所以本章的问题是：**能不能只记住"遍历进行到哪了"，每次只算出下一项，要一项给一项？** 这就是迭代器模式。

具体有三道题：

1. **BSTIterator**：给一棵二叉搜索树（BST），要按从小到大的顺序一个一个吐出节点值，但不能先把整棵树转成数组（那需要 O(n) 额外内存）。
2. **PeekingIterator**：普通迭代器只有"看一眼并取走下一项"（`next`），但有时你想"先偷看下一项但不取走"（`peek`）。怎么在不破坏输出顺序的前提下支持偷看？
3. **NestedIterator**：给一个嵌套列表（列表里套列表，套任意深），要把它拍平成一个一个整数输出，但不能先把整个结构递归展开成大列表。

举个具体到数字的例子（嵌套迭代器）：输入 `[[],[1,[2,[]]],3]`，输出依次是 `1, 2, 3`。为什么是这三个？因为拍平后所有整数按出现顺序就是 1、2、3——两个空列表 `[]` 里没有任何整数，直接跳过，但不能因为它们空就报错或卡住。

## 二、关键概念（定义）

- **迭代协议（iteration protocol）**：Python 里"可迭代"的统一约定——对象提供 `__iter__` 返回自己，`next`（即 `__next__`）每次吐出一项、没有了就抛 `StopIteration` 异常。`for` 循环和 `list(...)` 认的就是这套协议，所以实现了它你的类就能直接被 `for` 遍历。
- **惰性求值 / 惰性展开（lazy evaluation）**：能拖到最后一刻才计算下一项，绝不提前把全部输出算出来存好。好处是省内存，而且中途结构变了也不会白算。
- **显式栈（explicit stack）**：把"递归时系统帮你保存的调用路径"改用一个自己的列表 `stack` 来保存。栈里存的是"还没访问完的节点/迭代器"，代表当前展开路径。用显式栈代替递归，深度再大也不会爆掉 Python 的递归上限。
- **缓存一项（cache one item）**：PeekingIterator 的核心招数——从底层迭代器里**提前取出**下一项存在手里（`cached`），`peek` 看的是它，`next` 交付的也是它，交付后把手里的清空。任何时刻手里最多压着一个"已取出但尚未交付"的值。
- **哨兵（sentinel）**：一个独一无二的占位对象（`object()` 造出来的实例），专门表示"手里没缓存"。为什么不用 `None` 表示没缓存？因为 `None` 本身可能是合法数据（比如序列 `[1, None, 3]` 里就有一个真的 None 要交付），二者混了就分不清"没值"和"值是 None"了。哨兵用 `is` 比较（同一性比较），全程序只有这一个对象等于它自己。
- **hasNext 幂等（idempotent）**：调用一次 `hasNext()` 和连调十次效果必须一样——允许多次调用，但**绝不能**因为多调了一次就把下一个值跳过或消耗掉。同理 `peek` 偷看多少次都只算一次取走。
- **均摊 / 摊还（amortized）**：单次操作最坏可能很慢（比如 BSTIterator 的某次 `next` 要压一整条左链），但把一整趟遍历的总代价平均到每次操作上，每次只有 O(1)。

## 三、解决思路（一步步推导）

### 3.1 BSTIterator：用栈记住"还没轮到的左链"

- **Step 1**：BST 的中序遍历（左→根→右）恰好是从小到大。我们要的就是中序遍历，但只走一步、歇一步。
- **Step 2**：最小的值在"从根一路向左"的链尽头。所以初始化时把这条左链整条压进栈。
- **Step 3**：栈顶永远是"下一个该输出的节点"。`next()` 就是弹出栈顶交付，然后处理它的右子树：把右子树的左链同样压进栈（右子树里最小的接班）。
- **Step 4**：`hasNext()` 就是问"栈空了吗"。

**手算演示**（这正是测试里那棵树 `tree_from_level([7,3,15,None,None,9,20])`，即根 7、左孩子 3、右孩子 15、15 的左右孩子是 9 和 20）：

1. 初始化：`_push_left(7)` 依次把 7、3 压栈（7 有左孩子 3，3 没有），栈 = `[7, 3]`（右边是栈顶）。
2. `next()`：弹出 3，它没有右子树，返回 3。
3. `next()`：弹出 7，把右子树 15 的左链压栈（15 的左孩子是 9）：栈 = `[15, 9]`，返回 7。
4. `next()`：弹出 9，没有右子树，返回 9。
5. `next()`：弹出 15，压右孩子 20 的左链：栈 = `[20]`，返回 15。
6. `next()`：弹出 20，返回 20。栈空，结束。

输出 `3, 7, 9, 15, 20`——正好是这棵 BST 从小到大的顺序。

### 3.2 PeekingIterator：手里压着一个值

- **Step 1**：偷看的前提是"值已经在手里"。所以 `peek` 先检查缓存槽，空的话从底层迭代器取一项填进去，再返回缓存。
- **Step 2**：`next` = 先 `peek`（保证缓存里有值）拿到值、交付、清空缓存槽。取走动作就是"清缓存"。
- **Step 3**：`hasNext` 就是"试着填一次缓存，填得上说明还有"。

**手算演示**（cell6 的小实例，数据是 `[1, None, 3]`，表格列是"第一次 peek / 第二次 peek / 真正 next"）：

| 第一次 peek | 第二次 peek | 真正 next |
|---|---|---|
| 1 | 1 | 1 |
| None | None | None |
| 3 | 3 | 3 |

第一轮：peek 触发填充，缓存 = 1，返回 1；第二次 peek 发现缓存非空（用 `is` 和哨兵比），不再取，还是 1；next 交付 1 并清缓存。第二轮数据本身就是 `None`——哨兵机制保证"缓存里放着一个真正的 None"和"缓存是空的"被正确区分，连续两次 peek 都返回 None、next 交付 None，一点不乱。

### 3.3 NestedIterator：迭代器栈 = 当前展开路径

- **Step 1**：递归展开的大忌是先建大列表，我们改用"走一步算一步"：栈里放一串迭代器，每个迭代器对应一层还没遍历完的列表，栈顶是最深层。
- **Step 2**：`_fill`（找下一个整数）：从栈顶迭代器取下一项——是整数就缓存它、收工；是列表就 `iter()` 它压栈、继续往深走；栈顶耗尽就弹栈、退回上一层。
- **Step 3**：栈彻底空了还找不到整数，说明整个结构里再没有整数，`hasNext` 返回 `False`。`next`/`peek` 与 PeekingIterator 同款：交付缓存、清缓存。

**手算演示**（cell6 的实例 `[[],[1,[2,[]]],3]`，最终打印"嵌套输出 [1, 2, 3]"）：

1. 初始栈 = `[外层iter]`。找下一个整数：取出 `[]`，是列表，压 `iter([])`；立刻耗尽，弹掉。取出 `[1,[2,[]]]`，压栈；取出 `1`，是整数，缓存 = 1。交付 **1**。
2. 继续找：在 `[1,[2,[]]]` 的迭代器里取出 `[2,[]]`，压栈；取出 `2`，缓存 = 2。交付 **2**。
3. 继续：取出 `[]`，压栈、耗尽、弹掉；`[2,[]]` 的迭代器也耗尽，弹掉；回到外层取出 `3`，缓存 = 3。交付 **3**。
4. 外层耗尽、弹栈，栈空，结束。空列表 `[]` 每次都被"压进去→发现是空的→弹出来"跳过了。

## 四、代码逐段讲解

cell3 先给了两个辅助设施，再给三个迭代器。

**辅助部分（TreeNode 与 tree_from_level）**：

```python
class TreeNode:
    def __init__(self,val=0,left=None,right=None):
        self.val,self.left,self.right=val,left,right

def tree_from_level(values):
    """Construct a finite binary tree from level order with None placeholders."""
    from collections import deque
    if not values or values[0] is None: return None
    root=TreeNode(values[0]); queue=deque([root]); i=1
    while queue and i<len(values):
        node=queue.popleft()
        if values[i] is not None: node.left=TreeNode(values[i]); queue.append(node.left)
        i+=1
        if i<len(values):
            if values[i] is not None: node.right=TreeNode(values[i]); queue.append(node.right)
            i+=1
    return root
```

`TreeNode` 用一行多重赋值同时设置值、左孩子、右孩子。`tree_from_level` 是"层序数组建树"的辅助函数：`[7,3,15,None,None,9,20]` 这种写法里 `None` 表示"这个位置没有节点"。它用队列（`deque`）做广度优先：每次从队首取一个节点，按序号把数组里接下来的两项分别当它的左右孩子，非 `None` 就建节点并入队。这个函数只是给测试造树用的，不是本章重点。

**BSTIterator**：

```python
class BSTIterator:
    def __init__(self,root): self.stack=[]; self._push_left(root)
    def _push_left(self,node):
        while node: self.stack.append(node); node=node.left
    def hasNext(self): return bool(self.stack)
    def next(self):
        if not self.stack: raise StopIteration
        node=self.stack.pop(); self._push_left(node.right); return node.val
    def __iter__(self): return self
    __next__=next
```

- `__init__` 一行干两件事：建空栈、把根的整条左链压进去。`_push_left` 就是一个 while 循环一路向左压栈，它是"走左链"这个动作的唯一实现，初始化和 `next` 里复用。
- `next`：空栈时抛 `StopIteration`（遵守迭代协议，别返回 `None` 冒充）；否则弹出栈顶，先把这个节点**右子树**的左链压栈（中序里它的右子树紧接着它），再返回它的值。`__next__=next` 这个类体赋值把我们的 `next` 直接挂到协议要求的 `__next__` 名字上，`__iter__` 返回自己，于是 `list(BSTIterator(...))` 这种写法直接可用。
- 注意栈里存的是**节点**不是值，因为弹出后还要访问 `node.right`。

**PeekingIterator**：

```python
class PeekingIterator:
    def __init__(self,iterable): self.iterator=iter(iterable); self.empty=object(); self.cached=self.empty
    def _fill(self):
        if self.cached is self.empty:
            try: self.cached=next(self.iterator)
            except StopIteration: return False
        return True
    def hasNext(self): return self._fill()
    def peek(self):
        if not self._fill(): raise StopIteration
        return self.cached
    def next(self):
        value=self.peek(); self.cached=self.empty; return value
    def __iter__(self): return self
    __next__=next
```

- `__init__` 里 `iter(iterable)` 把任何可迭代物统一换成迭代器；`self.empty=object()` 造出全宇宙独一无二的哨兵；缓存槽初始放的就是它。
- `_fill`（填缓存）是唯一碰底层迭代器的地方：缓存槽是哨兵（空的）才去取；取的时候用 `try/except StopIteration` 捕获"底层也没了"，返回 `False`。注意比较用的是 `is` 不是 `==`——哨兵靠同一性辨认，`==` 可能被奇怪的数据类型劫持。
- `peek`：填一次缓存，填不上就抛 `StopIteration`，填上了返回缓存但**不清空**——这就是"偷看不取走"。
- `next`：三步连招，`peek`（保证有值）→ 记下值 → 把缓存槽重置回哨兵（这一步就是"取走"）。取走后缓存变哨兵，下次 `_fill` 会自动再取下一项。

**NestedIterator**：

```python
class NestedIterator:
    def __init__(self,nested_list):
        if not isinstance(nested_list,list): raise TypeError('nested Python list required')
        self.stack=[iter(nested_list)]; self.empty=object(); self.cached=self.empty
    def _fill(self):
        if self.cached is not self.empty: return True
        while self.stack:
            try: value=next(self.stack[-1])
            except StopIteration: self.stack.pop(); continue
            if isinstance(value,int): self.cached=value; return True
            if not isinstance(value,list): raise TypeError('only integers and lists are supported')
            self.stack.append(iter(value))
        return False
    def hasNext(self): return self._fill()
    def next(self):
        if not self._fill(): raise StopIteration
        value=self.cached; self.cached=self.empty; return value
    def __iter__(self): return self
    __next__=next
```

- `__init__` 先做类型检查：根必须是个列表，不是就抛 `TypeError`（fail fast，别让错误潜伏到后面）。栈初始化为只含外层列表的迭代器，哨兵 + 缓存槽与 PeekingIterator 同款。
- `_fill` 的 while 循环是灵魂，四种情况一次处理一样：`try/except` 从**栈顶**（`self.stack[-1]`，当前最深的列表）取一项，取不到说明这层完了，弹栈 `continue` 退回上一层；取到整数就存缓存、返回 `True`；取到列表就压它的迭代器、继续循环往深走；取到既不是 int 也不是 list 的东西（比如字符串）就抛 `TypeError` 明确拒绝，不悄悄猜语义。
- `next` 与 PeekingIterator 的差别只在入口：这里 `next` 自己调 `_fill` 并在失败时抛 `StopIteration`，然后交付缓存。
- 每个列表元素从头到尾只被 `next` 取出**一次**——不管它是整数还是列表，取出后就交给缓存或压栈，绝不重复消耗。这就是"hasNext 反复调用不跳元素"的结构保证：`hasNext` 只填缓存，缓存不清就不会再取。

## 五、为什么是对的？复杂度是多少？（说人话）

**BSTIterator 为什么每次都吐对？** 关键性质是"栈顶永远是中序的下一个节点"。可以这样想：我们压栈时总是压"一条左链"，而中序遍历的规则是"一个节点输出完，轮到它的右子树里最小的，也就是右子树的最左节点"——`next` 里弹栈后立刻 `_push_left(node.right)` 恰好就是在找这个接班人。整趟下来每个节点恰好被压栈一次、弹栈一次，谁也没被跳过、谁也没被重复输出。

**PeekingIterator 为什么不乱序？** 所有读取都经过同一个缓存槽：值先从底层进入缓存，再从缓存交付给调用方，底层迭代器永远是"缓存空了才取下一项"。所以偷看多少次都不影响底层进度，交付顺序和不用 peek 时一字不差。

**NestedIterator 为什么对、为什么不怕深？** 它本质上就是把递归拍平的"递归调用栈"换成了自己维护的迭代器栈，展开路径和递归版本一模一样，所以输出正确；又因为栈是堆上的列表而不是系统调用栈，嵌套 1500 层也不会爆递归深度（测试里真的嵌了 1500 层）。空列表的处理（压栈→立刻耗尽→弹栈）保证空列表被无声跳过；而"缓存未清就不再取"保证了 `hasNext` 调一万次也只消耗零个整数。

**复杂度是多少？** 逐个说，配具体数字：

- BSTIterator：初始化压左链是 O(h)（h 是树高）；一次 `next` 最坏要压一整条右子树左链，也是 O(h)。但注意每个节点一辈子只进栈一次出栈一次，n 个节点的树完整遍历总共只有 2n 次栈操作，摊到每次 `next` 上就是均摊 O(1)。比如 1500 个节点就算全是右斜链（测试里就是这么造的），单次 `next` 只压一个节点，总代价 O(n)；换成完全平衡的树 h≈log n，单次最坏也就 log n 步，平均下来更小。空间是栈深 O(h)。
- PeekingIterator：每次操作都是查一次缓存、至多取一次底层，全是 O(1)。
- NestedIterator：每个元素（包括空列表这个"元素"）只被取出一次，所以总耗时按整个结构的节点总数算，是 O(N)；辅助空间是迭代器栈的深度 O(嵌套深度)。注意 cell4 特意说明：N 要算上空列表——空列表虽不产出整数，也要花常数工夫压栈再弹栈。

**一个诚实的前提**：这里的 `NestedIterator` 吃的是原生 Python 嵌套列表（int 和 list 两种类型）；LeetCode 341 给的是 `NestedInteger` 接口，需要把 `isinstance` 判断换成它的 `isInteger()/getInteger()/getList()` 访问器，不能原样照抄提交。

## 六、测试用例在测什么

cell8 的断言逐条看：

- `assert list(BSTIterator(tree_from_level([7,3,15,None,None,9,20])))==[3,7,9,15,20]`：正常值测试——这棵树的中序（升序）序列就是 `[3,7,9,15,20]`，检验左链压栈/右子树接班的整套流程。
- `assert list(BSTIterator(None))==[]`：边界测试——空树不应该抛错，应该老实输出空序列。
- `it=PeekingIterator([None,0,False])` 这一组：特殊值测试，专治哨兵写错。序列里的 `None`、`0`、`False` 全是"假值"——如果你的实现用 `if cached:` 之类真值判断来决定"有没有缓存"，`0` 和 `None` 就会被误判成"没有值"而跳过。断言要求 peek 两次都是 None、next 交付 None，剩下 `list(it)==[0,False]`（0 和 False 也一个不少），最后 `not it.hasNext()` 确认耗尽。
- NestedIterator 的四组参数化数据：`([],[])` 测空输入；`([[],[[]]],[])` 测"全是空列表"（含两层嵌套空），一个整数都没有也不能报错；`([1,[4,[6]]],[1,4,6])` 测层层嵌套的正经拍平；`([[],[1],[],[2,[3]]],[1,2,3])` 测空列表夹在有效数据中间的情况。每组内部还嵌了两个细节：`assert it.hasNext()` 在 `while` 条件里已经问过一次、循环体内再问一次，这是在测**幂等**——连问两次不会消耗元素；取完后再调 `it.next()` 必须抛 `StopIteration`（`try/except` 配 `else: raise AssertionError` 的写法是"必须抛异常，没抛就是错"的标准检查手法）。
- `nested=9; for _ in range(1500): nested=[nested]`：把 9 套 1500 层马甲再拍平，输出必须还是 `[9]`。这条测两件事：超深嵌套不爆递归（因为我们用显式栈）、无论多深都只吐出唯一的整数。
- 右斜链 1500 节点那条：从 0 开始每个节点挂右孩子，挂到 1499，断言 `list(BSTIterator(root))==list(range(1500))`。它验证的是均摊行为——每个 `next` 只需处理一个节点，1500 次 `next` 平稳完成，不存在哪个 `next` 突然卡住做巨量工作。

## 七、练习思路提示

- **练习 1（反复调用 hasNext 不消耗元素）**：提示——想清楚"消耗"发生在哪里：只有 `next` 交付时清缓存、只有缓存空了才碰底层迭代器，`hasNext`/`peek` 只填不清。验证方法可以模仿测试里的"循环体内多问一次 hasNext"，或者用 PeekingIterator 对一个列表先 `hasNext()` 十次再 `next()`，对照直接遍历的结果。边界别忘了：只剩一个元素时反复问、耗尽之后反复问，两种都不得改变输出。
- **练习 2（next 的最坏与均摊成本不同）**：提示——拿 BSTIterator 举具体数字：15 个节点排成完全左斜链时，第一次 `next` 前初始化压了 15 个节点（这次最坏 O(h)），但中间那些"叶子节点"的 `next` 一次弹栈就完事（O(1)）。统计整趟遍历的总压栈次数 = 总弹栈次数 = n，所以 n 次 `next` 总代价 O(n)，均摊每次 O(1)。你可以写个小实验给每次 `next` 计数栈操作次数，画出来看单次峰值和平均值的关系。边界考虑：单右斜链（每次 next 恰好压 1 个）和单左斜链（第一次最多、后面递减）两种极端。

## 八、对应 LeetCode 题目

- **173. Binary Search Tree Iterator**：对应 `BSTIterator`——练"显式栈保存左链、弹出后右子树接班"这套中序惰性遍历。
- **284. Peeking Iterator**：对应 `PeekingIterator`——练"缓存一项 + 哨兵区分空槽与 None"，偷看不取走。
- **341. Flatten Nested List Iterator**：对应 `NestedIterator`——练"迭代器栈代替递归展开嵌套结构"；注意提交时要把本章的 `isinstance` 类型判断替换成题目 `NestedInteger` 接口的访问器。
