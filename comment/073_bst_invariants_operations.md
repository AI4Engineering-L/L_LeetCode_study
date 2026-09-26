# N073 · 二叉搜索树与有序操作 —— 说人话详解

> 对应 notebook：`notebooks/10_trees_tries/073_bst_invariants_operations.ipynb`

## 一、这章要解决什么问题？（问题描述）

二叉搜索树（BST）是一种"把有序性藏进结构里"的树：左边的都比根小，右边的都比根大。有了这个性质，查找、插入、删除都能沿着一条路往下走，平均只要 O(log n) 步；中序遍历还会自动输出从小到大的序列。本章实现四个操作：`is_valid_bst` 判断一棵树是不是合法 BST，`kth_smallest` 找第 k 小的键，`insert_bst` 插入一个键，`delete_bst` 删除一个键。

这章最想让你记住的一个坑：**"每个左孩子小于父亲、右孩子大于父亲"并不等于 BST**。真正的条件是"整棵左子树的所有节点都小于根、整棵右子树的所有节点都大于根"。举个具体到数字的反例（cell8 第一条断言就是它），层序序列 `[5,1,4,None,None,3,6]`：

```
        5
       / \
      1   4
         / \
        3   6
```

这棵树里有两处违规。浅的一处：4 挂在 5 的右边，但 4<5，随便一比就能发现。深的一处才是本题的考点：3 挂在 5 的右子树里，但 3<5——如果你写验证代码时只拿每个节点和它的直接父亲比大小，3 和它父亲 4 比是合规的（3<4，左孩子更小），3 和 5 的矛盾根本看不见。所以输入这棵树，`is_valid_bst` 必须输出 `False`，而任何"只比父子"的偷懒实现都会漏判它。

## 二、关键概念（定义）

- **BST 不变量（全局范围约束）**：对任何节点，它左子树里的每一个键都小于它，右子树里的每一个键都大于它。注意是"每一个"，不是只看直接孩子。这个性质让"往哪边走"在每一个节点上都有唯一答案。
- **中序遍历（inorder）**：按"左、自己、右"的顺序访问节点。BST 的中序序列一定严格从小到大，这个等价关系是本章 `is_valid_bst` 的理论基础：与其传上下界去验证，不如直接走一遍中序看是不是递增。
- **上下界（范围约束）**：另一种验证思路——从根往下走，每个节点随身携带"我必须在 (low, high) 开区间内"的限制，进左子树就把上界收紧成当前值，进右子树就把下界收紧。本章代码没用它，但它是理解"全子树范围"最直观的方式，你应当能看懂别人这么写。
- **后继（successor）**：比某节点大的所有键里最小的那个。在 BST 里，一个节点的后继就是它右子树中最左边的那个节点（右子树里一路向左走到底）。
- **删除的三种情况**：删的节点没有孩子（直接摘掉）；只有一个孩子（孩子顶上来）；有两个孩子（不能硬删，用后继的键覆盖自己，再去删那个后继节点——后继没有左孩子，删它退化为前两种情况）。
- **集合语义（唯一键）**：本章把 BST 当成"集合"用：重复插入同一个键不会生成新节点，直接无视；键不存在时删除也什么都不做。
- **退化（degeneracy）**：如果按 2,1,3 或 7,6,5,... 这种倒霉顺序插入，BST 会变成一条链，高度 h=n，所有 O(h) 的操作退化成 O(n)。普通 BST 不保证平衡，这是练习 2 的主题，也是 AVL 树、红黑树存在的理由。

## 三、解决思路（一步步推导）

cell6 演示了"从空树开始，插入 5,3,6,2,4,7，再删除根 5"，我们把每一步都想清楚。

- **Step 1：插入就是一路问路。** 插 5 到空树，直接造一个节点当根。插入 3：3<5 往左，左边空，挂上。插入 6：6>5 往右，右边空，挂上。插入 2：2<5 往左遇到 3，2<3 再往左，空，挂上。插入 4：4<5 往左遇到 3，4>3 往右，空，挂上。插入 7：7>5 往右遇到 6，7>6 往右，空，挂上。每次插入走的都是"从根到空位"的一条路，绝不回头。
- **Step 2：中序序列验证结构。** 每插一个键，中序遍历应该输出严格递增序列，cell6 的表格正是这么记录的（见下）。如果任何一步出现重复或逆序，说明插入逻辑写错了。
- **Step 3：删除有两个孩子的根 5。** 5 既有左子树（3 带着 2、4）又有右子树（6 带着 7）。做法：先找后继——从右孩子 6 开始一路向左，6 没有左孩子，所以后继就是 6。把 6 抄写到根上（根的值变成 6），然后问题转化成"删除右子树里的旧 6 节点"；旧 6 没有左孩子，只有右孩子 7，让 7 顶上它的位置。最终树：根 6，左子树 3(2,4)，右孩子 7。
- **Step 4：核对。** 最终中序是 [2,3,4,6,7]，去掉了一个 5，其余递增，删除成功且没破坏 BST 性质。

