# N076 · 树的原地变换与Morris遍历 —— 说人话详解

> 对应 notebook：`notebooks/10_trees_tries/076_tree_transformations_morris.ipynb`

## 一、这章要解决什么问题？（问题描述）

前面几章的算法都只"读"树，这一章开始"改"树：把二叉树原地展开成一条右链（`flatten`，LeetCode 114 的"展开为链表"）、把整棵树左右镜像（`invert_tree`）、以及用 O(1) 额外空间做中序遍历（`morris_inorder`）。它们的共同主题是：**在动手改指针之前，先把以后还需要的链接存好；借用的临时链接，用完必须原样还回去**。

举一个具体到数字的例子。输入这棵树（层序序列 `[1,2,5,3,4,None,6]`，本章所有测试都用它）：

```
        1
       / \
      2   5
     / \    \
    3   4    6
```

`flatten` 之后，这棵树要变成"每个节点的左指针全空、沿着右指针一路走下去恰好是原前序序列"的右链，也就是 1→2→3→4→5→6（cell6 的表格记为"展开后前序右链"）。`morris_inorder` 在**完全不修改任何指针**（结束后逐指针验证）的前提下输出中序 `[3,2,4,1,5,6]`。为什么中序是这个顺序？按"左、自己、右"读：最左下是 3，然后 2，2 的右子是 4，然后回到根 1，再进右子树 5、6。

## 二、关键概念（定义）

- **原地变换（in-place）**：不新建节点、只用 O(h) 或 O(1) 的辅助空间，通过改孩子指针完成结构改造。判卷标准不是"打印出来像"，而是**指针结构**——测试里逐节点比对 `(left, right)` 是否和预期完全一致。
- **展开（flatten）**：把树改造成一条链。本章约定"链"是指向右孩子的单链：右链上的节点顺序等于原树的前序，且所有节点的 `left` 必须清成 `None`。
- **镜像（invert）**：每个节点把自己的左右孩子交换。整棵树照镜子，中序遍历的结果会整体反转。
- **中序前驱（inorder predecessor）**：中序遍历里排在某节点紧前面的那个节点。在结构上，它是"当前节点左子树里一路向右走到底的那个节点"。比如上面树里 1 的前驱是 4（左子树 2→4 向右到底），2 的前驱是 3。
- **线索（thread）**：Morris 遍历的核心道具。前驱节点本来右指针是空的，遍历临时把它指向"当前节点"，相当于从子树深处修了一条回祖先的天桥；第二次回到当前节点时，把这座天桥拆掉，右指针恢复为空。线索是"借"的，遍历结束时必须全部还清。
- **恢复义务**：凡是临时修改的结构，函数返回前必须恢复。Morris 遍历如果中途提前退出（比如只想取前 k 个就 return），就会留下没拆的线索，树从此带上"假右孩子"——这是 cell1 点名的错误用法，也是练习 2 的主题。
- **Morris 遍历**：利用线索代替栈/递归来记住"回去的路"的中序遍历，额外空间 O(1)（不计输出列表）。代价是遍历过程中树短暂地变成带环结构，且同一条边会被走两次。

## 三、解决思路（一步步推导）

### 1. `flatten`：前序走一遍，边走边缝

- **Step 1**：用栈做前序遍历（先根、再左、再右），同时用 `previous` 记住上一个访问的节点。
- **Step 2**：每弹出一个新节点，就先把它的两个孩子压栈**存好**，然后才动手把前一个节点 `previous` 的左指针清空、右指针缝到当前节点上。顺序不能反：先改 `previous` 就再也找不到还没访问的子树了。
- **Step 3**：手算例子树。弹 1（压 5、2），previous=None，只记住 1。弹 2（压 4、3），把 1.left 清空、1.right=2。弹 3，把 2.left 清空、2.right=3。弹 4，3.right=4。弹 5（压 6），4.right=5。弹 6，5.right=6。收尾把最后一个节点 6 的左右都清空。结果正是右链：

```
1 → 2 → 3 → 4 → 5 → 6    （每个节点的 left 全部为 None）
```

原树的六个节点一个没丢、一个没多，只是被重新串成"一条向右的糖葫芦"。
- **Step 4**：为什么右链顺序恰好是前序？因为前序的访问顺序就是"根、左子树、右子树"，而我们把每个节点按访问顺序缝到右链上，等价于把"先左后右"的结构改成"一路向右"。

### 2. `invert_tree`：每个节点交换两臂

- **Step 5**：任意顺序访问每个节点（栈、队列都行），访问时把 `left, right` 互换。换完的树是原树的镜像；对镜像再做一次镜像就还原——测试正是用"反转两次后逐指针比对快照"来验证的。

### 3. `morris_inorder`：借线索上天桥，再拆天桥

