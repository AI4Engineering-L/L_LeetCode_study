# N109 · 树形DP与局部约束 —— 说人话详解

> 对应 notebook：`notebooks/13_dynamic_programming/109_tree_dp_selection_matching.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章处理"树上的选择问题"：每个节点有选/不选两种待遇，但相邻节点之间有约束（比如父亲选了儿子就不能选、每个节点必须被某个摄像头看到）。核心三问：

1. **打家劫舍 III**：二叉树上每个房子有一定金额，**直接相连**的房子不能同晚都偷，求最大金额。
2. **监控二叉树**：相机装在节点上，能覆盖自己、父亲和孩子，求覆盖所有节点的最少相机数。
3. **一般树的加权独立集**：把上一套思路搬到邻接表表示的一般树上，每个点有权重，相邻的点不能同时选，求最大权和。

先看一个具体到数字的例子（notebook 第 6 格用的就是它，层序数组 `[3,2,3,None,3,None,1]` 对应这样一棵树：根 3，左孩子 2，右孩子 3；左孩子 2 又只有右孩子 3；右孩子 3 又只有右孩子 1）：

- 输入这棵树，问打家劫舍最大金额。
- 输出 `7`。
- 为什么是 7？直接相连的不能同时偷，所以最优偷"根 3 + 左孙 3 + 右孙 1"这三个互不相邻的点，得 3+3+1=7。中间那两个节点（孩子 2 和孩子 3）反而要放过去，因为选了它们就锁死了更值钱的孙子。

同一棵树上问最少相机，答案是 `2`：在两个孩子（2 号和右边的 3 号）各装一台，两台相机分别覆盖"孩子+它的孩子+根"，正好把 5 个节点全覆盖。

## 二、关键概念（定义）

- **树形 DP**：在树上做动态规划。它的命门在于"先算子树、再算父亲"，也就是**后序**（postorder：先左右孩子、后自己）。父亲的状态由孩子状态拼出来，所以孩子必须先就绪。
- **子树独立**：树上没有"跨子树"的边，一棵树从某个点断开后，各孩子的子树之间互不相连。因此一旦固定"父亲选还是不选"，每个子树就可以各自独立地求最优，互不打扰。这一条是所有树形 DP 正确性的根。
- **选/不选两个状态（dp 值是二元组）**：`dp[u] = (不选 u 的最优, 选 u 的最优)`。为什么不存一个数？因为父亲关心的是"你选没选"，两种情况要分别汇报（这正是练习 2 的主题）。
- **状态合并**：父亲的状态 = 把所有孩子的状态按转移规则加起来。比如"不选父亲"时每个孩子随便选不选（取两者较大值）；"选父亲"时每个孩子必须不选（只取孩子的不选值）。
- **三状态摄像头**：摄像头问题光"选/不选"不够，本章用 0/1/2 三个值描述子树根的处境——0 = 我的子树内部都处理好了，但**我自己还没被任何相机看到**；1 = 我这里装了相机；2 = 我已经被孩子的相机看到。空孩子（None）当作 2（已覆盖），这样代码就不必在空位置装相机。
- **方案恢复**：本章函数只返回最优值；想拿到"到底选了哪些点"，需要额外记录每个节点取的是哪个分支（练习 2 会逼你直面"只留一个数会丢信息"这件事）。
- **层序建树（`tree_from_level`）与邻接表（`adj`）**：同一棵树的两种表示。层序数组是 LeetCode 题目给的格式（`None` 是占位符）；邻接表 `adj[u]` 存 u 的所有邻居，适合一般树。

## 三、解决思路（一步步推导）

### 主线：rob_tree 在 `[3,2,3,None,3,None,1]` 上手算

- **Step 1：定状态。** 对每个节点 u 记 `dp[u] = (a, b)`：a = "u 不选"时 u 的子树能偷到的最大值；b = "u 选"时的最大值。空位置 None 记 `(0,0)`（没东西可偷）。
- **Step 2：定转移。**
  - 不选 u：两个孩子各自随便（选或不选取大），`a = max(左a,左b) + max(右a,右b)`。
  - 选 u：孩子必须都不选，`b = u.val + 左a + 右a`。
- **Step 3：后序手算。** notebook 第 6 格把这棵树的后序轨迹打成了表，节点处理顺序是"左孙 3 → 左孩子 2 → 右孙 1 → 右孩子 3 → 根 3"：

| 节点值 | 不选 | 选 |
|---|---|---|
| 3（左孙，叶子） | 0 | 3 |
| 2（左孩子） | 3 | 2 |
| 1（右孙，叶子） | 0 | 1 |
| 3（右孩子） | 1 | 3 |
| 3（根） | 6 | 7 |

逐行核对：左孙是叶子，不选偷 0、选偷 3。左孩子 2：不选 = max(0,0)+max(0,3) = 3（让孩子偷）；选 = 2+0+0 = 2（自己偷 2，孩子全锁）。右孩子 3 同理：不选 = 1（让右孙偷），选 = 3。根 3：不选 = max(3,2)+max(1,3) = 6；选 = 3+3+1 = 7（左右孩子的不选值 3 和 1）。最终 `max(6,7)=7`。

- **Step 4：体会"必须存两个数"。** 根的"选"=7 用到了孩子的**不选**值（3 和 1）；根的"不选"=6 用到了孩子的两个值的较大者。如果每个子树只汇报一个数，这两种拼法至少有一种会拼错。

### 副线：min_camera_cover 在同一棵树上手算

后序逐点判状态（空孩子按 2 处理）：

- 左孙 3：两个孩子都是"空=2"，没有未覆盖的孩子也没有装相机的孩子 → 状态 0（自己没人罩）。
- 左孩子 2：右孩子状态是 0（未覆盖）→ 在自己这里装相机，状态 1，相机数 +1（现在是 1）。这台相机同时罩住左孙、自己和根。
- 右孙 1：叶子，状态 0。
- 右孩子 3：右孩子状态 0 → 装相机，状态 1，相机数变成 2。
- 根：两个孩子都是 1（有相机）→ 根已被覆盖，状态 2。
- 收尾：根状态不是 0，不用补。答案 2。

贪心的直觉：孩子的孩子没被罩住时，与其"下去"在孙子上装，不如"上来"在当前点装——一台相机同时罩住下、己、上三个人，永远不会更差。

## 四、代码逐段讲解

cell3 里除了三个接口函数，还有四个辅助函数，我们按出场顺序讲。

### 辅助设施

```python
class TreeNode:
    def __init__(self,val=0,left=None,right=None):
        self.val,self.left,self.right=val,left,right