cell6 的表格（建议你运行后逐行核对）：

| 操作 | 中序 |
|------|------|
| 插入5 | [5] |
| 插入3 | [3, 5] |
| 插入6 | [3, 5, 6] |
| 插入2 | [2, 3, 5, 6] |
| 插入4 | [2, 3, 4, 5, 6] |
| 插入7 | [2, 3, 4, 5, 6, 7] |
| 删除根5 | [2, 3, 4, 6, 7] |

- **Step 5：`is_valid_bst` 的思路。** 走一遍中序，拿后一个和前一个比，只要出现"不严格大于"就判假。这利用了"中序严格递增 当且仅当 合法 BST（唯一键）"这条等价关系。
- **Step 6：`kth_smallest` 的思路。** 中序序列的第 k 个就是第 k 小，所以边走中序边数数，数到第 k 个停下。

## 四、代码逐段讲解

`TreeNode` 和 `tree_from_level` 与前两章完全相同，不再重复。本章新工具是中序遍历器。

### 1. 显式中序遍历器

```python
def _inorder_nodes(root):
    stack=[]; node=root
    while stack or node:
        while node: stack.append(node); node=node.left
        node=stack.pop(); yield node; node=node.right
```

这是教科书式的迭代中序。外层条件"栈非空或当前节点存在"表示还有活干；内层 `while node` 一路向左把沿途节点全部压栈；然后弹出栈顶——它是当前子树里最左（最小）的节点——交出去（`yield`），再转向它的右孩子，对右子树重复同样过程。整个过程不递归，深树不会爆栈。

### 2. 验证与第 k 小：中序序列上的简单巡检

```python
def is_valid_bst(root):
    previous=None; first=True
    for node in _inorder_nodes(root):
        if not first and node.val<=previous: return False
        previous=node.val; first=False
    return True
```

`previous` 存上一个访问到的值，`first` 标记是不是第一个节点（第一个节点没有"前一个"可比，跳过检查）。从第二个节点起，只要 `node.val<=previous`——出现相等或倒退——立刻返回 `False`。全部通过返回 `True`。空树时循环不执行，直接返回 `True`。

```python
def kth_smallest(root,k):
    if k<1: raise ValueError('positive rank required')
    for i,node in enumerate(_inorder_nodes(root),1):
        if i==k: return node.val
    raise ValueError('k exceeds number of nodes')
```

`enumerate(...,1)` 让计数从 1 开始，数到第 k 个就返回它的值。第一行 `if k<1: raise ValueError` 挡住非法名次：排名从 1 开始，k=0 或负数没有意义，与其返回错误答案不如直接报错。如果走完整棵树都没数到 k，说明 k 超过节点总数，也抛异常。

### 3. 插入：问到空位为止

```python
def insert_bst(root,x):
    if root is None: return TreeNode(x)
    node=root
    while True:
        if x==node.val: return root
        side='left' if x<node.val else 'right'
        child=getattr(node,side)
        if child is None: setattr(node,side,TreeNode(x)); return root
        node=child
```

空树时直接返回新节点。否则进入无限循环：键已存在就原样返回（集合语义，不插重复键）；否则根据大小决定走 `'left'` 还是 `'right'`。这里用了 `getattr(node,side)` / `setattr(node,side,...)` 这个紧凑写法——`side` 是字符串 `'left'` 或 `'right'`，`getattr` 按名字取属性、`setattr` 按名字设属性，这样"往左挂还是往右挂"用一行搞定，不用把几乎一样的代码写两遍。孩子是 `None` 说明问到空位了，把新节点挂上、返回根；否则继续往下问。

### 4. 删除：先定位，再分情况

```python
def delete_bst(root,x):
    parent=None; node=root
    while node and node.val!=x:
        parent=node; node=node.left if x<node.val else node.right
    if not node: return root
    if node.left and node.right:
        successor_parent=node; successor=node.right
        while successor.left: successor_parent=successor; successor=successor.left
        node.val=successor.val; parent,node=successor_parent,successor
    child=node.left if node.left else node.right
    if parent is None: return child
    if parent.left is node: parent.left=child
    else: parent.right=child
    return root
```

逐段读：

