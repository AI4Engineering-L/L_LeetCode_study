# N139 · 有序集合、Treap 与跳表原理 —— 说人话详解

> 对应 notebook：`notebooks/16_advanced_structures/139_balanced_trees_treaps_skiplists.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章解决"既要保持元素有序、又要随时插入删除、还要能问'排第几'和'第 k 个是谁'"的动态集合问题。普通二叉搜索树（BST）按"小的放左、大的放右"组织，查找很快，但如果你按 1, 2, 3, 4, 5 的顺序插入，它会退化成一条向右的链，每次操作变 O(n)。本章实现的 Treap 给每个节点随机发一个优先级，用旋转把树压平衡，让操作在期望意义下回到 O(log n)，同时每个节点额外记"子树大小"，从而支持 rank（比某数小的有几个）和 kth（第 k 小是谁）。

本章还把它用在一个具体题目上（LeetCode 220）：判断数组里是否存在两个下标差不超过 index_diff、且值差不超过 value_diff 的数对。一个具体到数字的例子：`nums=[1, 5, 9, 4]`，`index_diff=2`，`value_diff=3` → 输出 True，因为下标 1 和 3（差 2 ≤ 2）的值 5 和 4 只差 1 ≤ 3。算法用一棵只装"最近 index_diff 个元素"的 Treap，每步查"有没有落在 `[x-3, x+3]` 里的旧元素"。

## 二、关键概念（定义）

- **BST（二叉搜索树）**：每个节点满足"左子树所有键 < 它 < 右子树所有键"的树。中序遍历（先左、再根、后右）正好得到升序序列。
- **退化**：按有序序列插入普通 BST 时，每个新节点都走同一边，树变成链表，操作从 O(log n) 恶化到 O(n)。这是本章要解决的核心痛点。
- **Treap（树堆）**：Tree + Heap 的合成词。每个节点除了 key 还带一个随机 priority，要求 key 满足 BST 性质、priority 满足堆性质（父节点的 priority 更小）。key 管顺序，随机 priority 管平衡——随机数据不会故意"递增插入"，所以期望树高是 O(log n)。
- **旋转（rotation）**：只改变两个节点的父子关系、不改变中序顺序的局部调整。左旋把右孩子提上来，右旋把左孩子提上来。插入后若孩子的 priority 比父亲小（违反堆序），就朝反方向旋转把它扶正。
- **count（重复键计数）**：同一个值插入多次时，不建新节点，只把该节点的 count 加一。这样"多个 2"只占树里一个位置。
- **size（子树大小）**：每个节点记"以我为根的子树共有多少个元素（含重复计数）"。有它才能不遍历整树就回答 rank/kth。
- **rank / kth（顺序统计）**：rank(key) 返回严格小于 key 的元素个数（和 `bisect_left` 的语义一致）；kth(k) 返回升序排好后第 k 个元素（零基）。两者互为逆查询。
- **lower_bound(key)**：返回树里 ≥ key 的最小键，没有则返回 None。
- **期望复杂度 vs 最坏复杂度**：Treap 的 O(log n) 是"随机优先级下的平均值"，单次运行仍可能（概率极小地）退化到 O(n)；AVL 树和红黑树靠确定性的旋转规则保证最坏 O(log n)。跳表（skiplist）是另一种随机化结构，层数随硬币翻转决定，本章只作对照不实现。
- **固定随机源**：构造函数里 `Random(139)` 这种写死种子的随机数发生器只为测试可复现，不代表复杂度保证。

## 三、解决思路（一步步推导）

- **Step 1（节点设计）**：每个节点存 key、随机 priority、count（该 key 出现几次）、size（子树总元素数）、左右孩子。前两个管"长什么样"，后三个管"查得快"。
- **Step 2（插入）**：先按普通 BST 的方式向下找位置：key 相等就把 count 加一返回；比当前小往左、大往右。递归返回的路上检查堆序：如果左孩子的 priority 比我小，就右旋把我换下去；右孩子小就左旋。旋转后沿途 `_pull` 重算 size。
- **Step 3（删除）**：先查在不在（`key not in self` 直接返回 False）。找到节点后：count 大于 1 就只减一；否则用 `_merge` 把它的左右子树合成一棵顶替它。merge 的规则是：两棵子树谁的根 priority 小谁当新根，递归吞并另一棵。
- **Step 4（rank）**：从根往下走。若 key ≤ 当前节点键，答案只可能在左子树，往左；否则（key 更大）"当前节点的左子树全部 + 当前节点的 count 个重复"都小于 key，累加进答案后往右走。
- **Step 5（kth）**：从根往下走。左子树有 left 个元素：k 落在左子树内就往左；k 落在 [left, left+count) 内就返回当前键；否则从 k 里扣掉左子树和当前节点，往右继续。
- **Step 6（滑窗查询）**：`contains_nearby_almost_duplicate` 维护一棵只含最近 index_diff 个旧元素的 Treap。对新元素 x，用 lower_bound(x-t) 找到"≥ x-t 的最小旧值"，若它还 ≤ x+t，说明存在旧值落在 `[x-t, x+t]` 里，返回 True；否则把 x 插入，并把滑出窗口的元素删掉。

**手算演示（rank 与 kth，用 cell6 的最终集合）**：cell6 依次插入 `[5,2,8,2,6,1]`，打印的顺序统计是 `[1, 2, 2, 5, 6, 8]`——注意 2 只出现一个节点但 count=2，全树 size=6。`rank(5)` 怎么走：从根出发，每次遇到键 < 5 的节点就把"它的左子树 size + 它的 count"加进答案，遇到键 ≥ 5 的就往左；走完后累加的恰好是 1, 2, 2 三个元素，所以 rank(5)=3（三个元素严格小于 5）。反过来 `kth(3)`：从根往下，若 3 落在某节点"左子树大小"的区间 [left, left+count) 里就返回它的键——这里走到键 5 的节点时左子树大小加重复数正好罩住 3，返回 5，和排序数组 `[1,2,2,5,6,8]` 的第 4 个（零基 3）一致。

**手算演示（滑窗，nums=[1,5,9,4]，k=2，t=3）**：

| i | x | 查询前树内元素 | lower_bound(x-3) | 是否 ≤ x+3 | 动作 |
|---|---|---|---|---|---|
| 0 | 1 | {} | None（无 ≥ -2 的） | — | 插入 1 → {1} |
| 1 | 5 | {1} | None（无 ≥ 2 的） | — | 插入 5 → {1,5} |
| 2 | 9 | {1,5} | None（无 ≥ 6 的） | — | 插入 9；i≥k=2，删 nums[0]=1 → {5,9} |
| 3 | 4 | {5,9} | 5（≥1 的最小是 5） | 5 ≤ 7 成立 → 返回 True | — |

窗口里只留最近 2 个旧元素，所以下标 0 的 1 被及时删掉，不会产生 |4-1|=3 ≤ 3 但下标差 3 > 2 的误报。

## 四、代码逐段讲解

cell3 代码较多，我们按"节点与工具函数 → 类方法 → 题目函数"的顺序讲。

**节点与三个工具函数**

```python
class _TreapNode:
    def __init__(self,key,priority):
        self.key=key; self.priority=priority; self.count=1; self.size=1; self.left=self.right=None