```

二叉树节点：一个值、一个左指针、一个右指针，`val=0` 等默认值让你可以 `TreeNode()` 一句话造单节点树。

```python
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

把 LeetCode 的层序数组还原成树：BFS 逐个取数组元素，依次当作队头节点的左孩子、右孩子；遇到 `None` 占位就跳过不挂孩子。开头的判断挡住空输入（空数组或根就是 None 直接返回 None 树）。

```python
def _postorder_nodes(root):
    stack=[(root,False)]
    while stack:
        node,done=stack.pop()
        if not node: continue
        if done: yield node
        else:
            stack.append((node,True)); stack.append((node.right,False)); stack.append((node.left,False))
```

不用递归的后序遍历（避免深树爆递归栈）。技巧是给每个节点入栈两次：第一次带 `False`，弹出时把"(自己, True)、右孩子、左孩子"压栈（注意顺序：左孩子最后压、最先处理）；第二次带 `True` 弹出时才真正交出节点。这保证左孩子、右孩子都先于自己被 yield，正好是后序。`if not node: continue` 把 None 挡在门外。

```python
def _tree_order(adj,root=0):
    if not adj: return [],[]
    parent=[-1]*len(adj); parent[root]=root; order=[root]
    for u in order:
        for v in adj[u]:
            if v==parent[u]: continue
            if parent[v]!=-1: raise ValueError('tree required')
            parent[v]=u; order.append(v)
    if len(order)!=len(adj): raise ValueError('connected tree required')
    return parent,order
```

给邻接表做一次 BFS：`order` 是从根往下的访问顺序（父先于子），`parent[v]` 记每个点的父亲。两个守卫：邻居 v 已经有父亲又不是我的父亲，说明有环或多边（`tree required`）；走完没遍历到全部点，说明图不连通（`connected tree required`）。`parent[root]=root` 是让"跳过父亲"的判断对根也成立。

