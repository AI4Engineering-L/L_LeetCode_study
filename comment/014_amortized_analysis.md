# N014 · 均摊复杂度与操作计数 —— 说人话详解

> 对应 notebook：`notebooks/01_reasoning/014_amortized_analysis.ipynb`

## 一、这章要解决什么问题？（问题描述）

有些数据结构里，大多数操作便宜得要命，偶尔一次操作却贵得吓人。如果你只看"最贵那一次"，会得出"这个结构很慢"的错误结论；如果你能算"一大批操作加起来的总账"，会发现贵的那几次被便宜的操作摊平了。这一章要解决的问题是：**学会区分"单次最贵操作的成本"和"整个操作序列的总成本"，也就是均摊复杂度（amortized complexity）。**

载体是用两个栈实现一个队列。先看这个队列要干什么：

- 队列的规则是先进先出：先 push 进去的数，pop 的时候先出来。
- 输入 `push 1, push 2, push 3`，然后连 pop 三次，应该依次得到 `1, 2, 3`（谁先进队谁先出队）。

那"贵"在哪？栈只有一端能进出，队列要两端（尾进头出）。本章的方案是拿两个栈倒腾：**只有当输出栈空了，才把输入栈里的元素一次性全部反转搬过去**。这次搬运可能一次搬 n 个元素，单看这一次是 O(n) 的贵操作；但每个元素一辈子最多被搬一次，所以把 m 次操作的总账一算，均摊到每次只有 O(1)。这就是全章的核心：**单次可能贵，序列整体便宜。**

## 二、关键概念（定义）

- **均摊复杂度（amortized complexity）**：把一整串操作的总成本加起来，除以操作次数得到的平均值。它回答的是"平均每次操作花多少"，而不是"最坏那次花多少"。我们用它是因为对会偶尔"大扫除"的数据结构，均摊值才反映真实使用成本。
- **聚合法（aggregate method）**：最直接的均摊分析法——把 m 次操作的总代价老老实实加起来，再看它是 O(几倍的 m)。本章的路线就是聚合法：数一数总迁移次数，发现它不超过 push 次数。
- **记账法（accounting / banker's method）**：想象每次 push 时多收一点"预付金"存起来，等这个元素将来被搬运时用预付金付账。因为每个元素只在 push 时交一次钱、最多被搬一次，所以总预付金永远够付总搬运费，账不会赤字。cell4 说"给每次 push 预付其未来迁移成本"就是这个意思。
- **势能直觉（potential method，直觉版）**：把结构里"积压的元素"看成储蓄的势能——push 时势能升高（欠的搬运活变多），搬运发生时势能释放。只要势能不爆，总成本就有上界。
- **动态数组（dynamic array）**：知识点里提到的另一个均摊经典：Python 列表容量不够时会一次性申请更大的内存并把旧元素全部搬过去，单次 append 最坏 O(n)，但均摊 O(1)，道理和本章两栈队列同源。
- **输入栈 / 输出栈（incoming / outgoing）**：本章队列的两个栈。incoming 专门接新元素（push 往它 append），outgoing 专门出元素（pop 从它取）；outgoing 空了才把 incoming 整个倒过来。
- **"每个元素至多进出一次"（每个元素至多迁移一次）**：全章最关键的计数事实：元素从 incoming 搬到 outgoing 后就永远待在 outgoing 里（只等被 pop 掉），绝不会搬回去。所以搬运总次数 ≤ push 总次数——这就是总账线性的原因。
- **操作计数（instrumentation）**：在代码里埋一个计数器 `transfers`，实际运行时把搬运次数记录下来，用真实数字检验理论。本章的 `instrumented_push_pop` 就是干这个的。

## 三、解决思路（一步步推导）