def _size(node): return node.size if node else 0

def _pull(node):
    if node: node.size=node.count+_size(node.left)+_size(node.right)
    return node

def _rotate_left(node):
    root=node.right; node.right=root.left; root.left=node; _pull(node); return _pull(root)

def _rotate_right(node):
    root=node.left; node.left=root.right; root.right=node; _pull(node); return _pull(root)
```

`_TreapNode` 新建时 count 和 size 都是 1（一个元素、自己管自己）。`_size(node)` 对空节点返回 0，避免到处写 if 判空。`_pull(node)` 是"上拉重算"：size = 自己的 count + 左右子树 size，孩子变了之后必须调它。`_rotate_left` 把右孩子 `root` 提成新根：原根接到 root 的左侧，root 原来的左孩子挂给原根当右孩子——三步指针操作不改变中序顺序；先 `_pull(node)`（它现在变孩子了）再 `_pull(root)`，顺序不能反。`_rotate_right` 是镜像版本。

**构造、长度与查找**

```python
    def __init__(self,rng=None): self.root=None; self.rng=Random(139) if rng is None else rng; self.serial=0
```

一行初始化三样东西：根节点先置空；`self.rng` 是随机源，不传就用种子 139 的 `Random`（写死种子是为了测试可复现），传了就用你给的；`self.serial` 是插入序号，用来给优先级当"平票加时赛"。

```python
    def __len__(self): return _size(self.root)
    def __contains__(self,key):
        node=self.root
        while node:
            if node.key==key: return True
            node=node.left if key<node.key else node.right
        return False
```

`__len__` 让 `len(tree)` 直接读根的 size，O(1)。`__contains__` 是普通的 BST 下行查找，支持 `x in tree` 写法，走到空即不存在。

**插入 `insert`**

```python
    def insert(self,key):
        self.serial+=1; priority=(self.rng.getrandbits(64),self.serial)
        def put(node):
            if node is None: return _TreapNode(key,priority)
            if key==node.key: node.count+=1
            elif key<node.key:
                node.left=put(node.left)
                if node.left.priority<node.priority: node=_rotate_right(node)
            else:
                node.right=put(node.right)
                if node.right.priority<node.priority: node=_rotate_left(node)
            return _pull(node)
        self.root=put(self.root)
