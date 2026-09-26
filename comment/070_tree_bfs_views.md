# N070 · 树的层序遍历与视图 —— 说人话详解

> 对应 notebook：`notebooks/10_trees_tries/070_tree_bfs_views.ipynb`

## 一、这章要解决什么问题？（问题描述）

上一章我们用栈做深度优先，这一章换队列做**广度优先**：按"一层一层"的顺序访问树，先访问深度 0（根），再深度 1，再深度 2……三道典型题都建立在这个"分层"能力上：

1. **层序遍历（level order）**：把每一层的节点值收集成一个子列表。notebook 的例子由 `[3,9,20,None,None,15,7]` 构建出这棵树：

```
      3
     / \
    9   20
        / \
      15   7
```

   层序输出 `[[3],[9,20],[15,7]]`——根自己一层，9 和 20 一层，15 和 7 一层。
2. **锯齿遍历（zigzag）**：同一棵树，但第 0 层从左到右、第 1 层从右到左、第 2 层又从左到右……像蛇形走位。输出 `[[3],[20,9],[15,7]]`（注意 20 排到 9 前面）。
3. **右视图（right side view）**：想象你站在树的右侧往左看，每层你只能看到最靠右的那个节点。输出 `[3,20,7]`。

右视图有个容易踩的直觉坑，cell1 特意点了出来：**每层最右的节点不等于"沿着 right 指针一路走下去"**。反例是 `[1,2,None,3]` 这棵树（1 的左孩子是 2，2 的左孩子是 3，整棵树没有右孩子）：沿 right 指针走只能看到 1；但真正站在右边看，第 2 层最右的是 2、第 3 层最右的是 3，右视图是 `[1,2,3]`。cell8 专门测了这个反例。

## 二、关键概念（定义）

- **BFS（广度优先搜索）**：用**队列**（先进先出，FIFO）代替栈的搜索方式。先把起点入队，然后不断"出队一个、处理它、把它的孩子从队尾入队"。因为先入队的先处理，同一层的节点总是挤在一起被处理完，才轮到下一层。
- **队列（deque）**：`collections.deque` 是双端队列，`popleft()` 从左端出队、`append()` 从右端入队，两端操作都是 O(1)。用普通列表的 `pop(0)` 出队是 O(n)，树大了会明显变慢，所以 BFS 一律用 deque。
- **层大小（level size）**：开始处理一层之前，先记下 `len(queue)`——这一刻队列里恰好只有这一层的节点。处理这批节点时新入队的孩子属于下一层，只要我们的内层循环严格"取这么多个"，就不会把两层混在一起。这是本章最核心的技巧。
- **层边界/不变量**：cell4 的论证用了一个不变量（始终保持成立的性质）——"开始处理第 d 层时，队列里恰好是从左到右排列的第 d 层全部节点"。每层的处理都维持这个性质传给下一层。
- **锯齿遍历**：搜索过程完全不变，只是**展示**每层时按层号的奇偶决定要不要反转。注意反转的是"值的列表"，不是搜索顺序——BFS 永远从左到右入队。
- **右视图**：每层子列表的最后一个元素 `row[-1]`。它本质上是层序遍历的一个"投影"。
- **最大层宽（w）**：所有层里节点数最多的那层的节点数。BFS 的工作空间取决于 w 而不是树高——一棵 10 层的满二叉树约 1023 个节点，最底层就有 512 个，队列最胖的时候要装 512 个节点。

## 三、解决思路（一步步推导）

**Step 1：用 deque 做基本 BFS。** 根节点入队；循环"出队→记录值→左右孩子依次入队"直到队列空。

**Step 2：用"层大小快照"切层。** 在 while 循环开头取 `size=len(queue)`，内层 for 循环恰好执行 size 次。执行期间新入队的孩子堆在队尾，属于下一层，不会被本轮 for 碰到；for 结束时队列里恰好是完整的下一层。这就是"处理当前层之前固定队列长度"（cell1 原话）的含义。

**Step 3：每层攒一个 level 列表。** 内层 for 把值 append 进 level，for 结束把 level append 进 result。

**Step 4：锯齿 = 层序 + 按层号反转。** 拿到层序结果后，深度为奇数的行反转（第 0 行不反转）。

**Step 5：右视图 = 每行取尾。** 对层序结果的每一行取 `row[-1]`。

