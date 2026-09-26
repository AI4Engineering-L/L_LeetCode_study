# N068 · 约束满足、数独与 N 皇后 —— 说人话详解

> 对应 notebook：`notebooks/09_recursion_backtracking/068_constraint_satisfaction_queens_sudoku.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章讲**约束满足问题（CSP）**：题目给你一堆变量和一堆"哪些组合不允许"的规则，你要找到一个（或所有）给变量赋值的方案，使得所有规则同时满足。两道代表题：

**题一：N 皇后。** 在 n×n 棋盘上放 n 个皇后，要求任何两个皇后不互相攻击。皇后攻击同行、同列、两条对角线方向的格子，所以规则翻译成：每行恰好一个皇后、每列至多一个、每条对角线至多一个。比如 n=4 时恰好有 2 个解，其中一个长这样（Q 是皇后，. 是空）：

```
.Q..
...Q
Q...
..Q.
```

另一个解是它的镜像。n=1 时唯一解就是孤零零一个 Q。

**题二：数独求解器。** 9×9 的盘面，部分格子已填数字，你要把剩下的空格全部填上，满足：每行 1..9 各出现一次、每列各出现一次、每个 3×3 宫各出现一次。求解器还必须诚实——盘面无解时要返回 False，而不是硬填一锅违反规则的数字交差。notebook 测试里有一个无解盘面：第 0 行是 `.12345678`（这行缺 9），可第 3 行第 0 列已经放了 9，于是 (0,0) 这个格子既需要 9 又不许是 9，无解。

这类问题的关键心态和前几章不同：**别等全填完再检查，一发现冲突就立刻放弃这个分支**。越早发现死路，省下的搜索越多。

## 二、关键概念（定义）

- **约束传播 / 尽早拒绝**：每放一个皇后或填一个数字，就立刻用它更新"哪些位置/数字不能再用了"，下一步只在还合法的候选里挑。把检查从叶子提前到每一步，就是剪枝的本质。
- **行、列、对角线约束（N 皇后）**：因为每行恰好放一个，我们按行递归，每行只需决定"放哪一列"。"列"用一个集合就能查；两条对角线的巧妙之处在于用数字标识：从左上到右下的对角线上所有格子 `行号-列号` 相同（比如 (0,0),(1,1),(2,2) 都是 0），从右上到左下的对角线上所有格子 `行号+列号` 相同（比如 (0,2),(1,1),(2,0) 都是 2）。于是两个集合就能查全部对角线。
- **候选集（candidates）**：数独里某个空格还能填的数字集合，等于 1..9 减去"它所在行已用的、所在列已用的、所在宫已用的"。用三个集合数组 `rows/cols/boxes` 维护"已用"，减法一次算出候选。
- **宫（box）**：数独的 3×3 小九宫。格子 (r,c) 属于第 `(r//3)*3+c//3` 号宫——`r//3` 算出它在上中下哪一横带，`c//3` 算出左中右哪一竖带，两个拼出宫编号 0..8。
- **最少候选优先（MRV，Minimum Remaining Values）**：每次优先填"候选最少的空格"。直觉是：候选只有 1 个的格子没得选，先填它等于免费推进；候选少的格子也最容易提前暴露矛盾。注意这是**搜索顺序**的优化——换换填格顺序，解集合不变，但搜索树小很多。
- **位掩码扩展**：cell0 提到的进阶方向——用整数的二进制位代替集合（第 i 位是 1 表示数字 i 可用），集合运算变成位与位或，速度更快。本章实现用集合，思路是通用的。
- **区分"有解"与"无解"**：求解器的返回值 True/False 必须真实反映盘面可解性，且失败时要把所有试填的痕迹擦干净，把原题原样还给调用者。

## 三、解决思路（一步步推导）

**Step 1：N 皇后按行递归。** `visit(row)` 表示前 row 行都放好了且互不冲突，现在决定第 row 行放哪列。每行必放一个，所以行冲突从结构上就不存在。

**Step 2：三个集合查冲突。** 放之前问三个问题：这列有人吗（columns）？这条 `行-列` 对角线有人吗（diagonal1）？这条 `行+列` 对角线有人吗（diagonal2）？都没人才能放。

**Step 3：放了就记、退了就删。** 放皇后时把列号和两个对角线标识加进集合，递归下一行，返回后全部删掉。这样兄弟分支看到的又是干净的棋盘。

**Step 4：到第 n 行收盘。** `chosen` 里存着每行皇后所在的列，用字符串拼出棋盘图收集。

**Step 5：数独先扫描盘面。** 一遍扫描把已填数字登记进 rows/cols/boxes 三个集合数组，同时把空格坐标收进 empty 列表。扫描时若发现题面本身就有冲突（同一行两个 5），直接返回 False——题都不合法，谈不上求解。

**Step 6：MRV 挑格子。** 每次从"还没填的空格"里挑候选最少的那个填，用交换把它挪到 empty 列表前端，方便按位置递归。

**Step 7：试填与回溯。** 对选中格子的每个候选数字：填进盘面、登记三个集合、递归；成功返回 True，失败就撤销（删登记、恢复 '.'），试下一个候选。所有候选都失败就把交换还原并返回 False。

**手算演示 1：n=4 皇后，看分支怎么死、怎么活。**

1. `visit(0)` 试 col=0：登记列 0、对角线 d1=0-0=0、d2=0+0=0，chosen=[0]。
2. `visit(1)` 试列：col=0 列冲突；col=1 的 d1=1-1=0 冲突；col=2 干净（d1=-1、d2=3），放，chosen=[0,2]。
3. `visit(2)` 试列：col=0 列冲突；col=1 的 d2=2+1=3 冲突（被 (1,2) 占了）；col=2 列冲突；col=3 的 d1=2-3=-1 冲突（也被 (1,2) 占了）——**整行无解，回溯**。
4. `visit(1)` 改试 col=3：干净（d1=-2、d2=4），放，chosen=[0,3]。`visit(2)`：col=0 列冲突；col=1 干净（d1=1、d2=3 都没人占），放，chosen=[0,3,1]。`visit(3)`：col=0、1、3 都列冲突，col=2 的 d1=3-2=1 冲突（被 (2,1) 占了）——无解，回溯。`visit(2)` 再试 col=2：d1=0 冲突（被 (0,0) 占了）；col=3 列冲突——无解，回溯。`visit(1)` 候选耗尽，回溯。`visit(0)` 的 col=0 分支宣告死亡。
5. `visit(0)` 改试 col=1：登记 d1=-1、d2=1。`visit(1)`：col=0 的 d2=1+0=1 冲突；col=2 的 d1=1-2=-1 冲突；col=3 干净（d1=-2、d2=4），放。`visit(2)`：col=0 干净（d1=2、d2=2），放。`visit(3)`：col=0、1、3 列冲突，col=2 干净（d1=3-2=1、d2=3+2=5 都没人占），放！chosen=[1,3,0,2]，走到第 4 行 row==n——**收集解**，就是第一节那张棋盘图。
6. 之后继续回溯枚举，`visit(0)` 的 col=2 分支对称地产出镜像解 [2,0,3,1]；col=3 分支与 col=0 对称，全灭。总计 2 个解。

你看，n=4 就已经要"死几条分支才见活路"了，这正是 CSP 回溯的日常。

**手算演示 2：MRV 挑格子。** 假设某空格的行已有 {1,2,3,4,5,6,7}、列已有 {2,3,8}、宫已有 {5,9}，它的候选 = {1..9} - {1..7} - {2,3,8} - {5,9} = 空——这格无解，整条分支立刻判死；若候选只剩 {6} 一个，MRV 会第一个填它，因为别无选择、零分支。这就是"候选最少者优先"的威力。

## 四、代码逐段讲解

### 4.1 `solve_n_queens(n)`

```python
def solve_n_queens(n):
    if n<0: raise ValueError('n must be nonnegative')
    out=[]; columns=set(); diagonal1=set(); diagonal2=set(); chosen=[]
    def visit(row):
        if row==n:
            out.append(['.'*c+'Q'+'.'*(n-c-1) for c in chosen]); return
        for col in range(n):
            if col in columns or row-col in diagonal1 or row+col in diagonal2: continue
            columns.add(col); diagonal1.add(row-col); diagonal2.add(row+col); chosen.append(col)
            visit(row+1)
            chosen.pop(); columns.remove(col); diagonal1.remove(row-col); diagonal2.remove(row+col)
    visit(0); return out
```

- `if n<0: raise ValueError('n must be nonnegative')`：输入契约，n 为负直接报错（负数棋盘无意义）。
- 四个容器各司其职：columns/diagonal1/diagonal2 是三个"占用登记簿"，chosen 按行序存每行皇后所在列。
- `if row==n:`：n 行全部放完，当前 chosen 就是一个解；列表推导按每行的列号 c 拼出 `'.'*c+'Q'+'.'*(n-c-1)` 这样一行字符串（c 个点、一个 Q、补齐剩下的点）。
- `if col in columns or row-col in diagonal1 or row+col in diagonal2: continue`：三本登记簿查一遍，任何一本已有记录就跳过这个列——这就是"尽早拒绝"。
- 中间三行 add + append 是 choose，`visit(row+1)` 是 explore，最后四个 remove/pop 是 undo；登记和注销的项目一一对应。
- `visit(0); return out`：从第 0 行开始；返回所有解（LeetCode 51 要求全部解）。

### 4.2 `solve_sudoku(board)`

```python
def solve_sudoku(board):
    if len(board)!=9 or any(len(row)!=9 for row in board): raise ValueError('9 by 9 board required')
    rows=[set() for _ in range(9)]; cols=[set() for _ in range(9)]; boxes=[set() for _ in range(9)]; empty=[]
    digits=set('123456789')
    for r in range(9):
        for c in range(9):
            value=board[r][c]; box=(r//3)*3+c//3
            if value=='.': empty.append((r,c)); continue
            if value not in digits: raise ValueError('invalid cell')
            if value in rows[r] or value in cols[c] or value in boxes[box]: return False
            rows[r].add(value); cols[c].add(value); boxes[box].add(value)
    def candidates(r,c): return digits-rows[r]-cols[c]-boxes[(r//3)*3+c//3]
    def visit(position):
        if position==len(empty): return True
        best=min(range(position,len(empty)),key=lambda i:len(candidates(*empty[i])))
        empty[position],empty[best]=empty[best],empty[position]
        r,c=empty[position]; box=(r//3)*3+c//3
        for value in sorted(candidates(r,c)):
            board[r][c]=value; rows[r].add(value); cols[c].add(value); boxes[box].add(value)
            if visit(position+1): return True
            rows[r].remove(value); cols[c].remove(value); boxes[box].remove(value); board[r][c]='.'
        empty[position],empty[best]=empty[best],empty[position]
        return False
    return visit(0)
```

- 第一行 raise：形状契约——必须是 9×9。
- `rows/cols/boxes` 是 9 个集合的数组（列表推导建 9 个独立集合），分别登记每行/列/宫已用数字；`empty` 收集空格坐标。
- 扫描双重循环：空格进 empty；数字则先验合法性（必须是 1..9 里的字符，且在行/列/宫中没有重复——题面自带冲突就 `return False`），再登记。`box=(r//3)*3+c//3` 是宫编号公式。
- `candidates(r,c)`：用集合减法一行算出候选 = 全部数字 - 行已用 - 列已用 - 宫已用。
- `best=min(range(position,len(empty)),key=...)`：MRV——在"尚未处理"的空格（下标 position 往后）里挑候选数最少的。`min` 按 key 比较，返回下标。
- 两个 swap：把选中的格子换到 position 位置，这样 `visit(position+1)` 自然表示"前 position 个空格已定"；失败路径末尾还要换回去，因为换位也是对状态的修改，同样要撤销。
- `for value in sorted(candidates(r,c))`：按从小到大试填（排序让尝试顺序确定，便于复现）。
- 中间四行 add/赋值是 choose；`if visit(position+1): return True` 是 explore 且短路（找到第一个解就一路 True 上传）；后面四个 remove/恢复 '.' 是 undo。
- `return visit(0)`：函数返回 True（解开且 board 已是解）或 False（无解且 board 已还原）。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么三个集合就够查所有冲突？** N 皇后的行冲突被"按行递归、每行放一个"的结构消掉了；列冲突看列号即可；对角线冲突靠那两个数字恒等式——同一条"↘"对角线上所有格子的行号减列标是同一个数，同一条"↙"对角线上行号加列号是同一个数。所以"放之前查三个集合"等价于"和之前所有皇后逐个比对"，但查集合是 O(1)。

**为什么 MRV 不改变正确性？** 它只是决定"下一个先填哪个空格"。数独的解不依赖你填格子的先后顺序——一个盘面要么有解要么没有，换顺序不会把有解变成无解。MRV 挑的分支少，走得快，但"试遍所有候选、失败就撤销"的完备逻辑一点没少，所以该找到的解一样找得到，该判无解的一样判无解。

**为什么失败后盘面完好如初？** 每一层失败路径都把"填的数字从三个集合删掉、格子恢复 '.'、两个空格换位换回"，层层的撤销叠加起来，回到最外层时所有痕迹都被擦掉了。测试里用 deepcopy 前后对比验证了这一点。

**复杂度（结合数字说）：** N 皇后最坏是 O(n!) 级别——第一行 n 种选择、第二行至多 n-1 种……n=6 时 720 量级瞬间完成；n=8 经典题 40320 量级也很快；n=13、14 开始变慢，n 再大就得靠位运算等优化。数独的粗上界是 O(9ᴱ)（E 是空格数，每格至多 9 个候选），51 个空格的粗界是天文数字，但 MRV 加冲突检查让实际搜索树小得可怜——人出的数独题往往有唯一解，几乎一路"被迫"填下去；真正的坏例子是几乎空白的对抗性盘面，那时指数本性才暴露。工作空间方面，集合数组是常数级（9×3 个集合），递归深度最多 E。

## 六、测试用例在测什么

cell8 逐条解释（配合 deepcopy 快照）：

- `assert len(solve_n_queens(4))==2 and len(solve_n_queens(1))==1`：正常值与最小值。n=4 恰有 2 解是数学事实；n=1 是最小棋盘，唯一解。
- `for n in range(1,7): for board in solve_n_queens(n): pos=[row.index('Q') for row in board]; ...`：**解的合法性自检**。把每行 Q 的列号提出来，检查 `len(set(pos))==n`（列互不相同）、`len({r-c ...})==n`（↘对角线互不相同）、`len({r+c ...})==n`（↙对角线互不相同）。这组断言不检查"是否漏解"，但保证"输出里的每个棋盘都真的是解"。
- 数独部分先解 LeetCode 37 的经典题（`puzzle` 是那张著名的 53..7.... 盘），然后四组 all：每行恰是 1..9、每列恰是 1..9、每个 3×3 宫恰是 1..9，以及 `puzzle[r][c]=='.' or puzzle[r][c]==b[r][c]`——**预填数字不许被改动**（求解器不能篡改题目）。
- 无解盘面测试：`unsolved` 构造出"(0,0) 只能填 9 但列里已有 9"的死局；断言 `solve_sudoku(unsolved) is False`（诚实报告无解）且 `unsolved==old`（失败后盘面零残留）。这两条合起来正是第一节强调的"区分无解与乱填"。

## 七、练习思路提示

- **练习 1（比较固定填格顺序与最少候选优先）**：思路是把 `best=min(...)` 一行改成 `best=position`（永远按扫描顺序填），跑同一批盘面对比。提示观察点：两种版本答案必须完全相同（正确性不变），但递归调用次数（可在 visit 里挂个计数器）差几个数量级；越空旷的盘面差距越明显，几乎填满的盘面差距小。手算示例：某盘面有一个只剩候选 {7} 的格子，MRV 第一步就零成本推进，固定顺序可能要先在别处碰几次壁。
- **练习 2（统计搜索节点而非只比运行时间）**：思路是在 visit 函数入口加一行计数（全局变量或 nonlocal），对"节点数"和"耗时"分别建表。提示要点：运行时间受机器波动和集合常数影响，节点数才是搜索树大小的干净度量；你可以发现 MRV 的节点数下降而单节点开销略升（每次要算一遍 min），两者乘积才是真实耗时——这正是"度量要度量到本质"的练习意图。手算示例：n=4 皇后把 visit 调用数数出来（按第三节流程画树数节点），再和 n=5 对比增长速度。

## 八、对应 LeetCode 题目

- **51. N-Queens**：对应 `solve_n_queens`，练的是"集合查冲突 + 行号±列号标识对角线 + 输出棋盘图"这一整套 CSP 基本功。
- **37. Sudoku Solver**：对应 `solve_sudoku`，练的是"三集合登记簿、候选集减法、MRV 挑格、失败全撤销"，以及"无解返回 False"的诚实契约。

一句话总结：约束满足问题的通用套路是**"每走一步就检查，用集合把检查变 O(1)，用 MRV 决定先走哪步，失败就把痕迹擦干净"。**