- **Step 6**：站在当前节点 `current`，如果它没有左孩子，直接访问它，走向右孩子。
- **Step 7**：如果有左孩子，先找它的中序前驱（左子树一路向右到底），看前驱的右指针：如果是空的，说明当前节点的左子树还没访问，修一条线索（前驱.right=current）然后走左孩子；如果前驱的右指针指回 current 自己，说明这是从线索走回来的——左子树已经访问完毕，拆掉线索、访问 current、走向右孩子。
- **Step 8**：手算例子树，线索一共建拆各两次：
  - current=1：左子树存在，前驱是 4（2 向右到 4）。4.right 空 → 修线索 4→1，走进左子树。
  - current=2：前驱是 3。3.right 空 → 修线索 3→2，走左。
  - current=3：无左孩子 → 输出 3，沿右走——踩着线索 3→2 回到 2。
  - current=2（第二次）：前驱 3 的右指针指回自己 → 拆线索（3.right=None），输出 2，走向右孩子 4。
  - current=4：无左孩子 → 输出 4，沿右走——踩着线索 4→1 回到根。
  - current=1（第二次）：前驱 4 的右指针指回自己 → 拆线索（4.right=None），输出 1，走向右孩子 5。
  - current=5：输出 5，走右到 6。current=6：输出 6，右为空，结束。
  - 输出 [3,2,4,1,5,6]，两条线索都已拆除，树恢复原样。

## 四、代码逐段讲解

`TreeNode`、`tree_from_level` 与前几章相同。看三个新函数。

### 1. 展开为右链

```python
def flatten(root):
    stack=[root] if root else []
    previous=None
    while stack:
        node=stack.pop()
        if node.right: stack.append(node.right)
        if node.left: stack.append(node.left)
        if previous: previous.left=None; previous.right=node
        previous=node
    if previous: previous.left=None; previous.right=None
```

`stack=[root] if root else []` 挡住空树：空栈直接跳过循环。弹出节点后**先**把右、左孩子压栈（先压右再压左，下次先弹左，保证前序），**再**改 `previous` 的指针——这两行的先后顺序是"先保存后修改"纪律的直接体现：一旦先把 `previous.right` 改成 node，原来挂在 previous 上的右子树就永远丢了。`if previous` 是在挡第一次循环（还没有上一个节点，谁也别改）。循环结束后最后一个节点 previous 可能还挂着旧孩子（它是叶子时左右本来是 None，但保险起见），统一清空。

### 2. 镜像

```python
def invert_tree(root):
    stack=[root] if root else []
    while stack:
        node=stack.pop(); node.left,node.right=node.right,node.left
        if node.left: stack.append(node.left)
        if node.right: stack.append(node.right)
    return root
```

核心就一行：`node.left,node.right=node.right,node.left`，Python 的多重赋值右边先整体求值再赋值，所以这是真正的"同时交换"，不需要临时变量。交换后原来的右孩子现在成了 `node.left`，把它压栈继续处理。注意压栈判断在交换之后做，压的是换位后的引用，效果等同"把原树每个节点都换臂"。空树时返回 None。

### 3. Morris 中序

```python
def morris_inorder(root):
    answer=[]; current=root
    while current:
        if current.left is None: answer.append(current.val); current=current.right
        else:
            predecessor=current.left
            while predecessor.right and predecessor.right is not current: predecessor=predecessor.right
            if predecessor.right is None: predecessor.right=current; current=current.left
            else: predecessor.right=None; answer.append(current.val); current=current.right
    return answer
```

- 没有左孩子：直接访问，往右走。注意"往右走"可能是普通右边，也可能踩着线索跳回祖先——对算法来说两者毫无区别，这正是线索的妙处。
- 找前驱：`predecessor=current.left` 后，`while predecessor.right and predecessor.right is not current` 一路向右。第二个条件很关键：如果右指针指回 current，说明线索已存在（这是第二次来），必须停下，否则会绕着环无限转。
- 前驱右指针为空 → 第一次到这，"建线索、走左"。前驱右指针指回 current → 第二次到这，左子树已收工，"拆线索（`predecessor.right=None` 还原为空）、访问 current、走右"。建与拆严格配对，保证结束时树完全复原。
- 整个函数除了输出列表 `answer`，只用了 `current` 和 `predecessor` 两个变量，辅助空间 O(1)。

## 五、为什么是对的？复杂度是多少？（说人话）

**`flatten` 为什么不会弄丢子树？** 每次动手改 `previous` 的指针之前，当前节点 `node` 的两个孩子已经压进栈里了；被清空和覆盖的只是 `previous` 身上已经"用完"的指针。也就是说，任何还等着访问的子树，要么在栈里，要么还挂在未处理的节点上，永远不会被写坏。按前序缝出来的右链，顺序自然就是前序。

**Morris 为什么既不重不漏又能复原？** 站在任何一个节点上，只有两种可能：左子树没访问过（第一次来，建线索进去），或访问完了（从线索回来，拆线索出上）。每条线索从建立到拆除之间恰好把整个左子树访问完毕，节点恰好被输出一次；而"第二次遇到线索就拆"保证了每条线索必然被拆——不拆掉它，循环条件 `predecessor.right is not current` 就无法成立，流程根本走不到访问当前节点那一步，所以不存在"漏拆"的路径。遍历结束时，所有前驱原本为空的右指针都恢复了空，树的形状和来之前一模一样。

