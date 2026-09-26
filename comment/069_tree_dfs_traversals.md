# N069 · 树的递归与迭代遍历 —— 说人话详解

> 对应 notebook：`notebooks/10_trees_tries/069_tree_dfs_traversals.ipynb`

## 一、这章要解决什么问题？（问题描述）

给你一棵二叉树，你要按某种顺序把所有节点的值取出来。所谓"某种顺序"由**处理根节点的时机**决定，一共三种：

- **前序（preorder）**：先处理自己，再处理左子树，最后右子树。
- **中序（inorder）**：先处理左子树，再处理自己，最后右子树。
- **后序（postorder）**：先处理左子树，再处理右子树，最后自己。

拿 notebook 的例子说，这棵树（由 `[1,2,3,4,5]` 按层序构建）：

```
      1
     / \
    2   3
   / \
  4   5
```

- 前序：`[1,2,4,5,3]`——1 打头（自己最先），然后整棵左子树 2,4,5，最后 3。
- 中序：`[4,2,5,1,3]`——左子树全部排完（4,2,5），轮到 1，最后右子树 3。对二叉搜索树来说中序恰好是升序。
- 后序：`[4,5,2,3,1]`——孩子全处理完才轮到 1，所以 1 排最后。

递归写三种遍历是 trivial 的（三行递归），本章真正要解决的问题是：**把递归"翻译"成显式栈的循环写法**。为什么要翻译？因为 Python 默认递归深度约 1000 层，一棵 1500 层的链状树（notebook 测试里就造了一棵）会让递归版直接 `RecursionError`，而显式栈版本稳稳跑完。理解这个翻译过程，你就理解了"递归调用栈"到底在替你干什么。

另外本章还顺带处理 N 叉树（每个节点可以有任意多个孩子）的前序遍历。

## 二、关键概念（定义）

- **二叉树 / TreeNode**：每个节点存一个值 `val` 和两个指针 `left`、`right`。`None` 表示"这里没有子树"。整棵树由根节点的指针代表。
- **递归栈（调用栈）**：函数每递归调用一次，Python 就在调用栈上压一帧，记着"这个调用进行到哪、局部变量是什么"。递归返回时弹帧恢复现场。树的深度有多深，调用栈就有多深——这是递归版的天花板。
- **显式栈**：自己维护一个普通列表当栈（后进先出，LIFO），把"接下来要访问的节点"存在里面。循环从栈顶取节点处理，就能模拟递归的效果，而且栈深度不受 Python 递归限制约束。
- **层序构建（tree_from_level）**：按"从上到下、从左到右"的顺序给定节点值（`None` 占位表示空），用队列把树搭出来。这是 notebooks 里造测试树的工具函数。
- **展开标记（expanded 标志）**：后序迭代版的核心道具。栈里放 `(节点, 是否已展开)` 二元组：False 表示"第一次见到，孩子还没处理"；True 表示"孩子都处理完了，现在轮到输出你"。它模拟的是递归里"调用前压栈"和"返回后恢复"两个时刻。
- **入栈顺序反转**：栈是后进先出，所以想让孩子按"先左后右"被处理，就必须**先压右再压左**，让左在栈顶。N 叉树同理：`extend(reversed(children))` 让第一个孩子最后压、最先出。
- **遍历输出的唯一性**：同一棵树，三种遍历的输出序列各自唯一；但注意"只有前序+后序"不一定能还原唯一的树（要有中序才行）——这是本章知识点"遍历输出"的延伸常识。

## 三、解决思路（一步步推导）

**Step 1：先明确三种遍历的递归定义。** 它们只有一行差别——"处理自己"这行代码放在两个递归调用之前、之间还是之后：

- 前序：`自己 → 左 → 右`；中序：`左 → 自己 → 右`；后序：`左 → 右 → 自己`。

**Step 2：前序迭代——"弹出即处理"。** 前序的特点是节点第一次被碰到就要输出。所以我们弹出节点、立刻记录它的值、再把孩子压栈。压栈顺序右先左后，保证左孩子先被弹出处理。

**Step 3：中序迭代——"一路向左，弹了再向右"。** 中序要先输出最左边的节点。我们从根出发沿左指针一路压栈；压不动了（node 为 None）弹出栈顶——它就是当前最左节点——输出它，然后转向它的右子树，重复这个过程。

**Step 4：后序迭代——用展开标记模拟"返回时机"。** 后序必须等两个孩子都处理完才能输出节点，单靠"入栈顺序"玩不转，于是每个节点进栈两次：第一次带 False（安排孩子），第二次带 True（真正输出）。

**Step 5：N 叉树前序。** 和二叉前序同构，只是"左右两个孩子"换成"一列孩子"，压栈时整串反转。

**手算演示：在 `[1,2,3,4,5]` 这棵树上把三个迭代版本各走一遍（对应 cell6 表格）。**

前序，栈的变化：