```

先造优先级：64 位随机数在前，插入序号 serial 在后组成元组。元组比较先比随机数，几乎不会相等；万一相等就比 serial，保证任何两个优先级都能分出大小，堆序判断不会卡在"相等"。递归 `put`：空位就落新节点；键相等只加 count（不建重复节点）；否则递归进一侧，回来后若孩子优先级更小就旋转恢复堆序，最后 `_pull` 更新自己的 size。

**合并 `_merge` 与删除 `discard`**

```python
    def _merge(self,left,right):
        if not left: return right
        if not right: return left
        if left.priority<right.priority: left.right=self._merge(left.right,right); return _pull(left)
        right.left=self._merge(left,right.left); return _pull(right)
    def discard(self,key):
        if key not in self: return False
        def erase(node):
            if key<node.key: node.left=erase(node.left)
            elif key>node.key: node.right=erase(node.right)
            elif node.count>1: node.count-=1
            else: return self._merge(node.left,node.right)
            return _pull(node)
        self.root=erase(self.root); return True
```

`_merge` 合并"所有键都小于右树"的两棵 Treap：谁的根优先级小谁当根，被挤下去的一方递归和对方剩下的部分合并。`discard` 先判存在（顺便让返回值 True/False 如实反映删没删到），然后递归找到目标：count>1 只减计数；count==1 就把左右子树 merge 起来顶替自己。沿途 `_pull` 维护 size。

**rank / kth / lower_bound**

```python
    def rank(self,key):
        node=self.root; answer=0
        while node:
            if key<=node.key: node=node.left
            else: answer+=_size(node.left)+node.count; node=node.right
        return answer
    def kth(self,k):
        if not 0<=k<len(self): raise IndexError('zero-based rank outside tree')
        node=self.root
        while node:
            left=_size(node.left)
            if k<left: node=node.left
            elif k<left+node.count: return node.key
            else: k-=left+node.count; node=node.right
    def lower_bound(self,key):
        node=self.root; answer=None
        while node:
            if node.key>=key: answer=node.key; node=node.left
            else: node=node.right
        return answer
```

这三个全是"从根往下走一遍"的循环。`rank`：遇到 key ≤ 当前键就往左（当前子树和右子树都不小于 key）；否则左子树加当前 count 全部严格小于 key，累加后往右。`kth`：第一行挡越界的 k（报错信息里明说 zero-based）；下行时用左子树大小 left 判断 k 落在左子树、当前节点（含重复）还是右子树，落在右侧就扣掉左子树和当前节点再继续。`lower_bound`：遇到 ≥ key 的键就记下来当候选并往左找更贴近的，遇到更小的就往右，走完 answer 就是 ≥ key 的最小键（没有则保持 None）。

**题目函数 `contains_nearby_almost_duplicate`**

```python
def contains_nearby_almost_duplicate(nums,index_diff,value_diff):
    if index_diff<=0 or value_diff<0: return False
    tree=OrderStatisticTreap()
    for i,x in enumerate(nums):
        candidate=tree.lower_bound(x-value_diff)
        if candidate is not None and candidate<=x+value_diff: return True
        tree.insert(x)
        if i>=index_diff: tree.discard(nums[i-index_diff])
    return False