**反转两次为什么一定还原？** 反转把每个节点的左右孩子互换，这个操作对每个节点是独立的、且做两次恰好回到原样（交换是"自反"的：`swap(swap(x))=x`）。两个节点即使在第一次反转后换了位置，第二次反转时它们各自的孩子再次被互换，指针全部各归各位——测试里逐指针比对快照正是对这句话的机械验收。

**一个常见疑问：Morris 遍历会不会把树走丢？** 不会。线索建立期间树确实短暂地带了环（比如例子树上 4.right 指向 1），但找前驱的内层 `while` 用 `predecessor.right is not current` 专门检测"前方是回自己那条线索"并停下，循环永远不会绕环跑；每条线索的寿命被严格限制在"建"和"拆"两次相遇之间。

**复杂度**：三个函数都把每个节点处理常数次（Morris 中每条边最多被走两次：下去一次、沿线索或普通指针回来一次），时间都是 O(n)；n=10⁵ 的树就是二十万步上下的指针移动，很快。空间上，`flatten` 和 `invert_tree` 的显式栈最坏 O(n)（一条链时），`morris_inorder` 除了输出列表只用两个变量，辅助空间 O(1)——这正是它相对栈遍历的核心优势：树再深也不会爆栈、不占内存。

## 六、测试用例在测什么

cell8 的测试围绕"指针结构"展开，先做一次前序遍历，把每个节点的 `(left, right)` 指针对存进 `snapshot`，同时记下前序的节点序列 `preorder`——这就是后面所有判定的"标准答案"。

- `assert morris_inorder(r)==[3,2,4,1,5,6]`：中序结果的标准值检验。
- `assert all((n.left,n.right)==edges for n,edges in snapshot.items())`：Morris 跑完之后逐节点比对指针——这是"恢复义务"的直接验收：哪怕只拆漏一条线索，这个比对立刻失败。它测的不是输出对不对，而是"树有没有被动过"。
- `invert_tree(invert_tree(r)); assert all(...)`：反转两次等于没反转，逐指针比对快照。它测的是"反转这个变换是自反的"，同时也再次确认 invert 没有弄丢或复制节点。
- `flatten(r)` 后的循环：沿右链走下去，每个节点必须满足两条——`n.left is None`（左指针全清）且 `n not in after`（不绕回已访问节点，防环）；走完的节点序列 `after` 必须和之前记录的前序 `preorder` **逐对象相等**（`==` 对列表比较的是每个元素是否同一个对象）。它同时验收了"顺序是前序""left 清空""无环"三个合同条款。

注意这一整套测试从头到尾没有比较过一个 `val`——它盯的全是指针。这就是本章的判卷哲学：值没变不代表结构没坏，验收原地变换必须看链接本身。全部通过后打印 `N076: 所有本章断言通过`。

## 七、练习思路提示

- **练习 1（证明 Morris 临时边最后会删除）**：提示——按"线索的一生"来论证。每条线索建立时，建立它的那个节点 `current` 还没被访问；只要遍历继续，`current` 迟早会再次成为当前节点（沿这条线索回来），而第二次到达时唯一出口就是拆线索。换句话说，建线索的次数和拆线索的次数严格相等，循环正常结束时不可能有未拆的线索。写验证程序的方向：在morris 代码里给建/拆各加一个计数器，遍历各种形状的树（含单边链、满树、随机树），断言两个计数器相等且结束后指针快照不变。
- **练习 2（解释早停遍历可能破坏恢复）**：提示——把 `morris_inorder` 改成"输出满 k 个就 return"，然后在 return 前对树做指针快照比对，你会看到某些 left-heavy 的树上快照不再相等：没走完的左子树里还挂着未拆的线索（比如例子树上取前 2 个就停，线索 4→1 还挂着，节点 4 凭空多出一个指向 1 的"右孩子"）。讨论两种修法：要么老实走完全程再切前 k 个；要么封装成生成器并在生成器被关闭时（finally 分支）继续拆线索——想清楚后者为什么危险（你不知道当前位置还欠哪几条线索）。

## 八、对应 LeetCode 题目

- **114. Flatten Binary Tree to Linked List**：原地展开为右链，直接对应 `flatten`，验收标准正是本章强调的"右链 = 前序、left 全空"。
- **226. Invert Binary Tree**：镜像翻转，直接对应 `invert_tree`，练的是最简单的整树指针变换，也常用来复习多重赋值交换。
- **94. Binary Tree Inorder Traversal**：中序遍历，官方标 canonical 的是栈/递归解法，本章的 `morris_inorder` 是它的 O(1) 空间进阶版（extension），练的是"用线索代替栈记住回路"。
