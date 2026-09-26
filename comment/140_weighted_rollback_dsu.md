# N140 · 带权与可回滚并查集 —— 说人话详解

> 对应 notebook：`notebooks/16_advanced_structures/140_weighted_rollback_dsu.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章给并查集加两个"高级配件"。第一个配件是"带权"：普通并查集只回答"x 和 y 是不是一伙的"，带权并查集还回答"x 是 y 的几倍"。经典场景（LeetCode 399）是：告诉你 `a/b=2`、`b/c=3` 这类等式，要你算 `a/c` 是多少（答案是 6）。第二个配件是"可回滚"：有些算法需要"先合并、做完事再撤销，恢复到合并之前的状态"，普通并查集的路径压缩会把沿途节点直接挂到根上，撤销时根本不知道原来指向谁，所以回滚版必须忍痛不做路径压缩，改用"记历史"的方式精确还原。

一个具体到数字的例子（cell6 的）：`union('a','b',2)` 表示 a/b=2，`union('b','c',3)` 表示 b/c=3，随后 `ratio('a','c')` 返回 6.0——因为 a=2b、b=3c，串联相乘得 a=6c。回滚演示：4 个点先 `union(0,1)`，打个快照，再 `union(1,2)`，此时连通分量数是 2；`rollback(saved)` 之后分量数回到 3，第二次合并被完整撤销。

## 二、关键概念（定义）

- **并查集（DSU）**：用"每个元素记一个父亲"的方式维护"哪些元素属于同一组"，支持合并（union）和查根（find）。两元素根相同就是同一组。
- **带权并查集（weighted DSU）**：在父亲指针之外再存一个数。关键点：`weight[x]` 不是 x 的什么绝对属性，而是"x 除以它的父亲等于多少"（x/parent[x]）的**相对比值**。整棵树遵守"从节点沿路径连乘 weight 到根，得到节点/根的比值"这条约定。
- **路径压缩时权值要跟着算**：普通并查集压缩时只改父指针；带权版必须在把节点直接挂到根的同时，把它的新 weight 设成"沿途各段 weight 的连乘积"。只改指针不算乘积，根找对了、数值关系却坏了——这是本章最强调的坑。
- **按大小合并（union by size）**：合并两棵树时，把小的挂在大的下面，保证树高是 O(log n)。带权版靠它撑住复杂度（同时又用路径压缩进一步压平）。
- **回滚栈（history）**：RollbackDSU 把每次合并改掉的"旧值"（谁的父亲被改了、旧 size 是多少）压进一个栈，撤销时弹出恢复。无效合并（本来就同根）也压一个 None 占位，保证"栈长度 = 操作数"，快照编号才对得上操作边界。
- **快照（snapshot）**：`snapshot()` 返回当前历史长度，相当于"拍下此刻的状态编号"；`rollback(编号)` 把之后的所有合并逐个撤销，回到那个时刻。注意只能回到"当前历史的祖先"，回滚时被舍弃的未来操作不会复活。
- **路径压缩与回滚不兼容**：压缩会一次改掉一长串父指针，而且改之前不留记录，撤销无从谈起。所以 RollbackDSU 的 find 只是老实地一层层向上走，一次都不压缩。
- **浮点容差（isclose）**：等式约束可能有浮点误差，比较时用 `isclose(..., rel_tol=1e-9, abs_tol=1e-12)` 而不是 `==`。
- **离线删边扩展**：并查集不擅长删边；经典技巧是离线把"删边"倒过来变加边，配合本章的回滚能力，属于迁移方向（notebook 提名但未展开）。

## 三、解决思路（一步步推导）

### 带权部分

- **Step 1**：约定 `weight[x] = x / parent[x]`，根自己的 weight 恒为 1.0（根除以自己是 1）。
- **Step 2（find + 压缩）**：先沿父指针走到根，把沿途节点记进 path；然后倒序遍历 path，维护累计乘积 ratio，每遇到一个节点 v 就把 `weight[v]` 更新为"v 到根的累计比值"并把 parent[v] 直指根。这样压缩之后每个节点的 weight 仍然精确表示"它除以根"。
- **Step 3（union 推公式）**：已知 x/y = value，x 的根是 rx（x/rx = wx），y 的根是 ry（y/ry = wy）。若 rx ≠ ry 要把两棵树接起来。假如让 rx 挂到 ry 下面，需要 rx/ry = (x/y)·(wy/wx) = value·wy/wx，这个数就是挂上去时填的 weight；反过来 ry 挂 rx 就取倒数 wx/(value·wy)。cell4 的论证翻成人话就是：x = wx·rx，y = wy·ry，x/y = value 联立解出 rx/ry。
- **Step 4（同根校验）**：若 rx == ry，说明 x、y 的关系早已确定，算出 wx/wy 与 value 比对，对不上就抛"矛盾等式"异常，对得上就返回 False（没有真的合并）。
- **Step 5（ratio 查询）**：x、y 不同根或没见过就返回 -1.0（题目约定的"无法求解"）；同根则 x/y = (x/根)/(y/根) = weight[x]/weight[y]。

**手算演示（cell6 带权部分）**：
1. `union('a','b',2)`：a、b 各自成根，size 都是 1。size[rx]<size[ry] 不成立（1<1 假），走 else 分支：b 挂到 a 下，`weight[b] = wx/(value*wy) = 1/(2*1) = 0.5`，即 b/a = 0.5（b 是 a 的一半，等价 a=2b）。
2. `union('b','c',3)`：find(b) 顺带把 b 压到根 a，此时 wx = weight[b] = 0.5，wy = weight[c] = 1.0；size[a]=2 更大，else 分支：c 挂到 a 下，`weight[c] = 0.5/(3*1) = 1/6`，即 c/a = 1/6（a 是 c 的 6 倍）。
3. 查 `ratio('a','c')`：同根 a，weight[a]/weight[c] = 1/(1/6) = **6.0**。表格里三行数据就是 a→根 a 权 1.0、b→根 a 权 0.5、c→根 a 权 1/6。

### 回滚部分

- **Step 6**：不做路径压缩、不做带权，只维护 parent、size 和分量计数 components；union 时按大小挂小树到大树，并把 `(a, b, 旧size[a])` 压栈；本来同根就压 None。
- **Step 7（rollback）**：传入一个历史长度 snapshot，只要当前栈比它长就弹栈：None 直接跳过（它本来就没改任何东西），正常记录则恢复 `parent[b]=b`、`size[a]=旧值`、components 加一。弹到指定长度即回到当时状态。

**手算演示（cell6 回滚部分，4 个点）**：`union(0,1)` 后 components=3，栈里记 `[(0,1,size=1)]`；snapshot() 记下栈长 1。`union(1,2)`：1 的根是 0，2 自成根，0 的 size=2 更大，于是 2 挂 0，components=2，栈变成两条记录，打印"回滚前分量 2"。`rollback(1)` 弹出 `(0,2,2)`：parent[2] 恢复指自己，size[0] 恢复 2，components 加回 3，打印"回滚后分量 3"。第一条合并完好无损。

## 四、代码逐段讲解

cell3 有三块：WeightedDSU 类、calc_equation 函数、RollbackDSU 类。

**WeightedDSU 的初始化与 add**

```python
    def __init__(self): self.parent={}; self.weight={}; self.size={}
    def add(self,x):
        if x not in self.parent: self.parent[x]=x; self.weight[x]=1.0; self.size[x]=1