**手算演示：`[3,9,20,None,None,15,7]` 这棵树一轮一轮走（对应 cell6 表格的三列：深度、层节点、右侧可见）。**

1. 初始队列=[3]。第一轮 while：快照 size=len(queue)=1，恰好是第 0 层的节点数。弹出 3，level=[3]；3 的左孩子 9 入队、右孩子 20 入队 → 队列=[9,20]。本轮结束，result=[[3]]。
2. 第二轮 while：快照 size=2（第 1 层有两个节点）。弹出 9（叶子，无孩子入队），弹出 20（左孩子 15 入队、右孩子 7 入队），level=[9,20] → 队列=[15,7]。result=[[3],[9,20]]。
3. 第三轮 while：快照 size=2（第 2 层）。弹出 15（叶子）、弹出 7（叶子），level=[15,7] → 队列空，循环结束。
4. 最终 result=`[[3],[9,20],[15,7]]`；每行取尾得右视图 `[3,20,7]`；深度 1 的行反转得锯齿 `[[3],[20,9],[15,7]]`。cell6 表格逐行列出了深度 0/1/2 的层节点和右侧可见列，和这里完全一致。

建议你手算时把"每轮开打的队列快照"单独写成一行——漏入队（忘了 9 也是第 1 层的）是这类题最常见的错误，快照能帮你当场对账。

## 四、代码逐段讲解

### 4.1 树节点与构建工具（与上一章相同）

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

- TreeNode 一行三个属性赋值，默认 0/None/None。
- `tree_from_level` 本身就是一个小 BFS：队列存"等着领孩子的节点"，i 扫过输入；`None` 占位表示空指针，不建节点也不入队。`[3,9,20,None,None,15,7]` 里 9 的两个孩子是两个 None，所以 9 是叶子；15 和 7 挂在 20 下面。

### 4.2 `level_order(root)`——本章的地基

```python
def level_order(root):
    if not root: return []
    queue=deque([root]); result=[]
    while queue:
        level=[]
        for _ in range(len(queue)):
            node=queue.popleft(); level.append(node.val)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result
```

- `if not root: return []`：空树直接返回空列表。
- `queue=deque([root])`：队列初始化只有一个根。
- `for _ in range(len(queue))`：**全章最关键的一行**。`len(queue)` 在 for 开始前求值一次，正好是当前层的节点数；循环体内入队的新节点只会追加到队尾，不影响本层的取数个数。`_` 是惯用的"我不关心循环变量"占位名。
- `node=queue.popleft(); level.append(node.val)`：出队并收值。
- 两个 if 依次把左孩子、右孩子入队——左先右后，保证下一层在队列里也是从左到右排列。
- `result.append(level)`：内层 for 跑完，这一层收齐，整层归档。

### 4.3 `zigzag_level_order(root)`——层序 + 按奇偶反转

```python
def zigzag_level_order(root):
    return [row if depth%2==0 else row[::-1] for depth,row in enumerate(level_order(root))]
```

- 这是一行列表推导：`enumerate` 给每层配上深度号 depth；深度为偶数（0、2、4……）保留原样，奇数（1、3、5……）用切片 `row[::-1]` 反转。
- 值得体会的是它复用 `level_order` 而不是重写 BFS——锯齿只是展示层的差异，不碰搜索本身，所以"先做标准层序、再做纯列表变换"是既正确又好读的分层写法。

### 4.4 `right_side_view(root)`——每层取最右

```python
def right_side_view(root):
    return [row[-1] for row in level_order(root)]
```

- 同样是一行：对每一层取 `row[-1]`（Python 负下标，倒数第一个）。
- 因为 `level_order` 的每一层都是从左到右排的，`row[-1]` 恰好是这层最右的节点——"每层最右"的正确来源是层序，而不是沿着 right 指针走（第一节的反例就是证据）。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么队列里永远不会混层？** 我们盯住一个始终成立的性质：每当一轮 while 开始（也就是即将处理新一层）时，队列里装的恰好是这一层的全部节点，而且顺序从左到右。用归纳的方式说人话：第一轮开始时队列只有根，深度 0 层，成立；假设第 d 层开始时成立，内层 for 恰好把这 d 层的节点全部弹出，弹出的过程中它们的孩子按"父节点从左到右、每个父节点先左后右"的顺序追加到队尾——这恰好就是第 d+1 层从左到右的排列。于是性质一层传一层，永不破坏。锯齿和右视图都建立在"每行内部是从左到右"这个排列上，所以它们也跟着正确。