- **Step 1：明确为什么"每次出队都倒腾"不行。** 笨办法是每次 pop 都把 incoming 整个倒出来找最底下的元素再倒回去——每次 pop 都是 O(n)，m 次操作总成本 O(nm)，太亏。
- **Step 2：改进——只在输出栈空时才整体搬运。** outgoing 空了，才把 incoming 的元素逐个 pop 出来 push 进 outgoing。由于栈是后进先出，倒完之后**最早进队的元素恰好落在 outgoing 的栈顶**，pop 直接取它就是队头。
- **Step 3：验证顺序正确性。** cell4 给出的不变量是：逻辑上的队列顺序永远等于 `reversed(outgoing) 接 incoming`。搬运这个动作本身不会打乱这个顺序（它只是把 incoming 原样反转接到 outgoing 前面），所以无论何时看，队列顺序都没变。
- **Step 4：算总账。** 每个元素从 incoming 搬到 outgoing 一次之后，只会被 pop 掉，绝不回搬。所以无论操作序列多长，搬运总次数 ≤ push 总次数。m 次操作里 push 至多 m 次，于是搬运总共至多 m 次——每次搬运本身 O(1)，总成本 O(m)，均摊每次 O(1)。
- **Step 5：诚实面对单次最坏。** 队列里积压了 n 个元素时的那次 pop，要一口气搬 n 个，单次最坏 O(n)。均摊 O(1) 和单次 O(n) 同时成立，两者不矛盾。

**手算演示（操作序列 `push 1, push 2, pop, push 3, pop, pop`，正是 cell6 表格的数据）：**

| 操作 | 输入栈 | 输出栈 | 累计迁移 |
|------|--------|--------|----------|
| push 1 | [1] | [] | 0 |
| push 2 | [1, 2] | [] | 0 |
| pop | [] | [2] | 2 |
| push 3 | [3] | [2] | 2 |
| pop | [3] | [] | 2 |
| pop | [] | [] | 3 |

逐行解说：push 1、push 2 只是往 incoming 里放，零搬运。第一次 pop 时 outgoing 是空的，触发搬运——把 incoming 里的 2、1 依次弹出压入 outgoing（得到 [2,1]，注意 1 在栈顶），累计迁移 +2；然后 pop 返回 1（最早进队的），outgoing 剩 [2]。push 3 后再 pop：outgoing 非空，直接返回 2，零搬运。最后一次 pop：outgoing 空了，把 3 搬过去（+1），返回 3。三次 pop 依次得到 1、2、3，先进先出成立；总迁移 3 次，恰好等于 push 次数 3——总账线性的预言在这个小例子上精确兑现。

## 四、代码逐段讲解

cell3 定义了一个类和一个带计数的驱动函数。

### 类：`TwoStackQueue` —— 两个栈拼成的队列

```python
class TwoStackQueue:
    def __init__(self):
        self.incoming=[]
        self.outgoing=[]
        self.transfers=0
    def push(self,x):
        self.incoming.append(x)
    def pop(self):
        if not self.outgoing:
            while self.incoming:
                self.outgoing.append(self.incoming.pop())
                self.transfers+=1
        if not self.outgoing:
            raise IndexError('pop from empty queue')
        return self.outgoing.pop()
    def empty(self):
        return not (self.incoming or self.outgoing)
```

- `__init__` 里三个字段：`incoming` 输入栈（接新元素）、`outgoing` 输出栈（出队用）、`transfers` 迁移计数器（纯属教学测量用，算法本身不需要它）。
- `push(self,x)`：只做一件事——append 到 incoming。永远 O(1)，从不搬运。
- `pop` 的第一段 `if not self.outgoing: while self.incoming: ...`：**只有**输出栈空了，才把输入栈倒空：`self.incoming.pop()` 从输入栈顶取一个（最后进的），`append` 压进输出栈，于是最早进的元素最后压入、落在输出栈顶。每搬一个 `transfers+=1` 记一笔账。
- `pop` 的第二段 `if not self.outgoing: raise IndexError('pop from empty queue')`：搬完（或本来就）两栈全空还想要元素，说明是对空队列 pop——抛 IndexError，和 Python 列表空时取元素的行为一致。这段是边界守卫，防止静默返回 None 之类的错误值。
- `return self.outgoing.pop()`：从输出栈顶取元素，这个元素就是当前队头（最早入队且未出队的）。
- `empty`：`not (self.incoming or self.outgoing)`——两个栈都空，队列才是空。`or` 短路：任一栈非空整个表达式为真值，not 一下得到 False（非空）。
- 整个类的"聪明"只浓缩在一个判断里：`if not self.outgoing`。搬运是**懒**的——能不搬就不搬，只有逼不得已（输出栈空还要出队）才一次性搬完。均摊省钱的源头就是这份"懒惰"。