```

三个字典分别存父指针、比值、子树大小——用字典而不是数组，是因为变量名可以是字符串（'a'、'b'）。`add` 把新变量登记为"自己的根、权 1.0、大小 1"；已存在就什么都不做（幂等）。

**带权查找 find**

```python
    def find(self,x):
        if x not in self.parent: raise KeyError(x)
        path=[]; node=x
        while self.parent[node]!=node: path.append(node); node=self.parent[node]
        ratio=1.0
        for v in reversed(path): ratio*=self.weight[v]; self.weight[v]=ratio; self.parent[v]=node
        return node
```

第一行挡没登记过的变量（直接抛 KeyError，和 ratio 返回 -1 的温和策略不同：find 是内部接口，出错就该炸）。第一段循环沿父指针爬到根，沿途节点进 path。第二段倒序遍历 path：从最靠近根的节点开始，ratio 累乘沿途 weight——注意 `ratio*=self.weight[v]` 用的是 v 更新**前**的值（v 到它父亲那段），随后才把 `self.weight[v]` 覆盖为累计值、把 parent[v] 直指根 node。倒序保证先算靠根的段、再算靠叶的段，一层层把"到父亲的比"换算成"到根的比"。

**带权合并 union**

```python
    def union(self,x,y,value):
        if value==0: raise ValueError('nonzero ratio required')
        self.add(x); self.add(y); rx=self.find(x); ry=self.find(y); wx=self.weight[x]; wy=self.weight[y]
        if rx==ry:
            if not isclose(wx/wy,value,rel_tol=1e-9,abs_tol=1e-12): raise ValueError('inconsistent equation')
            return False
        if self.size[rx]<self.size[ry]:
            self.parent[rx]=ry; self.weight[rx]=value*wy/wx; self.size[ry]+=self.size[rx]
        else:
            self.parent[ry]=rx; self.weight[ry]=wx/(value*wy); self.size[rx]+=self.size[ry]
        return True