1. 栈=[1]。弹出 1，输出 1；压右 3 再压左 2 → 栈=[3,2]。
2. 弹出 2，输出 2；压右 5 再压左 4 → 栈=[3,5,4]。
3. 弹出 4，输出 4（无孩子）→ 栈=[3,5]。弹出 5，输出 5 → 栈=[3]。
4. 弹出 3，输出 3。总输出 `[1,2,4,5,3]`，与 cell6 表格"前序"一行一致。

中序，栈和指针的变化：

1. node=1 压栈，走向左 → node=2 压栈，走向左 → node=4 压栈，node=None 停。栈=[1,2,4]。
2. 弹出 4，输出 4；node=4.right=None。弹出 2，输出 2；node=2.right=5。
3. 5 压栈，node=None。弹出 5，输出 5。弹出 1，输出 1；node=1.right=3。
4. 3 压栈、弹出，输出 3。总输出 `[4,2,5,1,3]`。

后序，带标记的栈：

1. 栈=[(1,F)]。弹出 (1,F)：压 (1,T)、(3,F)、(2,F) → 栈=[(1,T),(3,F),(2,F)]。
2. 弹出 (2,F)：压 (2,T)、(5,F)、(4,F)。弹出 (4,F)→压 (4,T)；弹出 (4,T) 输出 4。
3. 弹出 (5,F)→(5,T)，弹出 (5,T) 输出 5；弹出 (2,T) 输出 2；弹出 (3,F)→(3,T)，输出 3；弹出 (1,T) 输出 1。
4. 总输出 `[4,5,2,3,1]`。你可以数一数：每个节点恰好进栈两次、出栈两次，第二次（T）才输出。

## 四、代码逐段讲解

### 4.1 树节点与构建工具

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

- `TreeNode.__init__` 一行同时给三个属性赋值，元组右侧 `(val,left,right)` 对应三个参数，默认值 0/None/None。
- `tree_from_level` 用队列按层序"发号"：队列里存"已经建好、等着领孩子的节点"，i 是下一个待消费的输入下标。`values[i] is not None` 才建真节点，None 就让指针保持默认的 None。它返回根节点（输入空或根为 None 时返回 None）。

### 4.2 `preorder(root)`

```python
def preorder(root):
    if not root: return []
    answer=[]; stack=[root]
    while stack:
        node=stack.pop(); answer.append(node.val)
        if node.right: stack.append(node.right)
        if node.left: stack.append(node.left)
    return answer
```

- `if not root: return []`：空树输出空列表。
- `stack=[root]`：初始栈只有根。
- `node=stack.pop(); answer.append(node.val)`：弹出即输出——这正是前序"自己最先"的体现。
- 先压 right 再压 left：栈后进先出，左孩子压得晚、弹得早，所以左子树先被处理。

### 4.3 `inorder(root)`

```python
def inorder(root):
    answer=[]; stack=[]; node=root
    while node or stack:
        while node: stack.append(node); node=node.left
        node=stack.pop(); answer.append(node.val); node=node.right
    return answer
```

- 外层条件 `while node or stack`：node 非 None 表示"还有没探完的左链"，stack 非空表示"还有压着没输出的节点"；两者都空才结束。
- 内层 `while node:`：沿左指针一路压栈，直到没有左孩子。此刻栈顶就是整棵未输出部分的最左节点。
- `node=stack.pop(); answer.append(node.val)`：最左节点出栈输出——中序"左在自己前"的体现。
- `node=node.right`：转向右子树，回到外层重新走"一路向左"的逻辑。右子树为 None 时内层不压，下一轮直接弹上一层节点。

### 4.4 `postorder_iterative(root)`

```python
def postorder_iterative(root):
    out=[]; stack=[(root,False)]
    while stack:
        node,expanded=stack.pop()
        if not node: continue
        if expanded: out.append(node.val)
        else:
            stack.append((node,True)); stack.append((node.right,False)); stack.append((node.left,False))
    return out
```

- `stack=[(root,False)]`：注意根为 None 时也直接进栈，靠下一行兜底，不需要单独判空。
- `if not node: continue`：弹出的是 None 占位（来自孩子为空的压栈），直接跳过。这样压孩子时就不必先判空。
- `if expanded: out.append(node.val)`：第二次弹出（孩子已处理完），此刻输出。
- else 分支按顺序压三个：(自己,True)、(右孩子,False)、(左孩子,False)。左孩子最后压所以最先弹——保证"左右自己"的处理次序；等两个孩子那条支线全部走完，(自己,True) 才会浮到栈顶被弹出。这个"一变三"的套路就是把递归的"进入/返回"两个时刻显式化了。

### 4.5 N 叉树前序

```python
class NaryNode:
    def __init__(self,val,children=None): self.val=val; self.children=[] if children is None else children

def nary_preorder(root):
    out=[]; stack=[root] if root else []
    while stack:
        node=stack.pop(); out.append(node.val); stack.extend(reversed(node.children))
    return out
```