### 函数：`instrumented_push_pop` —— 边跑边记账的驱动器

```python
def instrumented_push_pop(ops):
    queue=TwoStackQueue()
    popped=[]
    trace=[]
    for op,value in ops:
        if op=='push': queue.push(value)
        elif op=='pop': popped.append(queue.pop())
        else: raise ValueError('unknown operation')
        trace.append((op,list(queue.incoming),list(queue.outgoing),queue.transfers))
    return popped,queue.transfers,trace
```

- `ops` 是形如 `[('push',1),('pop',None),...]` 的操作序列，每个元素是（操作名，附带值）。
- `for op,value in ops` 解包每条指令；`push` 就调 push，`pop` 忽略 value 调 pop 并把返回值收进 `popped`；操作名不认识就抛 ValueError 挡住拼写错误。
- `trace.append((op, list(...), list(...), queue.transfers))`：每步操作后拍一张快照。注意特意写了 `list(...)` 做拷贝——不拷贝的话，trace 里存的是栈对象的引用，后面栈一变，历史快照会跟着变，表就全错了。
- 返回三元组：出队结果列表、总迁移次数、逐步快照。cell6 的表格就是拿 trace 生成的，第三节那张手算表和它逐行对应。

## 五、为什么是对的？复杂度是多少？（说人话）

**为什么队列顺序永远正确？** cell4 的论证翻成大白话：任何时刻，把 outgoing 从栈底到栈顶读出来再倒个头，然后接上 incoming 从栈底到栈顶，得到的正好是"排队顺序"。为什么？因为 incoming 里永远是"后进队的在下层"，一次整体反转把它接到 outgoing 上，早进队的恰好排在离出口最近的地方；而这次搬运只是把两段拼接，不改变各自的相对次序。所以每次 pop 从 outgoing 栈顶拿到的，必然是当前最早入队且还没出队的元素——先进先出成立。

**为什么总账是线性的？** 数一数搬运：一个元素被 push 进 incoming 后，它要么一直躺着不动，要么在某次 outgoing 空的 pop 里被搬进 outgoing；搬进 outgoing 之后它的命运只剩被 pop 掉，**绝不会搬回 incoming**。所以每个元素一生至多被搬运一次，n 个元素总共至多搬 n 次。也就是说，无论 m 次操作如何交错，`transfers ≤ push 次数 ≤ m`。用记账法说：每次 push 时预付它未来那一次搬运的钱，总预付金一定够付总搬运费，账不赤字。

**复杂度到底是什么？** 分三层说清（cell4 原文"m 次合法操作总 O(m)，单次 pop 最坏 O(n)、均摊 O(1)，存储 O(n)"）：单次 push 恒为 O(1)；单次 pop 最坏 O(n)——队列积压 n 个元素时那次 pop 要一口气全搬；但 m 次操作的总成本是 O(m)，均摊每次 O(1)。具体数字感受：一百万次操作（一半 push 一半 pop），最笨的估法会担心"某次 pop 搬五十万"，但总账告诉我们全部搬运加起来不超过一百万次，整体一秒钟内轻松跑完。空间上，两个栈合计存的元素不超过当前队列长度 n，所以存储 O(n)；transfers 计数器只是 O(1) 的一个整数。

用一张小表把"单次视角"和"序列视角"并排放，差别一目了然：

