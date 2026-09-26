# N053 · 队列、双端队列与循环缓冲区 —— 说人话详解

> 对应 notebook：`notebooks/07_stack_queue/053_queue_deque_implementations.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章回答一个工程味道很浓的问题：**怎么自己造一个"先来先服务"的容器，而且每次操作都是瞬间完成**。

用 Python 的 `list` 做队列有个坑：入队 `append` 很快，但出队 `pop(0)` 要把后面所有元素整体往前挪一格，队列越长越慢。循环缓冲区（环形数组）就是解药：开一块**固定大小**的数组，用 `head`（头指针）和 `size`（当前元素个数）两个整数记录状态，出队只是"head 往前走一格"，谁都不用搬。数组走到底就通过取模运算绕回开头复用空出来的格子——像一条首尾相接的跑道。

具体例子：容量 3 的循环队列，依次执行 put 1、put 2、get、put 3、put 4（cell6 的实际序列）。最后物理数组是 `[4, None, 3]`、head=2、size=2——注意 4 存在了下标 0（绕回来了），而逻辑上队列从头读到尾是 `3, 4`（先放的 1、2 已被两个 get 取走）。输出顺序 1→2（出队顺序）证明它确实是先进先出（FIFO：First In, First Out）。

本章还要做两件配套的事：一是把容器推广成**双端队列**（两头都能进出）；二是用**两个栈拼出一个队列**，体会"均摊 O(1)"的含义。

## 二、关键概念（定义）

- **队列（queue）与 FIFO**：只允许从队尾进、队头出的容器，最早进来的最早出去（先进先出）。像排队买奶茶：先排的先买到。
- **环形数组（循环缓冲区，circular buffer）**：一块固定长度的数组，下标用 `% capacity` 取模，越界就绕回 0，逻辑上首尾相接成一个环。它让"出队"不用搬移任何元素。
- **head / size**：两个状态变量。head 是逻辑队头在物理数组里的下标；size 是当前存了几个元素。队尾位置不需要单独记——它就是 `(head+size) % capacity`，随时能算出来。
- **满与空的判定**：空队列和满队列都可能碰到"head 和 tail 指到同一格"的情况，光看下标分不清。cell1 给出两条路：要么额外记一个 size（本章选这条），要么故意留一个空槽不存数据。这是环形数组最经典的坑。
- **双端队列（deque，double-ended queue）**：两头都能插入、都能删除的队列。普通队列只是它的一个子集——只允许"尾进头出"这两种操作。
- **取模回绕（mod 运算）**：`(head-1) % capacity` 在 head=0 时得到 capacity-1（不是 -1，Python 的 `%` 对负数也返回非负结果），这就是"往左走出数组边界时绕到最右端"的实现方式。
- **两栈队列（incoming/outgoing）**：一个栈只管收（incoming），一个栈只管发（outgoing）。pop 时如果 outgoing 空了，就把 incoming 整个倒进去——倒一次的代价被之后的多次 pop 分摊，平均每次还是 O(1)，这叫**均摊分析**（N014 讲过）。
- **操作成本（O(1) vs O(n)）**：O(1) 表示不论存多少元素、耗时恒定；O(n) 表示元素越多越慢（比如 `list.pop(0)` 要搬移全部剩余元素）。

## 三、解决思路（一步步推导）

**CircularDeque 的设计步骤：**

1. 构造时开 `k` 个格子的数组，`head=0`、`size=0`，一切从空开始。
2. 不变的公式（cell4 的核心）：**第 i 个逻辑元素永远住在 `(head+i) % capacity` 号格子**。队尾（最后一个元素）就是 i=size-1，队尾的"下一个空位"就是 i=size。
3. 尾插：写到 `(head+size) % capacity`，然后 size 加一。
4. 头插：先把 head 往左挪一格（`head=(head-1)%capacity`，会绕回），再在新 head 写值，size 加一。
5. 头删：把 head 格子清成 None，head 往右挪一格，size 减一。
6. 尾删：size 先减一，再把"新的最后一个位置"清成 None。
7. 每个操作进门先问一句：满了（size==capacity）还能插吗？空了（size==0）还能删/读吗？满了或空了就返回 False/-1，不抛异常——这是 LC641 的接口约定。

**手算演示（cell6 的表格，容量 3，依次 put 1、put 2、get、put 3、put 4、get）：**

| 操作 | 值 | head | size | 物理数组 | 说明 |
|------|----|------|------|----------|------|
| put | 1 | 0 | 1 | [1, None, None] | 写 (0+0)%3=0 号格 |
| put | 2 | 0 | 2 | [1, 2, None] | 写 (0+1)%3=1 号格 |
| get | — | 1 | 1 | [None, 2, None] | 1 出队，head 右移到 1 |
| put | 3 | 1 | 2 | [None, 2, 3] | 写 (1+1)%3=2 号格 |
| put | 4 | 1 | 3 | [4, 2, 3] | 写 (1+2)%3=**0** 号格，绕回！ |
| get | — | 2 | 2 | [4, None, 3] | 2 出队，head 右移到 2 |

最后一行里逻辑队列是"从 head=2 读起：data[2]=3，再 (2+1)%3=0 号格的 4"，即队列为 `3, 4`。下标 0 的格子被"已出队的旧元素空出来又被新元素 4 复用"，这就是循环复用。

**TwoStackQueue 的设计步骤：**

1. `push` 一律压进 incoming，什么都不多想。
2. `pop` 时先看 outgoing 有没有存货：有就直接弹它的栈顶。
3. outgoing 空了，就把 incoming 里全部元素逐个弹出、逐个压进 outgoing——这一倒，顺序正好反过来，最早进队的跑到了 outgoing 的栈顶，最先被弹出。
4. 两个栈都空说明队列空，抛 IndexError。

**手算演示：push 0,1,2,3,4 后 pop 一次——** incoming=[0,1,2,3,4]（0 在栈底），outgoing=[]。pop 发现 outgoing 空，倒栈：incoming 依次弹 4,3,2,1,0，outgoing 变成 [4,3,2,1,0]（0 在顶）。弹 outgoing 得 0——最早 push 的先出来，FIFO 达成；后面 4 次 pop 都不再倒栈。

## 四、代码逐段讲解

**CircularDeque（逐字照抄，逐段讲）：**

```python
class CircularDeque:
    def __init__(self,k):
        if k<1: raise ValueError('positive capacity required')
        self.data=[None]*k; self.head=0; self.size=0
    def isEmpty(self): return self.size==0
    def isFull(self): return self.size==len(self.data)