```

第一行挡除零：比值是 0 的等式在乘除体系里没意义。先 add 保证两点都登记，find 找到两根并**顺手把 x、y 压到根**（所以接下来的 wx、wy 已经是 x/根、y/根）。同根分支做一致性校验（容差比较），矛盾就抛 `inconsistent equation`，一致返回 False。两个挂接方向就是第三节推的两条公式：小树 rx 挂大树 ry 时填 `value*wy/wx`，反之填倒数 `wx/(value*wy)`；size 累加、返回 True。

**比值查询 ratio 与题目封装**

```python
    def ratio(self,x,y):
        if x not in self.parent or y not in self.parent: return -1.0
        if self.find(x)!=self.find(y): return -1.0
        return self.weight[x]/self.weight[y]

def calc_equation(equations,values,queries):
    if len(equations)!=len(values): raise ValueError('one value per equation required')
    dsu=WeightedDSU()
    for (x,y),value in zip(equations,values): dsu.union(x,y,value)
    return [dsu.ratio(x,y) for x,y in queries]
```

ratio 前两行分别处理"变量没出现过"和"不同连通块"，都返回 -1.0（题目的约定答案）。`calc_equation` 是 LeetCode 399 的直接封装：先检查等式数和数值数一致（防呆），把每条等式 union 进去，再逐个查询输出列表。

**RollbackDSU**

```python
    def __init__(self,n): self.parent=list(range(n)); self.size=[1]*n; self.components=n; self.history=[]
    def find(self,x):
        if not 0<=x<len(self.parent): raise IndexError('vertex outside DSU')
        while self.parent[x]!=x: x=self.parent[x]
        return x
    def union(self,a,b):
        a,b=self.find(a),self.find(b)
        if a==b: self.history.append(None); return False
        if self.size[a]<self.size[b]: a,b=b,a
        self.history.append((a,b,self.size[a])); self.parent[b]=a; self.size[a]+=self.size[b]; self.components-=1
        return True
    def snapshot(self): return len(self.history)
    def rollback(self,snapshot):
        if not 0<=snapshot<=len(self.history): raise ValueError('snapshot outside active history')
        while len(self.history)>snapshot:
            change=self.history.pop()
            if change is None: continue
            a,b,old_size=change; self.parent[b]=b; self.size[a]=old_size; self.components+=1