- 第一段是定位：沿着和查找一样的路线走，`parent` 始终跟在 `node` 后面，直到找到值为 x 的节点或走出树（`node` 为 `None`）。没找到就直接返回原树，什么都不改。
- `if node.left and node.right:` 处理最麻烦的"两个孩子"情况：从右孩子开始，`while successor.left` 一路向左找后继，同时记下后继的父亲；`node.val=successor.val` 把后继的键抄到当前节点上；接着 `parent,node=successor_parent,successor` 把"待删除对象"偷换成那个后继节点。此后继没有左孩子，所以接下来必然走"至多一个孩子"的简单分支。注意这个做法修改了原节点的值（用后继的值顶替），接口并不承诺保留被删键原来所在的那个对象——这是 cell1 明说的取舍。
- `child=node.left if node.left else node.right` 取待删节点唯一的孩子（没有孩子时是 `None`）。这一行同时覆盖"零孩子"（child=None，相当于拿空顶替）和"一个孩子"两种情况。
- `if parent is None: return child` 对应"删的是根且根至多一个孩子"：根没了，孩子直接成为新根返回（空树时 child 是 None，返回空树）。
- 最后三行是普通情况下的"接骨"：看待删节点是父亲的左孩子还是右孩子，把父亲那条指针改指向 child。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么"中序严格递增"就等于"合法 BST"？** 如果树合法，中序访问的顺序是"左子树全部 → 根 → 右子树全部"，而左子树全部小于根、右子树全部大于根，用这个逻辑从整棵树推到每个子树，就能得出序列一定严格递增。反过来，如果中序有两处不递增，就能在它们的公共祖先附近找到一对违反大小关系的节点，所以不递增的树一定不合法。两方向合起来，检查序列就够了，不需要显式传上下界。

**为什么"用后继替换"不会破坏有序性？** 我们删的是有两个孩子的节点 m，后继 s 是 m 的右子树里最小的键。第一，s 大于 m 的整棵左子树（左子树全部小于 m，而 s>m）；第二，s 小于 m 的右子树里其他所有键（它本来就是那里最小的）。把 s 的值抄进 m 的位置后，"左边全小于它、右边全大于它"依旧成立；而被真正摘掉的旧 s 节点没有左孩子，摘除它不影响任何别的键的相对位置。

**复杂度**：查找、插入、删除都只沿着一条从根往下的路径走，代价是 O(h)，h 是树高。树比较随机时 h 大约是 log₂n——n=10⁵ 时约 17 层，每步开销极小；但如果按有序序列插入导致树退化成链，h=n=10⁵，操作就变成十万步的线性扫描，这就是"普通 BST 不能当成平衡树用 O(log n)"的含义。`is_valid_bst` 要遍历每个节点，是 O(n)。`kth_smallest` 先下探到最左（O(h)）再数 k 个，是 O(h+k)。中序遍历的栈最坏装下一条左链，是 O(h) 空间。

## 六、测试用例在测什么

- `assert not is_valid_bst(tree_from_level([5,1,4,None,None,3,6]))`：测"局部父子都合规但全局违规"的经典反例——右子树里藏着 3，比根 5 小。如果你的实现只比较父子大小，这条会漏判，测试直接失败。
- 后面的随机对拍是本章测试的重头戏：用固定种子的随机数做 200 轮操作，每轮随机决定插入还是删除一个 0–29 之间的随机键，同时用 Python 的 `set`（记作 `ref`）作为"标准答案账本"同步记账。每轮操作后做三重核对：第一，`is_valid_bst(r)` 必须为真，保证插删没把结构改坏；第二，树的中序序列必须恰好等于 `sorted(ref)`，保证"树里有哪些键"和账本完全一致；第三，对账本里每个名次 k，`kth_smallest(r,k)` 必须等于账本里第 k 小的键。200 轮 × 三重核对全过，插、删、查、找第 k 小四条路径都被反复锤炼过，最后打印 `N073: 所有本章断言通过`。

## 七、练习思路提示

- **练习 1（明确重复键策略）**：本章实现是"集合语义"——插入已存在的键直接无视。提示：想想另外两种常见设计——第一种是每个节点加一个 `count` 字段记出现次数，重复插入只加计数、删除先减计数减到 0 才摘节点；第二种是统一约定"等于根的键走左边"（即允许 `左 ≤ 根 < 右`）。注意第二种约定下 `is_valid_bst` 的严格递增检查要放宽成"不递减"，否则合法的树会被误判。先手算：把 [5,3,3] 按你选的策略插进树，画出结构、写出中序，再对照本章接口验证。
- **练习 2（解释普通 BST 不保证对数高度）**：提示——最有说服力的方式是亲手造反例。按 1,2,3,4,5,6,7 的顺序调用 `insert_bst`，你会发现每个新键都比已有的大，一路向右挂成一条链，高度是 7；而"满二叉树"放 7 个键只需要 3 层。再量一下 `kth_smallest` 在这种链上的工作量，体会 O(h) 变成 O(n) 的后果。修复方向是让树在插入/删除后自我调整（旋转），即 AVL 树、红黑树那一族结构，本章不实现但值得知道名字。

## 八、对应 LeetCode 题目

- **98. Validate Binary Search Tree**：验证 BST，直接对应 `is_valid_bst`，考的正是"必须整棵子树比较、不能只看父子"这个坑。
- **230. Kth Smallest Element in a BST**：BST 第 k 小，直接对应 `kth_smallest`，练的是"中序即有序序列，边走边数提前停"。
- **450. Delete Node in a BST**：BST 删除节点，直接对应 `delete_bst`，核心难点就是"两个孩子时用后继替换"那一手。