| 视角 | push（单次） | pop（单次最坏） | m 次操作总计 | 均摊每次 |
|------|--------------|------------------|--------------|----------|
| 只看单次最坏 | O(1) | O(n) | —（会高估成 O(nm)） | — |
| 看整段序列 | — | — | O(m) | O(1) |

注意两行并不矛盾：它们回答的是不同的问题。"这个队列会不会被某一下卡住"看第一行，"长期用起来贵不贵"看第二行——均摊分析的价值就是把第二行算出来。

## 六、测试用例在测什么

cell8 的两段测试：

- `a,moves,_=instrumented_push_pop([('push',1),('push',2),('push',3),('pop',None),('pop',None),('pop',None)])` 然后 `assert a==[1,2,3] and moves==3`：**正常值 + 总账测试**。三个元素先进后出三次，出队顺序必须是 [1,2,3]（先进先出的直接验证）；搬运总数必须是 3——三次 push、一次触发搬运（把 3、2、1 一次搬完），理论"迁移次数 ≤ push 次数"在这里取到等号，用真实计数器钉死了均摊论证。
- `q=TwoStackQueue(); for i in range(20): q.push(i); assert q.pop()==i`：**交错操作 + 即时出队测试**。push 完立刻 pop，重复 20 轮，每轮 pop 出来的必须刚 push 进去的 i（此时队列里只有它，队头就是它）。
- `assert q.transfers==20 and q.empty()`：**总账复核 + 空状态测试**。20 轮里每轮都触发一次"搬 1 个元素"，所以累计迁移恰为 20——再次验证迁移数从不超 push 数；最后两个栈都必须空，确认没有元素泄漏滞留。

三段测试各管一段，分工明确：

| 断言 | 类型 | 它防的是哪类 bug |
|------|------|------------------|
| `a==[1,2,3]` | 正常值 | 先进先出顺序错 |
| `moves==3` | 总账 | 搬运比"每元素一次"更多（来回倒腾） |
| 20 轮 push 后立刻 pop 得 i | 交错操作 | 立即出队时取错元素 |
| `q.transfers==20` | 总账复核 | 计数与理论不符 |
| `q.empty()` | 空状态 | 元素滞留没出队 |

## 七、练习思路提示

cell9 的两道练习：

- **练习 1（构造某次出队很慢的序列）**：目标是亲眼看见"单次 pop 最坏 O(n)"。提示：先连着 push 一大批（比如 5 个）让队列积压，然后来一次 pop——这一次 pop 要搬全部 5 个元素，transfers 一下跳 5。用 `instrumented_push_pop` 跑你设计的序列，从 trace 表里指出哪一行的累计迁移突然变大。手算示例：`push 1..5` 后接一个 `pop`，该行迁移从 0 跳到 5。边界情况：两个栈全空时 pop 应抛 IndexError，把这条也记进你的手算。
- **练习 2（证明一批操作总成本线性）**：把第五节的论证自己写一遍。提示骨架：设操作序列有 p 次 push、q 次 pop，总 m=p+q 次；关键事实是每个元素至多被搬运一次（它被搬进 outgoing 后只会被 pop 掉，不会回搬），所以总迁移 ≤ p；每次搬运是常数步，push 本身各 O(1)，于是总成本 ≤ c·p + c·m = O(m)。用手算例子验证：设计一个 8 步的序列，先手推每步的 transfers 累计值，再跑 `instrumented_push_pop` 比对你的预测和计数器是否一致。

## 八、对应 LeetCode 题目

cell10 列出的题目：

- **232. Implement Queue using Stacks（用栈实现队列，preview）**：这题就是 `TwoStackQueue` 的原题——练的是"输出栈空才整体倒腾"的懒搬运技巧，以及"每元素至多迁移一次 ⇒ 均摊 O(1)"的账本论证。标 preview 说明它是后续正式练习的预告，本章先把证明写扎实。

照 notebook 原文提醒：以上条目用于知识映射，本章实现遵循教学契约，刷题时以 LeetCode 官方题面与评测为准。