```

- `if k<1: raise ValueError(...)` 是在挡非法容量：0 或负容量的数组没有任何可用格子，与其后面出各种怪错，不如构造时就报错（cell1 的要求：容量必须为正）。
- 初始 `head=0; size=0`：数组全是 None，0 个元素。判断空/满只看 size——这正是"用 size 区分空与满"这一决策的落点。

```python
    def insertFront(self,value):
        if self.isFull(): return False
        self.head=(self.head-1)%len(self.data)
        self.data[self.head]=value; self.size+=1; return True
    def insertLast(self,value):
        if self.isFull(): return False
        self.data[(self.head+self.size)%len(self.data)]=value
        self.size+=1; return True
```

- `insertFront` 先 `self.head=(self.head-1)%len(...)` 把头指针**往左绕一格**再写——注意顺序：先挪再写，新元素才正好占据"比原队头更靠前"的位置。head=0 时 `(0-1)%3=2`，绕到数组末尾。
- `insertLast` 不需要 tail 变量：`(head+size)%capacity` 就是队尾后的第一个空位。满了插不进去就返回 False（LC 约定的返回值，不是抛异常）。

```python
    def deleteFront(self):
        if self.isEmpty(): return False
        self.data[self.head]=None; self.head=(self.head+1)%len(self.data)
        self.size-=1; return True
    def deleteLast(self):
        if self.isEmpty(): return False
        self.size-=1; self.data[(self.head+self.size)%len(self.data)]=None
        return True
    def getFront(self): return -1 if self.isEmpty() else self.data[self.head]
    def getRear(self): return -1 if self.isEmpty() else self.data[(self.head+self.size-1)%len(self.data)]
```

- `deleteFront` 把旧 head 格清成 None（帮垃圾回收、也让 cell6 的表格看得清），然后 head 右移绕环、size 减一。
- `deleteLast` 的顺序有点巧：**先 size-=1 再算下标**，这样 `(head+size)` 正好指到原来最后一个元素的位置，一行清掉。getRear 则用 `head+size-1` 指向当前最后一个元素。
- `getFront/getRear` 空的时候返回 -1（LC 的约定值），否则返回真实数据，不改动任何状态。

```python
class CircularQueue(CircularDeque):
    enQueue=CircularDeque.insertLast
    deQueue=CircularDeque.deleteFront
    Front=CircularDeque.getFront
    Rear=CircularDeque.getRear
```

- 这是"普通队列 = 双端队列的受限版"的直接体现：四个类属性只是给双端操作起了 LC622 需要的名字（enQueue=尾插、deQueue=头删），一个新方法都不用写。

```python
class TwoStackQueue:
    def __init__(self): self.incoming=[]; self.outgoing=[]
    def push(self,x): self.incoming.append(x)
    def pop(self):
        if not self.outgoing:
            while self.incoming: self.outgoing.append(self.incoming.pop())
        if not self.outgoing: raise IndexError('empty queue')
        return self.outgoing.pop()