```

第一行挡非法参数：index_diff ≤ 0 意味着不允许任何数对（下标差至少 1），value_diff < 0 同理无解，直接 False。主循环里 `lower_bound(x-value_diff)` 找到"≥ x-t 的最小旧值"，若它 ≤ x+t 就命中；查询必须在插入 x 之前（否则 x 会找到自己）；`if i>=index_diff: tree.discard(nums[i-index_diff])` 把滑出窗口的旧元素删掉，保证树里始终只有最近 index_diff 个先前元素，下标约束由此成立。

## 五、为什么是对的？复杂度是多少？（说人话）

为什么旋转不破坏排序：左旋和右旋只是把"父亲和孩子"换个位置，节点之间的中序访问顺序一步都没变，所以"左小右大"的 BST 性质在旋转前后都成立；旋转唯一改变的是堆序的违反——把优先级更小的孩子转上来，父子间的堆序就修好了。插入路径上每一层最多修一次，删除时用 merge 让优先级最小者当新根，两棵子树的堆序也保持。因此整棵树同时满足"键看中序是升序、优先级看父子是父小子大"两条约定。

为什么 rank/kth 是对的：处理到某节点时，"严格小于 key 的元素个数"恰好被三块瓜分——左子树、当前节点的重复、右子树；key ≤ 当前键时右子树和当前节点都不算数，只能往左；key > 当前键时左子树和当前节点的 count 全部小于 key，可以放心累加。kth 同理，用左子树大小做"跳过多少个"的判断。两者都只是沿树高走一遍，不遍历全树。

为什么滑窗是对的：树里恰好保存着"下标在 [i-index_diff, i-1] 的旧元素"，不多不少（每步都删掉了最老的）；`lower_bound(x-t)` 若返回的 candidate ≤ x+t，就说明存在旧值 v 满足 x-t ≤ v ≤ x+t，即 |x-v| ≤ t，配合下标差约束正好是题目要的数对。

复杂度：随机优先级互相独立时，Treap 的期望树高是 O(log n)，插入、删除、rank、kth、lower_bound 都是期望 O(log n)。最坏情况仍然可能是 O(n)——随机数运气极差时树可以退化，这是"期望保证"和"最坏保证"的本质区别（AVL/红黑树才有最坏保证）。n = 10^5 时，一次操作期望约二三十层递归，十万次操作约几百万步，秒级以内。空间是 O(不同 key 的个数)，重复值只花一个 count 字段。另注意两点：本章递归实现在最坏退化树上会受递归深度限制；跳表、AVL、红黑树在本章只作结构对照，并未实现。

## 六、测试用例在测什么

cell8 是本章最"卷"的测试，分三段：

- **结构审计函数 `audit`**：递归检查整棵树的三条约定——(1) BST 性质：每个键严格落在父辈给它的开区间 `(low, high)` 内；(2) 堆性质：每个孩子的 priority 严格大于父亲（注意 `node.priority<child.priority` 用的是严格小于，配合 serial 平票保证）；(3) size 一致性：`node.size == count + 左右子树实际元素数`（递归返回值现场重算对比），同时检查 `count>=1`。返回子树元素总数，顶层再和 `len(reference)`、`len(tree)` 三方对账。
- **700 轮随机增删**（两套独立随机源：树用 Random(5)，数据用 Random(139)）：每轮随机一个数，一半概率插入（同步 `insort` 进参考列表）、一半概率删除并断言返回值和参考列表的 `in`/`remove` 结果一致。每轮之后做四重校验：audit 全过且总数等于参考长度；`[tree.kth(i) for i in range(len(tree))]` 逐位等于排好序的参考列表（kth 全域正确性）；`tree.rank(x)` 等于 `bisect_left(reference, x)`（rank 的 bisect 语义）；`tree.lower_bound(x)` 等于参考列表中第一个 ≥ x 的元素（没有则 None）。这一段同时覆盖了重复插入（count 增长）和重复删除（count 减到 0 才真正摘节点）。
- **180 轮题目对拍**：随机 12 个数、k ∈ [0,6)、t ∈ [-1,8)（t=-1 这种"值差为负"的非法边界也在测），用双重循环暴力枚举所有数对算出期望值，断言 `contains_nearby_almost_duplicate(a,k,t)` 与之一致。t=-1 时暴力必然 False，正好钉住第一行的参数挡板。

最后打印 `N139: 所有本章断言通过`。

## 七、练习思路提示

**练习 1：说明随机平衡是期望界而非每次保证。** 提示：写个小实验——用同一个类换不同种子的 Random 建 Treap，插入 0..n-1 的有序序列，递归测每棵的树高，画个分布：大多数种子树高在 log n 附近，但理论上存在坏种子使树高接近 n。再对照说明：AVL/红黑树靠确定性旋转规则对任何输入都保证最坏 O(log n)，而 Treap 是"对随机数取平均"。可以顺手解释 priority 里带 serial 的用意：保证优先级两两不同，堆序判断永远能分出胜负。

**练习 2：比较 bisect 加列表插入的成本。** 提示：参考实现 `reference` 用的就是 `insort`——二分找位置 O(log n)，但插入要把后面所有元素后移，最坏 O(n)。设计对比实验：对 n = 10^4、10^5 的随机流分别用"Treap insert"和"insort 进列表"计时，再对比 `tree.kth` 与直接下标访问 `reference[i]`（后者 O(1)，Treap 是 O(log n)）。结论方向：动态有序场景 Treap 增删占优；一次性建好、只读查询的场景排序列表 + bisect 更简单更快，别为了用树而用树。

## 八、对应 LeetCode 题目

- **220. Contains Duplicate III（存在重复元素 III）**：本章 canonical 题，`contains_nearby_almost_duplicate` 就是它的完整解，练的是"有序集合 + 滑窗 + lower_bound 范围查询"三件套。
- **1206. Design Skiplist（设计跳表）**：extension 题，跳表是和 Treap 并列的另一种"靠随机化保平衡"的有序结构（层级靠抛硬币决定），本题要求实现跳表的搜索/插入/删除，正好对照本章"随机优先级 vs 随机层数"两种随机化的用法。