- `NaryNode` 用 `children` 列表代替 left/right；`[] if children is None else children` 避免可变默认参数的坑（直接写 `children=[]` 会让所有节点共享同一个列表）。
- `stack=[root] if root else []`：条件表达式一次性处理空树。
- `stack.extend(reversed(node.children))`：把一串孩子**倒序**压栈，第一个孩子最后压、最先弹，实现"按孩子顺序从左到右"的前序。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么显式栈能模拟递归？** 递归的本质是：每碰到一个节点就"记下它、先去忙孩子、忙完回来处理它"。递归版这份"记事"由调用栈自动完成；迭代版我们把"要做的事"显式放进自己的栈里。前序最简单——节点弹出时就是处理时机，一次进栈就够；后序麻烦在"回来处理"这个时机需要区分，于是用 (节点, False/True) 让每个节点进两次栈：第一次是递归"进入"，第二次对应递归"返回"。栈的后进先出配合"右孩子先压栈"，保证左子树总是先被处理完——这正是 cell4 说的"显式栈中的节点或展开标记表示尚未完成的递归调用"。

**复杂度（结合数字说）：** 每个节点进栈、出栈各常数次（后序是各两次），所以三种遍历都是 O(n) 时间——一棵 10 万节点的树也就二三十万次栈操作，一眨眼。空间上，二叉树的工作栈是 O(h)（h 是树高）：完全平衡的 10 万节点树高约 17（2¹⁷≈13 万），栈里最多同时十几个节点；最坏退化成链时 h=n，栈就 O(n)。输出本身 O(n) 不算工作空间。N 叉树前序最坏也是 O(n)（比如根有 n-1 个孩子的"菊花图"，一压就是一整串）。迭代版完全不碰 Python 递归深度限制，测试里 1500 层的链就是专门验证这一点的。

## 六、测试用例在测什么

cell8 逐条解释：

- `assert preorder(r)==[1,2,4,5,3]` 等三行：正常值。用 5 节点小树核对三种遍历的精确输出序列，和 cell6 表格一一对应，验证"处理时机"没有放错位置。
- `assert preorder(None)==inorder(None)==postorder_iterative(None)==[]`：边界值。空树的任何遍历都是空列表，三个函数串起来测（链式比较等于三个两两比较）。
- `def reference(node): ...` 的递归参照：**交叉验证**。用三行式的朴素递归当标准答案，对同一棵树比对三个迭代版输出。递归定义直白不容易写错，它是"信得过的尺子"。
- `r=TreeNode(0); node=r; for i in range(1,1500): node.right=TreeNode(i); ...`：**深树压力测试**。造一棵 1500 节点、每层只有右孩子的链状树。这棵树的前序和中序都是 0..1499 顺序排列（一路向右，无分叉），后序反过来了是 1499..0。它一石二鸟：既验证长链下的输出正确性，又证明迭代栈不受 Python 默认约 1000 层递归限制的影响——递归版在这个输入上必炸。
- `n=NaryNode(1,[NaryNode(2),NaryNode(3,[NaryNode(4)])]); assert nary_preorder(n)==[1,2,3,4]：N 叉树正常值。结构是 1 有孩子 2、3，3 有孩子 4；前序先根后按孩子顺序递归，输出 [1,2,3,4]，验证 `reversed` 压栈的方向没搞反。

## 七、练习思路提示

- **练习 1（每种遍历分别实现递归与迭代）**：思路是补全矩阵——本章迭代版有了，你就写三个递归版；反过来再挑战中序、后序的"无标记"迭代写法。提示：后序有个经典技巧是"前序改成自己→右→左，最后整体反转"，等价于左→右→自己；中序还有一种"每轮把路径压满"的统一写法。每写一版，先用 [1,2,3,4,5] 手算期望输出（本章第三节就有现成答案），再用 cell8 的 reference 做自动比对。边界别忘了空树和单节点。
- **练习 2（比较 N 叉树的孩子展开顺序）**：思路是做实验——把 `stack.extend(reversed(node.children))` 改成 `stack.extend(node.children)`，观察输出变化。提示：反转与否决定第一个孩子是先出栈还是最后出栈。用测试里那棵 [1,[2,3,[4]]] 的树手算：正确版本输出 [1,2,3,4]；去掉 reversed 后，1 的孩子按 [2,3] 原序压栈，栈顶变成 3，于是先访问 3 及其孩子 4，最后才是 2，输出变成 [1,3,4,2]——这就是"按孩子自然顺序访问必须倒序压栈"的直接证据。可以把结论推广：栈做 DFS 时，你想让谁先被访问，就把谁最后压。

## 八、对应 LeetCode 题目

- **144. Binary Tree Preorder Traversal**：对应 `preorder`，练"弹出即输出 + 右先左后压栈"。
- **94. Binary Tree Inorder Traversal**：对应 `inorder`，练"一路向左压满、弹出转右"的节奏；这题在 BST 场景还常被用来按升序取值。
- **145. Binary Tree Postorder Traversal**：对应 `postorder_iterative`，练展开标记（或"改前序再反转"的替代方案），它是最能逼你理解"递归返回时机"的一题。

一句话总结：**三种遍历只是"处理自己"的时机不同；递归靠调用栈自动记账，迭代靠自己压栈记账，后序因为要"等孩子回来"所以每个节点得进两次栈。**