```

- `push` 无条件压 incoming，O(1)。
- `pop` 里第一个 `if` 是倒栈：outgoing 空才倒，倒就倒干净。第二个 `if` 是在倒完之后复查：两个栈都空说明队列真的没元素，抛 IndexError。
- 倒栈那一瞬可能是 O(n)，但每个元素一生只被倒一次，长期平均是 O(1)——均摊分析的教科书例子。

## 五、为什么是对的？复杂度是多少？（说人话）

- **为什么对**：一切都可以用 cell4 那条公式验证——"第 i 个逻辑元素总位于 (head+i) mod capacity"。你逐个检查六个操作：insertLast 在 i=size 的位置放新元素然后 size+1，公式仍然成立；insertFront 相当于让所有旧元素的 i 集体加一（新元素成为 i=0），head 左移一格恰好实现了这一点；deleteFront 让旧 i≥1 的元素 i 各减一，head 右移一格也对上；deleteLast 只是拿走 i=size-1。每一步操作后公式依然成立，而这条公式保证了"早进的元素 i 小、靠近队头"，顺序就永远不会乱。空与满的判定交给 size：size==0 谁也读不到（返回 -1/False），size==capacity 谁也插不进（返回 False），两者永远不会混淆。
- **复杂度**：循环队列的六个操作都只做"算下标、写一格、改一两个整数"，最坏也是 O(1)；空间就是开数组时的 O(capacity)。两栈队列的 push 是 O(1)；pop 单次最坏 O(n)（倒栈那一刻），但均摊 O(1)。举具体数字：容量 10⁵ 的循环队列，做 10⁶ 次混合操作也就是百万次的常数操作，几秒内轻松跑完；反过来用 `list.pop(0)` 做 10⁶ 次出队，每次平均搬 5×10⁵ 个元素，总量是 5×10¹¹ 次搬移，根本跑不动。

## 六、测试用例在测什么

- `q=CircularQueue(1); assert q.enQueue(7) and not q.enQueue(8)`：最小容量边界。容量只有 1，第一个插入成功返回 True，第二个因满返回 False——专测"满判定"。
- `assert q.Front()==q.Rear()==7 and q.deQueue() and not q.deQueue()`：同一个测试继续——只有一个元素时头尾读到的都是它；删一次成功（True），再删因空返回 False——专测"空判定"和空读返回值。
- 中间那一大段（`rng=Random(53)` 起）：**1000 次随机操作的对照实验**。它用官方 `collections.deque`（容量 5 封顶）当"标准答案"：随机数种子固定为 53，所以每次运行的操作序列完全一样，可复现。四种操作随机出现（op 0/1 是头插/尾插，op 2/3 是头删/尾删），每一步都断言三件事：返回值和"预期该成功还是该失败"一致、size 和参照长度一致、getFront/getRear 与参照两端一致（空时都是 -1）。这 1000 步几乎必然覆盖"满时插、空时删、绕环读写"的所有状态组合，比手写十条用例强得多。
- `t=TwoStackQueue()` 那段：push 0 到 4，再连续 pop 5 次，断言拿回来的顺序就是 `[0,1,2,3,4]`——验证"两个 LIFO 栈拼出来的是 FIFO 队列"，且倒栈后连续 pop 不断出正确顺序。

## 七、练习思路提示

- **练习 1（不用 size 区分满与空）**：提示：经典做法是**牺牲一个空槽**——只允许存 capacity-1 个元素，规定 `head==tail` 为空、`(tail+1)%capacity==head` 为满。先手算容量 3 的队列：实际最多存 2 个元素，push 两次后第三次必须失败。练习要求你回答"容量变化"：同样开 3 格数组，可用容量从 3 变成 2，这是省掉 size 字段的代价。对照测试时记得把 cell8 随机测试里的 `<5` 改成对应的新上限。
- **练习 2（deque vs list.pop(0)）**：提示：写一个小计时实验——两种容器各做 10 万次"尾部进、头部出"，用 `time.perf_counter` 分别计时。预测：deque 几毫秒（每步 O(1)），list 要好几秒（每步 pop(0) 平均搬一半元素）。再想一层：为什么 `list.pop()`（弹尾部）不慢？因为数组的尾部本来就没有后面的人需要搬移。这个练习帮你把"容器操作成本"从口诀变成亲测数据。

## 八、对应 LeetCode 题目

- **622. Design Circular Queue**：练环形数组三件套——head/size 状态、取模回绕、满空判定，本章 `CircularQueue` 就是按它的接口写的。
- **641. Design Circular Deque**：练双端操作（头插/尾插/头删/尾删）与下标公式的对应，`CircularDeque` 是它的直接实现。
- **232. Implement Queue using Stacks**：练两栈倒换实现 FIFO 与均摊 O(1) 的直觉，对应 `TwoStackQueue`。