### 1. `rob_tree`

```python
def rob_tree(root):
    dp={None:(0,0)}
    for node in _postorder_nodes(root):
        l0,l1=dp[node.left]; r0,r1=dp[node.right]
        dp[node]=(max(l0,l1)+max(r0,r1),node.val+l0+r0)
    return max(dp[root])
```

用字典 `dp` 存每个节点的二元组，键就是节点对象本身；`{None:(0,0)}` 预置空树的值，于是"孩子是 None"不需要特判，查表自然得 (0,0)。循环按后序取出节点，先拆出左右孩子的四元信息 `l0,l1,r0,r1`，再按 Step 2 的两条公式组装自己的二元组：不选 = 两个 max 相加，选 = 自身值加两个"孩子不选"值。最后 `max(dp[root])` 在根的选/不选之间取大。整个算法每个节点算一次、每次 O(1)，是线性时间。

### 2. `min_camera_cover`

```python
def min_camera_cover(root):
    state={None:2}; count=0
    for node in _postorder_nodes(root):
        left,right=state[node.left],state[node.right]
        if 0 in (left,right): state[node]=1; count+=1
        elif 1 in (left,right): state[node]=2
        else: state[node]=0
    return count+(root is not None and state[root]==0)
```

同样后序、同样字典。三分支转移：只要有孩子未覆盖（状态 0），就在当前点装相机（状态 1、计数加一）；否则只要有孩子装了相机（状态 1），当前点已被照到（状态 2）；否则（孩子们都是 2，即都被"更下面"的相机照顾了，没照到我这层）当前点暂时没人罩，状态 0，把装相机的决定**留给父亲**——这是贪心的精髓：在当前点装不如在父亲装划算（父亲那台能多罩一个点）。最后一行处理根的特例：根没有父亲，如果转完根还是状态 0，没人能罩它了，只能自己在根上补一台。`(root is not None and state[root]==0)` 是个布尔表达式，参与加法时 True 当 1、False 当 0；`root is not None` 同时挡住了空树（空树一个相机都不用，返回 0）。

### 3. `tree_independent_set`

```python
def tree_independent_set(adj,weights):
    if len(adj)!=len(weights): raise ValueError('one weight per vertex')
    parent,order=_tree_order(adj); dp=[[0,0] for _ in adj]
    for u in reversed(order):
        dp[u][1]=weights[u]
        for v in adj[u]:
            if parent[v]==u: dp[u][0]+=max(dp[v]); dp[u][1]+=dp[v][0]
    return max(dp[0]) if dp else 0
```

这是 rob_tree 的"一般树版"：状态还是每点二元组 [不选, 选]，但孩子不再固定两个，而是扫邻居里所有"父亲是我"的点（`parent[v]==u` 筛出真孩子，把父亲本人和已经是 u 孩子的重复边排除）。处理顺序用 `reversed(order)`：order 是从根到叶的 BFS 序，倒过来就是"孩子先于父亲"的自底向上序，效果等价于二叉树版的后序。转移是累积式的：不选 u 就把每个孩子的 max 加进来（孩子随便）；选 u 就初始化为权重、每个孩子只加"不选"值。开头的长度检查要求每个点恰好一个权重；结尾 `if dp else 0` 挡住空图（`max(dp[0])` 对空列表会越界）。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么是对的？** 先说独立集类（rob_tree 和 tree_independent_set）：约束只有"父子不能同时选"。当我们固定"父亲选"时，每个孩子必须不选，孩子的子树内部爱怎么选怎么选，跟兄弟子树毫无关系（树上没有跨子树的边）；固定"父亲不选"时孩子两边随便，同样各自独立。所以二元组 `(不选, 选)` 把"父亲两种意图下子树的最优值"都备齐了，父亲拼自己的答案时查表即可，两种情况都不会算错。反例留给你（练习 2）：如果只存一个 max 值，"父亲选"这条分支就查不到可靠的"孩子不选"值。再说摄像头：只要某棵子树的根状态是 0（未覆盖），这台子树内部已经没有相机能罩到它了（有则状态不会是 0），唯一的补救是它自己、它父亲或它的孩子装相机；三者中"装在父亲"覆盖面最大（父亲那台同时罩住父亲、它、它的孩子），至少不劣于装在它自己身上，所以我们把决定上交。孩子都有相机时当前点免费被罩（状态 2）；孩子们都干净但没相机时（状态 0）继续上交。最后根没有更上一层可交，只能自己装——这就是结尾那笔补加。