**复杂度（结合数字说）：** 每个节点恰好入队、出队各一次，所以 `level_order` 是 O(n) 时间——10 万节点的树也就 20 万次队尾/队头操作，deque 两端都是 O(1)，瞬间完成。空间上，队列最胖的时候装的是"最宽的那一层"，即 O(w)：完全平衡的 10 万节点树最宽层约 5 万个节点，队列就得装下它们；而一棵细长的链 w=1，队列永远只有 1 个元素。注意 result 输出本身 O(n) 是题目要求必须付的。本章 `right_side_view` 复用了整份层序结果，额外空间是 O(n)（n 个层行都留着）；cell4 提到它可以优化到 O(w)——做法是不存整层、只在每层 for 快结束时记下"本层最后一个出队的值"，感兴趣可以当小练习。

## 六、测试用例在测什么

cell8 逐条解释：

- `assert level_order(r)==[[3],[9,20],[15,7]]`：正常值。三层结构的标准答案，同时验证"层不混"（9、20 同层）和"层内从左到右"（9 在 20 前）。
- `assert right_side_view(r)==[3,20,7]`：正常值。每层最右依次是 3、20、7；注意第 2 层最右是 7 而不是 15。
- `assert zigzag_level_order(r)==[[3],[20,9],[15,7]]`：正常值。奇数深度 1 的 [9,20] 反转成 [20,9]，深度 0 和 2 保持原样——同时检验了"哪层该反转"的奇偶判断。
- `assert level_order(None)==right_side_view(None)==[]`：边界值。空树两个函数都返回空列表（链式断言一次测两个函数）。
- `r=tree_from_level([1,2,None,3]); assert right_side_view(r)==[1,2,3]`：**反例测试**，第一节详细讲过。这棵树只有左链（1←2←3），沿 right 指针走只能看到 [1]；正确右视图是 [1,2,3]。这条断言专防"右视图=沿右指针走"的错误直觉。

## 七、练习思路提示

- **练习 1（不反转结果列表实现锯齿）**：提示——反转 `row[::-1]` 发生在结果全部收集之后；想避免它，可以在收集层内值的时候就按方向插入：深度为奇数时用 `level.insert(0, v)`（头插）代替 `level.append(v)`，这样每层攒完天然是反的；或者改用 deque 存层，奇数层 `appendleft`。另一个思路是把"入队顺序"随深度切换（奇数层先右后左入队），但要注意这样改的是搜索顺序而非展示顺序，得想清楚每层内节点顺序到底由什么决定。手算示例就用 [3,9,20,15,7] 这棵树，先写出期望的 [[3],[20,9],[15,7]] 再动手改代码。
- **练习 2（解释 BFS 辅助空间取决于最大层宽）**：提示——数一数队列在每一轮开始时的长度，它恰好等于该层节点数；全程的最大值就是空间占用。构造两个极端例子手算：(a) 10 层满二叉树（约 1023 个节点），第 9 层有 512 个节点，队列最胖时 512，比树高 10 大得多；(b) 1023 层的右斜链（也是 1023 个节点），队列任何时刻最多 1 个。两个例子节点数相同，空间却差 512 倍——这就是"空间看宽度、DFS 栈看高度"的对照。结论用 cell4 的话说就是：level_order 队列 O(w)、输出 O(n)。

## 八、对应 LeetCode 题目

- **102. Binary Tree Level Order Traversal**：对应 `level_order`，考的就是"层大小快照"这个分层技巧，是三题的基础。
- **103. Binary Tree Zigzag Level Order Traversal**：对应 `zigzag_level_order`，在 102 之上加"按层号奇偶反转展示"，练的是把搜索和展示解耦。
- **199. Binary Tree Right Side View**：对应 `right_side_view`，考"每层最后一个节点"的正确取法，反例（无右子树的树）是这题的经典陷阱。

一句话总结：**BFS 用 deque，进队从左到右；每轮先给队列长度拍快照，拍下的就是这一层；锯齿只是反转显示，右视图只是每层取尾——地基都是同一个标准层序。**