```

构造时 n 个点各自为根、components 计数从 n 起步。`find` 挡越界下标后老实逐层上爬——**没有任何压缩**，这是回滚能力的代价。`union` 先换成根比较：同根也压 None 占位（栈长 = 操作数，快照编号才能对齐操作边界）；`if self.size[a]<self.size[b]: a,b=b,a` 用交换保证 a 永远是大树、b 挂到 a 上；压栈的三元组 `(a, b, 旧size[a])` 恰好是本次修改涉及的全部旧值（parent[b] 原本必然是 b 自己，无需另存）。`snapshot` 就是当前栈长。`rollback` 先挡非法编号（不能回滚到未来或负数），然后弹栈：None 跳过，正常记录逆序恢复三个字段——parent[b] 指回自己、size[a] 还原旧值、分量数加一。恢复顺序天然是"后做的先撤销"，正好逆掉之前的修改。

## 五、为什么是对的？复杂度是多少？（说人话）

带权部分为什么对：核心约定是"任意时刻，节点 v 沿父指针把各段 weight 连乘，得到的都是 v/根 的真实比值"。find 压缩时倒序累乘，等价于把多段比换乘成一段等价比，约定保持；union 挂接时填的公式就是从 x = wx·rx、y = wy·ry、x/y = value 三条式子解出来的 rx/ry，新挂的那条边精确维持约定；同根校验则是用同一条推理去验证旧约束和新等式是否打架。所以 ratio 只需拿两个"到根的比"相除，结果就是 x/y。

回滚部分为什么对：每次成功的 union 恰好改三个字段（parent[b]、size[a]、components），而这三个旧值要么必然是已知默认（parent[b] 原来必是 b 自己），要么被记进了栈（旧 size[a]）；无效 union 一个字段都不改，只占位。所以按栈倒着弹就能逐操作精确还原，任意快照点都恢复得到。find 不压缩看似吃亏，其实正是正确性的前提——一旦压缩，一次 find 会改一串没有记录的父指针，这些改动永远无法撤销。

复杂度：带权 DSU 同时用了按大小合并和路径压缩，单次操作均摊接近 O(α(n))（反阿克曼函数，n = 10^5 时也不超过 4，基本当常数看）；浮点比值有累积误差，所以比较一律用容差。回滚 DSU 不压缩，find/union 沿树走最坏 O(log n)（按大小合并保证树高不超过 log2 n，n=10^5 时约 17 层）；撤销 t 次合并是 O(t)（每弹一条栈恢复三个字段）；空间是 O(n + 历史长度)。还要记住那条限制：快照只能回到"还活着的历史祖先"，你回滚掉的那段操作历史已经丢弃，之后再用旧编号回滚是非法的（rollback 开头的范围检查会拦住）。

## 六、测试用例在测什么

- `assert calc_equation([['a','b'],['b','c']],[2,3],[['a','c'],['c','a'],['x','x']])==[6.0,1/6,-1.0]`：这是 LeetCode 399 的标准用例。前两查询测"链式相乘"（a/c=2×3=6）和"反向取倒数"（c/a=1/6）；第三个 `['x','x']` 是特殊值边界——x 从没在任何等式里出现过，即使问"x 除以 x"也返回 -1.0（变量不存在，不当作 1.0 处理）。
- 带权随机对拍（种子 140，100 轮）：每轮随机 6 个变量的真值（1..9）和 8 条随机边，边的比值取 `values[a]/values[b]`（保证自洽不冲突）。用邻接表 + BFS 独立算出任意两点的期望比值（连乘路径积），和 `d.ratio(a,b)` 容差比对。a、b 取到 0..6：孤立点（比如没被任何边碰到的 6 号）期望必是 -1.0，专门测"不存在/不连通返回 -1"的分支。
- 回滚随机测试（n=8，300 步）：每步三分之一概率回滚到随机历史位置（同时把参考边集截断到同样长度），否则随机 union 一条边并记录。每步之后做四重校验：(1) 用当前边集跑 Floyd-Warshall 传递闭包，断言任意两点 `find(i)==find(j)` 当且仅当闭包可达——连通性语义整体正确；(2) 记下 find 前后 `r.parent` 完全不变——验证 find 确实零压缩（这是回滚版的生命线）；(3) `r.snapshot()==len(edges)`——栈长与操作数严格对齐；(4) `r.components` 等于 8 个点不同根的个数——分量计数在合并和撤销后都准确。

最后打印 `N140: 所有本章断言通过`。

## 七、练习思路提示

**练习 1：把比值改为差值约束。** 提示：把"weight 是连乘的比值"换成"weight 是连加的差"：约定 `weight[x] = x − parent[x]`（x 比它父亲大多少）。路径压缩时把沿途 weight **累加**而不是累乘；union 推公式也从乘除换成加减：已知 x − y = d、x − rx = wx、y − ry = wy，那么 rx 挂 ry 时新边的权是 `wy + d − wx`。手算示例：约束 a−b=2、b−c=3，问 a−c 应得 5。注意除零挡板 `value==0` 在差值体系里要换成什么（想想零差值是否合法——是合法的，它还提供"相等"信息）。

**练习 2：对同时间秘密传播比较 BFS 与临时合并。** 提示（对应 LeetCode 2092）：把会议按时间戳分组，同一时刻的一批会议必须"同时"处理。解法 A：对每个时刻的子图做 BFS，从持有秘密的与会者出发扩散；解法 B：用本章 RollbackDSU 把该时刻的所有会议 union 起来，组内任一人有秘密则全组感染，然后 rollback 回快照，避免临时合并污染后续时刻。先手算一个两时刻小例子（比如 t=1 时 [1,2]、t=2 时 [2,3]，1 初始有秘密），分别走两种解法核对结果，再讨论两者分别适合什么数据形态（BFS 天然直观；临时合并 + 回滚在组很大、重复配对多时更省）。

## 八、对应 LeetCode 题目

- **399. Evaluate Division（除法求值）**：本章 canonical 题，`calc_equation` 就是完整解，练的是带权并查集的"相对比值 + 路径压缩连乘 + 矛盾检测"全套。
- **2092. Find All People With Secret（找出知晓秘密的所有专家）**：extension 题，同一时间的会议需要临时合并再撤销（或按时刻 BFS），练的是本章 RollbackDSU 的 snapshot/rollback 与"同时间步内成组处理"的配合，正好对应练习 2。