**复杂度**：三个接口都是每个点处理一次、每次扫自己的邻居（二叉树邻居至多 2 个），所以时间 O(n)。辅助空间方面，`dp`/`state` 字典把**每个**子树的状态都存了下来，是 O(n)，不要误写成 O(h)（h 是树高）——O(h) 是递归栈的深度，不是这份数据结构的大小。拿具体数字感受：n = 10⁵ 个节点时，三百万级的基本操作，一瞬间跑完。邻接表接口要求输入是连通无向树（`_tree_order` 里那两个 raise 会替你把关）；二叉树对象不能有共享孩子或环。

## 六、测试用例在测什么

- `assert rob_tree(tree_from_level([3,2,3,None,3,None,1]))==7`：正常值测试，就是第一、三节手算的例子，同时顺带验证了 `tree_from_level` 能正确还原带 `None` 占位的层序数组。
- `assert min_camera_cover(TreeNode())==1 and min_camera_cover(None)==0`：两条边界。单节点树没有任何邻居，只能在它自己身上装一台（测的是"根状态 0 需要补装"的收尾逻辑）；空树一台都不用（测的是 `root is not None` 这个短路判断，没有它会对 None 状态查询报错或多数一台）。
- 后半部分是随机对拍：`rng=Random(109)` 固定随机种子保证可复现；对 n=1..8 的每种规模各造 20 棵随机二叉树（`available` 列表保证每个新节点挂在还有空位的节点下面），再转成邻接表。然后用**位掩码暴力**当裁判：独立集枚举所有 2ⁿ 个选/不选组合，`not(mask>>u&1 and mask>>v&1)` 过滤掉"父子同选"的非法组合，取权和最大；摄像头同样枚举所有相机摆放，检查每个点"自己有相机或某个邻居有相机"，取相机数最少。断言 `rob_tree`、`tree_independent_set` 与暴力一致（这同时验证了"二叉树版和一般树版等价"），`min_camera_cover` 与暴力一致。小树上全枚举不会错，对上它就说明转移方程没写歪。

## 七、练习思路提示

- **练习 1（把二叉树版推广到一般树）**：提示——`rob_tree` 的转移里"孩子固定两个"是唯一绑死二叉树的地方。把"左孩子公式 + 右孩子公式"改写成"对所有孩子累加"，你就得到了……其实本章的 `tree_independent_set` 已经就是这个答案。你要做的是自己推一遍再对照：输入改成邻接表和权数组、边界（单点树、空图、n=1）怎么处理、手算例子建议用"根 3 带三个孩子 2,2,2"（答案 6，孩子全选）来验证邻居个数不固定时转移仍然对。
- **练习 2（只用一个最优值会丢什么信息）**：提示——造一条链：根值 10，孩子值 9，孙子值 8。孩子子树的最优值是 9（选孩子自己），但这个 9 是"选了孩子"才达到的。如果 dp 表只存这一个 9，那么当根（值 10）想选自己时，它需要的是"孩子不选"时的子树值（应该是 8），而表里查不到，硬用 9 就违反了"父子不同选"。请把这个"10+9=19 是假方案、真最优是 10+8=18"的例子写清楚，再解释二元组 `(不选, 选)` 如何把两种意图分开存、让父亲两种问法都有答案。

## 八、对应 LeetCode 题目

- **337. House Robber III**：练"选/不选二元组状态 + 后序自底向上合并"，本章 `rob_tree` 即其标准解，附带学一手非递归后序。
- **968. Binary Tree Cameras**：练"两状态不够用时要敢加第三状态 + 空孩子当已覆盖 + 根的收尾特判"，对应 `min_camera_cover`，本质是树上贪心但用 DP 状态来论证。
